"""Consistent module tools and tab-background regeneration, without user data."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock,patch
import tkinter as tk
import unittest
import customtkinter as cst
from PIL import Image
from app.ui.surfaces import surface,_crop_region
from app.ui.learning_layout import background
from app.statistics.tabs import StatisticsTabs
from app.grammar.editor import GrammarEditor
from app.grammar.editor_theory import GrammarTheoryEditor
from app.tests.test_grammar_editor import questions
from app.tests.test_grammar_editor_theory import source


class ModulePanelTests(unittest.TestCase):
    def test_session_button_labels_fit_in_all_languages(self):
        from app.grammar.practise import GrammarController
        from app.tests.test_grammar_category_filter import questions as training_questions
        from app.shared.translations import translate
        for language in ('cs','de','en','es','fr','sk'):
            with patch('app.shared.settings.T',side_effect=lambda key:translate(key,language)):
                controller=GrammarController(self.root,training_questions(),'unused.csv',Mock(),learned_by='Czech')
                self.root.update()
                for button in (controller.view.theory,controller.view.category_filter):
                    self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                    self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height())
                self.assertLessEqual(abs(controller.view.shortcuts._label.winfo_rootx()-controller.view.mode._label.winfo_rootx()),3)

    def test_summary_cards_share_width_and_stay_centered_with_two_or_three_modules(self):
        from types import SimpleNamespace
        from app.statistics.components import summary_cards
        from app.statistics.viewer import _set_conjugation_available
        host=cst.CTkFrame(self.root);host.pack(fill='both',expand=True)
        container,cards=summary_cards(host,['Vocabulary','Conjugation','Grammar'])
        window=SimpleNamespace(summary_cards=cards,statistics_tabs=Mock())
        for available in (False,True,False):
            _set_conjugation_available(window,available);self.root.update()
            visible=[cards[0].master,cards[2].master]+([cards[1].master] if available else [])
            widths=[card.winfo_width() for card in visible]
            self.assertLessEqual(max(widths)-min(widths),2)
            left=visible[0].winfo_rootx();right=visible[-1].winfo_rootx()+visible[-1].winfo_width()
            self.assertLessEqual(abs((left+right)/2-(container.winfo_rootx()+container.winfo_width()/2)),2)

    def test_grammar_session_is_on_right_and_answer_actions_are_separate(self):
        from app.grammar.practise import GrammarController
        from app.tests.test_grammar_category_filter import questions as training_questions
        with patch('app.shared.settings.T',side_effect=lambda key:key):
            controller=GrammarController(self.root,training_questions(),'unused.csv',Mock(),learned_by='Czech')
            self.root.update();view=controller.view
            for item in (view.counter,view.score,view.mode,view.theory,view.category_filter,view.shortcuts):
                self.assertIs(item.master,view.session_panel)
            self.assertIs(view.prompt.master,view.question)
            self.assertIs(view.anchor.master,view.question)
            self.assertIsNot(view.reveal.master,view.session_panel)
            self.assertEqual(view.reveal.master.cget('fg_color'),'transparent')
            self.assertGreater(view.session_panel._parent_frame.winfo_rootx(),view.question._parent_frame.winfo_rootx())
            self.assertGreater(view.next.grid_info()['padx'],0)
            self.assertFalse(hasattr(view,'previous_category'))
            self.assertFalse(hasattr(view,'previous_theory'))
            scale=view.shortcuts._get_widget_scaling()
            # Verify the logical spacing exactly; Tk/CTk 6 may round a fractional
            # DPI pixel differently from Python round (7.5 -> 7 rather than 8).
            self.assertEqual(view.shortcuts._last_geometry_manager_call['kwargs']['pady'],(6,12))
            for actual,expected in zip(view.shortcuts.grid_info()['pady'],(6*scale,12*scale)):
                self.assertLessEqual(abs(actual-expected),1)

    def setUp(self):
        try:self.root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        self.root.geometry('1400x900');self.root.update()
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy();self.assertFalse(self.errors)

    def test_question_and_theory_actions_share_green_panel_and_have_exit(self):
        with TemporaryDirectory() as folder,patch('app.shared.settings.T',side_effect=lambda key:key):
            folder=Path(folder)
            for editor_type,name,data in [(GrammarEditor,'English_gra.csv',questions()),
                                          (GrammarTheoryEditor,'Czech_English_gra_ex.csv',source())]:
                path=folder/name;data.to_csv(path,sep=';',index=False)
                editor=editor_type(self.root,'English',path,Mock());self.root.update()
                view=editor.view
                self.assertEqual(view.tools.cget('fg_color'),'#d7dfca')
                self.assertIsNot(view.category_filter.master,view.tools)
                self.assertIs(view.category_filter.master.master,view.header)
                self.assertIs(view.query.master,view.category_filter.master)
                self.assertLess(view.category_filter.grid_info()['row'],view.query.grid_info()['row'])
                self.assertIs(view.count.master,view.tools)
                self.assertIs(view.shortcuts.master,view.tools)
                labels=[child.cget('text') for child in view.header.winfo_children() if isinstance(child,cst.CTkButton)]
                self.assertIn('Exit app',labels)
                self.assertTrue(any(isinstance(child,cst.CTkLabel) and child.cget('image') for child in view.header.winfo_children()))

    def test_changing_available_tabs_reconnects_every_new_button_surface(self):
        host=cst.CTkFrame(self.root);host.pack(fill='both',expand=True)
        backdrop=background(host,'statistics_warm_v2.png')
        tabs=StatisticsTabs(host,lambda key:key);tabs.pack(fill='both',expand=True,padx=20,pady=20)
        layer=surface(tabs,backdrop);nav=surface(tabs.navigation,layer)
        for button in tabs.navigation.winfo_children():
            if isinstance(button,cst.CTkButton):surface(button,nav)
        for available in (False,True,False,True):
            tabs.set_conjugation_available(available);self.root.update();nav.paint()
            for button in tabs.navigation.winfo_children():
                if not isinstance(button,cst.CTkButton):continue
                self.assertTrue(hasattr(button,'_surface'))
                button._surface.paint()
                image=button._surface._image
                self.assertIsNotNone(image)
                self.assertNotEqual(image.getpixel((0,0)),(0,0,0))

    def test_temporary_out_of_bounds_crop_never_introduces_black_pixels(self):
        image=Image.new('RGB',(20,20),'#d7dfca')
        for bounds in [(-5,-5,30,30),(15,15,40,40),(30,30,50,50)]:
            cropped=_crop_region(image,bounds)
            self.assertEqual(cropped.getextrema(),((215,215),(223,223),(202,202)))

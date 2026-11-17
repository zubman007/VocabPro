"""Save navigation, translated geometry and corrupt-data regression scenarios."""
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest import TestCase
from unittest.mock import Mock, patch
import customtkinter as cst
from app.grammar.editor import GrammarEditor
from app.grammar.editor_theory import GrammarTheoryEditor
from app.grammar.practise import GrammarController
from app.repositories.grammar import Load_questions_from_csv
from app.tests.test_grammar_editor import questions
from app.tests.test_grammar_editor_theory import source
from app.tests.test_grammar_category_filter import questions as lesson
from app.shared.translations import translate
from app.ui.module_style import HEADER


class ModuleConsistencyTests(TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root=cst.CTk()
        self.root.geometry('1400x900')
        self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for timer in self.root.tk.call('after','info'):
            self.root.tk.call('after','cancel',timer)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def test_both_grammar_editors_save_and_leave_once(self):
        with TemporaryDirectory() as folder:
            for cls,data,name in ((GrammarEditor,questions(),'English_gra.csv'),
                    (GrammarTheoryEditor,source(),'Czech_English_gra_ex.csv')):
                with self.subTest(editor=cls.__name__):
                    path=Path(folder)/name
                    data.to_csv(path,sep=';',index=False)
                    back=Mock()
                    editor=cls(self.root,'English',path,back)
                    with patch('app.grammar.editor.messagebox.askyesnocancel') as ask:
                        self.assertTrue(editor.save())
                        ask.assert_not_called()
                    back.assert_called_once()
                    self.assertTrue(editor.bindings.closed)

    def test_practice_empty_and_dirty_save_both_leave(self):
        for dirty in (False,True):
            with self.subTest(dirty=dirty):
                back=Mock()
                controller=GrammarController(self.root,lesson(),Path(self.directory.name)/'English_gra.csv',back)
                if dirty:controller.choose(0)
                with patch('app.grammar.practise.save_answers') as save:
                    self.assertTrue(controller.save())
                    self.assertEqual(save.call_count,int(dirty))
                back.assert_called_once()
                self.assertTrue(controller.bindings.closed)

    def test_failed_editor_save_preserves_screen_and_dirty_data(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'English_gra.csv'
            questions().to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            back=Mock()
            editor=GrammarEditor(self.root,'English',path,back)
            with patch.object(editor.document,'save',side_effect=PermissionError('locked')), \
                    patch('app.grammar.editor.messagebox.showerror') as error:
                self.assertFalse(editor.save())
            error.assert_called_once()
            back.assert_not_called()
            self.assertFalse(editor.bindings.closed)
            self.assertEqual(path.read_bytes(),before)

    def test_session_and_header_labels_fit_all_locales_and_sizes(self):
        start=perf_counter()
        for size in ('1200x800','1600x950'):
            self.root.geometry(size)
            for locale in ('cs','en','de','es','fr','sk'):
                with self.subTest(size=size,locale=locale), \
                        patch('app.shared.settings.T',side_effect=lambda key:translate(key,locale)):
                    controller=GrammarController(self.root,lesson(),Path(self.directory.name)/'English_gra.csv',Mock())
                    self.root.update()
                    view=controller.view
                    self.assertEqual(view.header.cget('fg_color'),HEADER)
                    self.assertEqual(view.counter.cget('font')[1],24)
                    for host in (view.header,view.session_panel):
                        for button in host.winfo_children():
                            if not isinstance(button,cst.CTkButton):continue
                            self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                            self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height())
                    if controller.session.current.get('category'):
                        self.assertIn('\n',view.mode.cget('text'))
        elapsed=perf_counter()-start
        print(f'PERF translated grammar layout: 12 scenarios in {elapsed:.2f}s')
        self.assertLess(elapsed,90)

    def test_extra_csv_fields_report_row_and_never_rewrite_source(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'English_gra.csv'
            path.write_text('prompt;anchor;option_1;option_2;option_3;option_4\n'
                'Choose;Sentence;a;b;c;d;unexpected\n',encoding='utf-8')
            before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'row 2'):
                Load_questions_from_csv(path)
            self.assertEqual(path.read_bytes(),before)

    def test_conjugation_header_and_bottom_actions_share_training_style(self):
        from app.conjugation.layout import build
        for locale in ('cs','en','de','es','fr','sk'):
            with self.subTest(locale=locale),patch('app.shared.settings.T',side_effect=lambda key:translate(key,locale)):
                view=build(self.root,[('s1','Yo')],Mock(),Mock(),Mock(),Mock(),Mock())
                self.root.update()
                self.assertEqual(view.header.cget('fg_color'),HEADER)
                footer=view.footer
                buttons=[w for w in footer.winfo_children() if isinstance(w,cst.CTkButton)]
                self.assertEqual(len(buttons),2)
                self.assertEqual(footer.grid_columnconfigure(0)['uniform'],'actions')
                self.assertEqual(footer.grid_columnconfigure(1)['uniform'],'actions')
                # CTk rounds the two scaled edges independently on Windows.
                self.assertLessEqual(abs(buttons[0].winfo_width()-buttons[1].winfo_width()),2)
                for button in buttons:
                    self.assertEqual(button.cget('height'),54)
                    self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                view.root.destroy()

    def test_invalid_conjugation_reports_error_without_replacing_screen(self):
        from app.conjugation.practise import Conjugation
        from app import main
        with TemporaryDirectory() as folder:
            base=Path(folder);(base/'files').mkdir()
            path=base/'files'/'Czech_Spanish_con.csv'
            path.write_text('ID;R\n1;S\n',encoding='utf-8')
            marker=cst.CTkLabel(self.root,text='Existing screen');marker.pack()
            with patch_context(root_dir=base),patch_preferences(learned_by='Czech'), \
                    patch('app.conjugation.practise.messagebox.showerror') as error:
                self.assertIsNone(Conjugation(self.root,'Spanish'))
            error.assert_called_once()
            self.assertTrue(marker.winfo_exists())

"""Branded headers, standard actions and extension slots on actual Tk widgets."""
from app.tests.context_helpers import patch_preferences
from unittest import TestCase
from unittest.mock import Mock,patch
import customtkinter as cst
from app.ui.components.module_header import ModuleHeader
from app.shared.translations import translate


class ModuleHeaderTests(TestCase):
    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1400x850');self.root.update()
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy();self.assertFalse(self.errors)

    def test_style_logo_and_standard_actions_fit_all_locales_and_widths(self):
        for width in (1000,1400):
            self.root.geometry(f'{width}x850')
            for locale in ('cs','en','de','es','fr','sk'):
                with self.subTest(width=width,locale=locale):
                    tr=lambda key:translate(key,locale)
                    callback=Mock()
                    header=ModuleHeader(self.root,tr('Edit grammar questions'),translate=tr,
                        actions=[('save',callback),('close',Mock()),('exit',Mock())])
                    header.pack(fill='x');self.root.update()
                    self.assertTrue(header.logo_label.winfo_ismapped())
                    self.assertEqual(header.logo_label.cget('image').cget('size'),(64,64))
                    self.assertEqual(header.title_label.cget('text_color'),'#fffcf5')
                    self.assertEqual(header.title_label.cget('font')[1],32)
                    self.assertEqual(header.buttons['save'].cget('text'),tr('Save'))
                    for button in header.buttons.values():
                        self.assertEqual(button.cget('font')[1],18)
                        self.assertEqual(button.cget('height'),44)
                        self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                    header.buttons['save'].invoke();callback.assert_called_once()
                    header.destroy()

    def test_detail_and_extensions_preserve_logo_and_action_positions(self):
        header=ModuleHeader(self.root,'Title',actions=[('save',Mock()),('close',Mock())])
        header.pack(fill='x')
        header.set_detail(cst.CTkLabel(header,text='Language selector'))
        tabs=cst.CTkLabel(header,text='Questions / Theory')
        header.place_extension(tabs)
        filters=cst.CTkFrame(header,fg_color='#ded4bf')
        header.place_extension(filters)
        cst.CTkEntry(filters).pack(fill='x',padx=12,pady=12)
        self.root.update()
        self.assertGreater(filters.winfo_rooty(),tabs.winfo_rooty())
        self.assertGreater(tabs.winfo_rooty(),header.logo_label.winfo_rooty()+header.logo_label.winfo_height())
        self.assertLess(header.buttons['save'].winfo_rootx(),header.buttons['close'].winfo_rootx())
        header.refresh_action('close',text='Stop saving',state='disabled')
        self.assertEqual(header.buttons['close'].cget('state'),'disabled')

    def test_statistics_build_uses_header_and_preserves_language_switch(self):
        from app import main
        from app.statistics import viewer
        from app.statistics.window import StatisticsWindow
        window=StatisticsWindow(self.root);window.geometry('1400x850')
        with patch.object(viewer.StatisticsController,'load') as load, \
                patch_preferences(first_language='Spanish'),patch_preferences(second_language='English'):
            viewer._build_statistics(window)
            window.deiconify();self.root.update()
            self.assertIsInstance(window.header,ModuleHeader)
            self.assertIs(window.header.title_label.master,window.header)
            self.assertTrue(window.header.logo_label.winfo_ismapped())
            self.assertEqual(window._statistics_language.get(),'Spanish')
            load.assert_called_once()
            window.header.buttons['close'].invoke()
            self.assertFalse(window.winfo_exists())


def header_regressions():
    """Focused suite; not auto-discovered twice by the complete test runner."""
    import unittest
    return unittest.defaultTestLoader.loadTestsFromNames([
        'app.tests.test_module_header.ModuleHeaderTests',
        'app.tests.test_shared_controls.SharedControlsTests.test_about_and_preferences_header_actions_share_training_style_in_all_languages',
        'app.tests.test_editor_async_ui',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
        'app.tests.test_learning_ui.LearningUiTests.test_conjugation_feedback_preserves_scoring_and_separates_header_rows',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_editor_ctrl_h_opens_synonyms_for_selected_word',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_synonym_dialog_background_and_actions_fit_in_six_languages',
        'app.tests.test_module_panels.ModulePanelTests.test_question_and_theory_actions_share_green_panel_and_have_exit',
        'app.tests.test_shortcut_hint_layout.ShortcutHintLayoutTests.test_all_items_fit_and_remain_present_across_languages_and_widths',
        'app.tests.test_localization_audit.LocalizationAuditTests.test_shortcut_descriptions_and_enum_values_exist_in_every_language',
    ])

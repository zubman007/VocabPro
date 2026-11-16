"""Editorial policy, audit blind spots and application-language modal contracts."""
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch
import re
import customtkinter as cst
from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.shared.translations import LANGUAGES, get_catalog, translate
from app.shared.localization_audit import format_contract, source_findings
from app.tests.test_preferences_data import sample_preferences
from app.ui import messagebox
from app.ui.components.app_dialog import AppDialog


class LocalizationPolicyTests(TestCase):
    def test_czech_and_slovak_use_formal_address_and_keep_stable_ids(self):
        patterns = {
            'cs': r'\b(Tvůj|tvůj|Tvoje|tvoje|Vyber|vyber|Zadej|zadej|Vyplň|vyplň|Otevři|otevři|Ulož|ulož|Použij|použij|můžeš|nastavíš|spustíš|Sleduj|Přelož|jsi)\b',
            'sk': r'\b(Tvoj|tvoj|Tvoja|tvoja|Tvoje|tvoje|Vyber|vyber|Zadaj|zadaj|Vyplň|vyplň|Otvor|otvor|Ulož|ulož|Použi|použi|môžeš|nastavíš|spustíš|Sleduj|Prelož)\b',
        }
        for code, pattern in patterns.items():
            for key, text in get_catalog(code).items():
                self.assertIsNone(re.search(pattern, text), (code, key, text))
            self.assertTrue(translate('Your own language and all learned language need to be different.', code).startswith('Váš'))
        self.assertIn('Not practiced', get_catalog('en'))

    def test_german_uses_du_and_english_distinguishes_practice_noun_from_verb(self):
        for key, text in get_catalog('de').items():
            self.assertIsNone(re.search(r'\b(Sie|Ihnen|Ihre|Ihrer|Ihren|Ihrem)\b', text), (key, text))
        self.assertEqual(translate('Practice in context', 'en'), 'Practise in context')
        self.assertEqual(translate('Not practiced', 'en'), 'Not practised')
        self.assertIn('practice session', translate('Changes are saved with the practice session.', 'en'))

    def test_contextual_terms_remain_distinct_and_percent_units_cannot_wrap(self):
        self.assertEqual(translate('Repeat', 'es'), 'Repasar')
        self.assertIn('errores repetidos', translate('No repeatedly missed words yet.', 'es'))
        self.assertEqual(translate('Delete', 'sk'), 'Odstrániť')
        self.assertEqual(translate('Clear contents', 'sk'), 'Vyprázdniť obsah')
        self.assertEqual(translate('Phrase', 'de'), 'Phrase')  # Not necessarily an idiom.
        for language in LANGUAGES:
            text = translate('Last {count} answers: {accuracy}%', language).format(count=5, accuracy=40)
            self.assertIn('40%' if language == 'English' else '40\N{NO-BREAK SPACE}%', text)

    def test_nested_format_specs_are_checked_before_evaluation(self):
        contract = format_contract('{count:0{width}d}')
        self.assertIn(('width', None, ''), contract)
        for text in ('{count:{width}bad}', '{count:{width:{precision}}}', '{name:{width.__class__}}', '{count!s:0{width}d}'):
            with self.subTest(text=text), self.assertRaises(ValueError): format_contract(text)

    def test_native_dialog_imports_and_positional_ui_text_cannot_escape_audit(self):
        for source in ('from tkinter import messagebox', 'from tkinter.messagebox import askyesno', 'import tkinter.messagebox'):
            with self.subTest(source=source):
                self.assertEqual(len(source_findings(source, 'fixture.py', set())[1]), 1)
        source = 'messagebox.askyesno("Raw title", "Raw message")'
        self.assertEqual(len(source_findings(source, 'fixture.py', set())[1]), 2)
        source = 'MessageDialog(parent, "Raw title", "Raw message", choices)'
        self.assertEqual(len(source_findings(source, 'fixture.py', set())[1]), 2)
        source = 'from app.ui import messagebox\nmessagebox.askyesno(tr("Confirm"), tr("Save"))'
        missing, hardcoded, _, _ = source_findings(source, 'fixture.py', {'Confirm', 'Save'})
        self.assertEqual((missing, hardcoded), ([], []))


class LocalizedMessageTests(TestCase):
    def setUp(self):
        self.root = cst.CTk(); self.root.geometry('1000x700')
        self.context = AppContext(preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.root.update()

    def tearDown(self):
        for child in tuple(self.root.winfo_children()): child.destroy()
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy()
        cst.set_widget_scaling(1); cst.set_window_scaling(1)
        self.assertEqual(self.errors, [])

    def answer(self, action, owner=None):
        owner = owner or self.root
        def perform():
            dialog = next(child for child in owner.winfo_children() if isinstance(child, messagebox.MessageDialog))
            action(dialog)
        self.root.after(30, perform)

    def test_real_modal_helpers_keep_all_result_contracts_and_native_defaults(self):
        for token, expected in (('yes', True), ('no', False), ('cancel', None)):
            self.answer(lambda dialog, token=token: dialog.buttons[token].invoke())
            self.assertIs(messagebox.askyesnocancel('title', 'message', parent=self.root), expected)
        for token, expected in (('yes', True), ('no', False)):
            self.answer(lambda dialog, token=token: dialog.buttons[token].invoke())
            self.assertIs(messagebox.askyesno('title', 'message', parent=self.root), expected)
        for helper in (messagebox.showinfo, messagebox.showwarning, messagebox.showerror):
            self.answer(lambda dialog: dialog.buttons['ok'].invoke())
            self.assertEqual(helper('title', 'message', parent=self.root), 'ok')
        self.answer(lambda dialog: dialog._return())
        self.assertTrue(messagebox.askyesnocancel('title', 'message', parent=self.root))
        self.answer(lambda dialog: dialog._return())
        self.assertTrue(messagebox.askyesno('title', 'message', parent=self.root))
        self.answer(lambda dialog: dialog._return())
        self.assertIsNone(messagebox.askyesnocancel('title', 'message', parent=self.root, default='cancel'))

    def test_close_escape_and_focused_keyboard_preserve_cancellation_semantics(self):
        self.answer(lambda dialog: dialog.tk.eval(dialog.protocol('WM_DELETE_WINDOW')))
        self.assertIsNone(messagebox.askyesnocancel('title', 'message', parent=self.root))
        self.answer(lambda dialog: dialog.tk.eval(dialog.protocol('WM_DELETE_WINDOW')))
        self.assertFalse(messagebox.askyesno('title', 'message', parent=self.root))
        dialog = messagebox.MessageDialog(self.root, 'title', 'message', ('yes', 'no', 'cancel'), translate=self.context.translate)
        with patch.object(dialog, 'focus_get', return_value=dialog.buttons['yes']._text_label):
            dialog._return()
        self.assertEqual(dialog.result, 'yes')
        dialog = messagebox.MessageDialog(self.root, 'title', 'message', ('yes', 'no', 'cancel'), translate=self.context.translate)
        with patch.object(dialog, 'clipboard_clear') as clear, patch.object(dialog, 'clipboard_append') as copy:
            dialog._copy_message()
            clear.assert_called_once(); copy.assert_called_once_with('message')
        dialog._escape()
        self.assertEqual(dialog.result, 'cancel')

    def test_nested_modal_restores_grab_and_owner_can_close_with_message_open(self):
        owner = AppDialog(self.root); owner.geometry('600x400'); owner.present(modal=True)
        self.answer(lambda dialog: dialog.buttons['ok'].invoke(), owner)
        messagebox.showerror('title', 'message', parent=owner)
        self.assertIs(owner.grab_current(), owner)
        self.answer(lambda dialog: owner.destroy(), owner)
        self.assertIsNone(messagebox.askyesnocancel('title', 'message', parent=owner))

    def test_wrapper_uses_app_language_default_root_and_does_not_translate_content_twice(self):
        self.context.preferences = replace(self.context.preferences, app_language='Czech')
        def inspect(dialog):
            self.assertEqual(dialog.buttons['yes'].cget('text'), 'Ano')
            self.assertEqual(dialog.buttons['no'].cget('text'), 'Ne')
            self.assertEqual(dialog.title(), translate('Confirm', 'cs'))
            self.assertEqual(dialog.message_label.cget('text'), 'Literal {name}\n\ntechnical detail')
            dialog.buttons['no'].invoke()
        self.answer(inspect)
        self.assertFalse(messagebox.askyesno(message='Literal {name}', detail='technical detail'))

    def test_long_messages_and_captions_fit_six_languages_at_three_scales(self):
        for scale in (1, 1.25, 1.5):
            cst.set_widget_scaling(scale); cst.set_window_scaling(scale)
            for language in LANGUAGES:
                tr = lambda key: translate(key, language)
                dialog = messagebox.MessageDialog(self.root, tr('Confirm'), (tr('Guide editor details') + '\n') * 12,
                    ('yes', 'no', 'cancel'), translate=tr)
                dialog.present(); self.root.update()
                for token, button in dialog.buttons.items():
                    self.assertEqual(button.cget('text'), tr(messagebox.CAPTIONS[token]))
                    self.assertLessEqual(button._text_label.winfo_reqwidth(), button.winfo_width() + 2)
                self.assertLessEqual(dialog.message_label._label.winfo_reqwidth(), dialog.message_label.winfo_width() + 2)
                body = dialog.message_label.master
                self.assertLess(body._parent_canvas.yview()[1] - body._parent_canvas.yview()[0], 1)
                dialog.destroy()

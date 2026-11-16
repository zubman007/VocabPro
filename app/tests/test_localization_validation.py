"""Adversarial catalog/source checks and localized UI formats/errors."""
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from app.shared import translations as tr
from app.shared.localization_audit import audit, catalog_findings, format_contract, source_findings
from app.shared.messages import UserMessageError, error_text
from app.shared.localization_format import number, percent, date_text


class LocalizationValidationTests(TestCase):
    def test_project_catalogs_and_source_pass_the_repeatable_audit(self):
        result = audit()
        self.assertEqual(result['catalog_issues'], [])
        self.assertEqual(result['missing_source_keys'], [])
        self.assertEqual(result['hardcoded_candidates'], [])

    def test_placeholder_reordering_is_allowed_but_missing_fields_and_formats_fail(self):
        self.assertEqual(format_contract('{name}: {count:03d}'), format_contract('{count:03d} — {name}'))
        for text in ('{name}', '{name}: {other:03d}', '{name}: {count:.2f}', '{name}: {count:invalid}', '{name'):
            with self.subTest(text=text):
                result = catalog_findings({'en': {'key': '{name}: {count:03d}'}, 'cs': {'key': text}})
                self.assertTrue(any(item['language'] == 'cs' for item in result))
        for text in ('{count!x}', '{count!s:03d}', '{}', '{name.__class__}'):
            with self.subTest(text=text), self.assertRaises(ValueError): format_contract(text)
        self.assertEqual(format_contract('{{literal}} {count}'), format_contract('{count} {{other literal}}'))

    def test_catalog_validation_detects_missing_extra_empty_invalid_and_source_placeholder(self):
        result = catalog_findings({'en': {'missing': 'value', 'Count {count}': 'Lost field'},
                                   'cs': {'empty': '  ', 'invalid': 12, 'replacement': '\ufffd'}})
        kinds = {item['kind'] for item in result}
        self.assertTrue({'missing', 'extra', 'invalid', 'encoding', 'source_placeholder'} <= kinds)

    def test_duplicate_and_missing_files_are_reported_without_fallback_hiding_them(self):
        with TemporaryDirectory() as folder:
            root = Path(folder); (root / 'locales').mkdir(); (root / 'app').mkdir()
            (root / 'locales/en.json').write_text('{"Save":"Save","Save":"Duplicate"}', encoding='utf-8')
            result = audit(root)
            self.assertEqual(len([item for item in result['catalog_issues'] if item['kind'] == 'load']), 6)
            self.assertTrue(any('Duplicate translation ID' in item['detail'] for item in result['catalog_issues']))

    def test_source_scan_detects_composed_ui_errors_plots_and_translated_wrapper_ids(self):
        source = '''
label.configure(text=f"Hello {name}")
messagebox.showerror(title=tr("Missing"), message=str(error))
axes.set_xlabel("Number of widgets")
window.title("New dialog")
controller.can_leave(True, save, message="Unknown prompt")
read_document(path, message="Known")
label.configure(text=tr("Known") + name)
label.configure(text="  ·  ID " + identifier)
label.configure(text="Not translated {}".format(name))
tr(f"Dynamic {count}")
mail['Subject'] = f'{app_name} - backup'
text(parent, "Raw helper text")
menu.add_command(label="Raw menu")
shell(parent, "Unknown shell title", image)
popup_menu_add_command("Raw popup command", callback)
'''
        missing, hardcoded, _, _ = source_findings(source, 'fixture.py', {'Known'})
        self.assertEqual(len(missing), 4)
        self.assertEqual(len(hardcoded), 9)
        self.assertNotIn('Known', [item['text'] for item in hardcoded])

    def test_whitespace_and_missing_translations_fall_back_then_unknown_ids_survive(self):
        with TemporaryDirectory() as folder, patch.object(tr, 'LOCALES_DIR', Path(folder)):
            for code, data in {'en': {'Save': 'Save changes'}, 'cs': {'Save': '   '}}.items():
                (Path(folder) / f'{code}.json').write_text(json.dumps(data), encoding='utf-8')
            tr._load_catalog.cache_clear()
            try:
                self.assertEqual(tr.translate('Save', 'cs'), 'Save changes')
                self.assertEqual(tr.translate('Save', 'fr'), 'Save changes')
                self.assertEqual(tr.translate('Save', 'unknown'), 'Save changes')
                self.assertEqual(tr.translate('New message', 'cs'), 'New message')
            finally: tr._load_catalog.cache_clear()

    def test_ui_languages_are_explicit_not_every_registered_learning_language(self):
        from app.shared import languages
        with patch.object(languages, 'LANGUAGE_CODES', {**languages.LANGUAGE_CODES, 'Italian': 'it'}):
            self.assertNotIn('Italian', tr.LANGUAGE_CODES)
            self.assertEqual(tr.translate('Save', 'Italian'), tr.translate('Save', 'en'))

    def test_shared_choices_have_no_ambiguous_localized_values(self):
        from app.vocabulary.editor_localization import ENUMS
        for language in tr.LANGUAGES:
            for column, values in ENUMS.items():
                with self.subTest(language=language, column=column):
                    labels = [tr.translate(value, language) for value in values]
                    self.assertEqual(len(labels), len(set(labels)))
        missing, _, _, _ = source_findings('raise UserMessageError("Missing ID", count=1)', 'fixture.py', set())
        self.assertEqual(missing[0]['key'], 'Missing ID')

    def test_localized_errors_keep_templates_and_language_parameters_until_presentation(self):
        error = UserMessageError('No speech voice configured for {language}', language='Czech')
        self.assertIn('Czech', str(error))
        for language in tr.LANGUAGES:
            translate = lambda key: tr.translate(key, language)
            self.assertEqual(error_text(error, translate), translate(error.message_id).format(language=translate('Czech')))
            self.assertIn('diagnostic', error_text(OSError('diagnostic'), translate))
            self.assertNotEqual(error_text(OSError('diagnostic'), translate), 'diagnostic')
            self.assertEqual(error_text(ValueError('No recording captured'), translate), translate('No recording captured'))

    def test_ui_numbers_dates_and_neutral_counts_do_not_change_storage(self):
        self.assertEqual(number(12.5, 'Czech', 2), '12,50')
        self.assertEqual(number(12.5, 'English', 2), '12.50')
        self.assertEqual(percent(.125, 'fr', 1), '12,5\N{NO-BREAK SPACE}%')
        self.assertEqual(percent(.125, 'en', 1), '12.5%')
        self.assertEqual(date_text(date(2026, 11, 16), 'cs'), '16.11.2026')
        self.assertEqual(date_text(date(2026, 11, 16), 'fr'), '16/11/2026')
        self.assertEqual(date_text(date(2026, 11, 16), 'en'), '2026-11-16')
        for language in tr.LANGUAGES:
            for count in (0, 1, 2, 5, 21):
                self.assertIn(str(count), tr.translate('Words to review: {count}', language).format(count=count))

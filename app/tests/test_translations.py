"""Catalog integrity, fallback behavior and coverage of real UI message IDs."""
import ast
import csv
import json
from pathlib import Path
import tempfile
import unicodedata
import unittest
from unittest.mock import patch, Mock
from app.shared import translations as tr


from app.paths import ROOT_DIR
ROOT = ROOT_DIR


class TranslationTests(unittest.TestCase):
    def setUp(self):
        tr._load_catalog.cache_clear()
        self.addCleanup(tr._load_catalog.cache_clear)

    def test_all_languages_have_identical_unique_sorted_nonempty_messages(self):
        english = tr.get_catalog('English')
        self.assertGreater(len(english), 200)
        for language in tr.LANGUAGES:
            catalog = tr._load_catalog(tr.LANGUAGE_CODES[language])
            self.assertEqual(set(catalog), set(english), language)
            self.assertEqual(list(catalog), sorted(catalog), language)
            for key, text in catalog.items():
                self.assertTrue(text.strip(), (language, key))
                self.assertEqual(text, unicodedata.normalize('NFC', text), (language, key))

    def test_real_ui_literals_and_preference_names_exist(self):
        messages = set(tr.get_catalog('English'))
        missing = []
        for path in [ROOT / 'start.py', *(ROOT / 'app').rglob('*.py')]:
            if path.is_relative_to(ROOT / 'app' / 'tests'):
                continue
            if path.name in ('sandbox.py', 'Activation_standalone.py') or path.name.startswith('_'):
                continue
            tree = ast.parse(path.read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                name = getattr(node.func, 'attr', getattr(node.func, 'id', ''))
                if name not in ('T', 'translate'):
                    continue
                argument = node.args[0]
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    if argument.value not in messages:
                        missing.append((path.name, argument.value))
        self.assertEqual(missing, [])
        with (ROOT / 'files' / 'settings.csv').open(encoding='utf-8-sig', newline='') as file:
            names = [row['Name'] for row in csv.DictReader(file, delimiter=';')]
        self.assertEqual([name for name in names if name not in messages], [])

    def test_lookup_supports_names_codes_and_read_only_legacy_access(self):
        self.assertEqual(tr.translate('Save', 'Czech'), 'Uložit')
        self.assertEqual(tr.translate('Save', 'cs'), 'Uložit')
        self.assertEqual(tr.translation['Save']['Czech'], 'Uložit')
        with self.assertRaises(TypeError):
            tr.get_catalog('cs')['Save'] = 'changed'
        with self.assertRaises(KeyError):
            tr.translation['not a known message']

    def test_repeated_lookups_load_only_the_requested_language_once(self):
        for _ in range(50):
            tr.translate('Save', 'cs')
            tr.translate('Cancel', 'Czech')
        self.assertEqual(tr._load_catalog.cache_info().misses, 1)

    def test_partial_missing_and_unknown_languages_have_safe_fallbacks(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(tr, 'LOCALES_DIR', Path(directory)):
            (Path(directory) / 'en.json').write_text('{"Save": "Save changes"}', encoding='utf-8')
            (Path(directory) / 'cs.json').write_text('{"Save": ""}', encoding='utf-8')
            self.assertEqual(tr.translate('Save', 'cs'), 'Save changes')
            self.assertEqual(tr.translate('Save', 'fr'), 'Save changes')
            self.assertEqual(tr.translate('Save', 'unknown'), 'Save changes')
            self.assertEqual(tr.translate('  new label  ', 'cs'), '  new label  ')

    def test_duplicates_and_invalid_catalog_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(tr, 'LOCALES_DIR', Path(directory)):
            path = Path(directory) / 'en.json'
            for text in ('{"Save":"one","Save":"two"}', '{"Save":42}', '[]'):
                path.write_text(text, encoding='utf-8')
                tr._load_catalog.cache_clear()
                with self.assertRaises(ValueError):
                    tr.get_catalog('English')

    def test_legacy_composed_labels_keep_their_spacing(self):
        for language in tr.LANGUAGES:
            self.assertTrue(tr.translate(' words to repeat', language).startswith(' '))
            self.assertTrue(tr.translate('Success Rate (grammar): ', language).endswith(' '))

    def test_audio_state_is_not_translated_before_persistence(self):
        import pandas as pd
        from app.vocabulary import editor
        source = pd.DataFrame({'ID': [1], 'Audio': ['Own']})
        filtered = source.copy()
        table = Mock()
        table.get_selected_cells.return_value = {(0, 1)}
        table.get_cell_data.return_value = 1
        controller=editor.EditorController.__new__(editor.EditorController)
        controller.main_df,controller.filt_df,controller.edit_tbl=source,filtered,table
        controller.headers,controller.audio_folder=['ID','Audio'],'unused/'
        with patch.object(editor, 'exists', return_value=False), \
             patch.object(editor.pygame.mixer, 'quit'), patch.object(editor.pygame.mixer, 'init'), \
             patch('app.shared.settings.T', return_value='Bez zvuku'):
            controller.Delete_audio()
        self.assertEqual(source.at[0, 'Audio'], 'No audio')
        self.assertEqual(filtered.at[0, 'Audio'], 'No audio')
        table.set_cell_data.assert_called_once_with(0, 1, 'No audio')

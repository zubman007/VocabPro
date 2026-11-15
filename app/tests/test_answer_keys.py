"""Windows keypad flags and synonym preference persistence."""
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest
from app.ui.answer_keys import answer_index
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import save_preferences, load_preferences
from app.tests.test_preferences_data import sample_preferences


class AnswerKeyTests(unittest.TestCase):
    def test_windows_numpad_virtual_keys_and_num_lock(self):
        for i in range(4):
            for state in (0,0x8,0x10,0x18):
                self.assertEqual(answer_index(SimpleNamespace(keysym=str(i+1),keycode=97+i,state=state)),i)
                self.assertEqual(answer_index(SimpleNamespace(keysym=f'KP_{i+1}',keycode=97+i,state=state)),i)
        self.assertIsNone(answer_index(SimpleNamespace(keysym='1',keycode=97,state=4)))

    def test_synonym_setting_defaults_and_persists(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'settings.csv'
            frame=sample_preferences();frame.to_csv(path,sep=';',index=False)
            self.assertTrue(RuntimePreferences.from_frame(frame).show_synonyms)
            save_preferences(frame,{'Automatically show synonyms in repeat':'0'},path)
            self.assertFalse(RuntimePreferences.from_frame(load_preferences(path)).show_synonyms)

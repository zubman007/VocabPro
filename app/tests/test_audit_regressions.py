"""Regression checks for defects found during the application-wide audit."""
from app.core.context import get_context
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
import pygame
from app import main
from app.shared.audio_effects import play_effect
from app.vocabulary.editor_attributes import clean_audio_files, enrich_attributes


class AuditRegressionTests(unittest.TestCase):
    def test_unavailable_sound_is_optional(self):
        with patch('app.shared.audio_effects.pygame.mixer.get_init', return_value=None), \
             patch('app.shared.audio_effects.pygame.mixer.music.load') as load:
            self.assertFalse(play_effect('wrong.wav'))
            load.assert_not_called()
        with patch('app.shared.audio_effects.pygame.mixer.get_init', return_value=(44100, -16, 2)), \
             patch('app.shared.audio_effects.pygame.mixer.music.get_busy', return_value=False), \
             patch('app.shared.audio_effects._load_sound', side_effect=pygame.error('missing')):
            self.assertFalse(play_effect('wrong.wav'))

    def test_new_course_contains_manual_part_of_speech_column(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch_context(files_dir=directory), patch_preferences(learned_by='Czech'):
            from app.repositories.courses import ensure_course
            ensure_course(get_context().files_dir,'Czech','English')
            path = Path(directory) / 'Czech_English_voc.csv'
            self.assertIn('Part of Speech', pd.read_csv(path, sep=';').columns)
            path.write_text('custom existing content', encoding='utf-8')
            ensure_course(get_context().files_dir,'Czech','English')
            self.assertEqual(path.read_text(encoding='utf-8'), 'custom existing content')

    def test_own_mp3_survives_missing_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '5.mp3'
            path.write_bytes(b'own recording')
            frame = pd.DataFrame({'ID': [5], 'Audio': ['Own']}, index=[9])
            clean_audio_files(frame, 9, directory)
            self.assertEqual(path.read_bytes(), b'own recording')
            self.assertEqual(frame.at[9, 'Audio'], 'Own')

    def test_enrichment_supports_filtered_index_and_preserves_manual_attributes(self):
        frame = pd.DataFrame({'ID': [5], 'Audio': ['No audio'], 'English': ['word'],
            'Enabled': ['True'], 'Description': ['manual description'], 'Example': ['manual example'],
            'Phonetic': ['manual phonetic'], 'Part of Speech': ['Verb']}, index=[9])
        with tempfile.TemporaryDirectory() as directory, \
             patch('app.services.api.Dict_api') as dictionary, patch('app.services.api.MW') as mw, \
             patch('app.services.api.Eveleven_labs') as speech:
            before = frame.copy(deep=True)
            result = enrich_attributes(frame, 'English', directory)
            pd.testing.assert_frame_equal(result, before)
            dictionary.assert_not_called()
            mw.assert_not_called()
            speech.assert_not_called()

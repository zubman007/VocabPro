"""Course selection, initialization and runtime preferences without real data."""
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.home.data import course_overview
from app.preferences.data import RuntimePreferences, PreferenceError
from app.tests.test_preferences_data import sample_preferences
from app import main
from app.core.context import get_context
from types import SimpleNamespace


def course():
    return pd.DataFrame({'ID':list(range(1,7)), 'Spanish':['a','b','c','d','NA','null'],
        'Czech':['one']*6, 'Audio':['Own']*6, 'Description':['-']*6, 'Example':['-']*6,
        'Part of Speech':['Noun']*6, 'Enabled':['True']*5+['False'],
        'Repetition':['SSSSS','SSSS','S','SSSSS','', 'SSSSS'],
        'Next repetition':['2026-01-01','2026-01-01','2026-01-01','2027-01-01',
                           '2026-01-01','2026-01-01']})


class HomeDataTests(unittest.TestCase):
    def test_refresh_does_not_destroy_current_screen_before_data_is_ready(self):
        with patch('app.main.Load_setting'), patch('app.main._try_bkp'), \
             patch('app.main._load_vocab_stats',side_effect=ValueError('bad course')), \
             patch('app.main.s.Clear_frames') as clear:
            with self.assertRaises(ValueError):main.main_proc(SimpleNamespace())
        clear.assert_not_called()

    def test_due_counts_and_selected_batches_preserve_learning_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            course().to_csv(path/'Czech_Spanish_voc.csv',sep=';',index=False)
            pd.DataFrame({'ID':[1,2],'Description':['long','text']}).to_csv(path/'Czech_Spanish_con.csv',sep=';',index=False)
            pd.DataFrame({'question_id':[1,2,3]}).to_csv(path/'Spanish_gra.csv',sep=';',index=False)
            result=course_overview(path,'Czech','Spanish',2,10,datetime(2026,11,13))
            self.assertEqual((result['all_count'],result['rep_count'],result['lrn_count']),(6,2,3))
            self.assertEqual(result['rep_words'].ID.tolist(),[1,6])
            self.assertEqual(len(result['lrn_words']),2)
            self.assertEqual((result['con_count'],result['gra_count']),(2,3))
            self.assertNotIn('success_count',result['rep_words'])

    def test_fallback_keeps_four_success_boundary_and_literal_words(self):
        with tempfile.TemporaryDirectory() as directory:
            frame=course();frame['Next repetition']='2027-01-01'
            frame.to_csv(Path(directory)/'Czech_Spanish_voc.csv',sep=';',index=False)
            result=course_overview(directory,'Czech','Spanish',10,10,datetime(2026,11,13))
            self.assertEqual(result['rep_count'],0)
            self.assertEqual(set(result['rep_words'].ID),{1,2,4,6})
            frame.loc[4,'Next repetition']='2026-01-01'
            frame.to_csv(Path(directory)/'Czech_Spanish_voc.csv',sep=';',index=False)
            result=course_overview(directory,'Czech','Spanish',10,10,datetime(2026,11,13))
            self.assertEqual(result['lrn_words'].Spanish.tolist(),['NA'])

    def test_missing_course_has_complete_empty_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            result=course_overview(directory,'Czech','Spanish',10,10)
            self.assertTrue(result['rep_words'].empty)
            self.assertEqual(result['gra_count'],0)
            self.assertEqual(result['con_count'],0)

    def test_bad_date_does_not_crash_home_or_rewrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_Spanish_voc.csv';frame=course()
            frame.loc[0,'Next repetition']='not a date'
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            result=course_overview(directory,'Czech','Spanish',10,10)
            self.assertEqual(result['all_count'],6)
            self.assertEqual(path.read_bytes(),before)

    def test_invalid_runtime_preferences_do_not_partially_change_context(self):
        frame=sample_preferences();frame.loc[frame.Name=='Learn batch','Value']='broken'
        context=get_context()
        previous=(context.preferences,context.preferences_frame)
        with patch('app.main.load_preferences',return_value=frame), patch('app.main.ensure_course_files') as ensure:
            with self.assertRaises(PreferenceError):main.Load_setting()
        self.assertEqual((context.preferences,context.preferences_frame),previous)
        ensure.assert_not_called()

    def test_runtime_preferences_keep_probabilities_and_normalized_date(self):
        config=RuntimePreferences.from_frame(sample_preferences())
        self.assertEqual(config.context_probabilities,(20,20))
        self.assertEqual(config.audio_probabilities,(20,20))
        self.assertEqual(config.next_backup,'2026-11-21 15:16:41')

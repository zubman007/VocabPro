from datetime import datetime
import unittest
import pandas as pd
from app.vocabulary.practise_session import PracticeSession, ChoicePool


def batch():
    return pd.DataFrame({'ID':[10,20,30],'Repetition':['','SSSS','SSSS'],
        'Next repetition':['2026-11-12 10:00:00']*3,'Description':['first','second','third'],
        'Audio':['Own']*3})


class PracticeSessionTests(unittest.TestCase):
    def make_session(self):
        return PracticeSession(batch(),{0:0,1:1,2:2},200)

    def test_initial_learning_requires_original_number_of_successes(self):
        session=self.make_session()
        self.assertTrue(session.introduce(10))
        self.assertFalse(session.introduce(10))
        for _ in range(3):
            self.assertFalse(session.succeed(10))
        self.assertIn(10,session.positions)
        self.assertTrue(session.succeed(10,datetime(2026,11,12,10)))
        self.assertEqual(session.history(10),'SSSSS')
        self.assertEqual(session.data.at[10,'Next repetition'],'2026-11-13 10:00:00')

    def test_failure_and_completion_preserve_history(self):
        session=self.make_session()
        session.fail(20)
        self.assertEqual(session.history(20),'SSSSF')
        self.assertTrue(session.succeed(20))
        self.assertEqual(session.history(20),'SSSSFS')
        self.assertFalse(session.succeed(20))
        self.assertEqual(session.completed.count(20),1)

    def test_skip_maintains_fast_index_and_never_repeats_completed_word(self):
        session=self.make_session()
        session.skip(20)
        self.assertEqual(set(session.remaining),{10,30})
        for word_id,position in session.positions.items():
            self.assertEqual(session.remaining[position],word_id)
        for _ in range(20):
            self.assertNotEqual(session.pick()['ID'],20)
        session.skip(10)
        session.skip(30)
        self.assertFalse(session)

    def test_snapshots_and_source_are_independent(self):
        source=batch()
        original=source.copy(deep=True)
        session=PracticeSession(source,{0:0},200)
        session.skip(20)
        session.set_attribute(20,'Description','No found')
        remaining,completed=session.frames()
        self.assertEqual(completed.loc[0,'Description'],'No found')
        remaining.loc[0,'Audio']='changed snapshot'
        self.assertEqual(session.data.at[10,'Audio'],'Own')
        pd.testing.assert_frame_equal(source,original)

    def test_duplicate_ids_are_rejected(self):
        source=batch()
        source['ID']=[1,1,2]
        with self.assertRaises(ValueError):
            PracticeSession(source,{0:0},200)


class ChoicePoolTests(unittest.TestCase):
    def test_audio_delete_targets_both_formats_without_touching_real_files(self):
        from unittest.mock import Mock, patch
        from app.vocabulary.practise_audio import PracticeAudio
        audio = PracticeAudio('Czech', 'Spanish')
        paths = (Mock(), Mock())
        with patch.object(audio, 'paths', return_value=paths), \
             patch('app.vocabulary.practise_audio.pygame.mixer.get_init', return_value=True), \
             patch('app.vocabulary.practise_audio.pygame.mixer.quit') as quit_mixer, \
             patch('app.vocabulary.practise_audio.pygame.mixer.init') as init_mixer:
            audio.delete(123)
        for path in paths:
            path.unlink.assert_called_once_with(missing_ok=True)
        quit_mixer.assert_called_once_with()
        init_mixer.assert_called_once_with()

    def test_small_course_falls_back_without_sampling_error(self):
        self.assertIsNone(ChoicePool(['one','two']).options('one'))

    def test_candidates_keep_original_row_weighting(self):
        pool=ChoicePool(['correct','wrong','wrong','other'])
        self.assertEqual(pool._candidates('correct').count('wrong'),2)
        self.assertCountEqual(pool.options('correct'),['correct','wrong','wrong','other'])

    def test_cache_is_bounded_and_reused(self):
        pool=ChoicePool(map(str,range(100)))
        self.assertIs(pool._candidates('0'),pool._candidates('0'))
        for index in range(100):
            pool._candidates(str(index))
        self.assertLessEqual(len(pool._cache),64)

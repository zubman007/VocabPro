"""Record maxima, legacy compatibility, rollback and fair first-attempt scoring."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.repositories.practice_records import PracticeRecords, load_records, update_records, record_path
from app.shared.storage import FileChangedError
from app.preferences.data import RuntimePreferences, with_defaults, validate_preferences, PreferenceError, group_for, section_for
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_training_sessions import question
from app.grammar.session import GrammarSession
from app.conjugation.session import ConjugationSession
from app.conjugation.data import Verb


class PracticeRecordTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'English_gra.csv'

    def test_absent_and_legacy_records_are_read_only_and_new_maximum_is_unknown(self):
        self.assertEqual(load_records(self.path),PracticeRecords())
        record_path(self.path).write_bytes(b'best_streak\r\n11\r\n')
        before=record_path(self.path).read_bytes()
        self.assertEqual(load_records(self.path),PracticeRecords(11,None))
        self.assertEqual(record_path(self.path).read_bytes(),before)

    def test_independent_maxima_never_decrease_or_sum_separate_rounds(self):
        for streak,correct in ((4,8),(2,5),(6,6),(1,9)):
            with update_records(self.path,streak,correct):pass
        self.assertEqual(load_records(self.path),PracticeRecords(6,9))
        before=record_path(self.path).read_bytes()
        with patch('app.repositories.practice_records.save_csv') as write:
            with update_records(self.path,6,9):pass
            write.assert_not_called()
        self.assertEqual(record_path(self.path).read_bytes(),before)

    def test_module_language_and_conjugation_pair_are_isolated(self):
        paths=[self.path,self.path.with_name('Spanish_gra.csv'),self.path.with_name('Czech_English_con.csv'),
               self.path.with_name('Spanish_English_con.csv')]
        for index,path in enumerate(paths):
            with update_records(path,index+1,index+2):pass
        self.assertEqual([load_records(p).best_correct for p in paths],[2,3,4,5])

    def test_failed_answer_save_restores_exact_legacy_bytes_after_schema_expansion(self):
        record_path(self.path).write_bytes(b'\xef\xbb\xbfbest_streak\r\n0011\r\n')
        before=record_path(self.path).read_bytes()
        with self.assertRaises(PermissionError):
            with update_records(self.path,12,15):raise PermissionError('answers locked')
        self.assertEqual(record_path(self.path).read_bytes(),before)
        with update_records(self.path,12,15):pass
        self.assertEqual(load_records(self.path),PracticeRecords(12,15))

    def test_failure_removes_only_own_new_record_and_keeps_concurrent_change(self):
        with self.assertRaises(PermissionError):
            with update_records(self.path,1,2):raise PermissionError()
        self.assertFalse(record_path(self.path).exists())
        with self.assertRaises(FileChangedError):
            with update_records(self.path,1,2):
                record_path(self.path).write_text('best_streak;best_correct\n4;5\n',encoding='utf8')
                raise PermissionError()
        self.assertEqual(load_records(self.path),PracticeRecords(4,5))

    def test_disabled_tracking_does_not_read_or_write_record_and_still_saves_answers(self):
        record_path(self.path).write_text('malformed but retained',encoding='utf8')
        saved=[]
        with patch('app.repositories.practice_records.load_records',side_effect=AssertionError):
            with update_records(self.path,100,200,enabled=False):saved.append(True)
        self.assertEqual(saved,[True]);self.assertEqual(record_path(self.path).read_text(encoding='utf8'),'malformed but retained')

    def test_invalid_record_and_candidate_are_not_overwritten(self):
        for text in ('best_streak;best_correct\n1;bad\n','best_streak\n-1\n','best_streak\n1\n2\n','unknown\n1\n'):
            record_path(self.path).write_text(text,encoding='utf8');before=record_path(self.path).read_bytes()
            with self.assertRaises(ValueError):
                with update_records(self.path,4,5):pass
            self.assertEqual(record_path(self.path).read_bytes(),before)
        for value in (True,-1,None,1.5):
            with self.assertRaises(ValueError):
                with update_records(self.path,value,5):pass

    def test_write_failure_preserves_previous_record_and_no_temporary_files(self):
        with update_records(self.path,1,3):pass
        before=record_path(self.path).read_bytes()
        with patch('app.shared.storage.os.replace',side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                with update_records(self.path,2,5):pass
        self.assertEqual(record_path(self.path).read_bytes(),before)
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')),[])

    def test_statistics_reload_records_when_answer_cache_is_unchanged(self):
        from app.statistics.data import training_statistics
        pd.DataFrame({'R':['S'],'category':['A']}).to_csv(self.path,sep=';',index=False)
        before=self.path.read_bytes()
        first=training_statistics(self.path,'grammar');self.assertIsNone(first['best_correct'])
        with update_records(self.path,3,4):pass
        second=training_statistics(self.path,'grammar')
        self.assertEqual((second['best_streak'],second['best_correct']),(3,4))
        self.assertEqual(self.path.read_bytes(),before)

    def test_new_preferences_default_on_validate_and_stay_independent(self):
        frame=sample_preferences();before=frame.copy(deep=True)
        defaults=with_defaults(frame)
        for key in ('Track personal records','Show personal records'):
            self.assertEqual(section_for(key),'Learning');self.assertEqual(group_for(key),'Practice records')
            with self.assertRaises(PreferenceError):validate_preferences(defaults,{key:'invalid'})
        prefs=RuntimePreferences.from_frame(validate_preferences(defaults,{'Track personal records':'0'}))
        self.assertFalse(prefs.track_personal_records);self.assertTrue(prefs.show_personal_records)
        pd.testing.assert_frame_equal(frame,before)

    def test_grammar_skips_break_streak_and_restart_resets_session_correct(self):
        state=GrammarSession([question(str(i)) for i in range(5)])
        state.advance();state.answer(state.options.index('yes'));state.advance()
        state.advance();self.assertEqual(state.streak,0)
        state.answer(state.options.index('yes'));self.assertEqual((state.correct,state.best_streak),(2,1))
        state.restart();self.assertEqual((state.correct,state.best_streak),(0,0))

    def test_conjugation_scores_whole_verb_once_and_skip_breaks_streak(self):
        frame=pd.DataFrame({'ID':['a','b','c'],'R':['','',''],'LR':['','','']})
        verbs=[Verb(key,forms={'s1':'one','s2':'two'}) for key in frame.ID]
        state=ConjugationSession(frame,verbs,(('s1','I'),('s2','you')))
        state.advance();state.confirm({'s1':'one','s2':'two'})
        self.assertEqual((state.correct,state.streak,state.best_streak),(1,1,1))
        state.advance();state.advance(skip=True)
        self.assertEqual(state.streak,0)
        state.confirm({'s1':'one','s2':'wrong'});state.confirm({'s1':'one','s2':'wrong'})
        state.confirm({'s1':'one','s2':'two'})
        self.assertEqual((state.correct,state.incorrect,state.best_streak,state.completed),(1,1,1,2))

    def test_backup_preserves_both_record_columns(self):
        from app.repositories.courses import backup_files
        with update_records(self.path,2,4):pass
        self.assertEqual(dict(backup_files(self.path.parent)),{record_path(self.path).name:record_path(self.path).read_bytes()})

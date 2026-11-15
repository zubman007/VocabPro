"""Historical records, rollback, cache refresh and live record feedback."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.repositories.grammar_records import load_record, record_path, update_record
from app.tests import test_grammar_session_insight as fixtures


class GrammarRecordTests(TestCase):
    def test_persistence_maximum_rollback_and_language_isolation(self):
        with TemporaryDirectory() as folder:
            course=Path(folder)/'English_gra.csv'
            self.assertEqual(load_record(course),0)
            self.assertFalse(record_path(course).exists())
            with self.assertRaises(OSError):
                with update_record(course,3):raise OSError('Failed answers')
            self.assertFalse(record_path(course).exists())
            with update_record(course,5):pass
            before=record_path(course).read_bytes()
            with update_record(course,2):pass
            self.assertEqual(record_path(course).read_bytes(),before)
            with self.assertRaises(OSError):
                with update_record(course,8):raise OSError('Failed answers')
            self.assertEqual(load_record(course),5)
            self.assertEqual(load_record(Path(folder)/'Spanish_gra.csv'),0)

    def test_statistics_refresh_record_without_csv_history_change(self):
        from app.statistics.data import training_statistics
        with TemporaryDirectory() as folder:
            course=Path(folder)/'English_gra.csv'
            pd.DataFrame({'R':['SF'],'category':['Articles']}).to_csv(course,sep=';',index=False)
            before=course.read_bytes()
            self.assertEqual(training_statistics(course,'grammar')['best_streak'],0)
            with update_record(course,4):pass
            self.assertEqual(training_statistics(course,'grammar')['best_streak'],4)
            self.assertEqual(course.read_bytes(),before)

    def test_invalid_record_is_rejected_without_overwrite(self):
        with TemporaryDirectory() as folder:
            course=Path(folder)/'English_gra.csv'
            record_path(course).write_text('best_streak\ninvalid\n',encoding='utf-8')
            before=record_path(course).read_bytes()
            with self.assertRaises(ValueError):
                with update_record(course,9):pass
            self.assertEqual(record_path(course).read_bytes(),before)


class RecordUiTests(TestCase):
    setUp=fixtures.SessionInsightUiTests.setUp
    tearDown=fixtures.SessionInsightUiTests.tearDown
    lesson=fixtures.SessionInsightUiTests.lesson
    settle=fixtures.SessionInsightUiTests.settle
    def test_record_notification_equal_exceeded_save_and_restart(self):
        course=Path(self.directory.name)/'English_gra.csv'
        with update_record(course,2):pass
        controller=self.lesson();self.settle()
        for index in range(3):
            controller.choose(controller.session.options.index('yes'))
            self.assertEqual('New record' in controller.view.score.cget('text'),index==2)
            controller.next_question()
        controller.restart()
        self.assertEqual(controller.record_candidate,3)
        self.assertIn('New record',controller.view.score.cget('text'))
        with patch('app.grammar.practise.save_answers',side_effect=OSError('test')),patch('app.grammar.practise.messagebox.showerror'):
            self.assertFalse(controller.save(close=False))
        self.assertEqual(load_record(course),2)
        self.assertEqual(len(controller.pending_answers),3)
        with patch('app.grammar.practise.save_answers'):
            self.assertTrue(controller.save(close=False))
        self.assertEqual(load_record(course),3)

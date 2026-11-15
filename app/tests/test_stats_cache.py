"""Cache invalidation, bounded retention and unchanged statistics semantics."""
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.statistics.cache import StatisticsCache
from app.statistics import data as stats_data
from app.tests.test_editor_save import course


class StatisticsCacheTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'data.csv'
        self.path.write_text('one',encoding='utf-8')

    def test_hits_copy_results_and_invalidate_on_file_or_options_change(self):
        cache=StatisticsCache()
        def calculate(path):return pd.DataFrame({'text':[path.read_text()]})
        with patch.object(self,'calculate',side_effect=calculate,create=True) as work:
            first=cache.get(self.path,'test',(),work)
            first.loc[0,'text']='modified by UI'
            self.assertEqual(cache.get(self.path,'test',(),work).iloc[0,0],'one')
            self.assertEqual(work.call_count,1)
            self.path.write_text('two changed',encoding='utf-8')
            self.assertEqual(cache.get(self.path,'test',(),work).iloc[0,0],'two changed')
            cache.get(self.path,'test',('changed settings',),work)
            self.assertEqual(work.call_count,3)
            self.path.unlink()
            with self.assertRaises(FileNotFoundError):cache.get(self.path,'test',(),work)

    def test_eviction_and_retry_when_source_changes_during_calculation(self):
        cache=StatisticsCache(limit=2)
        calls=[]
        def calculate(path):
            value=path.read_text()
            calls.append(value)
            if len(calls)==1:path.write_text('changed while reading',encoding='utf-8')
            return value
        self.assertEqual(cache.get(self.path,'test',(),calculate),'changed while reading')
        self.assertEqual(len(calls),2)
        for option in (1,2,3):cache.get(self.path,'test',(option,),calculate)
        self.assertEqual(len(cache._entries),2)

    def test_errors_are_not_cached(self):
        cache=StatisticsCache()
        with self.assertRaises(ValueError):
            cache.get(self.path,'test',(),lambda path: (_ for _ in ()).throw(ValueError()))
        self.assertEqual(cache._entries,{})

    def test_vocabulary_cache_covers_day_settings_and_original_history_rules(self):
        frame=course().drop(columns='Custom')
        frame.loc[0,'Repetition']='SSSSSSF'
        frame.to_csv(self.path,sep=';',index=False)
        cache=StatisticsCache()
        def load(day=date(2026,11,13),horizon=7):
            return stats_data.vocabulary_statistics(self.path,'English','Czech',horizon,
                {1:1,2:2},30,['Noun'],pd.Series({'Noun':100}),today=day)
        with patch.object(stats_data,'cache',cache),patch('app.statistics.data.pd.read_csv',wraps=pd.read_csv) as read:
            result=load()
            self.assertEqual(result['summary'],(1,1,1))
            self.assertEqual(result['table'].loc[0,'English'],'NA')
            pd.testing.assert_frame_equal(result['table'],load()['table'])
            self.assertEqual(read.call_count,1)
            load(day=date(2026,11,14));load(horizon=8)
            self.assertEqual(read.call_count,3)

    def test_grammar_answer_or_category_change_refreshes_cached_summary(self):
        pd.DataFrame({'category':['A','B'],'R':['SF','S']}).to_csv(self.path,sep=';',index=False)
        with patch.object(stats_data,'cache',StatisticsCache()),patch('app.statistics.data.pd.read_csv',wraps=pd.read_csv) as read:
            result=stats_data.training_statistics(self.path,'grammar')
            self.assertEqual(result['summary'],(2,2,1))
            stats_data.training_statistics(self.path,'grammar')
            self.assertEqual(read.call_count,1)
            pd.DataFrame({'category':['A','A'],'R':['SFF','S']}).to_csv(self.path,sep=';',index=False)
            result=stats_data.training_statistics(self.path,'grammar')
            self.assertEqual(result['summary'],(2,2,2))
            self.assertEqual(result['categories'][0].questions,2)
            self.assertEqual(read.call_count,2)

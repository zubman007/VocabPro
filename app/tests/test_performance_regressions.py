"""Operation budgets and generous runtime checks, using synthetic data only."""
from pathlib import Path
from statistics import median
import tempfile
from time import perf_counter
import unittest
from unittest.mock import patch
import pandas as pd
from app.statistics import data as statistics
from app.statistics.cache import StatisticsCache
from app.grammar.category_filter import category_options
from app.vocabulary.practise_session import ChoicePool
from app.shared.background_task import BackgroundTask
from app.tests.test_background_task import Scheduler


class PerformanceRegressionTests(unittest.TestCase):
    def test_ten_thousand_questions_are_read_only_once_for_twenty_cached_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar.csv'
            pd.DataFrame({'category':['Topic '+str(i%80) for i in range(10000)],
                'R':['SFS'*20]*10000}).to_csv(path,sep=';',index=False)
            with patch.object(statistics,'cache',StatisticsCache()),patch('app.statistics.data.pd.read_csv',wraps=pd.read_csv) as read:
                begin=perf_counter();cold=statistics.training_statistics(path,'grammar');cold_time=perf_counter()-begin
                timings=[]
                for _ in range(20):
                    begin=perf_counter();warm=statistics.training_statistics(path,'grammar');timings.append(perf_counter()-begin)
                    self.assertEqual(warm['summary'],cold['summary'])
                self.assertEqual(read.call_count,1)
                self.assertEqual(len(cold['categories']),80)
                self.assertLess(median(timings),max(cold_time*.8,.01))
                self.assertLess(cold_time,10)
                print(f'PERF grammar 10000 rows: cold {cold_time*1000:.1f} ms; cached median {median(timings)*1000:.2f} ms')

    def test_category_counts_scale_to_fifty_thousand_questions_without_mutation(self):
        questions=[{'id':i,'category':'Topic '+str(i%100)} for i in range(50000)]
        begin=perf_counter();options=category_options(questions);elapsed=perf_counter()-begin
        self.assertEqual(len(options),100)
        self.assertEqual(sum(count for _,_,count in options),50000)
        self.assertEqual(questions[0],{'id':0,'category':'Topic 0'})
        self.assertLess(elapsed,10)
        print(f'PERF category aggregation 50000 questions: {elapsed*1000:.1f} ms')

    def test_latest_progress_is_coalesced_instead_of_queueing_fifty_thousand_ui_events(self):
        owner=Scheduler();seen=[]
        def work(cancelled,progress):
            for i in range(50000):progress(i,50000)
            return 'done'
        task=BackgroundTask(owner,work,lambda value:None,self.fail,lambda *args:seen.append(args)).start()
        task.thread.join(5)
        self.assertFalse(task.thread.is_alive())
        self.assertEqual(len(owner.jobs),1)
        owner.run()
        self.assertEqual(seen,[(49999,50000)])
        self.assertFalse(owner.jobs)

    def test_large_choice_pool_reuses_candidates_and_has_bounded_cache(self):
        pool=ChoicePool('word '+str(i) for i in range(10000))
        first=pool._candidates('word 1')
        self.assertIs(pool._candidates('word 1'),first)
        for i in range(100):pool.options('word '+str(i))
        self.assertLessEqual(len(pool._cache),64)

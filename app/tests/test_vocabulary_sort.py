"""Numeric/date ordering, stable ties and view-only sorting."""
import unittest
import pandas as pd
from app.vocabulary.editor_data import sort_vocabulary


class SortTests(unittest.TestCase):
    def test_numeric_values_are_not_sorted_lexically(self):
        frame=pd.DataFrame({'ID':['10','2','1'],'Synonym count':['2','10','0']})
        self.assertEqual(sort_vocabulary(frame,'ID').ID.tolist(),['1','2','10'])
        self.assertEqual(sort_vocabulary(frame,'Synonym count',True).ID.tolist(),['2','10','1'])
        self.assertEqual(frame.ID.tolist(),['10','2','1'])

    def test_dates_compare_instants_and_invalid_dates_remain_last(self):
        frame=pd.DataFrame({'ID':[1,2,3],'Next repetition':[
            '2026-11-14T00:30:00+02:00','2026-11-13T23:00:00+00:00','Now']})
        self.assertEqual(sort_vocabulary(frame,'Next repetition').ID.tolist(),[1,2,3])
        self.assertEqual(sort_vocabulary(frame,'Next repetition',True).ID.tolist(),[2,1,3])

    def test_case_insensitive_text_and_stable_ties(self):
        frame=pd.DataFrame({'ID':[1,2,3],'English':['Zebra','apple','APPLE']})
        self.assertEqual(sort_vocabulary(frame,'English').ID.tolist(),[2,3,1])

import unittest
import pandas as pd
from app.statistics.difficult_words import difficult_words


class DifficultyTests(unittest.TestCase):
    def test_ranking_filters_short_and_old_failures(self):
        frame = pd.DataFrame({'Spanish':['a','b','c','d','e','f'], 'Czech':['x']*6,
            'Repetition':['FFFFSS','FFSSS','FFFF','FFFFF','FFFF'+'S'*10,'FF?SSS'],
            'Enabled':['True','True','True','False','True','True']})
        original = frame.copy(deep=True)
        items, count = difficult_words(frame,'Spanish','Czech',limit=2)
        self.assertEqual(count,4)
        self.assertEqual([item.word for item in items],['d','a'])
        self.assertEqual(items[0].errors,5)
        pd.testing.assert_frame_equal(frame,original)

    def test_empty_data_returns_no_candidates(self):
        frame = pd.DataFrame(columns=['Spanish','Czech','Repetition','Enabled'])
        self.assertEqual(difficult_words(frame,'Spanish','Czech'),([],0))

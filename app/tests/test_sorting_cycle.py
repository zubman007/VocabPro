"""The shared cycle switches metrics and restores the original order."""
from unittest import TestCase
from app.ui.sorting import next_sort, sort_arrow


class SortingCycleTests(TestCase):
    def test_three_clicks_and_switching_columns(self):
        state=None
        for expected,arrow in [(('ID',False),'↑'),(('ID',True),'↓'),(None,'↕')]:
            state=next_sort(state,'ID')
            self.assertEqual(state,expected)
            self.assertEqual(sort_arrow(state,'ID'),arrow)
        self.assertEqual(next_sort(('ID',True),'Tags'),('Tags',False))

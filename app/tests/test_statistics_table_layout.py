"""Pagination expands vertically; only the outer statistics page scrolls."""
from unittest import TestCase
from types import SimpleNamespace
import customtkinter as cst
import pandas as pd
from app.statistics.table import StatisticsTable
from app.ui.widgets import VerticalScrolledFrame_class


class StatisticsTableLayoutTests(TestCase):
    def test_header_cycle_preserves_numeric_order_and_restores_source(self):
        self.table.set_data(pd.DataFrame({'Word':[10,2,30]}))
        for expected in ([2,10,30],[30,10,2],[10,2,30]):
            self.table.sort('Word')
            values=[int(self.table.tree.item(item,'values')[0]) for item in self.table.tree.get_children()]
            self.assertEqual(values,expected)

    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1100x700')
        self.scroller=VerticalScrolledFrame_class(self.root)
        self.scroller.pack(fill='both',expand=True)
        self.table=StatisticsTable(self.scroller.interior,lambda text:text)
        self.table.pack(fill='x')

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.after_cancel(job)
        self.root.destroy()

    def test_page_height_tracks_pagination_search_and_empty_data(self):
        self.table.set_data(pd.DataFrame({'Word':[f'word {i}' for i in range(53)]}))
        self.root.update()
        self.assertEqual(int(self.table.tree.cget('height')),25)
        self.assertEqual(self.table.tree.yview(),(0.0,1.0))
        self.table._turn(1);self.root.update()
        self.assertEqual(int(self.table.tree.cget('height')),25)
        self.assertEqual(len(self.table.tree.get_children()),25)
        self.assertEqual(self.table.next.cget('state'),'normal')
        self.table._turn(1);self.root.update()
        self.assertEqual(int(self.table.tree.cget('height')),3)
        self.assertEqual(len(self.table.tree.get_children()),3)
        self.assertEqual(self.table.next.cget('state'),'disabled')
        self.table.search.insert(0,'missing');self.table._search_changed();self.root.update()
        self.assertEqual(int(self.table.tree.cget('height')),1)
        self.assertEqual(len(self.table.tree.get_children()),0)
        self.assertEqual(self.table.next.cget('state'),'disabled')

    def test_wheel_scrolls_outer_page_and_no_vertical_scrollbar_exists(self):
        self.table.set_data(pd.DataFrame({'Word':range(50)}));self.root.update()
        bars=[child for child in self.table.tree.master.winfo_children() if child.winfo_class()=='TScrollbar']
        self.assertFalse(any(str(bar.cget('orient'))=='vertical' for bar in bars))
        self.assertFalse(any(bar.winfo_ismapped() for bar in bars))
        before=self.scroller.canvas.yview()
        self.assertEqual(self.table._scroll_page(SimpleNamespace(delta=-120)),'break')
        self.root.update()
        self.assertGreater(self.scroller.canvas.yview()[0],before[0])

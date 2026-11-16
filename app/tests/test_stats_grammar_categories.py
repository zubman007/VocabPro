"""Category aggregation and real Tk refresh without touching course files."""
import tkinter as tk
import unittest
from unittest.mock import Mock
import customtkinter as cst
import pandas as pd
from app.statistics.grammar_categories import (grammar_categories, GrammarCategoriesPanel,
    GrammarCategory, order_categories)
from app.shared.translations import translate


class GrammarCategoryTests(unittest.TestCase):
    def test_answer_totals_and_category_counts_fit_all_languages_and_reset_on_switch(self):
        from app.shared.translations import get_catalog
        root=cst.CTk();errors=[]
        root.report_callback_exception=lambda *args:errors.append(args)
        source=pd.DataFrame({'category':['A','A','B','C'],'R':['SSF','F?','SS','']})
        before=source.copy(deep=True)
        def labels(parent):
            result=[]
            for child in parent.winfo_children():
                if isinstance(child,cst.CTkLabel):result.append(child)
                else:result.extend(labels(child))
            return result
        try:
            for locale in ('cs','en','de','es','fr','sk'):
                for width in (600,1200):
                    with self.subTest(locale=locale,width=width):
                        for caption in ('Recorded answers','Correct answers','Incorrect answers'):
                            self.assertIn(caption,get_catalog(locale))
                        root.geometry(f'{width}x850')
                        panel=GrammarCategoriesPanel(root,lambda text:translate(text,locale),lambda category:None)
                        panel.pack(fill='both',expand=True);panel.set_data(source);root.update()
                        self.assertEqual([panel.summary_counts[key].cget('text') for key in
                            ('Recorded answers','Correct answers','Incorrect answers')],['6','4','2'])
                        self.assertEqual(panel.category_count.cget('text'),
                            translate('Total categories: {count}',locale).format(count=3))
                        rows=panel.rows.winfo_children()
                        texts=[label.cget('text') for label in labels(rows[0])]
                        self.assertIn(f"{translate('Correct answers',locale)}: 2",texts)
                        self.assertIn(f"{translate('Incorrect answers',locale)}: 2",texts)
                        for label in labels(panel):
                            self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2,label.cget('text'))
                        for button in panel.sort_buttons.values():
                            self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                            self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height()-8)
                        # Narrow layouts must retain wrapped translations; the
                        # compact height budget applies where a row fits on one line.
                        if width>=1200:
                            self.assertLessEqual(rows[0].winfo_reqheight()/panel._get_widget_scaling(),90)
                        panel.set_items([]);root.update()
                        self.assertTrue(all(label.cget('text')=='0' for label in panel.summary_counts.values()))
                        panel.set_data(pd.DataFrame({'R':['SSFF']}));root.update()
                        self.assertEqual(panel.summary_counts['Recorded answers'].cget('text'),'4')
                        panel.destroy()
            pd.testing.assert_frame_equal(source,before)
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()
        self.assertEqual(errors,[])

    def test_weighted_accuracy_coverage_and_weakest_first(self):
        source=pd.DataFrame({'category':[' A ','A','B','B','C'],
            'R':['S','FFFF','SS',None,'']})
        before=source.copy(deep=True)
        items=grammar_categories(source)
        self.assertEqual([x.name for x in items],['A','B','C'])
        self.assertEqual(items[0].accuracy,.2)
        self.assertEqual((items[0].questions,items[0].practised,items[0].attempts),(2,2,5))
        self.assertEqual((items[1].questions,items[1].practised),(2,1))
        self.assertIsNone(items[2].accuracy)
        pd.testing.assert_frame_equal(source,before)

    def test_missing_columns_blank_categories_and_invalid_history(self):
        self.assertEqual(grammar_categories(pd.DataFrame()),[])
        self.assertEqual(grammar_categories(pd.DataFrame(columns=['category','R'])),[])
        items=grammar_categories(pd.DataFrame({'Category':['',None,'NA'],'R':['?',None,'FS?']}))
        self.assertEqual([x.name for x in items],['NA',''])
        self.assertEqual(items[0].attempts,2)
        self.assertEqual(items[1].questions,2)
        self.assertEqual(items[1].practised,0)
        self.assertEqual(grammar_categories(pd.DataFrame({'category':['A']}))[0].attempts,0)

    def test_sorting_questions_and_practised_counts_is_numeric_and_distinct(self):
        items=[GrammarCategory('Small',10,9,2,8),GrammarCategory('Large',100,1,9,1),
               GrammarCategory('Medium',20,8,2,2),GrammarCategory('Never',12,0,0,0)]
        original=list(items)
        self.assertEqual([item.name for item in order_categories(items,'questions',True)],
                         ['Large','Medium','Never','Small'])
        self.assertEqual([item.name for item in order_categories(items,'questions')],
                         ['Small','Never','Medium','Large'])
        self.assertEqual([item.name for item in order_categories(items,'practised',True)],
                         ['Small','Medium','Large','Never'])
        self.assertEqual(items,original)

    def test_sorting_accuracy_keeps_unknown_after_real_zero_in_both_directions(self):
        items=[GrammarCategory('Unknown',5,0,0,0),GrammarCategory('Zero',1,1,0,3),
               GrammarCategory('Half',2,1,2,2),GrammarCategory('Perfect',10,9,10,0)]
        self.assertEqual([item.name for item in order_categories(items)],['Zero','Half','Perfect','Unknown'])
        self.assertEqual([item.name for item in order_categories(items,'accuracy',True)],
                         ['Perfect','Half','Zero','Unknown'])
        self.assertEqual(order_categories([]),[])
        with self.assertRaises(ValueError):order_categories(items,'not a metric')

    def test_equal_values_are_deterministic_and_accuracy_retains_attempt_tiebreak(self):
        items=[GrammarCategory('Beta',10,2,1,1),GrammarCategory('alpha',10,2,1,1),
               GrammarCategory('More evidence',10,2,10,10)]
        self.assertEqual([item.name for item in order_categories(items)],['More evidence','alpha','Beta'])
        for descending in (False,True):
            self.assertEqual([item.name for item in order_categories(items,'questions',descending)],
                             ['alpha','Beta','More evidence'])

    def test_sort_buttons_reuse_rows_keep_callbacks_and_preserve_totals_on_refresh(self):
        root=cst.CTk();root.geometry('1200x900');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        callback=Mock()
        try:
            panel=GrammarCategoriesPanel(root,lambda text:translate(text,'en'),callback)
            panel.pack(fill='x')
            self.assertTrue(all(button.cget('state')=='disabled' for button in panel.sort_buttons.values()))
            items=[GrammarCategory('Small',10,9,2,8),GrammarCategory('Large',100,1,9,1),
                   GrammarCategory('Medium',20,8,2,2),GrammarCategory('Never',12,0,0,0)]
            panel.set_items(items);root.update()
            row_ids={str(row) for row in panel.rows.winfo_children()}
            from dataclasses import replace
            panel.set_items([replace(item) for item in items])
            self.assertEqual({str(row) for row in panel.rows.winfo_children()},row_ids)
            self.assertEqual([label.cget('text') for label in panel.summary_counts.values()],['24','13','11'])
            for key,expected in [('questions',['Small','Never','Medium','Large']),
                                 ('questions',['Large','Medium','Never','Small']),
                                 ('questions',['Small','Large','Medium','Never']),
                                 ('practised',['Never','Large','Medium','Small']),
                                 ('accuracy',['Small','Medium','Large','Never'])]:
                panel.sort_buttons[key].invoke();root.update()
                self.assertEqual([item.name for item in panel.visible],expected)
                displayed=[item.name for item,row in sorted(panel._category_rows,key=lambda pair:pair[1].grid_info()['row'])]
                self.assertEqual(displayed,expected)
                self.assertEqual({str(row) for row in panel.rows.winfo_children()},row_ids)
                self.assertEqual([label.cget('text') for label in panel.summary_counts.values()],['24','13','11'])
            for item,row in panel._category_rows:
                next(child for child in row.winfo_children() if isinstance(child,cst.CTkButton)).invoke()
                self.assertEqual(callback.call_args.args,(item.name,))
            callback.reset_mock()
            panel.sort_buttons['questions'].invoke()
            panel.set_items([GrammarCategory('New language',2,1,1,0)])
            self.assertEqual(panel.sort_key,'questions')
            self.assertFalse(panel.descending)
            for item,row in panel._category_rows:
                next(child for child in row.winfo_children() if isinstance(child,cst.CTkButton)).invoke()
            callback.assert_called_once_with('New language')
            panel.set_items([]);root.update()
            self.assertEqual(panel.visible,[])
            self.assertTrue(all(button.cget('state')=='disabled' for button in panel.sort_buttons.values()))
            self.assertEqual([label.cget('text') for label in panel.summary_counts.values()],['0','0','0'])
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()
        self.assertEqual(errors,[])

    def test_panel_refresh_clears_old_language_and_handles_missing_data(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x850')
        try:
            panel=GrammarCategoriesPanel(root,lambda text:translate(text,'en'))
            panel.pack(fill='both',expand=True)
            panel.set_data(pd.DataFrame({'category':['A','B'],'R':['SF','']}))
            root.update_idletasks()
            root.update()
            wide_height=panel.description._label.winfo_reqheight()
            self.assertLess(wide_height,30,(panel.winfo_width(),panel.description.cget('wraplength')))
            root.geometry('600x850');root.update()
            self.assertGreater(panel.description._label.winfo_reqheight(),wide_height)
            self.assertLessEqual(panel.description._label.winfo_reqwidth(),panel.description.winfo_width()+2)
            self.assertEqual(len(panel.rows.winfo_children()),2)
            panel.set_data(pd.DataFrame({'category':['C'],'R':['S']}))
            root.update_idletasks()
            self.assertEqual(len(panel.rows.winfo_children()),1)
            panel.set_data(pd.DataFrame())
            root.update_idletasks()
            self.assertEqual(len(panel.rows.winfo_children()),1)
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

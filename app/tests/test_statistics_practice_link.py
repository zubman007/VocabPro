"""Statistics category actions launch the correct language and filter without writing history."""
from app.core.context import get_context
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import tkinter as tk
import unittest
import customtkinter as cst
import pandas as pd
from app.statistics.grammar_categories import GrammarCategoriesPanel
from app.statistics.viewer import _practise_category
from app.grammar.practise import GrammarController, Grammar_training
from app.tests.test_grammar_category_filter import questions
from app.tests.test_grammar_editor import questions as csv_questions


class StatisticsPracticeTests(unittest.TestCase):
    def setUp(self):
        try:self.root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        self.root.geometry('1400x850');self.root.update()
        self.translation=patch('app.shared.settings.T',side_effect=lambda key:key)
        self.translation.start()

    def tearDown(self):
        self.translation.stop()
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy()

    def test_category_buttons_bind_each_own_category_including_uncategorised(self):
        callback=Mock()
        panel=GrammarCategoriesPanel(self.root,lambda key:key,callback)
        panel.set_data(pd.DataFrame({'category':['Articles','Tenses',''],'R':['S','F','']}))
        for row in panel.rows.winfo_children():
            button=next(w for w in row.winfo_children() if isinstance(w,cst.CTkButton))
            button.invoke()
        self.assertCountEqual([call.args[0] for call in callback.call_args_list],['Articles','Tenses',''])

    def test_initial_filter_starts_immediately_but_all_questions_remain_available(self):
        with patch('app.grammar.practise.save_answers') as save:
            controller=GrammarController(self.root,questions(),'unused.csv',Mock(),learned_by='Czech',initial_categories=[' ARTICLES '])
            self.assertEqual(len(controller.session.questions),2)
            self.assertEqual(controller.session.current['category'],'Articles')
            self.assertEqual(controller.selected_categories,{'articles'})
            self.assertEqual(controller.view.filter_status.winfo_manager(),'grid')
            controller.restart()
            self.assertEqual(len(controller.session.questions),2)
            controller.apply_filter({key for key,_,_ in controller.categories})
            self.assertEqual(len(controller.session.questions),4)
            save.assert_not_called()

    def test_missing_category_preserves_existing_screen(self):
        marker=cst.CTkFrame(self.root);marker.pack()
        with self.assertRaises(ValueError):
            GrammarController(self.root,questions(),'unused.csv',Mock(),learned_by='Czech',initial_categories=['Removed topic'])
        self.assertTrue(marker.winfo_exists())

    def test_selected_statistics_language_is_forwarded_and_window_closes_only_on_success(self):
        window=cst.CTkToplevel(self.root)
        window._statistics_language=cst.StringVar(value='Spanish')
        with patch('app.grammar.practise.Grammar_training') as launch:
            _practise_category(window,'Ser / Estar')
        launch.assert_called_once()
        self.assertEqual(launch.call_args.args,(self.root,'Spanish'))
        self.assertEqual(launch.call_args.kwargs['categories'],['Ser / Estar'])
        self.assertIs(launch.call_args.kwargs['context'],get_context(window))
        self.assertTrue(callable(launch.call_args.kwargs['on_back']))
        self.assertFalse(window.winfo_exists())
        window=cst.CTkToplevel(self.root);window._statistics_language=cst.StringVar(value='English')
        with patch('app.grammar.practise.Grammar_training',side_effect=ValueError('No questions')), \
             patch('app.statistics.viewer.messagebox.showerror') as error:
            _practise_category(window,'Removed')
        self.assertTrue(window.winfo_exists())
        self.assertFalse(window._opening_practice)
        error.assert_called_once()
        window.destroy()

    def test_real_entry_point_reads_temporary_course_and_does_not_change_it(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'files').mkdir()
            path=base/'files'/'English_gra.csv';csv_questions().to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            with patch_context(root_dir=base),patch_preferences(learned_by=''):
                controller=Grammar_training(self.root,'English',categories=['Tenses'])
            self.assertEqual(controller.session.current['category'],'Tenses')
            self.assertEqual(len(controller.session.questions),1)
            self.assertEqual(path.read_bytes(),before)

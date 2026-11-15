"""Theory availability, previous-category state and long dialog content."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst
from app.grammar.practise import GrammarController
from app.repositories.grammar_theory import load_theory
from app.grammar.theory_data import category_key
from app.grammar.theory_window import TheoryWindow


class TheoryTests(unittest.TestCase):
    def test_missing_empty_and_normalized_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'theory.csv'
            self.assertEqual(load_theory(path),{})
            path.write_text('category;title;rules\n Articles ;Articles;Use a or the\nEmpty;Empty;\n',encoding='utf-8')
            theory=load_theory(path)
            self.assertEqual(list(theory),['articles'])
            self.assertEqual(theory[category_key('ARTICLES')]['rules'],'Use a or the')

    def test_current_previous_finish_restart_and_learning_language(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw()
        try:
            with tempfile.TemporaryDirectory() as directory, patch('app.shared.settings.T',side_effect=lambda text:text):
                path=Path(directory)/'English_gra.csv'
                (path.parent/'Czech_English_gra_ex.csv').write_text(
                    'category;title;rules\nArticles;Articles;A rule\n',encoding='utf-8')
                questions=[dict(id=str(index),category=category,prompt='Choose',anchor='Text',
                    options=['yes','no','a','b'],correct_answer='yes',explanation='Reason')
                    for index,category in enumerate(['Articles','Missing'])]
                with patch('app.grammar.session.Shuffle_copy',side_effect=lambda items,order:list(items)):
                    controller=GrammarController(root,questions,path,Mock(),learned_by='Czech')
                    self.assertEqual(controller.view.theory.cget('state'),'normal')
                    self.assertFalse(hasattr(controller.view,'previous_theory'))
                    controller.show_theory()
                    self.assertIsInstance(controller._theory_window,TheoryWindow)
                    controller._theory_window.destroy()
                    controller.choose(controller.session.options.index('yes'))
                    self.assertEqual(controller.view.theory.cget('state'),'normal')
                    controller.show_theory()
                    self.assertIsInstance(controller._theory_window,TheoryWindow)
                    controller._theory_window.destroy()
                    controller.next_question()
                    self.assertEqual(controller.view.theory.cget('state'),'disabled')
                    controller.show_theory()
                    self.assertFalse(controller._theory_window.winfo_exists())
                    controller.next_question()
                    self.assertEqual(controller.view.theory.cget('state'),'disabled')
                    controller.restart()
                    self.assertEqual(controller.view.theory.cget('state'),'normal')
                    other=GrammarController(root,questions,path,Mock(),learned_by='German')
                    self.assertEqual(other.view.theory.cget('state'),'disabled')
                    other.show_theory()
                    self.assertIsNone(other._theory_window)
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

    def test_long_theory_is_scrollable(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw()
        root.update()
        errors=[]
        root.report_callback_exception=lambda *args:errors.append(args)
        try:
            with patch('app.shared.settings.T',side_effect=lambda text:text):
                dialog=TheoryWindow(root,{'title':'Articles','category':'Articles','level':'A2',
                    'rules':'A long rule. '*1000,'examples':'One | Two'})
                root.after(400,root.quit);root.mainloop()
                self.assertGreater(dialog.body.winfo_height(),dialog.body._parent_canvas.winfo_height())
                dialog.body._parent_canvas.yview_moveto(1)
                root.update()
                self.assertGreater(dialog.body._parent_canvas.yview()[0],0)
                dialog.destroy()
                self.assertEqual(errors,[])
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

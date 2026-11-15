"""Long instructions, sentences and feedback scroll without moving answer controls offscreen."""
from unittest.mock import Mock, patch
import tkinter as tk
import unittest
import customtkinter as cst
from app.grammar.practise import GrammarController


class LongQuestionTests(unittest.TestCase):
    def test_long_text_remains_accessible_and_next_question_resets_scroll(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1200x800');root.update()
        errors=[];root.report_callback_exception=lambda *error:errors.append(error)
        try:
            question=dict(id='1',prompt='A long instruction. '*100,anchor='A long sentence with context. '*200,
                options=['one','two','three','four'],correct_answer='one',explanation='A detailed explanation. '*150)
            with patch('app.shared.settings.T',side_effect=lambda key:key), \
                 patch('app.grammar.practise.save_answers') as save:
                controller=GrammarController(root,[question],'unused.csv',Mock(),learned_by='Czech')
                root.update_idletasks()
                canvas=controller.view.question._parent_canvas
                self.assertGreater(controller.view.question.winfo_height(),canvas.winfo_height())
                self.assertEqual(controller.view.anchor.cget('text'),question['anchor'])
                canvas.yview_moveto(1);root.update_idletasks()
                self.assertGreater(canvas.yview()[0],0)
                for size in ('1200x800','1400x900'):
                    root.geometry(size);root.update_idletasks()
                    for widget in [*controller.view.options,controller.view.next,controller.view.reveal]:
                        self.assertGreaterEqual(widget.winfo_rooty(),root.winfo_rooty())
                        self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(),root.winfo_rooty()+root.winfo_height())
                controller.reveal();root.update_idletasks()
                self.assertEqual(controller.view.result.cget('text'),question['explanation'])
                self.assertGreater(canvas.yview()[0],0)
                canvas.yview_moveto(1);root.update_idletasks()
                self.assertGreater(canvas.yview()[0],0)
                controller.restart();root.update_idletasks()
                self.assertAlmostEqual(canvas.yview()[0],0,places=2)
                save.assert_not_called()
                self.assertEqual(errors,[])
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

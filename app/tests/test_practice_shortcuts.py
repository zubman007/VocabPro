"""Shortcut dispatch, modal guards and read-only previous-question review."""
from types import SimpleNamespace
from unittest.mock import Mock, patch
import tkinter as tk
import unittest
import customtkinter as cst
from app.grammar.practise import GrammarController
from app.grammar.theory_data import category_key
from app.vocabulary.practise import PracticeController
from app.tests.test_grammar_category_filter import questions


class ShortcutTests(unittest.TestCase):
    def setUp(self):
        try:self.root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        self.root.geometry('1400x850');self.root.update()
        self.errors=[];self.root.report_callback_exception=lambda *error:self.errors.append(error)
        self.translation=patch('app.shared.settings.T',side_effect=lambda key:key)
        self.translation.start()

    def tearDown(self):
        self.translation.stop()
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def controller(self):
        return GrammarController(self.root,questions()[:2],'unused.csv',Mock(),learned_by='Czech')

    def test_four_answer_shortcuts_score_once_and_are_removed_with_the_screen(self):
        external=self.root.bind('1',lambda event:None,add='+')
        controller=self.controller()
        with patch('app.grammar.practise.save_answers') as save,patch('app.grammar.practise.play_effect'):
            for index in range(4):
                controller.restart();save.reset_mock()
                self.assertIn(controller.bindings.tokens[str(index+1)],self.root.bind(str(index+1)))
                controller.answer_shortcut(index,SimpleNamespace(state=0))
                controller.answer_shortcut(index,SimpleNamespace(state=0))
                save.assert_not_called()
                self.assertEqual(controller.session.correct+controller.session.incorrect,1)
                self.assertTrue(controller.session.revealed)
        controller.view.root.destroy()
        self.assertIn(external,self.root.bind('1'))
        for key in ('2','3','4','<Control-z>','<Alt-Right>'):self.assertEqual(self.root.bind(key),'')

    def test_navigation_and_review_never_write_another_answer(self):
        controller=self.controller()
        with patch('app.grammar.practise.save_answers') as save:
            first=controller.session.current
            controller.continue_if_revealed()
            self.assertIs(controller.session.current,first)
            controller.review_previous()
            self.assertIsNone(controller._review_window)
            controller.reveal_or_next()
            self.assertTrue(controller.session.revealed)
            controller.continue_if_revealed()
            current=controller.session.current
            scores=(controller.session.correct,controller.session.incorrect)
            controller.review_previous()
            review=controller._review_window
            self.assertTrue(review.winfo_exists())
            controller.answer_shortcut(0)
            controller.next_shortcut()
            self.assertIs(controller.session.current,current)
            self.assertEqual((controller.session.correct,controller.session.incorrect),scores)
            review.destroy()
            controller.next_shortcut()
            self.assertIsNone(controller.session.current)
            save.assert_not_called()

    def test_physical_czech_keys_and_numpad_dispatch_to_all_four_answers(self):
        controller=self.controller()
        with patch.object(controller,'choose') as choose:
            for index in range(4):
                controller.answer_key(SimpleNamespace(keysym=('plus','ecaron','scaron','ccaron')[index],keycode=180+index,state=0))
                choose.assert_called_with(index)
                controller.answer_key(SimpleNamespace(keysym=f'KP_{index+1}',keycode=97+index,state=0))
                choose.assert_called_with(index)
            choose.reset_mock()
            controller.answer_key(SimpleNamespace(keysym='ecaron',keycode=50,state=4))
            controller.answer_key(SimpleNamespace(keysym='a',keycode=65,state=0))
            choose.assert_not_called()

    def test_czech_key_event_from_question_canvas_and_unrelated_hidden_window(self):
        controller=self.controller()
        unused=cst.CTkToplevel(self.root);unused.withdraw()
        self.root.update();self.root.focus_force()
        controller.view.question._parent_canvas.focus_set();self.root.update()
        with patch('app.grammar.practise.save_answers') as save,patch('app.grammar.practise.play_effect'):
            # Windows cannot synthesize accented keysyms absent from the active
            # OS layout; those mappings are covered by the dispatch test above.
            for key in ('plus','1','2','3','4'):
                controller.restart();save.reset_mock()
                controller.view.question._parent_canvas.event_generate('<KeyPress>',keysym=key)
                self.root.update()
                save.assert_not_called()
        unused.destroy()

    def test_real_key_event_reaches_the_controller(self):
        controller=self.controller()
        self.root.update()
        self.root.focus_force()
        self.root.update()
        with patch('app.grammar.practise.save_answers') as save,patch('app.grammar.practise.play_effect'):
            self.root.event_generate('<KeyPress>',keysym='1',state=0x8)
            self.root.update()
            save.assert_not_called()

    def test_filter_and_theory_shortcuts_guard_the_parent_question(self):
        controller=self.controller()
        with patch('app.grammar.practise.save_answers') as save:
            controller.answer_shortcut(0,SimpleNamespace(state=4))
            save.assert_not_called()
            controller.filter_shortcut()
            self.assertTrue(controller._filter_window.winfo_exists())
            controller.answer_shortcut(0)
            save.assert_not_called()
            controller._filter_window.destroy()
            question=controller.session.current
            controller.theory={category_key(question['category']):dict(category=question['category'],title='Theory',rules='A rule')}
            controller.theory_shortcut()
            self.assertTrue(controller._theory_window.winfo_exists())
            controller.answer_shortcut(0)
            save.assert_not_called()
            controller._theory_window.destroy()

    def test_vocabulary_number_keys_only_work_for_visible_choices_without_modifiers(self):
        controller=PracticeController.__new__(PracticeController)
        controller.app=self.root
        controller.action_frm=Mock();controller.action_frm.winfo_ismapped.return_value=True
        controller.opc_frm=Mock();controller.opc_frm.winfo_ismapped.return_value=True
        controller.Conf_resp=Mock()
        event=SimpleNamespace(state=0)
        controller.Choice_shortcut('answer',event)
        controller.Conf_resp.assert_called_once_with('answer',event)
        controller.Conf_resp.reset_mock()
        controller.Choice_shortcut('answer',SimpleNamespace(state=4))
        controller.opc_frm.winfo_ismapped.return_value=False
        controller.Choice_shortcut('answer',event)
        controller.opc_frm.winfo_ismapped.return_value=True
        dialog=cst.CTkToplevel(self.root)
        controller.Choice_shortcut('answer',event)
        dialog.destroy()
        controller.Conf_resp.assert_not_called()

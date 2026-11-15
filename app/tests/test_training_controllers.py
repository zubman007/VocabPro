"""Controller lifecycle and persistence failures using Tk and synthetic data."""
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.grammar.practise import GrammarController
from app.conjugation.practise import ConjugationController
from app.conjugation.data import Verb


class ControllerTests(unittest.TestCase):
    def test_conjugation_window_close_obeys_cancel_and_discard(self):
        controller=self.conjugation()
        controller.session.selection.loc[0,'R']='S'
        token=self.root.protocol('WM_DELETE_WINDOW')
        with patch.object(self.root,'destroy') as destroy,\
                patch('app.conjugation.practise.messagebox.askyesnocancel',return_value=None) as ask:
            self.root.tk.call(token)
            ask.assert_called_once();destroy.assert_not_called()
            self.assertFalse(controller.bindings.closed)
            ask.return_value=False
            self.root.tk.call(token)
            destroy.assert_called_once()
            self.assertTrue(controller.bindings.closed)

    def test_exit_save_failure_preserves_screen_and_pending_changes(self):
        controller=self.grammar();controller.choose(0)
        with patch.object(self.root,'destroy') as destroy,\
                patch('app.grammar.practise.messagebox.askyesnocancel',return_value=True),\
                patch('app.grammar.practise.save_answers',side_effect=PermissionError('locked')),\
                patch('app.grammar.practise.messagebox.showerror'):
            controller.exit_app()
            destroy.assert_not_called()
            self.assertFalse(controller.bindings.closed)
            self.assertEqual(len(controller.pending_answers),1)

    def test_conjugation_clean_back_neither_prompts_nor_saves(self):
        controller=self.conjugation()
        with patch('app.conjugation.practise.messagebox.askyesnocancel') as ask, \
             patch('app.conjugation.practise.save_results') as save:
            controller.back()
            ask.assert_not_called();save.assert_not_called()
        controller.on_back.assert_called_once()

    def setUp(self):
        try:
            self.root = cst.CTk()
            self.root.geometry('1200x800')
            self.root.update()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.directory=TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.errors = []
        self.root.report_callback_exception = lambda *error: self.errors.append(error)
        self.translation = patch('app.shared.settings.T', side_effect=lambda value: value)
        self.translation.start()

    def tearDown(self):
        self.translation.stop()
        for timer in self.root.tk.call('after', 'info'):
            self.root.tk.call('after', 'cancel', timer)
        self.root.destroy()
        self.assertEqual(self.errors, [])

    def grammar(self):
        question = dict(id='1', prompt='Choose', anchor='Sentence', options=['yes','no','x','y'],
                        correct_answer='yes', explanation='Reason', count_trailing_s=0)
        return GrammarController(self.root, [question], Path(self.directory.name)/'English_gra.csv', Mock())

    def conjugation(self):
        source = pd.DataFrame({'ID':[1], 'R':[''], 'LR':['']})
        verb = Verb(1, 'form', '', '', '', '', '', 'present', 'base', 'target')
        return ConjugationController(self.root, source, source, [verb], [('s1','I'), ('s2','You')],
                                     Path(self.directory.name)/'Czech_English_con.csv', Mock())

    def test_grammar_write_failure_keeps_answer_retryable(self):
        controller = self.grammar()
        index = controller.session.options.index('yes')
        with patch('app.grammar.practise.play_effect'):controller.choose(index)
        self.assertEqual(len(controller.pending_answers),1)
        with patch('app.grammar.practise.save_answers',side_effect=PermissionError('locked')), \
             patch('app.grammar.practise.messagebox.showerror') as error:
            self.assertFalse(controller.save())
        error.assert_called_once()
        self.assertEqual(len(controller.pending_answers),1)
        self.assertEqual(controller.session.correct,1)
        with patch('app.grammar.practise.save_answers') as save, patch('app.grammar.practise.play_effect'):
            controller.choose(index)
            controller.save()
        save.assert_called_once()
        self.assertEqual(controller.pending_answers,[])
        self.assertEqual(controller.session.correct, 1)
        self.assertTrue((Path(self.directory.name)/'English_gra_records.csv').exists())

    def test_reveal_and_finish_do_not_save_or_score_twice(self):
        controller = self.grammar()
        with patch('app.grammar.practise.save_answers') as save:
            controller.reveal()
            controller.reveal()
            controller.next_question()
            controller.reveal()
        save.assert_not_called()
        self.assertEqual(controller.session.incorrect, 1)
        self.assertEqual(controller.view.prompt.cget('text'), 'Done')
        controller.view.next.invoke()
        self.assertEqual(controller.session.incorrect, 0)
        self.assertEqual(controller.session.current['id'], '1')

    def test_switching_screens_releases_only_the_old_screens_bindings(self):
        external = self.root.bind('<Return>', lambda event: None, add='+')
        first = self.grammar()
        old_tokens = list(first.bindings.tokens.values())
        second = self.conjugation()
        self.assertTrue(first.bindings.closed)
        self.assertIn(external, self.root.bind('<Return>'))
        self.assertFalse(any(token in self.root.bind('<Return>') for token in old_tokens))
        second.view.root.destroy()
        self.assertTrue(second.bindings.closed)
        self.assertIn(external, self.root.bind('<Return>'))
        for sequence in ('<Control-s>', '<Control-r>', '<KeyRelease-Control_L>'):
            self.assertEqual(self.root.bind(sequence), '')

    def test_conjugation_failed_final_save_can_be_retried_without_duplicate_result(self):
        controller = self.conjugation()
        controller.view.variables['s1'].set('form')
        with patch('app.conjugation.practise.save_results',side_effect=PermissionError('locked')), \
             patch('app.conjugation.practise.messagebox.showerror'), patch('app.conjugation.practise.play_effect'):
            controller.confirm()
            controller.confirm()
        self.assertFalse(controller.bindings.closed)
        self.assertEqual(controller.session.completed, 1)
        self.assertEqual(controller.session.selection.R.tolist(), ['S'])
        controller.on_back.assert_not_called()
        with patch('app.conjugation.practise.save_results',return_value=controller.source) as save:
            controller.save()
            controller.save()
        save.assert_called_once()
        controller.on_back.assert_called_once_with()
        self.assertTrue(controller.bindings.closed)

    def test_skip_final_verb_saves_without_success(self):
        controller = self.conjugation()
        with patch('app.conjugation.practise.save_results',return_value=controller.source) as save:
            controller.skip()
        save.assert_called_once()
        self.assertEqual(controller.session.completed, 0)
        self.assertEqual(controller.session.selection.R.tolist(), [''])
        controller.on_back.assert_called_once_with()

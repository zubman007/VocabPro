"""Missing CSV fields, deferred answer commits and clean/dirty navigation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock,patch
import tkinter as tk
import unittest
from time import perf_counter, sleep
import customtkinter as cst
import pandas as pd
from app.repositories.grammar import Load_questions_from_csv, save_answers
from app.grammar.practise import GrammarController
from app.shared.storage import FileChangedError


def source(path):
    path.write_text('question_id;prompt;anchor;option_1;option_2;option_3;option_4;explanation;R;LR\n'
        '1;Choose;Sentence;yes;no;x;y\n2;Choose;Other;right;wrong;x;y\n',encoding='utf-8')


class GrammarPersistenceTests(unittest.TestCase):
    def test_short_csv_rows_load_empty_optional_fields_and_atomic_batch_commit(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'English_gra.csv';source(path)
            questions=Load_questions_from_csv(path)
            self.assertEqual(questions[0]['repetition'],'')
            self.assertEqual(questions[0]['explanation'],'')
            before=path.read_bytes()
            answer=('1','S',questions[0],'2026-11-14 10:00:00')
            with self.assertRaises(FileChangedError):save_answers(path,[answer,('99','F',None,'2026-11-14 11:00:00')])
            self.assertEqual(path.read_bytes(),before)
            save_answers(path,[answer,('1','F',questions[0],'2026-11-14 12:00:00')])
            frame=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False).set_index('question_id')
            self.assertEqual(frame.loc['1','R'],'SF')
            self.assertEqual(frame.loc['1','LR'],'2026-11-14 12:00:00')
            self.assertEqual(frame.loc['2','R'],'')

    def test_no_answers_never_touches_the_file(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'English_gra.csv';source(path);before=path.read_bytes()
            save_answers(path,[])
            self.assertEqual(path.read_bytes(),before)


class GrammarNavigationTests(unittest.TestCase):
    def test_grammar_editor_unchanged_apply_does_not_trigger_save_question(self):
        from app.grammar.editor import GrammarEditor
        from app.tests.test_grammar_editor import questions
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw()
        try:
            with TemporaryDirectory() as folder,patch('app.shared.settings.T',side_effect=lambda value:value):
                path=Path(folder)/'English_gra.csv';questions().to_csv(path,sep=';',index=False)
                back=Mock();editor=GrammarEditor(root,'English',path,back)
                editor.apply()
                with patch('app.grammar.editor.messagebox.askyesnocancel') as ask:editor.back();ask.assert_not_called()
                back.assert_called_once()
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

    def test_clean_back_and_deferred_save_cancel_discard_and_keyboard_save(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x900');root.update()
        try:
            with TemporaryDirectory() as folder,patch('app.shared.settings.T',side_effect=lambda value:value),patch('app.grammar.practise.play_effect'):
                path=Path(folder)/'English_gra.csv';source(path);before=path.read_bytes()
                back=Mock()
                controller=GrammarController(root,Load_questions_from_csv(path),path,back,learned_by='Czech')
                with patch('app.grammar.practise.messagebox.askyesnocancel') as ask:controller.back();ask.assert_not_called()
                back.assert_called_once()
                controller=GrammarController(root,Load_questions_from_csv(path),path,Mock(),learned_by='Czech')
                question=controller.session.current
                controller.choose(controller.session.options.index(question['correct_answer']))
                self.assertEqual(path.read_bytes(),before)
                self.assertEqual(len(controller.pending_answers),1)
                controller.restart()
                self.assertEqual(len(controller.pending_answers),1)
                with patch('app.grammar.practise.messagebox.askyesnocancel',return_value=None):controller.back()
                self.assertFalse(controller.bindings.closed)
                # Queue the synthetic key after pending focus/mapping events; specify modifier state.
                root.focus_force();root.update()
                # Windows grants native focus asynchronously; queued key events are
                # discarded until this interpreter owns focus. Wait for that state.
                deadline=perf_counter()+2
                while root.focus_displayof() is None and perf_counter()<deadline:
                    root.update();sleep(.005)
                self.assertIsNotNone(root.focus_displayof(),'Windows did not grant the test window focus')
                received=Mock()
                observer=root.bind('<Control-s>',received,add='+')
                root.event_generate('<KeyPress>', keysym='s', state=0x4, when='tail');root.update()
                received.assert_called_once()
                root.unbind('<Control-s>',observer)
                self.assertFalse(controller.pending_answers)
                self.assertTrue(controller.bindings.closed)
                saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False).set_index('question_id')
                self.assertEqual(saved.loc[question['id'],'R'],'S')
                controller=GrammarController(root,Load_questions_from_csv(path),path,Mock(),learned_by='Czech')
                controller.choose(controller.session.options.index(controller.session.current['correct_answer']))
                committed=path.read_bytes()
                with patch('app.grammar.practise.messagebox.askyesnocancel',return_value=False):controller.back()
                self.assertEqual(path.read_bytes(),committed)
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

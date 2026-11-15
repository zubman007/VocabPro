"""Grammar editing with synthetic CSVs; no writes to user courses."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.grammar.editor_data import GrammarDocument, FIELDS
from app.grammar.editor import GrammarEditor
from app.shared.storage import FileChangedError
from app.repositories.grammar import Load_questions_from_csv, save_answers


def questions():
    return pd.DataFrame({'question_id':['001','002'],'category':['Articles','Tenses'],
        'prompt':['Choose','Choose'],'anchor':['A sentence','Another sentence'],
        'option_1':['one','yes'],'option_2':['two','no'],'option_3':['three','maybe'],
        'option_4':['four','never'],'explanation':['A reason','Another reason'],
        'R':['SF','SS'],'LR':['2026-11-13 10:00:00',''], 'custom':['007;keep','NA']})


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'English_gra.csv'
        questions().to_csv(self.path,sep=';',index=False)

    def test_edit_correct_answer_and_save_preserve_history_and_extra_columns(self):
        document=GrammarDocument(self.path)
        values=document.question('001');values['anchor']='Changed; sentence\nwith a newline'
        document.update('001',values,2)
        document.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.question_id.tolist(),['001','002'])
        self.assertEqual(saved.loc[0,'option_1'],'three')
        self.assertEqual(saved.loc[0,'anchor'],values['anchor'])
        self.assertEqual(saved.R.tolist(),['SF','SS'])
        self.assertEqual(saved.custom.tolist(),['007;keep','NA'])
        self.assertFalse(document.dirty)

    def test_invalid_question_and_external_change_do_not_overwrite_file(self):
        document=GrammarDocument(self.path);original=self.path.read_bytes()
        values=document.question('001');values['option_2']=values['option_1']
        with self.assertRaises(ValueError):document.update('001',values)
        self.assertEqual(self.path.read_bytes(),original)
        self.path.write_bytes(original+b'\n')
        with self.assertRaises(FileChangedError):document.save()
        self.assertEqual(self.path.read_bytes(),original+b'\n')

    def test_new_question_ids_and_deleting_only_the_requested_row(self):
        document=GrammarDocument(self.path)
        identifier=document.add()
        self.assertEqual(identifier,'3')
        values=document.question('001')
        document.update(identifier,values)
        document.delete('002')
        document.save()
        self.assertEqual(document.frame.question_id.tolist(),['1','2'])
        self.assertEqual(document.question('2')['R'],'')
        self.assertEqual(document.question('1')['R'],'SF')

    def test_old_practice_question_cannot_write_to_renumbered_question(self):
        old_question=Load_questions_from_csv(self.path)[1]
        document=GrammarDocument(self.path)
        document.delete('001');document.save()
        original=self.path.read_bytes()
        with self.assertRaises(FileChangedError):
            save_answers(self.path,[(old_question['id'],'F',old_question,'2026-11-13 12:00:00')])
        self.assertEqual(self.path.read_bytes(),original)


class EditorUiTests(unittest.TestCase):
    def test_filter_apply_save_and_unsaved_back(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x900');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            with tempfile.TemporaryDirectory() as directory,patch('app.shared.settings.T',side_effect=lambda text:text), \
                    patch('app.grammar.editor.messagebox.showinfo'):
                path=Path(directory)/'English_gra.csv';questions().to_csv(path,sep=';',index=False)
                before=path.read_bytes();back=Mock()
                editor=GrammarEditor(root,'English',path,back)
                root.update()
                self.assertEqual(editor.view.tree.heading('id','text'),'ID')
                self.assertEqual(editor.view.category_filter.cget('dropdown_text_color'),'#244743')
                self.assertEqual(len(editor.view.tabs.cget('values')),2)
                self.assertGreater(sum(editor.view.tree.column(key,'width') for key in ('id','category','sentence')),
                    editor.view.tree.winfo_width()*.95)
                editor.view.category_filter.set('Tenses');editor.filter();root.update()
                self.assertEqual(editor.view.tree.get_children(),('002',))
                field=editor.view.fields['anchor'];field.delete('1.0','end');field.insert('1.0','Updated')
                editor.view.correct.set(1)
                self.assertTrue(editor.apply())
                self.assertEqual(editor.document.question('002')['option_1'],'no')
                self.assertEqual(path.read_bytes(),before)
                self.assertTrue(editor.save(close=False))
                saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
                self.assertEqual(saved.loc[1,'anchor'],'Updated')
                self.assertEqual(saved.R.tolist(),['SF','SS'])
                editor.document.frame.loc[1,'option_2']=editor.document.frame.loc[1,'option_1']
                editor.view.category_filter.set('Articles');editor.filter()
                with patch('app.grammar.editor.messagebox.showerror') as error:
                    self.assertFalse(editor.save())
                self.assertEqual(editor.current,'002')
                self.assertIn('002',error.call_args.kwargs['message'])
                option=editor.view.fields['option_2']
                option.delete(0,'end');option.insert(0,'a different answer')
                self.assertTrue(editor.apply())
                option.delete(0,'end');option.insert(0,editor.view.fields['option_1'].get())
                with patch('app.grammar.editor.messagebox.showerror'):
                    self.assertFalse(editor.apply())
                self.assertEqual(option.get(),editor.view.fields['option_1'].get())
                field.delete('1.0','end');field.insert('1.0','Not saved')
                with patch('app.grammar.editor.messagebox.askyesnocancel',return_value=None):editor.back()
                back.assert_not_called()
                with patch('app.grammar.editor.messagebox.askyesnocancel',return_value=False):editor.back()
                back.assert_called_once()
                self.assertEqual(errors,[])
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

"""Theory edits and language-specific file creation use only temporary CSVs."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.grammar.editor_theory import GrammarTheoryEditor
from app.grammar.editor_theory_data import GrammarTheoryDocument
from app.repositories.grammar_theory import load_theory
from app.shared.storage import FileChangedError
from app.repositories.grammar_theory import ensure_theory_categories


def source():
    return pd.DataFrame({'category':['Articles','Tenses'],'title':['Articles','Verb tenses'],
        'rules':['A rule','Another rule'],'examples':['A | B','C'], 'extra':['007','NA']})


class TheoryDocumentTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'Czech_English_gra_ex.csv'
        source().to_csv(self.path,sep=';',index=False)

    def test_save_preserves_extra_fields_and_the_reader_accepts_multiline_theory(self):
        document=GrammarTheoryDocument(self.path)
        values=document.question('1');values['rules']='A rule; with punctuation\nand another line'
        document.update('1',values);document.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.extra.tolist(),['007','NA'])
        self.assertNotIn('_editor_id',saved)
        self.assertNotIn('question_count',saved)
        self.assertEqual(load_theory(self.path)['articles']['rules'],values['rules'])

    def test_duplicate_categories_and_concurrent_changes_are_rejected(self):
        document=GrammarTheoryDocument(self.path)
        values=document.question('1');values['category']=' TENSES '
        with self.assertRaises(ValueError):document.update('1',values)
        original=self.path.read_bytes();self.path.write_bytes(original+b'\n')
        with self.assertRaises(FileChangedError):document.save()
        self.assertEqual(self.path.read_bytes(),original+b'\n')

    def test_new_language_file_is_created_only_on_save(self):
        path=self.path.with_name('German_English_gra_ex.csv')
        document=GrammarTheoryDocument(path)
        identifier=document.add()
        document.update(identifier,dict(category='Articles',title='Artikel',rules='A rule'))
        self.assertFalse(path.exists())
        document.save()
        self.assertEqual(set(load_theory(path)),{'articles'})
        document.delete(identifier);document.save()
        self.assertEqual(load_theory(path),{})

    def test_missing_category_gets_empty_counterpart_without_changing_existing_theory(self):
        self.assertEqual(ensure_theory_categories(self.path,['Articles','New',' new ']),1)
        frame=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(frame.loc[frame.category.eq('New'),'title'].tolist(),[''])
        self.assertEqual(frame.loc[0,'rules'],'A rule')
        self.assertEqual(frame.loc[0,'extra'],'007')
        self.assertNotIn('new',load_theory(self.path))
        document=GrammarTheoryDocument(self.path)
        document.save()
        before=self.path.read_bytes()
        self.assertEqual(ensure_theory_categories(self.path,['NEW']),0)
        self.assertEqual(self.path.read_bytes(),before)


class TheoryEditorUiTests(unittest.TestCase):
    def test_theory_form_filters_edits_and_saves_without_touching_questions(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x900');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            with tempfile.TemporaryDirectory() as directory,patch('app.shared.settings.T',side_effect=lambda text:text), \
                 patch('app.grammar.editor.messagebox.showinfo'):
                path=Path(directory)/'Czech_English_gra_ex.csv';source().to_csv(path,sep=';',index=False)
                question_path=path.with_name('English_gra.csv')
                question_path.write_text('category;prompt\nNew category;A question\n',encoding='utf-8')
                original=question_path.read_bytes()
                editor=GrammarTheoryEditor(root,'English',path,Mock())
                root.update()
                self.assertIn('New category',editor.view.fields['category'].cget('values'))
                self.assertNotIn('option_1',editor.view.fields)
                editor.view.query.insert(0,'tenses');editor.filter()
                self.assertEqual(len(editor.view.tree.get_children()),1)
                rules=editor.view.fields['rules'];rules.delete('1.0','end');rules.insert('1.0','Updated rule')
                self.assertTrue(editor.save(close=False))
                self.assertEqual(load_theory(path)['tenses']['rules'],'Updated rule')
                self.assertEqual(question_path.read_bytes(),original)
                self.assertEqual(errors,[])
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

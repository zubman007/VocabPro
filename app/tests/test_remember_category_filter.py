"""Persistent filters use temporary files and remain separate for each course."""
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch
import customtkinter as cst
from app.repositories.grammar_filters import load_filter, save_filter
from app.grammar.practise import Grammar_training
from app.tests.test_grammar_editor import questions


class RememberFilterTests(unittest.TestCase):
    def test_saving_settings_preserves_filter_changed_while_dialog_was_open(self):
        from app.tests.test_preferences_data import sample_preferences
        from app.repositories.preferences import load_preferences, save_preferences
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            original=sample_preferences();original.to_csv(path,sep=';',index=False)
            save_filter(path,'Czech','English',{'articles'},{'articles','tenses'})
            save_preferences(original,{'Learn batch':'12'},path)
            self.assertEqual(load_filter(path,'Czech','English',{'articles','tenses'}),{'articles'})
            saved=load_preferences(path)
            self.assertEqual(saved.loc[saved.Name.eq('Learn batch'),'Value'].iloc[0],'12')

    def test_course_separation_deleted_categories_and_all_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'filters.csv'
            save_filter(path,'Czech','English',{'articles'},{'articles','tenses'})
            save_filter(path,'Czech','Spanish',{'verbs'},{'verbs','other'})
            self.assertEqual(load_filter(path,'Czech','English',{'articles','tenses'}),{'articles'})
            self.assertEqual(load_filter(path,'Czech','Spanish',{'verbs','other'}),{'verbs'})
            self.assertIsNone(load_filter(path,'German','English',{'articles','tenses'}))
            self.assertIsNone(load_filter(path,'Czech','English',{'renamed'}))
            save_filter(path,'Czech','English',{'articles','tenses'},{'articles','tenses'})
            self.assertIsNone(load_filter(path,'Czech','English',{'articles','tenses','new'}))
            self.assertEqual(load_filter(path,'Czech','Spanish',{'verbs','other'}),{'verbs'})

    def test_malformed_file_falls_back_and_is_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'filters.csv';path.write_text('bad;schema\nx;y\n',encoding='utf-8')
            original=path.read_bytes()
            self.assertIsNone(load_filter(path,'Czech','English',{'articles'}))
            with self.assertRaises(ValueError):save_filter(path,'Czech','English',{'articles'},{'articles','tenses'})
            self.assertEqual(path.read_bytes(),original)

    def test_unchanged_filter_does_not_write_again(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'filters.csv'
            save_filter(path,'Czech','English',{'articles'},{'articles','tenses'})
            with patch('app.repositories.grammar_filters.save_csv') as write:
                save_filter(path,'Czech','English',{'articles'},{'articles','tenses'})
                write.assert_not_called()

    def test_reopen_restore_explicit_statistics_override_and_disabled_setting(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw();root.update()
        try:
            with tempfile.TemporaryDirectory() as directory,patch('app.shared.settings.T',side_effect=lambda key:key):
                base=Path(directory);(base/'files').mkdir()
                questions().to_csv(base/'files'/'English_gra.csv',sep=';',index=False)
                with patch_context(root_dir=base),patch_preferences(learned_by='Czech'),patch_preferences(remember_grammar_categories=True):
                    first=Grammar_training(root,'English');first.apply_filter({'tenses'})
                    second=Grammar_training(root,'English')
                    self.assertEqual(second.selected_categories,{'tenses'})
                    self.assertEqual(len(second.session.questions),1)
                    third=Grammar_training(root,'English',categories=['Articles'])
                    self.assertEqual(third.selected_categories,{'articles'})
                    saved=(base/'files'/'settings.csv').read_bytes()
                    with patch_preferences(remember_grammar_categories=False):
                        fourth=Grammar_training(root,'English')
                        self.assertEqual(len(fourth.session.questions),2)
                        fourth.apply_filter({'tenses'})
                    self.assertEqual((base/'files'/'settings.csv').read_bytes(),saved)
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

"""Optional persisted tags: old/new courses, editing and practice preservation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import pandas as pd
import customtkinter as cst
from app.repositories.vocabulary import load_vocabulary, save_practice
from app.repositories.courses import ensure_course
from app.vocabulary.editor_data import prepare_save, filter_vocabulary, sort_vocabulary, normalize_tags
from app.tests.test_editor_save import course


class VocabularyTagTests(TestCase):
    def test_multiple_tags_keep_order_remove_duplicates_and_empty_entries(self):
        self.assertEqual(normalize_tags(' animal, insult,, ANIMAL , travel '),'animal, insult, travel')
        for value in (None, '', ' , , ', float('nan')):
            self.assertEqual(normalize_tags(value), '')

    def test_exact_tag_filter_matches_individual_tags_not_partial_names(self):
        frame = pd.DataFrame({'Tags':['animal, insult','wild animal','travel','']})
        self.assertEqual(filter_vocabulary(frame,'Tags','equals','ANIMAL').Tags.tolist(),['animal, insult'])
        self.assertEqual(filter_vocabulary(frame,'Tags','equals','insult').Tags.tolist(),['animal, insult'])
        self.assertEqual(len(filter_vocabulary(frame,'Tags','contains','animal')),2)
        self.assertEqual(len(filter_vocabulary(frame,'Tags','excludes','animal')),2)
        self.assertEqual(filter_vocabulary(frame,'Tags','equals','').Tags.tolist(),[''])

    def test_multiple_tags_save_normalizes_only_tags_and_does_not_mutate_input(self):
        previous = course().assign(Tags='')
        edited = previous.drop(columns='Created').assign(Tags=' animal, insult, ANIMAL, ')
        result = prepare_save(edited, previous)
        self.assertEqual(result.Tags.tolist(), ['animal, insult'])
        self.assertEqual(edited.Tags.tolist(), [' animal, insult, ANIMAL, '])
        baseline = prepare_save(previous.drop(columns='Created'), previous)
        pd.testing.assert_frame_equal(result.drop(columns='Tags'), baseline.drop(columns='Tags'))

    def test_legacy_load_adds_empty_tags_without_rewriting_file(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';course().to_csv(path,sep=';',index=False)
            before=path.read_bytes();frame=load_vocabulary(path,'English','Czech')
            self.assertEqual(frame.Tags.tolist(),[''])
            self.assertEqual(path.read_bytes(),before)

    def test_new_course_contains_empty_persisted_tags(self):
        with TemporaryDirectory() as directory:
            ensure_course(directory,'Czech','Spanish')
            frame=pd.read_csv(Path(directory)/'Czech_Spanish_voc.csv',sep=';',keep_default_na=False)
            self.assertIn('Tags',frame.columns);self.assertTrue(frame.empty)

    def test_tag_edits_filter_sort_and_practice_preserve_values(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';previous=course();previous['Tags']=''
            edited=previous.drop(columns='Created').copy();edited['Tags']='work, travel'
            result=prepare_save(edited,previous)
            self.assertEqual(result.Tags.tolist(),['work, travel'])
            self.assertEqual(result.Repetition.tolist(),previous.Repetition.tolist())
            self.assertEqual(len(filter_vocabulary(result,'Tags','contains','TRAVEL')),1)
            self.assertEqual(sort_vocabulary(result,'Tags').Tags.tolist(),['work, travel'])
            result.to_csv(path,sep=';',index=False)
            session=result.copy();session['Repetition']='SFS'
            save_practice(path,session,session.iloc[:0],list(result),original=result)
            self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False).Tags.tolist(),['work, travel'])

    def test_editor_tags_are_editable_and_optional(self):
        from app.core.context import AppContext
        from app.preferences.data import RuntimePreferences
        from app.tests.test_preferences_data import sample_preferences
        from app.vocabulary.editor import EditorController
        with TemporaryDirectory() as directory:
            folder=Path(directory);course().to_csv(folder/'Czech_English_voc.csv',sep=';',index=False)
            root=cst.CTk()
            try:
                context=AppContext(files_dir=folder,preferences=RuntimePreferences.from_frame(sample_preferences()),on_home=lambda:None)
                editor=EditorController(root,'English',context=context)
                root.update()
                column=editor.headers.index('Tags')
                self.assertEqual(editor.default_vals[column],'')
                editor.edit_tbl.set_cell_data(0,column,'travel')
                editor.Sync_changes(1,'')
                self.assertEqual(editor.main_df.Tags.tolist(),['travel'])
            finally:
                for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
                root.destroy()

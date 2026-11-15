"""Stable IDs, filtered deletion, legacy compatibility and commit safety."""
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
from threading import Event
from unittest.mock import patch
import tempfile
import tkinter as tk
import unittest
import customtkinter as cst
import pandas as pd
from app.vocabulary.editor import EditorController
from app.repositories.vocabulary import save_course
from app.repositories.vocabulary import load_vocabulary
from app.vocabulary.id_sequence import next_word_id
from app.repositories.vocabulary import save_practice
from app.tests.test_editor_save import course
from app.repositories import synonyms


class VocabularyDeletionTests(unittest.TestCase):
    def test_deleting_word_removes_all_its_links_from_both_columns_only_after_save(self):
        from app.shared.storage import file_revision
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_voc.csv'
            words=pd.concat([course()]*4,ignore_index=True);words['ID']=[1,2,3,4]
            words.to_csv(path,sep=';',index=False)
            synonyms.replace_links(path,2,[1,3,4],None)
            _,revision=synonyms.load(path,words)
            synonyms.replace_links(path,1,[2,4],revision)
            links=synonyms.relation_path(path);before=links.read_bytes()
            edited=load_vocabulary(path,'English','Czech').loc[lambda frame:frame.ID.ne(2)].copy()
            self.assertEqual(links.read_bytes(),before)
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*args,**kw:frame), \
                 patch('app.vocabulary.save_workflow.clean_audio_files'):
                save_course(edited,path,'English',directory,file_revision(path),Event(),lambda *args:None)
            remaining=pd.read_csv(links,sep=';')
            self.assertEqual(remaining[['ID 1','ID 2']].values.tolist(),[[1,4]])
            self.assertEqual(pd.read_csv(path,sep=';').ID.tolist(),[1,3,4])

    def test_save_removes_word_keeps_ids_history_and_reuses_deleted_tail(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_voc.csv'
            frame=pd.concat([course(),course()],ignore_index=True)
            frame['ID']=[4,5];frame['Repetition']=['SF','SS']
            frame.to_csv(path,sep=';',index=False)
            synonyms.replace_links(path,4,[5],None)
            (Path(directory)/'5.wav').write_bytes(b'old recording')
            from app.shared.storage import file_revision
            revision=file_revision(path)
            edited=load_vocabulary(path,'English','Czech').iloc[:1].copy()
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*args,**kw:frame), \
                 patch('app.vocabulary.save_workflow.clean_audio_files'):
                save_course(edited,path,'English',directory,revision,Event(),lambda *args:None)
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(saved.ID.tolist(),['4'])
            self.assertEqual(saved.Repetition.tolist(),['SF'])
            self.assertNotIn('Enabled',saved)
            self.assertTrue(pd.read_csv(synonyms.relation_path(path),sep=';').empty)
            self.assertEqual(next_word_id(path,saved.assign(ID=saved.ID.astype(int))),5)
            self.assertFalse((Path(directory)/'5.wav').exists())
            self.assertEqual(next((Path(directory)/'deleted').glob('5_*.wav')).read_bytes(),b'old recording')
            reopened=load_vocabulary(path,'English','Czech')
            new=reopened.iloc[:1].copy();new['ID']=next_word_id(path,reopened)
            new['English']='new word';new['Repetition']=''
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*args,**kw:frame), \
                 patch('app.vocabulary.save_workflow.clean_audio_files'):
                save_course(pd.concat([reopened,new],ignore_index=True),path,'English',directory,file_revision(path),Event(),lambda *args:None)
            self.assertEqual(pd.read_csv(path,sep=';').ID.tolist(),[4,5])
            self.assertTrue(synonyms.load(path,pd.read_csv(path,sep=';'))[0].empty)
            other=Path(directory)/'Czech_Spanish_voc.csv'
            self.assertEqual(next_word_id(other,pd.DataFrame({'ID':[2]})),3)

    def test_only_tail_is_reused_and_old_counter_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv'
            (Path(directory)/'vocabulary_id_counters.csv').write_text('Course;Next ID\ncourse.csv;999\n')
            self.assertEqual(next_word_id(path,pd.DataFrame({'ID':[1,2,4]})),5)
            self.assertEqual(next_word_id(path,pd.DataFrame({'ID':[1,2,3]})),4)
            self.assertEqual(next_word_id(path,pd.DataFrame({'ID':[]})),1)

    def test_stale_practice_does_not_resurrect_a_deleted_word(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';source=course()
            source.to_csv(path,sep=';',index=False)
            source.iloc[:0].drop(columns='Enabled').to_csv(path,sep=';',index=False)
            save_practice(path,source.iloc[:0],source,list(source.columns))
            self.assertTrue(pd.read_csv(path,sep=';').empty)

    def test_filtered_deletion_requires_confirmation_and_does_not_touch_disk_until_save(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x850');root.update()
        try:
            with tempfile.TemporaryDirectory() as directory,patch('app.shared.settings.T',side_effect=lambda key:key),patch_preferences(learned_by='Czech'):
                base=Path(directory);(base/'files').mkdir()
                path=base/'files'/'Czech_English_voc.csv'
                frame=pd.concat([course(),course(),course()],ignore_index=True)
                frame['ID']=[1,5,9];frame['English']=['first','middle','last']
                frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
                with patch_context(root_dir=base):controller=EditorController(root,'English')
                controller.filt_col_var.set('English');controller.filt_entry_var.set('middle');controller.Filter()
                controller.edit_tbl.select_row(0)
                with patch('app.vocabulary.editor.messagebox.askyesno',return_value=False):controller.Delete_words()
                self.assertEqual(controller.main_df.ID.tolist(),[1,5,9])
                with patch('app.vocabulary.editor.messagebox.askyesno',return_value=True):controller.Delete_words()
                self.assertEqual(controller.main_df.ID.tolist(),[1,9])
                self.assertEqual(controller.edit_tbl.get_total_rows(),0)
                self.assertEqual(path.read_bytes(),before)
                controller.Refresh()
                self.assertEqual(controller.edit_tbl.get_total_rows(),2)
                controller.New_row(None)
                self.assertEqual(controller.main_df.ID.tolist(),[1,9,10])
                self.assertNotIn('Enabled',controller.headers)
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

"""Persistent ID tags: compatibility, membership, lessons and configuration limits."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import pandas as pd
from app.repositories.tags import encode_tags,decode_tags,save_catalog,load_catalog
from app.repositories.tag_lessons import tag_lesson
from app.shared.storage import file_revision
from app.tests.test_tag_catalog import catalog
from app.tests.test_editor_save import course
from app.vocabulary.practise_session import PracticeSession
from app.repositories.preferences import save_preferences
from app.tests.test_preferences_data import sample_preferences


class TagIdUpgradeTests(TestCase):
    def test_editor_and_practice_saves_persist_ids_and_preserve_other_fields(self):
        from unittest.mock import patch
        from threading import Event
        from app.core.context import AppContext
        from app.preferences.data import RuntimePreferences
        from app.repositories.vocabulary import read_words,save_practice
        from app.vocabulary.save_workflow import save_course
        with TemporaryDirectory() as directory:
            context=AppContext(files_dir=Path(directory),preferences=RuntimePreferences.from_frame(sample_preferences()))
            path=context.vocabulary_path('English');tag_path=context.tags_path('English')
            save_catalog(tag_path,catalog(),'Czech','English',None)
            original=course().assign(Tags='1, 3');original.to_csv(path,sep=';',index=False)
            edited=read_words(path)
            edited.ID=edited.ID.astype(int)
            edited['Tags']='Insults'
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*args,**kwargs:frame):
                save_course(edited,path,'English',context.audio_folder('English'),file_revision(path),Event(),None,context=context)
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(saved.Tags.tolist(),['3'])
            self.assertEqual(saved.Repetition.tolist(),['SF'])
            session=read_words(path);baseline=session.copy();session['Tags']='Animals'
            save_practice(path,session,session.iloc[:0],list(session),original=baseline)
            self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False).Tags.astype(str).tolist(),['1'])

    def test_editor_id_storage_display_language_disabled_tags_and_immediate_validation(self):
        from dataclasses import replace
        from types import SimpleNamespace
        from unittest.mock import patch
        import customtkinter as cst
        from app.core.context import AppContext
        from app.preferences.data import RuntimePreferences
        from app.vocabulary.editor import EditorController
        with TemporaryDirectory() as directory:
            root=cst.CTk();root.geometry('1450x950')
            try:
                context=AppContext(files_dir=Path(directory),preferences=RuntimePreferences.from_frame(sample_preferences()))
                save_catalog(context.tags_path('English'),catalog(),'Czech','English',None)
                path=context.vocabulary_path('English');course().assign(Tags='1, 3').to_csv(path,sep=';',index=False)
                before=path.read_bytes()
                editor=EditorController(root,'English',context=context);root.update()
                self.assertEqual(editor.main_df.Tags.tolist(),['Animals, Insults'])
                self.assertEqual(editor.main_df['Tag count'].tolist(),[2])
                editor.filt_col_var.set(editor.translate('Tag count'))
                editor.sign_var.set('>');editor.filt_entry_var.set('1');editor.Filter()
                self.assertEqual(editor.filt_df.ID.tolist(),[1])
                editor.sign_var.set('<');editor.Filter()
                self.assertTrue(editor.filt_df.empty)
                editor.Refresh()
                event=SimpleNamespace(column=editor.headers.index('Tags'),row=0,value='Animals, unknown')
                with patch('app.vocabulary.editor.messagebox.showerror') as error:
                    self.assertIsNone(editor.Validate_tag_cell(event));error.assert_called_once()
                event.value='Insults';self.assertEqual(editor.Validate_tag_cell(event),'Insults')
                context.preferences=replace(context.preferences,tags_enabled=False)
                editor=EditorController(root,'English',context=context);root.update()
                self.assertFalse(editor.edit_frm._word_tags_button.winfo_manager())
                self.assertEqual(path.read_bytes(),before)
            finally:
                for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
                root.destroy()

    def test_empty_statistics_tag_cannot_start_lesson(self):
        import customtkinter as cst
        from app.statistics.vocabulary_tags import VocabularyTagsPanel,TagStatistics
        root=cst.CTk()
        try:
            calls=[]
            panel=VocabularyTagsPanel(root,lambda key:key,calls.append);panel.pack(fill='both',expand=True)
            panel.set_items([TagStatistics('Empty tag',0,0,0,'1')]);root.update()
            buttons=[child for row in panel.rows.winfo_children() for child in row.winfo_children() if isinstance(child,cst.CTkButton)]
            self.assertEqual(len(buttons),1)
            self.assertEqual(buttons[0].cget('state'),'disabled')
            buttons[0].invoke();self.assertEqual(calls,[])
        finally:
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()

    def test_id_roundtrip_two_languages_cleanup_and_unknown_rejection(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_tags.csv'
            save_catalog(path,catalog(),'Czech','English',None)
            words=pd.DataFrame({'ID':[1],'Tags':['Animals, Nadávky, invented']})
            with self.assertRaises(ValueError):encode_tags(words,catalog(),'Czech','English')
            encoded=encode_tags(words,catalog(),'Czech','English',clean=True)
            self.assertEqual(encoded.Tags.tolist(),['1, 3'])
            self.assertEqual(decode_tags(encoded,path,'Czech','English',target=True).Tags.tolist(),['Animals, Insults'])
            with self.assertRaises(ValueError):encode_tags(encoded,catalog(),'Czech','English',maximum=1)

    def test_in_use_deletion_is_rejected_without_mutating_catalog(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_tags.csv'
            save_catalog(path,catalog(),'Czech','English',None)
            pd.DataFrame({'ID':['9'],'Tags':['1']}).to_csv(path.with_name('Czech_English_voc.csv'),sep=';',index=False)
            original=path.read_bytes()
            with self.assertRaises(ValueError):save_catalog(path,catalog().iloc[1:],'Czech','English',file_revision(path))
            self.assertEqual(path.read_bytes(),original)

    def test_lessons_order_dates_include_unlearned_and_handle_empty_tag(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'Czech_English_voc.csv';tags=folder/'Czech_English_tags.csv'
            save_catalog(tags,catalog(),'Czech','English',None)
            frame=pd.concat([course().assign(ID=1,Tags='1',Repetition='',**{'Next repetition':''}),
                course().assign(ID=2,Tags='1',**{'Next repetition':'2026-01-01 00:00:00'}),
                course().assign(ID=3,Tags='1',**{'Next repetition':'2025-01-01 00:00:00'})],ignore_index=True)
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            lesson=tag_lesson(path,tags,'Czech','English','1')
            self.assertEqual(lesson.ID.astype(int).tolist(),[1,3,2])
            lesson.ID=lesson.ID.astype(int)
            session=PracticeSession(lesson,{1:1},30)
            self.assertEqual(int(session.pick().ID),1)
            self.assertTrue(session.introduce(1))
            session.skip(1);self.assertEqual(int(session.pick().ID),3)
            self.assertTrue(tag_lesson(path,tags,'Czech','English','3').empty)
            self.assertTrue(tag_lesson(path,tags,'Czech','English','999').empty)
            self.assertEqual(path.read_bytes(),before)

    def test_settings_cannot_lower_limit_below_existing_assignments(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'settings.csv'
            frame=sample_preferences();frame.to_csv(path,sep=';',index=False)
            pd.DataFrame({'ID':['1'],'Tags':['1, 3']}).to_csv(folder/'Czech_English_voc.csv',sep=';',index=False)
            before=path.read_bytes()
            with self.assertRaises(ValueError):save_preferences(frame,{'Maximum tags per word':'1'},path)
            self.assertEqual(path.read_bytes(),before)

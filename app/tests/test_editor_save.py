"""Save/cancel/conflict safety with temporary CSV and no live providers."""
from pathlib import Path
from threading import Event
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.shared.background_task import CancelledError
from app.shared.storage import FileChangedError, file_revision
from app.repositories.vocabulary import save_course
from app.repositories.vocabulary import load_vocabulary
from app.vocabulary.editor_attributes import enrich_attributes


def course():
    return pd.DataFrame({'ID':[1], 'English':['NA'], 'Czech':['null'], 'Phonetic':['[]'],
        'Audio':['No audio'], 'Description':['manual'], 'Example':['manual example'],
        'Part of Speech':['Noun'], 'Enabled':['True'], 'Repetition':['SF'],
        'Next repetition':['2026-11-13 10:00:00'], 'Created':['2025-01-01'],
        'Custom':['007;keep']})


class EditorSaveTests(unittest.TestCase):
    def test_progress_counts_completed_rows_and_handles_empty_input(self):
        with tempfile.TemporaryDirectory() as directory:
            frame=pd.DataFrame({'ID':[8,2],'German':['one','two'],'Audio':['No audio']*2,
                'Description':['manual']*2,'Example':['manual']*2},index=[10,50])
            counts=[]
            enrich_attributes(frame,'German',directory,progress=lambda *value:counts.append(value),cleanup=False)
            self.assertEqual(counts,[(0,2),(1,2),(2,2)])
            counts.clear()
            enrich_attributes(frame.iloc[:0],'German',directory,progress=lambda *value:counts.append(value),cleanup=False)
            self.assertEqual(counts,[(0,0)])

    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'course.csv'
        course().to_csv(self.path,sep=';',index=False)
        self.revision=file_revision(self.path)
        self.edited=load_vocabulary(self.path,'English','Czech').drop(columns='Custom')

    def save(self, event=None):
        return save_course(self.edited,self.path,'English',self.directory.name,
                           self.revision,event or Event(),lambda *args:None)

    def test_complete_save_keeps_literal_text_and_unknown_columns(self):
        self.edited.loc[0,'Czech']='changed'
        with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*args,**kw:frame), \
             patch('app.vocabulary.save_workflow.clean_audio_files') as cleanup:
            self.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.English.tolist(),['NA'])
        self.assertEqual(saved.Custom.tolist(),['007;keep'])
        self.assertEqual(saved.Czech.tolist(),['changed'])
        self.assertEqual(saved.Repetition.tolist(),['SF'])
        cleanup.assert_called_once()

    def test_cancel_before_work_keeps_original(self):
        event=Event();event.set()
        with patch('app.vocabulary.save_workflow.enrich_attributes') as enrich:
            with self.assertRaises(CancelledError):self.save(event)
        enrich.assert_not_called()
        self.assertEqual(file_revision(self.path),self.revision)

    def test_cancel_after_enrichment_does_not_save_or_delete_audio(self):
        event=Event()
        def enrich(frame,*args,**kwargs):
            event.set()
            frame.loc[0,'Description']='changed'
            return frame
        original=self.edited.copy(deep=True)
        with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=enrich), \
             patch('app.vocabulary.save_workflow.clean_audio_files') as cleanup:
            with self.assertRaises(CancelledError):self.save(event)
        self.assertEqual(file_revision(self.path),self.revision)
        cleanup.assert_not_called()
        pd.testing.assert_frame_equal(self.edited,original)

    def test_concurrent_file_change_is_not_overwritten(self):
        def enrich(frame,*args,**kwargs):
            self.path.write_text('externally changed',encoding='utf-8')
            return frame
        with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=enrich), \
             patch('app.vocabulary.save_workflow.clean_audio_files') as cleanup:
            with self.assertRaises(FileChangedError):self.save()
        self.assertEqual(self.path.read_text(encoding='utf-8'),'externally changed')
        cleanup.assert_not_called()

    def test_failed_write_keeps_original_and_defers_audio_cleanup(self):
        with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=lambda frame,*a,**k:frame), \
             patch('app.vocabulary.save_workflow.save_csv',side_effect=PermissionError), \
             patch('app.vocabulary.save_workflow.clean_audio_files') as cleanup:
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(file_revision(self.path),self.revision)
        cleanup.assert_not_called()

    def test_non_destructive_enrichment_keeps_existing_audio(self):
        for suffix in ('wav','mp3'):(Path(self.directory.name)/f'1.{suffix}').write_bytes(b'old audio')
        frame=self.edited.copy()
        enrich_attributes(frame,'English',self.directory.name,cleanup=False)
        for suffix in ('wav','mp3'):
            self.assertEqual((Path(self.directory.name)/f'1.{suffix}').read_bytes(),b'old audio')

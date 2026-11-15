"""Audit regressions: exclusively synthetic data and temporary destinations."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest import TestCase
from unittest.mock import Mock, patch
import pandas as pd
from app.repositories import vocabulary, conjugation, grammar
from app.shared.storage import FileChangedError, file_revision
from app.shared.background_task import CancelledError
from app.tests.test_editor_save import course


class AuditSafetyTests(TestCase):
    def test_conjugation_preserves_external_text_and_extra_rows(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'verbs.csv'
            original = pd.DataFrame({'ID':[1,2], 'R':['S','F'], 'LR':['',''], 'English':['one','two']})
            latest = original.copy(); latest.loc[1,'English'] = 'external'
            latest.to_csv(path,sep=';',index=False)
            selection = original.iloc[:1].copy(); selection.loc[0,'R'] = 'SS'
            conjugation.save_results(original,selection,path)
            saved = pd.read_csv(path,sep=';',keep_default_na=False)
            self.assertEqual(saved.English.tolist(),['one','external'])
            self.assertEqual(saved.R.tolist(),['SS','F'])

    def test_conjugation_conflict_is_atomic(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'verbs.csv'
            original = pd.DataFrame({'ID':[1], 'R':['S'], 'LR':['']})
            latest=original.copy(); latest.loc[0,'R']='SF'; latest.to_csv(path,sep=';',index=False)
            selection=original.copy(); selection.loc[0,'R']='SS'
            before=path.read_bytes()
            with self.assertRaises(FileChangedError):conjugation.save_results(original,selection,path)
            self.assertEqual(path.read_bytes(),before)

    def test_vocabulary_delta_preserves_unedited_external_description(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'words.csv'; original=course().drop(columns='Enabled')
            latest=original.copy(); latest.loc[0,'Description']='external';latest.to_csv(path,sep=';',index=False)
            session=original.copy(); session.loc[0,'Repetition']='SFS'
            vocabulary.save_practice(path,session,session.iloc[:0],list(original),original=original)
            saved=pd.read_csv(path,sep=';',keep_default_na=False)
            self.assertEqual(saved.Description.tolist(),['external'])
            self.assertEqual(saved.Repetition.tolist(),['SFS'])

    def test_vocabulary_same_field_conflict_preserves_bytes(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'words.csv'; original=course().drop(columns='Enabled')
            latest=original.copy(); latest.loc[0,'Description']='external';latest.to_csv(path,sep=';',index=False)
            session=original.copy(); session.loc[0,'Description']='session'
            before=path.read_bytes()
            with self.assertRaises(FileChangedError):
                vocabulary.save_practice(path,session,session.iloc[:0],list(original),original=original)
            self.assertEqual(path.read_bytes(),before)

    def test_grammar_loader_rejects_duplicate_ids_before_training(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'questions.csv'
            path.write_text('question_id;prompt;anchor;option_1;option_2;option_3;option_4\n'
                '1;Choose;A;yes;no;x;y\n1;Choose;B;yes;no;x;y\n',encoding='utf-8-sig')
            with self.assertRaisesRegex(ValueError,'ID'):grammar.Load_questions_from_csv(path)

    def test_editor_playback_uses_child_audio_path(self):
        from app.vocabulary.editor import EditorController
        editor=EditorController.__new__(EditorController)
        editor._saving=False;editor.translate=lambda value:value;editor.edit_tbl=Mock()
        editor.edit_tbl.get_selected_cells.return_value={(0,0)}
        editor.edit_tbl.get_cell_data.return_value=1
        with TemporaryDirectory() as directory:
            editor.audio_folder=directory;(Path(directory)/'1.mp3').write_bytes(b'fake audio')
            with patch('app.vocabulary.editor.pygame.mixer') as mixer,patch('app.vocabulary.editor.messagebox.showerror') as error:
                editor.Play_audio(Mock(),None)
                mixer.music.load.assert_called_once_with(str(Path(directory)/'1.mp3'))
                error.assert_not_called()

    def test_cancelled_new_id_does_not_archive_audio(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';original=course();original.to_csv(path,sep=';',index=False)
            edited=original.copy();edited.loc[1]=original.iloc[0];edited.loc[1,'ID']=2
            audio=Path(directory)/'2.mp3';audio.write_bytes(b'old recording')
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=CancelledError):
                with self.assertRaises(CancelledError):
                    vocabulary.save_course(edited,path,'English',directory,file_revision(path),Event(),None)
            self.assertEqual(audio.read_bytes(),b'old recording')

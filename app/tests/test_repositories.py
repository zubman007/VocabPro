"""Persistence boundaries, snapshot conflicts and safe missing-file behavior."""
import ast
import importlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,defaultTestLoader
from unittest.mock import patch
from app.shared.storage import FileChangedError
from app.repositories.csv_store import read_document,commit_document
from app.repositories import vocabulary,preferences
from app.tests.test_editor_save import course
from app.tests.test_preferences_data import sample_preferences


class RepositoryTests(TestCase):
    def test_controllers_and_editable_documents_do_not_read_or_write_csv(self):
        root=Path(__file__).resolve().parents[1]
        for relative in ('vocabulary/editor.py','vocabulary/practise.py','vocabulary/editor_synonyms.py',
                'grammar/editor.py','grammar/practise.py','grammar/editor_data.py','grammar/editor_theory_data.py',
                'conjugation/practise.py','preferences/dialog.py'):
            for node in ast.walk(ast.parse((root/relative).read_text(encoding='utf-8'))):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,('read_csv','to_csv'),relative)
                if isinstance(node,ast.ImportFrom) and node.module=='app.shared.storage':
                    self.assertFalse({'file_revision','save_csv'} & {alias.name for alias in node.names},relative)

    def test_repositories_do_not_depend_on_ui_and_import_without_creating_files(self):
        folder=Path(__file__).resolve().parents[1]/'repositories'
        for path in folder.glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node,ast.ImportFrom):
                    self.assertFalse((node.module or '').startswith(('app.ui','customtkinter','tkinter','tksheet')),str(path))
            if path.stem!='__init__':importlib.import_module('app.repositories.'+path.stem)
        with TemporaryDirectory() as directory:
            path=Path(directory)/'missing.csv'
            frame,revision=read_document(path,optional=True,columns=['category','title'])
            self.assertTrue(frame.empty);self.assertIsNone(revision)
            self.assertFalse(path.exists())

    def test_vocabulary_snapshot_rejects_changes_during_load(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_voc.csv'
            course().to_csv(path,sep=';',index=False)
            original=vocabulary.load_vocabulary
            def concurrent_change(*args):
                frame=original(*args)
                with path.open('a',encoding='utf-8') as stream:stream.write('\n')
                return frame
            with patch.object(vocabulary,'load_vocabulary',side_effect=concurrent_change):
                with self.assertRaises(FileChangedError):vocabulary.load_editor_snapshot(path,'English','Czech')

    def test_missing_document_is_not_allowed_to_overwrite_an_externally_created_file(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'theory.csv'
            frame,revision=read_document(path,optional=True,columns=['category','title'])
            path.write_text('external content',encoding='utf-8')
            with self.assertRaises(FileChangedError):commit_document(path,frame,revision)
            self.assertEqual(path.read_text(encoding='utf-8'),'external content')

    def test_preferences_reject_changes_between_validation_and_commit(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            frame=sample_preferences();frame.to_csv(path,sep=';',index=False)
            validate=preferences.validate_preferences
            def concurrent_change(*args):
                result=validate(*args)
                external=frame.copy();external.loc[external.Name.eq('Learn batch'),'Value']='99'
                external.to_csv(path,sep=';',index=False)
                return result
            with patch.object(preferences,'validate_preferences',side_effect=concurrent_change):
                with self.assertRaises(FileChangedError):preferences.save_preferences(frame,{'Learn batch':'12'},path)
            self.assertEqual(preferences.load_preferences(path).set_index('Name').loc['Learn batch','Value'],'99')


def repository_ui_regressions():
    return defaultTestLoader.loadTestsFromNames([
        'app.tests.test_repositories.RepositoryTests',
        'app.tests.test_synonyms_ui',
        'app.tests.test_editor_async_ui',
        'app.tests.test_vocabulary_editor_dropdowns',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_grammar_editor_theory.TheoryEditorUiTests',
        'app.tests.test_grammar_theory',
        'app.tests.test_grammar_category_filter.FilterTests.test_filtered_round_restart_clear_and_dialog_cancel',
        'app.tests.test_learning_ui.LearningUiTests.test_preferences_dialog_stays_open_after_failed_write_then_saves',
        'app.tests.test_shared_controls.SharedControlsTests.test_about_and_preferences_header_actions_share_training_style_in_all_languages',
        'app.tests.test_module_header.ModuleHeaderTests.test_statistics_build_uses_header_and_preserves_language_switch',
        'app.tests.test_statistics_practice_link',
        'app.tests.test_app_context.ContextUiTests',
        'app.tests.test_screen_controller.ScreenControllerTests.test_async_editor_exit_waits_for_success_and_keeps_data_on_failure',
        'app.tests.test_module_consistency.ModuleConsistencyTests.test_both_grammar_editors_save_and_leave_once',
        'app.tests.test_learning_ui.LearningUiTests.test_conjugation_feedback_preserves_scoring_and_separates_header_rows',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
    ])

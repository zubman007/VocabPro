"""Context ownership, immutable settings, independent paths and worker snapshots."""
import ast
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from threading import Thread
from unittest import TestCase,defaultTestLoader
from unittest.mock import Mock,patch
from app.core.context import AppContext,get_context,_active
from app.tests.test_preferences_data import sample_preferences


class ContextTests(TestCase):
    def setUp(self):
        self.token=_active.set(AppContext())

    def tearDown(self):
        _active.reset(self.token)

    def test_context_paths_are_independent_and_do_not_create_files(self):
        with TemporaryDirectory() as directory:
            context=AppContext(root_dir=Path(directory)/'first')
            context.preferences=replace(context.preferences,learned_by='Czech')
            other=AppContext(root_dir=Path(directory)/'second',preferences=replace(context.preferences,learned_by='German'))
            self.assertEqual(context.vocabulary_path('Spanish').name,'Czech_Spanish_voc.csv')
            self.assertEqual(context.conjugation_path('Spanish').name,'Czech_Spanish_con.csv')
            self.assertEqual(context.grammar_path('Spanish').name,'Spanish_gra.csv')
            self.assertEqual(context.theory_path('Spanish').name,'Czech_Spanish_gra_ex.csv')
            self.assertEqual(other.audio_folder('English').name,'German_English')
            self.assertEqual(list(Path(directory).iterdir()),[])

    def test_explicit_and_inherited_contexts_win_over_current_context(self):
        first=AppContext();second=AppContext()
        owner=SimpleNamespace();first.bind(owner)
        second.bind(SimpleNamespace())
        child=SimpleNamespace(master=owner)
        self.assertIs(get_context(child),first)
        self.assertIs(get_context(child,second),second)
        self.assertIs(child.app_context,second)

    def test_localization_and_navigation_stay_bound_to_their_context(self):
        first=AppContext(on_home=Mock())
        second=AppContext(preferences=replace(first.preferences,app_language='Czech'),on_home=Mock())
        english=first.translate('Close');czech=second.translate('Close')
        self.assertNotEqual(english,czech)
        second.bind(SimpleNamespace())
        self.assertEqual(first.translate('Close'),english)
        first.go_home();first.on_home.assert_called_once();second.on_home.assert_not_called()

    def test_reload_publishes_complete_preferences_and_failure_preserves_snapshot(self):
        from app.main import Load_setting
        context=AppContext()
        frame=sample_preferences()
        with patch('app.main.load_preferences',return_value=frame),patch('app.main.ensure_course'),\
                patch('app.shared.audio_effects.configure') as audio:
            config=Load_setting(context)
        self.assertIs(context.preferences,config)
        audio.assert_called_once_with(config.sounds_enabled,config.sound_volume)
        invalid=frame.copy();invalid.loc[invalid.Name.eq('Learn batch'),'Value']='invalid'
        with patch('app.main.load_preferences',return_value=invalid),patch('app.main.ensure_course') as ensure:
            with self.assertRaises(ValueError):Load_setting(context)
        self.assertIs(context.preferences,config);self.assertIs(context.preferences_frame,frame)
        ensure.assert_not_called()

    def test_worker_receives_captured_context_instead_of_thread_default(self):
        from app.services.api import MW
        context=AppContext(root_dir=Path('isolated-course'))
        context.preferences=replace(context.preferences,learned_by='Czech')
        snapshot=replace(context,on_home=None,preferences_frame=None)
        context.preferences=replace(context.preferences,learned_by='German')
        errors=[]
        def work():
            try:MW(0,'frame','English',context=snapshot)
            except Exception as error:errors.append(error)
        with patch('app.services.api.merriam_entry',return_value='frame') as provider:
            thread=Thread(target=work);thread.start();thread.join(2)
            self.assertFalse(thread.is_alive())
            provider.assert_called_once_with(0,'frame','English','Czech',settings_path=snapshot.files_dir/'settings.csv')
        self.assertEqual(errors,[])

    def test_production_screens_no_longer_import_main(self):
        root=Path(__file__).resolve().parents[1]
        for folder in ('vocabulary','grammar','conjugation','statistics','preferences','about','services','shared'):
            for path in (root/folder).glob('*.py'):
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                    if isinstance(node,ast.ImportFrom):
                        self.assertFalse(node.module=='app' and any(alias.name=='main' for alias in node.names),str(path))

    def test_api_settings_cache_separates_paths_and_concurrent_readers(self):
        from concurrent.futures import ThreadPoolExecutor
        from app.repositories.api_settings import load_settings
        with TemporaryDirectory() as directory:
            paths=[Path(directory)/f'{index}.csv' for index in range(2)]
            for index,path in enumerate(paths):
                path.write_text(f'Name;Value\nkey;synthetic-{index}\n',encoding='utf-8')
            def read(index):
                for _ in range(50):
                    if load_settings(paths[index])['key']!=f'synthetic-{index}':return False
                return True
            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(list(pool.map(read,(0,1))),[True,True])


class ContextUiTests(TestCase):
    def setUp(self):
        import customtkinter as cst
        self.token=_active.set(AppContext())
        self.root=cst.CTk();self.root.geometry('1400x900');self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy();_active.reset(self.token)
        self.assertEqual(self.errors,[])

    def test_real_home_refresh_and_language_change_keep_context_and_temporary_paths(self):
        from app import main
        with TemporaryDirectory() as directory:
            context=AppContext(root_dir=directory)
            context.files_dir.mkdir()
            path=context.files_dir/'settings.csv'
            frame=sample_preferences();frame.to_csv(path,sep=';',index=False)
            main.main_proc(self.root,context)
            self.root.update()
            self.assertIs(self.root.app_context,context)
            old=self.root.winfo_children()[0]
            frame.loc[frame.Name.eq('App language'),'Value']='Czech'
            frame.to_csv(path,sep=';',index=False)
            context.go_home();self.root.update()
            self.assertEqual(context.preferences.app_language,'Czech')
            self.assertFalse(old.winfo_exists())
            self.assertEqual({p.name for p in context.files_dir.glob('*_voc.csv')},
                {'Czech_Spanish_voc.csv','Czech_English_voc.csv'})
            self.assertIs(get_context(self.root),context)

    def test_two_training_screens_keep_their_context_and_callback_language(self):
        import customtkinter as cst
        from app.grammar.practise import GrammarController
        from app.tests.test_grammar_category_filter import questions
        first=AppContext(on_home=Mock())
        second=AppContext(preferences=replace(first.preferences,app_language='Czech'),on_home=Mock())
        window=cst.CTkToplevel(self.root);window.geometry('1200x800')
        one=GrammarController(self.root,questions(),'first.csv',first.go_home,context=first)
        two=GrammarController(window,questions(),'second.csv',second.go_home,context=second)
        self.root.update()
        self.assertEqual(one.view.header.title_label.cget('text'),first.translate('Grammar Trainer'))
        self.assertEqual(two.view.header.title_label.cget('text'),second.translate('Grammar Trainer'))
        one.reveal();two.reveal();self.root.update()
        self.assertIs(one.context,first);self.assertIs(two.context,second)
        self.assertEqual(one.session.correct,0);self.assertEqual(two.session.correct,0)
        one.back();first.on_home.assert_called_once();second.on_home.assert_not_called()
        two.back();second.on_home.assert_called_once()
        window.destroy()

    def test_switching_grammar_editor_tabs_keeps_context_paths_and_home_callback(self):
        from app.grammar.editor import GrammarEditor
        from app.tests.test_grammar_editor import questions
        from app.ui.components.module_header import ModuleHeader
        with TemporaryDirectory() as directory:
            context=AppContext(root_dir=directory,on_home=Mock())
            context.preferences=replace(context.preferences,learned_by='Czech')
            context.files_dir.mkdir()
            path=context.grammar_path('English')
            questions().to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            editor=GrammarEditor(self.root,'English',path,context.go_home,context=context)
            editor.open_related();self.root.update()
            def headers(parent):
                result=[]
                for child in parent.winfo_children():
                    if isinstance(child,ModuleHeader):result.append(child)
                    else:result.extend(headers(child))
                return result
            header,=headers(self.root)
            self.assertIn(context.translate('Edit grammar theory'),header.title_label.cget('text'))
            self.assertIs(get_context(header),context)
            self.assertTrue(context.theory_path('English').exists())
            self.assertEqual(path.read_bytes(),before)
            header.buttons['close'].invoke()
            context.on_home.assert_called_once_with()


def context_regressions():
    return defaultTestLoader.loadTestsFromNames([
        'app.tests.test_app_context.ContextTests',
        'app.tests.test_app_context.ContextUiTests',
        'app.tests.test_home_data',
        'app.tests.test_autoplay_preferences',
        'app.tests.test_backup_background',
        'app.tests.test_training_controllers',
        'app.tests.test_grammar_deferred_save',
        'app.tests.test_remember_category_filter',
        'app.tests.test_statistics_practice_link',
        'app.tests.test_editor_async_ui',
        'app.tests.test_vocabulary_editor_dropdowns',
        'app.tests.test_synonyms_ui',
        'app.tests.test_module_header.ModuleHeaderTests',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_grammar_editor_theory.TheoryEditorUiTests',
        'app.tests.test_shared_controls.SharedControlsTests.test_about_and_preferences_header_actions_share_training_style_in_all_languages',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
        'app.tests.test_learning_ui.LearningUiTests.test_conjugation_feedback_preserves_scoring_and_separates_header_rows',
        'app.tests.test_module_panels.ModulePanelTests.test_question_and_theory_actions_share_green_panel_and_have_exit',
        'app.tests.test_api_http.AudioTransportTests.test_config_cache_refreshes_after_replacement',
        'app.tests.test_api_http.AudioTransportTests.test_failed_speech_does_not_mark_audio_available',
        'app.tests.test_editor_save',
        'app.tests.test_audit_regressions.AuditRegressionTests.test_new_course_contains_manual_part_of_speech_column',
        'app.tests.test_audit_regressions.AuditRegressionTests.test_enrichment_supports_filtered_index_and_preserves_manual_attributes',
        'app.tests.test_package_assets.PackageAssetTests.test_all_runtime_packages_import_without_old_root_modules',
    ])

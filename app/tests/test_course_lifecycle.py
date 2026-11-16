"""Settings-driven provisioning/retirement, lossless reactivation and grammar gates."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
import customtkinter as cst
from app.core.context import AppContext
from app.preferences.courses import COURSE_FIELD, StudyCourse, encode_courses, decode_courses, CourseConfigurationError
from app.preferences.data import RuntimePreferences, PreferenceError
from app.repositories.preferences import load_preferences, save_preferences
from app.repositories.course_files import course_assets
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course


COURSES = (StudyCourse('es', True, 20, 20), StudyCourse('en', True, 10, 15), StudyCourse('fr', True, 15, 25))


class CourseLifecycleTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.files = Path(self.folder.name); self.settings = self.files/'settings.csv'
        sample_preferences().to_csv(self.settings, sep=';', index=False)

    def save(self, courses=COURSES, **extra):
        return save_preferences(load_preferences(self.settings), {COURSE_FIELD: encode_courses('cs', courses), **extra}, self.settings)

    def assets(self): return course_assets(self.files, 'cs', 'fr')

    def test_all_required_assets_are_ready_and_parse_as_empty_documents_after_save(self):
        self.save()
        from app.grammar.editor_data import GrammarDocument
        from app.grammar.editor_theory_data import GrammarTheoryDocument
        from app.repositories.grammar_records import load_record
        from app.repositories.tags import load_catalog
        from app.repositories import synonyms
        assets = self.assets()
        for key in ('vocabulary','tags','synonyms','grammar','theory','records'):
            self.assertTrue(assets[key][0].exists(), key)
            self.assertTrue(pd.read_csv(assets[key][0], sep=';').empty)
        self.assertTrue(GrammarDocument(assets['grammar'][0]).frame.empty)
        self.assertTrue(GrammarTheoryDocument(assets['theory'][0]).frame.empty)
        self.assertEqual(load_record(assets['grammar'][0]), 0)
        self.assertTrue(load_catalog(assets['tags'][0], 'Czech', 'French')[0].empty)
        self.assertTrue(synonyms.load(assets['vocabulary'][0], pd.read_csv(assets['vocabulary'][0], sep=';'))[0].empty)
        self.assertTrue(assets['audio'].is_dir())
        self.assertFalse(assets['conjugation'][0].exists())

    def test_grammar_can_be_off_on_first_activation(self):
        self.save(tuple(replace(item, grammar_enabled=False) for item in COURSES))
        assets = self.assets()
        for key in ('vocabulary','tags','synonyms'):self.assertTrue(assets[key][0].exists())
        for key in ('grammar','theory','records'):self.assertFalse(assets[key][0].exists())
        self.assertFalse(RuntimePreferences.from_frame(load_preferences(self.settings)).grammar_enabled('fr'))

    def test_disabling_empty_course_removes_only_its_empty_assets_and_empty_audio_directory(self):
        self.save(); assets = self.assets()
        before = {p:p.read_bytes() for p in self.files.glob('*English*.csv')}
        self.save(tuple(replace(item, enabled=False) if item.target == 'fr' else item for item in COURSES))
        for key in ('vocabulary','tags','synonyms','grammar','theory','records'):
            self.assertFalse(assets[key][0].exists(), key)
        self.assertFalse(assets['audio'].exists())
        for path, content in before.items():self.assertEqual(path.read_bytes(), content)
        archived = RuntimePreferences.from_frame(load_preferences(self.settings)).study_courses[-1]
        self.assertEqual(archived, replace(COURSES[-1], enabled=False))

    def test_every_populated_csv_and_audio_file_survives_and_reactivates_with_original_bytes(self):
        self.save(); assets = self.assets()
        for key in ('vocabulary','tags','synonyms','grammar','theory','records'):
            path = assets[key][0]
            frame = pd.read_csv(path, sep=';')
            row = dict.fromkeys(frame.columns, ''); row[frame.columns[0]] = '1'
            pd.DataFrame([row], columns=frame.columns).to_csv(path, sep=';', index=False)
        assets['conjugation'][0].write_text('ID;R\n1;SF\n', encoding='utf-8')
        (assets['audio']/'recording.wav').write_bytes(b'synthetic audio')
        before = {p:p.read_bytes() for p in self.files.rglob('*') if p.is_file() and p != self.settings}
        disabled = tuple(replace(item, enabled=False) if item.target == 'fr' else item for item in COURSES)
        self.save(disabled)
        for path, content in before.items():self.assertEqual(path.read_bytes(), content)
        self.save()
        for path, content in before.items():self.assertEqual(path.read_bytes(), content)

    def test_mixed_course_keeps_data_but_retires_empty_companions(self):
        self.save(); assets = self.assets()
        words = course().rename(columns={'English':'French'}).assign(Repetition='SSFSF')
        words.to_csv(assets['vocabulary'][0], sep=';', index=False)
        original = assets['vocabulary'][0].read_bytes()
        (assets['audio']/'empty-but-user-owned.wav').write_bytes(b'')
        self.save(tuple(replace(item, enabled=False) if item.target == 'fr' else item for item in COURSES))
        self.assertEqual(assets['vocabulary'][0].read_bytes(), original)
        self.assertTrue((assets['audio']/'empty-but-user-owned.wav').exists())
        for key in ('tags','synonyms','grammar','theory','records'):self.assertFalse(assets[key][0].exists())
        self.save()
        self.assertEqual(assets['vocabulary'][0].read_bytes(), original)
        self.assertEqual(pd.read_csv(assets['vocabulary'][0], sep=';').Repetition.tolist(), ['SSFSF'])

    def test_disabling_grammar_preserves_questions_and_vocabulary_and_removes_empty_theory_record(self):
        self.save(); assets = self.assets()
        assets['grammar'][0].write_text('question_id;R\n1;SFSS\n', encoding='utf-8')
        original = assets['grammar'][0].read_bytes()
        disabled = tuple(replace(item, grammar_enabled=False) if item.target == 'fr' else item for item in COURSES)
        self.save(disabled)
        self.assertEqual(assets['grammar'][0].read_bytes(), original)
        for key in ('theory','records'):self.assertFalse(assets[key][0].exists())
        for key in ('vocabulary','tags','synonyms'):self.assertTrue(assets[key][0].exists())
        self.assertTrue(assets['audio'].is_dir())
        from app.main import Load_setting
        Load_setting(AppContext(files_dir=self.files))
        self.assertFalse(assets['theory'][0].exists())
        self.save()
        self.assertEqual(assets['grammar'][0].read_bytes(), original)
        self.assertTrue(assets['theory'][0].exists())

    def test_legacy_v1_defaults_grammar_on_and_v2_validates_boolean_identity_and_duplicates(self):
        legacy = json.dumps(dict(version=1, source='cs', courses=[dict(target='fr', enabled=True, context=10, audio=20)]))
        self.assertTrue(decode_courses(legacy, 'cs')[0].grammar_enabled)
        for courses in ((StudyCourse('fr'),StudyCourse('fr')), (StudyCourse('cs'),),
                        (StudyCourse('fr', grammar_enabled='yes'),)):
            with self.assertRaises(CourseConfigurationError):encode_courses('cs', courses)
        self.save()
        self.assertEqual(json.loads(load_preferences(self.settings).set_index('Name').at[COURSE_FIELD,'Value'])['version'],2)

    def test_invalid_save_and_failed_commit_leave_settings_and_existing_data_intact(self):
        initial = self.settings.read_bytes()
        with self.assertRaises(PreferenceError):self.save(**{'Learn batch':'-1'})
        self.assertEqual(set(self.files.iterdir()), {self.settings})
        with patch('app.repositories.preferences.commit_document', side_effect=PermissionError('synthetic lock')):
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(self.settings.read_bytes(), initial)
        self.assertEqual(set(self.files.iterdir()), {self.settings})

    def test_partial_preparation_failure_rolls_back_only_new_empty_creations(self):
        from app.repositories import course_files
        actual = course_files.save_csv; count = 0
        def fail(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 2:raise PermissionError('synthetic failure')
            return actual(*args, **kwargs)
        with patch.object(course_files, 'save_csv', side_effect=fail):
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(set(self.files.iterdir()), {self.settings})

    def test_rollback_keeps_a_concurrently_populated_new_file(self):
        path = self.assets()['vocabulary'][0]
        def fail(*args, **kwargs):
            course().rename(columns={'English':'French'}).to_csv(path, sep=';', index=False)
            raise PermissionError('synthetic failure')
        with patch('app.repositories.preferences.commit_document', side_effect=fail):
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(pd.read_csv(path, sep=';').Repetition.tolist(), ['SF'])

    def test_cleanup_failures_are_reported_after_successful_settings_commit(self):
        self.save()
        from app.repositories import course_files
        original = course_files._remove_empty_csv
        def locked(path, *args, **kwargs):
            if path == self.assets()['vocabulary'][0]:raise PermissionError('synthetic lock')
            return original(path, *args, **kwargs)
        with patch.object(course_files, '_remove_empty_csv', side_effect=locked):
            saved = self.save(tuple(replace(item,enabled=False) if item.target=='fr' else item for item in COURSES))
        self.assertIn('Czech_French_voc.csv', saved.attrs['course_cleanup_warnings'])
        self.assertNotIn('French', RuntimePreferences.from_frame(load_preferences(self.settings)).learning_languages)

    def test_empty_file_populated_during_cleanup_is_not_removed(self):
        self.save(); path = self.assets()['tags'][0]
        from app.repositories import course_files
        actual = course_files._empty_csv; reads = 0
        def changed(candidate, required):
            nonlocal reads
            if candidate == path:
                reads += 1
                if reads == 2:
                    pd.DataFrame([dict(ID=1,Czech='Nové',French='Nouveau',Note='keep')]).to_csv(path,sep=';',index=False)
            return actual(candidate, required)
        with patch.object(course_files,'_empty_csv',side_effect=changed):
            self.save(tuple(replace(item,enabled=False) if item.target=='fr' else item for item in COURSES))
        self.assertEqual(pd.read_csv(path,sep=';').Note.tolist(),['keep'])

    def test_rollback_keeps_a_concurrently_changed_empty_schema(self):
        path = self.assets()['vocabulary'][0]
        def fail(*args, **kwargs):
            data=pd.read_csv(path,sep=';');data['User extra']=''
            data.to_csv(path,sep=';',index=False)
            raise PermissionError('synthetic failure')
        with patch('app.repositories.preferences.commit_document',side_effect=fail):
            with self.assertRaises(PermissionError):self.save()
        self.assertIn('User extra',pd.read_csv(path,sep=';').columns)

    def test_source_change_preserves_shared_grammar_and_all_populated_old_pair_data(self):
        self.save()
        old=self.assets()['vocabulary'][0]
        course().rename(columns={'English':'French'}).to_csv(old,sep=';',index=False)
        original=old.read_bytes();grammar=self.assets()['grammar'][0];before=grammar.read_bytes()
        save_preferences(load_preferences(self.settings), {'Learned by':'English',
            COURSE_FIELD:encode_courses('en',(StudyCourse('fr'),))},self.settings)
        self.assertEqual(old.read_bytes(),original)
        self.assertEqual(grammar.read_bytes(),before)
        self.assertTrue((self.files/'English_French_voc.csv').exists())

    def test_disabled_grammar_never_reads_a_retained_malformed_file(self):
        self.save(tuple(replace(item,grammar_enabled=False) for item in COURSES))
        path = self.assets()['grammar'][0]; path.write_text('malformed retained data',encoding='utf-8')
        from app.home.data import course_overview
        from app.statistics.data import prepare_statistics
        from app.shared import config
        self.assertEqual(course_overview(self.files,'Czech','French',10,10,grammar_enabled=False)['gra_count'],0)
        result = prepare_statistics(self.files,'Czech','French',config.stat_horizon,config.days_gap_map,
                                    config.default_wait,config.PoS_types,config.PoS_ideal,grammar_enabled=False)
        self.assertIsNone(result[2])
        self.assertEqual(path.read_text(encoding='utf-8'),'malformed retained data')


class CourseLifecycleUiTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory(); self.files = Path(self.folder.name)
        self.settings = self.files/'settings.csv'; sample_preferences().to_csv(self.settings, sep=';', index=False)
        saved = save_preferences(load_preferences(self.settings), {COURSE_FIELD:encode_courses('cs',COURSES)}, self.settings)
        self.root = cst.CTk(); self.root.geometry('1400x900')
        self.context = AppContext(files_dir=self.files, preferences=RuntimePreferences.from_frame(saved));self.context.bind(self.root)
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for child in tuple(self.root.winfo_children()):child.destroy()
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy();self.folder.cleanup();self.assertEqual(self.errors,[])

    def test_disable_is_deferred_until_save_then_row_disappears_and_readding_restores_choices(self):
        from app.preferences.dialog import PreferencesDialog
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        row=dialog.course_editor.rows[2];row['toggle'].toggle()
        self.assertEqual(len(dialog.course_editor.rows),3)
        self.assertTrue((self.files/'Czech_French_voc.csv').exists())
        dialog.save();self.assertTrue(dialog.saved)
        self.assertFalse((self.files/'Czech_French_voc.csv').exists())
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        self.assertEqual(len(dialog.course_editor.rows),2)
        dialog.course_editor.add_course()
        row=dialog.course_editor.rows[-1]
        row['chooser']._dropdown_callback('French')
        self.assertEqual((row['context'].get(),row['audio'].get()),('15','25'))
        dialog.save();self.assertTrue((self.files/'Czech_French_voc.csv').exists())

    def test_choices_exclude_own_and_other_selected_languages_and_duplicate_injection_cannot_save(self):
        from app.preferences.dialog import PreferencesDialog
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        row=dialog.course_editor.rows[0]
        self.assertNotIn('Czech',row['chooser'].cget('values'))
        self.assertNotIn('English',row['chooser'].cget('values'))
        before=self.settings.read_bytes()
        row['target'].set('English');dialog.save()
        self.assertFalse(dialog.saved);self.assertEqual(self.settings.read_bytes(),before)
        row['target'].set('Czech');dialog.save()
        self.assertFalse(dialog.saved);self.assertEqual(self.settings.read_bytes(),before)

    def test_grammar_flag_hides_home_statistics_and_public_training_editor_entrypoints(self):
        from app.main import _build_main_window
        from app.statistics.tabs import StatisticsTabs
        from app.grammar.practise import Grammar_training
        from app.grammar.editor import Edit_grammar
        from app.grammar.editor_theory import Edit_grammar_theory
        courses=tuple(replace(item,grammar_enabled=False) for item in COURSES)
        self.context.preferences=replace(self.context.preferences,courses=courses)
        rows=pd.DataFrame({'ID':[1]})
        item=dict(rep_words=rows,lrn_words=rows,rep_count=1,lrn_count=1,all_count=1,gra_count=999,con_count=0)
        body=_build_main_window(self.root,dict.fromkeys(self.context.preferences.learning_languages,item),self.context)
        def labels(parent):
            for child in parent.winfo_children():
                if isinstance(child,cst.CTkLabel):yield child.cget('text')
                yield from labels(child)
        self.assertNotIn(self.context.translate('Grammar'),list(labels(body)))
        tabs=StatisticsTabs(self.root,self.context.translate)
        tabs.select('Grammar');tabs.set_grammar_available(False)
        self.assertEqual(tabs.selected,'Vocabulary')
        self.assertNotIn(self.context.translate('Grammar'),tabs.navigation.cget('values'))
        for entry in (Grammar_training,Edit_grammar,Edit_grammar_theory):
            self.assertIsNone(entry(self.root,'French',context=self.context))

    def test_disabled_populated_course_disappears_from_settings_and_about_omits_disabled_grammar(self):
        from app.preferences.dialog import PreferencesDialog
        from app.about.shortcuts import shortcut_sections
        words=self.files/'Czech_French_voc.csv'
        course().rename(columns={'English':'French'}).to_csv(words,sep=';',index=False)
        before=words.read_bytes()
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        dialog.course_editor.rows[-1]['toggle'].toggle();dialog.save()
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        self.assertEqual(len(dialog.course_editor.rows),2)
        self.assertEqual(words.read_bytes(),before)
        dialog.destroy()
        saved=save_preferences(load_preferences(self.settings),{COURSE_FIELD:encode_courses('cs',
            tuple(replace(item,grammar_enabled=False) for item in COURSES))},self.settings)
        self.context.preferences=RuntimePreferences.from_frame(saved)
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        self.assertNotIn('Remember grammar categories',dialog.fields)
        self.assertFalse(any(title in ('Grammar','Grammar editors') for title,_ in shortcut_sections(grammar_enabled=False)))

    def test_real_statistics_switch_hides_grammar_tab_and_summary_and_skips_corrupt_disabled_data(self):
        from app.statistics.viewer import Stats
        from time import monotonic, sleep
        courses=tuple(replace(item,grammar_enabled=False) if item.target=='fr' else item for item in COURSES)
        saved=save_preferences(load_preferences(self.settings),{COURSE_FIELD:encode_courses('cs',courses)},self.settings)
        self.context.preferences=RuntimePreferences.from_frame(saved)
        (self.files/'French_gra.csv').write_text('retained malformed data',encoding='utf-8')
        def settle(window):
            deadline=monotonic()+25
            while not window.ready and monotonic()<deadline:self.root.update();sleep(.005)
            self.assertTrue(window.ready)
        with patch('app.statistics.viewer.Generate_chart'):
            window=Stats(self.root,context=self.context,language='French',section='Grammar')
            try:
                settle(window)
                self.assertEqual(window.statistics_tabs.selected,'Vocabulary')
                self.assertNotIn('Grammar',window.statistics_tabs.navigation.cget('values'))
                self.assertFalse(window.summary_cards[2].master.grid_info())
                window.controller.language_switch._command('English');settle(window)
                self.assertIn('Grammar',window.statistics_tabs.navigation.cget('values'))
                self.assertTrue(window.summary_cards[2].master.grid_info())
                window.statistics_tabs.select('Grammar')
                self.assertEqual(window.statistics_tabs.selected,'Grammar')
            finally:window.destroy()

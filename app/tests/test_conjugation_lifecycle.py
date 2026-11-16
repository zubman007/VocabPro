"""Per-course activation, legacy settings, provisioning rollback and backup."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.core.context import AppContext
from app.preferences.courses import StudyCourse, COURSE_FIELD, encode_courses, decode_courses, CourseConfigurationError
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import load_preferences, save_preferences
from app.repositories.conjugation_persons import configuration_path, load_configuration, save_configuration
from app.repositories.course_files import ensure_course_files
from app.conjugation.persons import default_configuration
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.tests.test_conjugation_model import verbs


class ConjugationLifecycleTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.files=Path(self.folder.name);self.settings=self.files/'settings.csv'
        sample_preferences().to_csv(self.settings,sep=';',index=False)
        self.courses=(StudyCourse('es',conjugation_enabled=True),StudyCourse('en',conjugation_enabled=False))
        self.path=self.files/'Czech_Spanish_con.csv'

    def save(self,courses=None):
        saved=save_preferences(load_preferences(self.settings),
            {COURSE_FIELD:encode_courses('cs',courses or self.courses)},self.settings)
        return AppContext(files_dir=self.files,preferences=RuntimePreferences.from_frame(saved))

    def test_legacy_settings_preserve_old_visibility_without_parsing_or_rewriting_csv(self):
        self.path.write_text('opaque old data',encoding='utf-8');before=self.path.read_bytes()
        context=AppContext(files_dir=self.files,preferences=RuntimePreferences.from_frame(load_preferences(self.settings)))
        self.assertTrue(context.conjugation_enabled('es'));self.assertFalse(context.conjugation_enabled('en'))
        self.assertEqual(self.path.read_bytes(),before);self.assertFalse(configuration_path(self.files,'es').exists())
        for version in (1,2):
            item=dict(target='es',enabled=True,context=0,audio=0)
            if version==2:item['grammar']=True
            decoded=decode_courses(json.dumps(dict(version=version,source='cs',courses=[item])),'cs')
            self.assertIsNone(decoded[0].conjugation_enabled)
        for value in ('yes',1,None):
            with self.assertRaises(CourseConfigurationError):
                decode_courses(json.dumps(dict(version=3,source='cs',courses=[dict(item,conjugation=value)])),'cs')

    def test_activation_creates_valid_empty_csv_and_configuration_only_for_enabled_module(self):
        context=self.save()
        self.assertTrue(context.conjugation_enabled('es'));self.assertFalse(context.conjugation_enabled('en'))
        frame=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertTrue(frame.empty);self.assertIn('Person history',frame)
        config,_=load_configuration(self.files,'es',self.path);self.assertEqual(config,default_configuration('es'))
        self.assertTrue(configuration_path(self.files,'es').exists())
        self.assertFalse((self.files/'Czech_English_con.csv').exists());self.assertFalse(configuration_path(self.files,'en').exists())
        before={p:p.read_bytes() for p in self.files.glob('*') if p.is_file()}
        ensure_course_files(self.files,'cs',context.preferences.study_courses)
        for path,data in before.items():self.assertEqual(path.read_bytes(),data)

    def test_empty_and_populated_conjugation_survive_module_off_and_reactivate_unchanged(self):
        self.save()
        disabled=tuple(replace(c,conjugation_enabled=False) for c in self.courses)
        for populated in (False,True):
            if populated:verbs().to_csv(self.path,sep=';',index=False)
            before=self.path.read_bytes();person_path=configuration_path(self.files,'es');persons=person_path.read_bytes()
            context=self.save(disabled);self.assertFalse(context.conjugation_enabled('es'))
            self.assertEqual(self.path.read_bytes(),before);self.assertEqual(person_path.read_bytes(),persons)
            self.save();self.assertEqual(self.path.read_bytes(),before);self.assertEqual(person_path.read_bytes(),persons)

    def test_disabling_entire_empty_course_keeps_person_configuration_and_its_selection(self):
        self.save();config,revision=load_configuration(self.files,'es',self.path)
        save_configuration(self.files,replace(config,practice_person_ids=('s1',)),revision)
        person_path=configuration_path(self.files,'es');before=person_path.read_bytes()
        self.save(tuple(replace(c,enabled=False) if c.target=='es' else c for c in self.courses))
        self.assertFalse(self.path.exists());self.assertEqual(person_path.read_bytes(),before)
        self.save();self.assertEqual(person_path.read_bytes(),before)
        self.assertEqual(load_configuration(self.files,'es',self.path)[0].practice_person_ids,('s1',))

    def test_failed_settings_commit_removes_own_empty_creations_and_keeps_existing_data(self):
        initial=self.settings.read_bytes()
        with patch('app.repositories.preferences.commit_document',side_effect=PermissionError):
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(set(self.files.iterdir()),{self.settings});self.assertEqual(self.settings.read_bytes(),initial)
        verbs().to_csv(self.path,sep=';',index=False);before=self.path.read_bytes()
        with patch('app.repositories.preferences.commit_document',side_effect=PermissionError):
            with self.assertRaises(PermissionError):self.save()
        self.assertEqual(self.path.read_bytes(),before);self.assertFalse(configuration_path(self.files,'es').exists())

    def test_rollback_never_deletes_concurrently_edited_person_configuration(self):
        person_path=configuration_path(self.files,'es');changed=replace(default_configuration('es'),practice_person_ids=('s1',))
        def fail(*args,**kwargs):
            config,revision=load_configuration(self.files,'es',self.path)
            save_configuration(self.files,changed,revision)
            raise PermissionError('synthetic locked settings')
        with patch('app.repositories.preferences.commit_document',side_effect=fail):
            with self.assertRaises(PermissionError):self.save()
        self.assertTrue(person_path.exists());self.assertEqual(load_configuration(self.files,'es')[0],changed)

    def test_existing_six_person_english_file_is_kept_and_no_new_default_is_silently_substituted(self):
        english=self.files/'Czech_English_con.csv';verbs('English').to_csv(english,sep=';',index=False)
        before=english.read_bytes()
        self.save(tuple(replace(c,conjugation_enabled=True) for c in self.courses))
        self.assertEqual(english.read_bytes(),before)
        self.assertEqual(len(load_configuration(self.files,'en',english)[0].persons),6)

    def test_disabled_module_never_parses_retained_malformed_csv_or_person_config(self):
        from app.home.data import course_overview
        from app.statistics.data import prepare_statistics
        from app.shared import config
        self.save(tuple(replace(c,conjugation_enabled=False) for c in self.courses))
        course().rename(columns={'English':'Spanish'}).drop(columns='Phonetic').to_csv(
            self.files/'Czech_Spanish_voc.csv',sep=';',index=False)
        self.path.write_text('malformed retained CSV',encoding='utf-8')
        configuration_path(self.files,'es').write_text('{broken',encoding='utf-8')
        with patch('app.repositories.conjugation_persons.load_configuration',side_effect=AssertionError('disabled read')):
            overview=course_overview(self.files,'Czech','Spanish',10,10,conjugation_enabled=False)
            result=prepare_statistics(self.files,'Czech','Spanish',config.stat_horizon,config.days_gap_map,
                config.default_wait,config.PoS_types,config.PoS_ideal,conjugation_enabled=False)
        self.assertEqual((overview['con_count'],overview['con_practice_count']),(0,0));self.assertIsNone(result[1])

    def test_home_repeat_uses_selected_populated_forms_and_empty_selection_is_disabled(self):
        from app.home.data import course_overview
        self.save();verbs().to_csv(self.path,sep=';',index=False)
        for selection,count in ((('s1',),1),(('m3',),0),((),0)):
            config,revision=load_configuration(self.files,'es',self.path)
            save_configuration(self.files,replace(config,practice_person_ids=selection),revision)
            overview=course_overview(self.files,'Czech','Spanish',10,10)
            self.assertEqual(overview['con_count'],1);self.assertEqual(overview['con_practice_count'],count)

    def test_backup_includes_only_recognized_valid_person_json_and_original_bytes(self):
        from app.repositories.courses import backup_files
        config=replace(default_configuration('es'),practice_person_ids=())
        save_configuration(self.files,config,None)
        path=configuration_path(self.files,'es')
        (self.files/'private.json').write_text('{"secret":"synthetic"}',encoding='utf-8')
        (self.files/'Unknown_con_persons.json').write_text('{}',encoding='utf-8')
        self.assertEqual(dict(backup_files(self.files)),{path.name:path.read_bytes()})
        path.write_text('{}',encoding='utf-8')
        with self.assertRaises(ValueError):list(backup_files(self.files))

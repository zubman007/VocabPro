"""Language persons, lossless legacy adaptation and atomic lesson persistence."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.conjugation.persons import Person, default_configuration, decode_configuration, LEGACY_IDS
from app.conjugation.history import HISTORY_COLUMN, decode_history
from app.conjugation.data import build_verbs, eligible_verbs, select_verbs
from app.conjugation.session import ConjugationSession
from app.repositories.conjugation import ConjugationDocument, conjugation_columns, load_source, save_results
from app.repositories.conjugation_persons import configuration_path, load_configuration, save_configuration
from app.shared.storage import FileChangedError
from app.statistics.conjugation import person_statistics


def verbs(language='Spanish'):
    return pd.DataFrame([dict(ID='001', **{language:'enseñar', 'Czech':'učit',
        'Description':'free text', **dict.fromkeys(LEGACY_IDS,''),
        's1':'enseño','s2':'enseñas','R':'S?FSS','LR':'2026-11-01 10:00:00',
        'Custom':'007; NA\nuser text'})])


class ConjugationModelTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.files=Path(self.folder.name);self.path=self.files/'Czech_Spanish_con.csv'
        verbs().to_csv(self.path,sep=';',index=False)
        self.config=default_configuration('es')

    def lesson(self,config=None):
        config=config or self.config
        source=load_source(self.path,'Spanish','Czech',config)
        source.attrs['person_ids']=tuple(key for key,_ in config.practice)
        selection=select_verbs(eligible_verbs(source,config.practice),100)
        state=ConjugationSession(selection,build_verbs(selection,'Spanish','Czech',config.practice),config.practice)
        return source,state

    def test_defaults_are_language_specific_and_legacy_english_keeps_six_identities(self):
        for code in ('es','cs','sk','de','fr'):
            self.assertEqual(tuple(p.id for p in default_configuration(code).persons),LEGACY_IDS)
        self.assertEqual(len(default_configuration('en').persons),5)
        english=self.files/'Czech_English_con.csv';verbs('English').to_csv(english,sep=';',index=False)
        before=english.read_bytes()
        config,revision=load_configuration(self.files,'English',english)
        self.assertIsNone(revision);self.assertEqual(len(config.persons),6)
        self.assertEqual([p.label for p in config.persons if p.id in ('s2','m2')],['you (singular)','you (plural)'])
        self.assertEqual(english.read_bytes(),before)
        self.assertFalse(configuration_path(self.files,'en').exists())

    def test_invalid_configuration_versions_ids_references_and_duplicate_json_are_rejected(self):
        valid=json.loads(self.config.to_json())
        variants=[]
        for key,value in (('version',2),('version',True),('language','en'),('practice_person_ids',['unknown'])):
            variants.append({**valid,key:value})
        variants.extend(({**valid,'persons':[valid['persons'][0]]*2},
            {**valid,'persons':[{**p,'id':'R'} for p in valid['persons']]},
            {**valid,'persons':[{**p,'label':' '} for p in valid['persons']]},
            {**valid,'persons':[{**p,'enabled':0} for p in valid['persons']]},
            {**valid,'practice_person_ids':['s1','s1']},
            {**valid,'persons':[{**p,'enabled':False} for p in valid['persons']]}))
        for value in variants:
            with self.subTest(value=value),self.assertRaises(ValueError):decode_configuration(json.dumps(value),'es')
        with self.assertRaises(ValueError):decode_configuration(self.config.to_json().replace('"version": 1','"version": 1, "version": 1'),'es')
        self.assertEqual(replace(self.config,practice_person_ids=()).validate().practice,())

    def test_person_rename_order_deactivation_and_reactivation_preserve_forms_history_and_unknown_columns(self):
        extra=Person.create('vos')
        config=replace(self.config,persons=(*self.config.persons,extra),practice_person_ids=('s1',extra.id))
        save_configuration(self.files,config,None)
        document=ConjugationDocument(self.path,'Spanish','Czech',config)
        original=document.verb('001');document.update('001',{**original,extra.id:'enseñás'});document.save()
        backup=self.path.with_name(self.path.name+'.pre-persons.bak').read_bytes()
        config=replace(config,persons=(replace(extra,label='vos (regional)',enabled=False),*reversed(self.config.persons)),
                       practice_person_ids=('s1',))
        revision=load_configuration(self.files,'es',self.path)[1];save_configuration(self.files,config,revision)
        document=ConjugationDocument(self.path,'Spanish','Czech',config)
        self.assertNotIn(extra.id,document.fields)
        document.update('001',{**document.verb('001'),'Description':'edited'});document.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        for key in ('ID','R','LR','Custom','s1','s2'):self.assertEqual(saved.at[0,key],original[key])
        self.assertEqual(saved.at[0,extra.id],'enseñás')
        active=replace(config,persons=tuple(replace(p,enabled=True) for p in config.persons),practice_person_ids=(extra.id,))
        source,state=self.lesson(active);self.assertEqual(state.persons,((extra.id,'vos (regional)'),))
        self.assertEqual(state.advance().forms[extra.id],'enseñás')
        self.assertEqual(self.path.with_name(self.path.name+'.pre-persons.bak').read_bytes(),backup)

    def test_more_than_six_forms_and_incomplete_verbs_are_filtered_before_batch_selection(self):
        persons=tuple(Person.create(f'person {i}') for i in range(14))
        config=replace(self.config,persons=persons,practice_person_ids=(persons[-1].id,))
        frame=pd.concat([verbs(),verbs().assign(ID='002',R='')],ignore_index=True)
        frame[persons[-1].id]=['','available']
        frame.to_csv(self.path,sep=';',index=False)
        source,state=self.lesson(config)
        self.assertEqual(state.selection.ID.tolist(),['002'])
        current=state.advance();self.assertEqual(current.forms,{persons[-1].id:'available'})
        self.assertTrue(state.confirm({persons[-1].id:'AVAILABLE'}))
        self.assertEqual(decode_history(state.selection.iloc[0][HISTORY_COLUMN]),{persons[-1].id:'S'})
        self.assertEqual(len(source),2)

    def test_empty_person_selection_and_blank_forms_cannot_create_a_success(self):
        for config in (replace(self.config,practice_person_ids=()),replace(self.config,practice_person_ids=('m3',))):
            source,state=self.lesson(config)
            self.assertTrue(state.selection.empty);self.assertIsNone(state.advance())
            self.assertIsNone(state.confirm({}));self.assertNotIn(HISTORY_COLUMN,state.selection)
        self.assertEqual(source.R.tolist(),['S?FSS'])

    def test_per_person_first_attempt_is_independent_of_whole_round_failure_and_reveal(self):
        source,state=self.lesson();state.advance()
        self.assertFalse(state.confirm({'s1':' ENSENO ','s2':'wrong'}))
        self.assertEqual(state.selection.R.tolist(),['S?FSSF'])
        self.assertEqual(decode_history(state.selection.iloc[0][HISTORY_COLUMN]),{'s1':'S','s2':'F'})
        self.assertFalse(state.confirm({'s1':'wrong','s2':'wrong'}))
        self.assertTrue(state.confirm({'s1':'enseño','s2':'enseñas'}))
        self.assertIsNone(state.confirm({'s1':'enseño','s2':'enseñas'}))
        self.assertEqual(state.selection.R.tolist(),['S?FSSF'])
        self.assertEqual(decode_history(state.selection.iloc[0][HISTORY_COLUMN]),{'s1':'S','s2':'F'})
        self.assertNotIn(HISTORY_COLUMN,source)

    def test_skip_records_neither_round_nor_person_result(self):
        before=self.path.read_bytes()
        source,state=self.lesson();state.advance();self.assertIsNone(state.advance(skip=True))
        self.assertNotIn(HISTORY_COLUMN,state.selection)
        self.assertEqual(state.selection.R.tolist(),source.R.tolist())
        with patch('app.repositories.conjugation.save_csv') as write:
            save_results(source,state.selection,self.path);write.assert_not_called()
        self.assertEqual(self.path.read_bytes(),before)

    def test_wrong_person_is_saved_reloaded_and_counted_separately_without_scoring_revealed_answers(self):
        source,state=self.lesson();state.advance()
        self.assertFalse(state.confirm({'s1':'enseño','s2':'wrong'}))
        updated=save_results(source,state.selection,self.path)
        reloaded=load_source(self.path,'Spanish','Czech',self.config)
        self.assertEqual(decode_history(reloaded.iloc[0][HISTORY_COLUMN]),{'s1':'S','s2':'F'})
        statistics=person_statistics(reloaded,self.config)
        self.assertEqual((statistics[0].successes,statistics[0].failures),(1,0))
        self.assertEqual((statistics[1].successes,statistics[1].failures),(0,1))
        before=self.path.read_bytes()
        self.assertTrue(state.confirm({'s1':'enseño','s2':'enseñas'}))
        save_results(updated,state.selection,self.path)
        self.assertEqual(self.path.read_bytes(),before)

    def test_uppercase_spanish_n_and_czech_keyboard_variant_use_same_normalization(self):
        for answer in ('ENSEÑO','ENSEŇO',' ENSENO '):
            _,state=self.lesson();state.advance()
            self.assertTrue(state.confirm({'s1':answer,'s2':'ENSEÑAS'}))

    def test_first_save_backs_up_exact_legacy_bytes_and_retry_does_not_duplicate_results(self):
        before=self.path.read_bytes();source,state=self.lesson();state.advance()
        state.confirm({'s1':'enseño','s2':'enseñas'})
        updated=save_results(source,state.selection,self.path)
        self.assertEqual(self.path.with_name(self.path.name+'.pre-persons.bak').read_bytes(),before)
        with patch('app.repositories.conjugation.save_csv') as write:
            save_results(updated,state.selection,self.path);write.assert_not_called()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.R.tolist(),['S?FSSS'])
        self.assertEqual(saved.ID.tolist(),['001'])
        self.assertEqual(decode_history(saved.iloc[0][HISTORY_COLUMN]),{'s1':'S','s2':'S'})

    def test_failed_result_save_is_retryable_and_original_bytes_survive(self):
        before=self.path.read_bytes();source,state=self.lesson();state.advance();state.confirm({'s1':'no','s2':'no'})
        with patch('app.repositories.conjugation.save_csv',side_effect=PermissionError):
            with self.assertRaises(PermissionError):save_results(source,state.selection,self.path)
        self.assertEqual(self.path.read_bytes(),before)
        save_results(source,state.selection,self.path)
        self.assertEqual(pd.read_csv(self.path,sep=';').R.tolist(),['S?FSSF'])
        self.assertEqual(self.path.with_name(self.path.name+'.pre-persons.bak').read_bytes(),before)

    def test_concurrent_results_and_changed_scored_forms_reject_entire_save(self):
        source,state=self.lesson();state.advance();state.confirm({'s1':'enseño','s2':'enseñas'})
        for key,value in (('R','external'),('s1','changed form')):
            frame=verbs();frame[key]=value;frame.to_csv(self.path,sep=';',index=False)
            before=self.path.read_bytes()
            with self.subTest(key=key),self.assertRaises(FileChangedError):save_results(source,state.selection,self.path)
            self.assertEqual(self.path.read_bytes(),before)

    def test_unrelated_external_fields_merge_without_losing_unknown_values(self):
        source,state=self.lesson();state.advance();state.confirm({'s1':'enseño','s2':'enseñas'})
        frame=verbs();frame['Custom']='external';frame.to_csv(self.path,sep=';',index=False)
        save_results(source,state.selection,self.path)
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.Custom.tolist(),['external']);self.assertEqual(saved.R.tolist(),['S?FSSS'])

    def test_document_crud_never_renumbers_ids_and_preserves_existing_results(self):
        document=ConjugationDocument(self.path,'Spanish','Czech',self.config)
        first=document.add();document.update(first,dict(Spanish='ir',s1='voy'))
        document.delete('001');second=document.add();document.update(second,dict(Spanish='ser',s1='soy'))
        document.save()
        self.assertNotEqual(first,second);self.assertEqual(document.frame.ID.tolist(),[first,second])
        self.assertEqual(document.frame.R.tolist(),['',''])
        unchanged=ConjugationDocument(self.path,'Spanish','Czech',self.config)
        before=self.path.read_bytes();unchanged.save();self.assertEqual(self.path.read_bytes(),before)

    def test_editing_description_preserves_untouched_legacy_form_whitespace(self):
        frame=verbs();frame['s1']='  enseño  ';frame.to_csv(self.path,sep=';',index=False)
        document=ConjugationDocument(self.path,'Spanish','Czech',self.config)
        document.update('001',{'Description':'new description'});document.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.at[0,'s1'],'  enseño  ');self.assertEqual(saved.at[0,'s2'],'enseñas')

    def test_editor_conflict_and_failed_atomic_replace_preserve_data_and_leave_no_temporary_file(self):
        document=ConjugationDocument(self.path,'Spanish','Czech',self.config)
        document.update('001',{**document.verb('001'),'Description':'draft'})
        before=self.path.read_bytes()
        with patch('app.shared.storage.os.replace',side_effect=PermissionError):
            with self.assertRaises(PermissionError):document.save()
        self.assertEqual(self.path.read_bytes(),before);self.assertEqual(list(self.files.glob('*.tmp')),[])
        self.path.write_bytes(before+b'\n')
        with self.assertRaises(FileChangedError):document.save()
        self.assertEqual(self.path.read_bytes(),before+b'\n')

    def test_custom_columns_from_another_backup_are_recovered_as_inactive_definitions(self):
        extra=Person.create('vos');frame=verbs();frame[extra.id]='enseñás';frame.to_csv(self.path,sep=';',index=False)
        save_configuration(self.files,self.config,None)
        before=self.path.read_bytes();config,revision=load_configuration(self.files,'es',self.path)
        self.assertEqual(config.persons[-1],replace(extra,label=extra.id,enabled=False))
        self.assertNotIn(extra.id,config.practice_person_ids);self.assertEqual(self.path.read_bytes(),before)
        self.assertIsNotNone(revision)

    def test_person_configuration_saves_are_revision_checked_and_atomic(self):
        revision=save_configuration(self.files,self.config,None);path=configuration_path(self.files,'es')
        original=path.read_bytes();changed=replace(self.config,practice_person_ids=('s1',))
        with patch('app.shared.storage.os.replace',side_effect=PermissionError):
            with self.assertRaises(PermissionError):save_configuration(self.files,changed,revision)
        self.assertEqual(path.read_bytes(),original);self.assertEqual(list(self.files.glob('*.tmp')),[])
        save_configuration(self.files,changed,revision)
        with self.assertRaises(FileChangedError):save_configuration(self.files,self.config,revision)
        with self.assertRaises(FileChangedError):save_configuration(self.files,self.config,None)

    def test_explicit_editor_save_adds_new_blank_person_columns_even_without_other_edits(self):
        frame=verbs();frame[HISTORY_COLUMN]='';frame.to_csv(self.path,sep=';',index=False)
        before=self.path.read_bytes();extra=Person.create('vos')
        config=replace(self.config,persons=(*self.config.persons,extra))
        document=ConjugationDocument(self.path,'Spanish','Czech',config)
        self.assertEqual(self.path.read_bytes(),before)
        document.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved[extra.id].tolist(),[''])
        self.assertEqual(self.path.with_name(self.path.name+'.pre-persons.bak').read_bytes(),before)

    def test_invalid_person_history_is_not_silently_reset(self):
        for value in ('{}','{"version":1,"results":{"s1":"S?"}}',
                      '{"version":1,"results":{"R":"S"}}','{"version":1,"results":{"s1":"S","s1":"F"}}'):
            frame=verbs();frame[HISTORY_COLUMN]=value;frame.to_csv(self.path,sep=';',index=False)
            before=self.path.read_bytes()
            with self.subTest(value=value),self.assertRaises(ValueError):load_source(self.path,'Spanish','Czech',self.config)
            self.assertEqual(self.path.read_bytes(),before)

    def test_person_statistics_use_only_individual_observations_and_include_inactive_people(self):
        self.assertTrue(all(p.successes+p.failures==0 for p in person_statistics(verbs(),self.config)))
        frame=verbs();frame[HISTORY_COLUMN]=json.dumps(dict(version=1,results={'s1':'SSF','s2':'F'}))
        config=replace(self.config,persons=tuple(replace(p,enabled=False) if p.id=='s1' else p for p in self.config.persons),
                       practice_person_ids=('s2',))
        stats=person_statistics(frame,config)
        self.assertEqual((stats[0].successes,stats[0].failures,stats[0].enabled),(2,1,False))
        self.assertEqual((stats[1].successes,stats[1].failures),(0,1))

    def test_statistics_cache_tracks_configuration_and_separates_languages(self):
        from app.statistics.data import training_statistics
        from app.statistics.conjugation import person_statistics as calculate
        save_configuration(self.files,self.config,None)
        with patch('app.statistics.conjugation.person_statistics',wraps=calculate) as compute:
            first=training_statistics(self.path,'conjugation','Spanish')
            training_statistics(self.path,'conjugation','Spanish');self.assertEqual(compute.call_count,1)
            config,revision=load_configuration(self.files,'es',self.path)
            save_configuration(self.files,replace(config,persons=(replace(config.persons[0],label='já / yo'),*config.persons[1:])),revision)
            second=training_statistics(self.path,'conjugation','Spanish')
            self.assertEqual(compute.call_count,2);self.assertEqual(second['persons'][0].label,'já / yo')
            english=self.files/'Czech_English_con.csv'
            pd.DataFrame(columns=conjugation_columns('English','Czech',default_configuration('en'))).to_csv(english,sep=';',index=False)
            result=training_statistics(english,'conjugation','English')
            self.assertEqual(result['persons'][0].label,'I')
            self.assertTrue(all(p.successes+p.failures==0 for p in first['persons']))

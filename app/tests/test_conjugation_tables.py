"""Spreadsheet reconciliation, safe category migration and scoped summaries."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.conjugation.categories import (ConjugationTables, CATEGORY_COLUMN, catalog_path, load_catalog,
    category_names, category_ids, filter_categories, ensure_catalog)
from app.conjugation.persons import default_configuration
from app.repositories.conjugation import ConjugationDocument
from app.shared.storage import FileChangedError
from app.tests.test_conjugation_model import verbs


class ConjugationTablesTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'Czech_Spanish_con.csv'
        frame=pd.concat([verbs().assign(Description='presente simple, grupo 1'),
            verbs().assign(ID='002',Description='presente simple, irregular'),
            verbs().assign(ID='003',Description='imperativo, regular AR')],ignore_index=True)
        frame['category']='unrelated legacy metadata'
        frame.to_csv(self.path,sep=';',index=False);self.original=self.path.read_bytes()
        self.document=ConjugationDocument(self.path,'Spanish','Czech',default_configuration('es'))
        self.tables=ConjugationTables(self.document)

    def rows(self):return self.tables.verb_rows()
    def categories(self):return self.tables.catalog[['ID','Name','Description']].values.tolist()
    def apply(self,rows=None,categories=None,visible=None):
        rows=self.rows() if rows is None else rows
        self.tables.apply(rows,set(self.document.frame.ID) if visible is None else visible,
            self.categories() if categories is None else categories)

    def test_legacy_prefixes_generate_two_stable_categories_without_writing_source(self):
        self.assertEqual(self.tables.catalog.Name.tolist(),['presente simple','imperativo'])
        second=ConjugationTables(ConjugationDocument(self.path,'Spanish','Czech',default_configuration('es')))
        self.assertEqual(second.catalog.ID.tolist(),self.tables.catalog.ID.tolist())
        self.assertEqual(self.path.read_bytes(),self.original);self.assertFalse(catalog_path(self.path).exists())

    def test_ensure_only_creates_catalog_and_never_rewrites_verbs_or_existing_metadata(self):
        first=ensure_catalog(self.path,self.document.frame.drop(columns=CATEGORY_COLUMN))
        before=catalog_path(self.path).read_bytes();ensure_catalog(self.path,self.document.frame.drop(columns=CATEGORY_COLUMN))
        self.assertEqual(catalog_path(self.path).read_bytes(),before);self.assertEqual(self.path.read_bytes(),self.original)
        self.assertEqual(first.Name.tolist(),['presente simple','imperativo'])

    def test_renamed_catalog_recovers_bindings_before_source_schema_migration(self):
        source=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        catalog=ensure_catalog(self.path,source);old_ids=self.document.frame[CATEGORY_COLUMN].tolist()
        catalog['Name']=['Renamed present','Renamed imperative']
        catalog.to_csv(catalog_path(self.path),sep=';',index=False)
        recovered,_=load_catalog(self.path,source)
        self.assertEqual(len(recovered),2)
        self.assertEqual(category_ids(source,recovered).tolist(),old_ids)
        self.assertEqual(category_names(source,recovered).tolist(),['Renamed present','Renamed present','Renamed imperative'])
        self.assertEqual(self.path.read_bytes(),self.original)

    def test_bulk_paste_adds_uuid_records_and_preserves_histories_hidden_columns_and_row_ids(self):
        rows=self.rows();rows[0][1]='enseñar cambiado'
        rows.append(['','ir','jít','imperativo','free text',*['voy','','','','','']])
        self.apply(rows);self.tables.save()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.ID.tolist()[:3],['001','002','003']);self.assertEqual(len(set(saved.ID)),4)
        for key in ('R','LR','Custom','s1','s2'):
            self.assertEqual(saved.loc[:2,key].tolist(),pd.read_csv(self.path.with_name(self.path.name+'.pre-persons.bak'),sep=';',dtype=str,keep_default_na=False)[key].tolist())
        self.assertEqual(saved.iloc[-1].R,'');self.assertEqual(saved.iloc[-1].s1,'voy')
        self.assertTrue(catalog_path(self.path).exists())
        self.assertEqual(self.path.with_name(self.path.name+'.pre-categories.bak').read_bytes(),self.original)

    def test_category_rename_keeps_references_and_original_description(self):
        old=self.document.frame[CATEGORY_COLUMN].tolist();cats=self.categories();cats[0][1]='Přítomnost'
        self.apply(categories=cats);self.tables.save()
        self.assertEqual(self.document.frame[CATEGORY_COLUMN].tolist(),old)
        self.assertEqual(self.document.frame.Description.tolist(),['presente simple, grupo 1','presente simple, irregular','imperativo, regular AR'])
        self.assertEqual(category_names(self.document.frame,self.tables.catalog).tolist(),['Přítomnost','Přítomnost','imperativo'])

    def test_simultaneous_name_swap_cannot_swap_existing_verb_assignments(self):
        old=self.document.frame[CATEGORY_COLUMN].tolist();cats=self.categories()
        cats[0][1],cats[1][1]=cats[1][1],cats[0][1]
        self.apply(categories=cats);self.assertEqual(self.document.frame[CATEGORY_COLUMN].tolist(),old)

    def test_used_category_deletion_is_rejected_without_partial_changes(self):
        before=self.document.frame.copy(deep=True);catalog=self.tables.catalog.copy(deep=True)
        with self.assertRaises(ValueError):self.apply(categories=self.categories()[1:])
        pd.testing.assert_frame_equal(self.document.frame,before);pd.testing.assert_frame_equal(self.tables.catalog,catalog)

    def test_reassign_then_delete_category_and_keep_unfiltered_records(self):
        rows=self.rows()[:1];rows[0][3]='imperativo'
        self.apply(rows,visible={'001'})
        self.assertEqual(self.document.frame.ID.tolist(),['001','002','003'])
        self.assertEqual(category_names(self.document.frame,self.tables.catalog).tolist(),['imperativo','presente simple','imperativo'])

    def test_new_free_text_category_and_explicit_blank_assignment(self):
        rows=self.rows();rows[0][3]='New custom';rows[1][3]=''
        self.apply(rows);self.tables.save()
        self.assertIn('New custom',self.tables.catalog.Name.tolist())
        self.assertEqual(category_names(self.document.frame,self.tables.catalog).tolist(),['New custom','','imperativo'])
        self.assertEqual(load_catalog(self.path,self.document.frame)[0].Name.tolist(),self.tables.catalog.Name.tolist())

    def test_duplicate_categories_invalid_ids_or_extra_pasted_columns_are_rejected(self):
        cats=self.categories();cats[1][1]='PRESENTE SIMPLE'
        with self.assertRaises(ValueError):self.apply(categories=cats)
        rows=self.rows();rows[1][0]=rows[0][0]
        with self.assertRaises(ValueError):self.apply(rows)
        rows=self.rows();rows[0].append('unexpected data')
        with self.assertRaises(ValueError):self.apply(rows)
        self.assertEqual(self.path.read_bytes(),self.original)

    def test_failed_source_commit_rolls_back_new_catalog_and_keeps_pending_edits(self):
        rows=self.rows();rows[0][1]='changed';self.apply(rows)
        with patch('app.repositories.conjugation.commit_document',side_effect=PermissionError):
            with self.assertRaises(PermissionError):self.tables.save()
        self.assertFalse(catalog_path(self.path).exists());self.assertEqual(self.path.read_bytes(),self.original)
        self.assertEqual(self.document.frame.at[0,'Spanish'],'changed')
        self.tables.save();self.assertTrue(catalog_path(self.path).exists())

    def test_external_source_or_catalog_changes_are_not_overwritten(self):
        self.tables.save();before=catalog_path(self.path).read_bytes()
        rows=self.rows();rows[0][1]='changed';self.apply(rows)
        self.path.write_bytes(self.path.read_bytes()+b'\n')
        with self.assertRaises(FileChangedError):self.tables.save()
        self.assertEqual(catalog_path(self.path).read_bytes(),before)
        catalog_path(self.path).write_bytes(before+b'\n')
        with self.assertRaises(FileChangedError):self.tables.save()
        self.assertEqual(catalog_path(self.path).read_bytes(),before+b'\n')

    def test_category_filter_selects_only_requested_records_and_never_mutates_source(self):
        frame=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        filtered=filter_categories(frame,self.tables.catalog,['presente simple'])
        self.assertEqual(filtered.ID.tolist(),['001','002']);self.assertEqual(len(frame),3)
        self.assertTrue(filter_categories(frame,self.tables.catalog,['missing']).empty)
        self.assertEqual(self.path.read_bytes(),self.original)
        # Legacy statistics may contain only counters, without editable forms
        # or descriptions. Keep their histories visible as uncategorised.
        counters=frame[['ID','R','LR']]
        catalog,_=load_catalog(self.path,counters)
        self.assertEqual(category_names(counters,catalog).tolist(),['','',''])

    def test_statistics_weight_rounds_and_invalidate_on_catalog_rename(self):
        from app.statistics.data import training_statistics
        self.tables.save()
        first=training_statistics(self.path,'conjugation','Spanish')
        total=sum(c.questions for c in first['categories']);self.assertEqual(total,3)
        first_name=first['categories'][0].name
        cats=self.categories();cats[0][1]='Renamed';self.apply(categories=cats);self.tables.save()
        second=training_statistics(self.path,'conjugation','Spanish')
        self.assertIn('Renamed',[c.name for c in second['categories']])
        self.assertEqual(sum(c.successes for c in second['categories']),9)
        self.assertEqual(second['category_available'],frozenset(('Renamed','imperativo')))
        from dataclasses import replace
        from app.repositories.conjugation_persons import load_configuration,save_configuration
        config,revision=load_configuration(self.path.parent,'es',self.path)
        save_configuration(self.path.parent,replace(config,practice_person_ids=()),revision)
        self.assertEqual(training_statistics(self.path,'conjugation','Spanish')['category_available'],frozenset())

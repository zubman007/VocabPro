from datetime import datetime
import unittest
import pandas as pd
from app.vocabulary.editor_data import merge_table_edits, filter_vocabulary, prepare_save


def vocabulary():
    return pd.DataFrame({'ID':[1,2], 'English':['one','two'], 'Czech':['jedna','dva'],
        'Audio':['No audio','No audio'], 'Description':['-','-'], 'Example':['-','-'],
        'Phonetic':['[]','[]'], 'Part of Speech':['Noun','Noun'], 'Enabled':['True','True'],
        'Repetition':['S','F'], 'Next repetition':['2026-11-12 10:00:00','2026-11-13 10:00:00']})


class VocabularyEditorDataTests(unittest.TestCase):
    def test_filtered_edits_preserve_hidden_rows(self):
        source=vocabulary()
        selected=source.iloc[:1].copy()
        selected.loc[0,'Czech']='changed'
        updated,_=merge_table_edits(source,selected.values.tolist(),list(source.columns),'English','Czech')
        self.assertEqual(updated['ID'].tolist(),[1,2])
        self.assertEqual(updated['Czech'].tolist(),['changed','dva'])
        self.assertEqual(source['Czech'].tolist(),['jedna','dva'])

    def test_new_rows_are_added_once(self):
        source=vocabulary()
        row=source.iloc[:1].copy()
        row.loc[0,'ID']=3
        updated,_=merge_table_edits(source,row.values.tolist(),list(source.columns),'English','Czech')
        again,_=merge_table_edits(updated,row.values.tolist(),list(source.columns),'English','Czech')
        self.assertEqual(again['ID'].tolist(),[1,2,3])

    def test_duplicate_or_fractional_ids_do_not_mutate_source(self):
        source=vocabulary()
        before=source.copy(deep=True)
        for ids in ([1,1],[1,1.5],[1,'']):
            rows=source.copy()
            rows['ID']=ids
            with self.assertRaises(ValueError):
                merge_table_edits(source,rows.values.tolist(),list(source.columns),'English','Czech')
        pd.testing.assert_frame_equal(source,before)

    def test_empty_filtered_view_does_not_erase_vocabulary(self):
        source=vocabulary()
        updated,_=merge_table_edits(source,[],list(source.columns),'English','Czech')
        pd.testing.assert_frame_equal(updated,source)

    def test_filter_is_literal_and_case_insensitive(self):
        source=vocabulary()
        source.loc[0,'English']='[One]'
        self.assertEqual(filter_vocabulary(source,'English','contains',' [ONE] ')['ID'].tolist(),[1])
        self.assertEqual(filter_vocabulary(source,'English','excludes','[')['ID'].tolist(),[2])

    def test_save_preserves_history_and_creation_dates(self):
        edited=vocabulary()
        previous=edited.copy()
        previous['Created']=['2025-01-01','2025-02-01']
        edited.loc[0,'Repetition']='must not replace stored history'
        result=prepare_save(edited,previous,datetime(2026,11,12,10,0))
        self.assertEqual(result['Repetition'].tolist(),['S','F'])
        self.assertEqual(result['Created'].tolist(),['2025-01-01','2025-02-01'])
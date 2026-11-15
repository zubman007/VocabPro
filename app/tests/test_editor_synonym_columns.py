"""Derived relation counts, forged paste resistance and vocabulary CSV schema."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import pandas as pd
from app.vocabulary.editor_synonym_columns import add_columns,COLUMNS
from app.vocabulary.editor_data import prepare_save
from app.repositories import synonyms
from app.tests.test_editor_save import course


class ComputedSynonymTests(unittest.TestCase):
    def test_undirected_counts_include_both_ends_and_ignore_forged_values(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'Czech_English_voc.csv'
            words=pd.concat([course()]*3,ignore_index=True);words['ID']=[1,5,9]
            words.to_csv(path,sep=';',index=False)
            synonyms.replace_links(path,1,[5,9],None)
            words['Has synonyms']='forged';words['Synonym count']=999
            result=add_columns(words,path).set_index('ID')
            self.assertEqual(result['Synonym count'].to_dict(),{1:2,5:1,9:1})
            self.assertEqual(result.loc[1,'Has synonyms'],'●')
            reduced=add_columns(words.loc[words.ID.ne(1)],path)
            self.assertEqual(reduced['Synonym count'].tolist(),[0,0])
            self.assertEqual(reduced['Has synonyms'].tolist(),['—','—'])

    def test_prepare_save_never_serializes_computed_fields(self):
        previous=course()
        edited=previous.drop(columns='Created').copy()
        edited['Has synonyms']='●';edited['Synonym count']=3
        saved=prepare_save(edited,previous)
        self.assertFalse(set(COLUMNS)&set(saved.columns))

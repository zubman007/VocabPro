"""New-language initialization and safe removal of unused empty course files."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import pandas as pd
from app.repositories.courses import ensure_course, remove_unused_empty_courses
from app.home.data import course_overview
from app.repositories.vocabulary import load_vocabulary
from app.repositories import synonyms


class CourseFileTests(unittest.TestCase):
    def test_new_languages_create_only_working_vocabulary_schema(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory)
            for language in ('English','Spanish','German','French'):
                ensure_course(folder,'Czech',language)
                path=folder/f'Czech_{language}_voc.csv'
                frame=load_vocabulary(path,language,'Czech')
                self.assertTrue(frame.empty)
                self.assertEqual('Phonetic' in frame,language!='Spanish')
                self.assertNotIn('Enabled',frame)
                self.assertEqual(course_overview(folder,'Czech',language,10,10)['all_count'],0)
                self.assertTrue(synonyms.load(path,frame)[0].empty)
            self.assertEqual(len(list(folder.glob('*.csv'))),4)
            self.assertFalse((folder/'audio').exists())

    def test_switch_removes_only_unused_empty_courses_and_never_data(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory)
            for language in ('English','Spanish','German','French'):ensure_course(folder,'Czech',language)
            populated=folder/'Czech_English_voc.csv'
            frame=pd.read_csv(populated,sep=';')
            row=dict.fromkeys(frame.columns,'');row.update(ID=1,English='word',Czech='slovo')
            pd.DataFrame([row],columns=frame.columns).to_csv(populated,sep=';',index=False)
            before=populated.read_bytes()
            (folder/'Czech_German_synonyms.csv').write_text('ID 1;ID 2;Date\n')
            (folder/'Czech_French_synonyms.csv').write_text('ID 1;ID 2;Date\n1;2;2026-11-14\n')
            (folder/'unrelated.csv').write_text('ID;Repetition\n')
            removed=remove_unused_empty_courses(folder,'Czech',['Spanish'])
            self.assertEqual(set(removed),{'Czech_German_voc.csv','Czech_French_voc.csv','Czech_German_synonyms.csv'})
            self.assertTrue((folder/'Czech_Spanish_voc.csv').exists())
            self.assertEqual(populated.read_bytes(),before)
            self.assertTrue((folder/'Czech_French_synonyms.csv').exists())
            self.assertTrue((folder/'unrelated.csv').exists())
            ensure_course(folder,'Czech','German')
            self.assertTrue((folder/'Czech_German_voc.csv').exists())

    def test_existing_course_is_never_recreated(self):
        with TemporaryDirectory() as directory:
            ensure_course(directory,'Czech','German')
            path=Path(directory)/'Czech_German_voc.csv';original=path.read_bytes()
            ensure_course(directory,'Czech','German')
            self.assertEqual(path.read_bytes(),original)

"""Course-local links, stable references, persistence and strict answer rules."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import pandas as pd
from app.repositories import synonyms as sy
from app.vocabulary.practise_data import answers_match
from app.shared.storage import FileChangedError


class SynonymTests(unittest.TestCase):
    def test_each_synonym_is_one_logical_line_even_with_multiline_csv_text(self):
        sy.replace_links(self.course,1,[5],None)
        frame,_=sy.load(self.course,self.words)
        words=self.words.copy();words.loc[words.ID.eq(5),'English']='mad\nfurious'
        words.loc[words.ID.eq(5),'Czech']='first\nsecond'
        text=sy.describe(frame,words,1,'English','Czech')
        self.assertEqual(text,'mad furious — first second')
        self.assertEqual(len(text.splitlines()),1)

    def test_random_link_edits_remain_symmetric_unique_and_course_local(self):
        import random
        rng=random.Random(42)
        ids=[1,5,9]
        expected=set()
        for _ in range(35):
            source=rng.choice(ids)
            selected={target for target in ids if target!=source and rng.choice([True,False])}
            _,revision=sy.load(self.course,self.words)
            sy.replace_links(self.course,source,selected,revision)
            expected={pair for pair in expected if source not in pair}
            expected.update(tuple(sorted((source,target))) for target in selected)
            frame,_=sy.load(self.course,self.words)
            actual=[(int(a),int(b)) for a,b in frame[['ID 1','ID 2']].itertuples(index=False,name=None)]
            self.assertEqual(set(actual),expected)
            self.assertEqual(len(actual),len(set(actual)))
            self.assertTrue(all(first<second for first,second in actual))
            for word_id in ids:
                neighbors={b if a==word_id else a for a,b in expected if word_id in (a,b)}
                self.assertEqual(sy.linked_ids(frame,word_id),neighbors)

    def test_link_changes_do_not_cross_course_boundaries(self):
        other=self.course.with_name('Czech_Spanish_voc.csv')
        self.words.to_csv(other,sep=';',index=False)
        sy.replace_links(self.course,1,[5],None)
        sy.replace_links(other,1,[9],None)
        self.assertEqual(sy.linked_ids(sy.load(self.course,self.words)[0],1),{5})
        self.assertEqual(sy.linked_ids(sy.load(other,self.words)[0],1),{9})

    def test_failed_write_preserves_links_and_invalid_dates_are_rejected(self):
        from unittest.mock import patch
        sy.replace_links(self.course,1,[5],None)
        path=sy.relation_path(self.course);before=path.read_bytes()
        _,revision=sy.load(self.course,self.words)
        with patch('app.repositories.synonyms.save_csv',side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):sy.replace_links(self.course,1,[9],revision)
        self.assertEqual(path.read_bytes(),before)
        pd.DataFrame([[1,5,'not a date']],columns=sy.COLUMNS).to_csv(path,sep=';',index=False)
        with self.assertRaises(ValueError):sy.load(self.course,self.words)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.course = Path(self.temp.name)/'Czech_English_voc.csv'
        self.words = pd.DataFrame({'ID':[1,5,9],'English':['angry','mad','cross'],'Czech':['a','b','c']})
        self.words.to_csv(self.course,sep=';',index=False)

    def test_empty_missing_file_and_bidirectional_pair(self):
        frame, revision = sy.load(self.course,self.words)
        self.assertTrue(frame.empty)
        sy.replace_links(self.course,5,[1],revision)
        frame, revision = sy.load(self.course,self.words)
        self.assertEqual(frame.iloc[0].tolist()[:2],[1,5])
        self.assertEqual(sy.linked_ids(frame,1),{5})
        self.assertEqual(sy.linked_ids(frame,5),{1})
        date = frame.iloc[0]['Date']
        sy.replace_links(self.course,1,[5,5],revision)
        frame,_ = sy.load(self.course,self.words)
        self.assertEqual(len(frame),1)
        self.assertEqual(frame.iloc[0]['Date'],date)

    def test_no_transitivity_no_alternative_answer(self):
        sy.replace_links(self.course,1,[5],None)
        _, revision = sy.load(self.course,self.words)
        sy.replace_links(self.course,5,[1,9],revision)
        frame,_ = sy.load(self.course,self.words)
        self.assertEqual(sy.linked_ids(frame,1),{5})
        self.assertFalse(answers_match('angry','mad'))
        self.assertIn('mad',sy.describe(frame,self.words,1,'English','Czech'))

    def test_self_and_missing_id_rejected(self):
        for source, targets in [(1,[1]),(1,[99]),(99,[1])]:
            with self.assertRaises(ValueError):sy.replace_links(self.course,source,targets,None)
        self.assertFalse(sy.relation_path(self.course).exists())

    def test_reverse_duplicates_rejected(self):
        pd.DataFrame([[1,5,'2026-11-14'],[5,1,'2026-11-14']],columns=sy.COLUMNS).to_csv(sy.relation_path(self.course),sep=';',index=False)
        with self.assertRaises(ValueError):sy.load(self.course,self.words)

    def test_conflict_preserves_other_editor(self):
        sy.replace_links(self.course,1,[5],None)
        original=sy.relation_path(self.course).read_bytes()
        with self.assertRaises(FileChangedError):sy.replace_links(self.course,1,[9],None)
        self.assertEqual(sy.relation_path(self.course).read_bytes(),original)

    def test_deleted_word_is_hidden_and_cleaned_on_next_link_save(self):
        sy.replace_links(self.course,1,[5],None)
        words=self.words.loc[self.words.ID.ne(5)]
        words.to_csv(self.course,sep=';',index=False)
        frame,revision=sy.load(self.course,words)
        self.assertTrue(frame.empty)
        sy.replace_links(self.course,1,[9],revision)
        frame,_=sy.load(self.course,words)
        self.assertEqual(sy.linked_ids(frame,1),{9})

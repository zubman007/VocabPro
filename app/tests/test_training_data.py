"""Regression checks for extracted grammar and conjugation logic."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.repositories.grammar import Load_questions_from_csv, save_answers
from app.grammar.data import Shuffle_copy
from app.conjugation.data import Verb, PERSONS_MAP, select_verbs, build_verbs, answers_match, record_result
from app.repositories.conjugation import save_results


class GrammarDataTests(unittest.TestCase):
    def test_save_keeps_literal_text_and_leading_zero_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar_practise.csv'
            pd.DataFrame({'question_id':['001','002'], 'prompt':['NA','null'],
                'R':['','S'], 'LR':['','']}).to_csv(path,sep=';',index=False)
            save_answers(path,[('001','F',None,'2026-11-13 12:00:00')])
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(saved.question_id.tolist(),['001','002'])
            self.assertEqual(saved.prompt.tolist(),['NA','null'])
            self.assertEqual(saved.R.tolist(),['F','S'])

    def test_load_and_record_answer_preserve_other_questions(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar_questions.csv'
            frame=pd.DataFrame({
                'question_id':[1,2], 'prompt':['first','second'], 'anchor':['a','b'],
                'option_1':['correct','yes'], 'option_2':['no','wrong'],
                'option_3':['x','x'], 'option_4':['y','y'], 'category':['Articles','Tenses'],
                'R':['S','F'], 'LR':['',''],
            })
            frame.to_csv(path,sep=';',index=False)
            questions=Load_questions_from_csv(path)
            self.assertEqual(questions[0]['correct_answer'],'correct')
            self.assertEqual(questions[0]['category'],'Articles')
            self.assertEqual(questions[0]['count_trailing_s'],1)
            save_answers(path,[('1','F',None,'2026-11-13 12:00:00')])
            result=pd.read_csv(path,sep=';').fillna('')
            self.assertEqual(result['R'].tolist(),['SF','F'])
            self.assertEqual(result['category'].tolist(),['Articles','Tenses'])
            self.assertNotEqual(result.loc[0,'LR'],'')
            self.assertEqual(result.loc[1,'LR'],'')

    def test_question_order_prefers_weaker_with_equal_random_keys_without_mutating_source(self):
        items=[{'count_trailing_s':3},{'count_trailing_s':0},{'count_trailing_s':1}]
        with patch('app.grammar.data.random.random',return_value=.5):
            result=Shuffle_copy(items,1)
        self.assertEqual([x['count_trailing_s'] for x in result],[0,1,3])
        self.assertEqual(items[0]['count_trailing_s'],3)

    def test_invalid_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar_questions.csv'
            path.write_text('prompt;anchor\nquestion;context\n',encoding='utf-8')
            with self.assertRaises(ValueError):
                Load_questions_from_csv(path)


class ConjugationDataTests(unittest.TestCase):
    def test_selection_matches_previous_order_and_types_for_nondefault_index(self):
        import numpy as np
        from app.shared.learning_data import Count_trailing_s
        source = pd.DataFrame({'ID': [1, 2, 3, 4], 'R': ['S', 'F', 'F', 'SS'],
            'LR': ['', '2026-01-02', '2026-01-01', '2026-01-03'],
            'Spanish': ['a', 'b', 'c', 'd']}, index=[20, 40, 40, 80])
        original = source.copy(deep=True)
        expected = source.copy()
        expected['LR'] = pd.to_datetime(expected['LR'], errors='coerce')
        expected['trailing_s'] = expected['R'].map(Count_trailing_s)
        state = np.random.get_state()
        try:
            np.random.seed(123)
            expected = (expected.sample(frac=1).sort_values(['trailing_s', 'LR'],
                ascending=[True, True], na_position='first').head(3).drop(columns='trailing_s'))
            np.random.seed(123)
            result = select_verbs(source, 3)
        finally:
            np.random.set_state(state)
        pd.testing.assert_frame_equal(result, expected)
        pd.testing.assert_frame_equal(source, original)

    def test_build_verbs_keeps_large_integer_ids_and_explicit_column_order(self):
        identifier = 2**53 + 1
        frame = pd.DataFrame({'Spanish': ['hablar'], 'Czech': ['speak'],
            'Description': ['present'], 'ID': [identifier],
            **{key: [key] for key, _ in PERSONS_MAP['Spanish']}})
        verb, = build_verbs(frame, 'Spanish', 'Czech')
        self.assertEqual(verb.id, identifier)
        self.assertEqual((verb.base_lng, verb.targ_lng, verb.desc), ('speak', 'hablar', 'present'))
        for key, _ in PERSONS_MAP['Spanish']:
            self.assertEqual(getattr(verb, key), key)

    def test_batch_selection_prefers_weaker_and_older_without_mutation(self):
        frame=pd.DataFrame({'ID':[1,2,3],'R':['S','F','F'],
                            'LR':['2026-01-03','2026-01-02','2026-01-01']})
        original=frame.copy(deep=True)
        self.assertEqual(select_verbs(frame,2)['ID'].tolist(),[3,2])
        pd.testing.assert_frame_equal(frame,original)

    def test_matching_preserves_n_rules_and_ignores_missing_forms(self):
        verb=Verb(1,'enseño','','','','','','','','')
        answers={key:'' for key,_ in PERSONS_MAP['Spanish']}
        answers['s1']=' enseňo '
        self.assertTrue(answers_match(verb,answers,PERSONS_MAP['Spanish']))
        answers['s1']=' ENSENO '
        self.assertTrue(answers_match(verb,answers,PERSONS_MAP['Spanish']))
        answers['s1']='incorrect'
        self.assertFalse(answers_match(verb,answers,PERSONS_MAP['Spanish']))

    def test_results_update_only_selected_id(self):
        frame=pd.DataFrame({'ID':[1,2],'R':['S','F'],'LR':['','']})
        record_result(frame,1,'F')
        self.assertEqual(frame['R'].tolist(),['SF','F'])
        self.assertNotEqual(frame.loc[0,'LR'],'')
        self.assertEqual(frame.loc[1,'LR'],'')

    def test_failed_save_keeps_source_and_selection_unchanged(self):
        source=pd.DataFrame({'ID':[1,2],'R':['S','F'],'LR':['','']})
        selection=source.iloc[:1].copy()
        selection.loc[selection.index[0],'R']='SS'
        before=source.copy(deep=True)
        selected_before=selection.copy(deep=True)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'verbs.csv';source.to_csv(path,sep=';',index=False)
            original_bytes=path.read_bytes()
            with patch('app.repositories.conjugation.save_csv',side_effect=PermissionError):
                with self.assertRaises(PermissionError):
                    save_results(source,selection,path)
            self.assertEqual(path.read_bytes(),original_bytes)
        pd.testing.assert_frame_equal(source,before)
        pd.testing.assert_frame_equal(selection,selected_before)

from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.vocabulary.practise_data import answers_match as practice_answers_match, next_repetition, shuffle_letters
from app.repositories.vocabulary import save_practice


class PracticeDataTests(unittest.TestCase):
    def test_empty_alternatives_never_accept_an_empty_answer(self):
        for expected in ('word /', '/ word', '', '...'):
            self.assertFalse(practice_answers_match(expected,''))
            self.assertFalse(practice_answers_match(expected,'!!!'))
        self.assertTrue(practice_answers_match('word /','WORD'))

    def test_answer_normalization_cache_is_bounded(self):
        from app.vocabulary.practise_data import _answer_variants
        _answer_variants.cache_clear()
        for index in range(700):practice_answers_match('word',str(index))
        self.assertLessEqual(_answer_variants.cache_info().currsize,512)
        self.assertGreater(_answer_variants.cache_info().hits,0)
        _answer_variants.cache_clear()

    def test_matching_preserves_accents_punctuation_and_variants(self):
        self.assertTrue(practice_answers_match('café / cafetería',' CAFE! '))
        self.assertTrue(practice_answers_match('one / two','TWO'))
        self.assertFalse(practice_answers_match('one','three'))

    def test_schedule_keeps_initial_learning_and_failure_rules(self):
        now=datetime(2026,11,12,10,30)
        gaps={0:0,1:1,2:2}
        self.assertEqual(next_repetition('SSS',gaps,200,now),'2026-11-12 10:30:00')
        self.assertEqual(next_repetition('SSSSS',gaps,200,now),'2026-11-13 10:30:00')
        self.assertEqual(next_repetition('SSSSSSF',gaps,200,now),'2026-11-12 10:30:00')

    def test_hint_contains_word_letters_and_three_extra_letters(self):
        hint=shuffle_letters('hello world').replace(' ','').lower()
        expected='hello_world'
        self.assertEqual(len(hint),len(expected)+3)
        for letter in set(expected):
            self.assertGreaterEqual(hint.count(letter),expected.count(letter))

    def test_save_only_updates_practice_fields(self):
        source=pd.DataFrame({'ID':[1,2],'English':['one','two'],'Czech':['jedna','dva'],
            'Part of Speech':['Noun','Verb'],'Created':['2025-01-01','2025-02-01'],
            'Next repetition':['2026-11-12 10:00:00']*2,'Repetition':['S','F'],
            'Audio':['Own','No audio'],'Description':['old','old'],'Example':['example','example']})
        source['Custom']=['007','NA']
        source.loc[1,'English']='null'
        completed=source.iloc[:1].copy()
        completed.loc[0,'Repetition']='SS'
        completed.loc[0,'Description']='new'
        completed.loc[0,'Part of Speech']='must not replace manual value'
        remaining=source.iloc[0:0].copy()
        before=completed.copy(deep=True)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'vocabulary.csv'
            source.to_csv(path,sep=';',index=False)
            save_practice(path,remaining.drop(columns='Custom'),completed.drop(columns='Custom'),
                          [column for column in source.columns if column != 'Custom'])
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(saved.Custom.tolist(),['007','NA'])
            self.assertEqual(saved.English.tolist(),['one','null'])
            self.assertEqual(saved['Repetition'].tolist(),['SS','F'])
            self.assertEqual(saved['Part of Speech'].tolist(),['Noun','Verb'])
            self.assertEqual(saved['Description'].tolist(),['new','old'])
        pd.testing.assert_frame_equal(completed,before)

    def test_failure_preserves_session_frames(self):
        frame=pd.DataFrame({'ID':[1], 'Next repetition':['2026-11-12 10:00:00']})
        before=frame.copy(deep=True)
        with patch('app.repositories.vocabulary.pd.read_csv',side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                save_practice('unused.csv',frame,frame.iloc[:0],list(frame.columns))
        pd.testing.assert_frame_equal(frame,before)

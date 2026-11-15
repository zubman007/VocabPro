"""Weighted ordering, coverage and local progress on synthetic grammar records."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
import random
from tempfile import TemporaryDirectory
import unittest

from app.grammar.data import Shuffle_copy, question_weights
from app.grammar.session import GrammarSession
from app.repositories.grammar import Load_questions_from_csv, save_answers


NOW = datetime(2026, 11, 15, 12)


def question(identifier, history='', last='2026-11-15 12:00:00', category='Topic'):
    return dict(id=str(identifier), category=category, repetition=history, last_review=last,
                count_trailing_s=len(history)-len(history.rstrip('S')),
                prompt='Choose', anchor='A sentence', options=['yes','no','x','y'],
                correct_answer='yes', explanation='A reason')


class SelectionTests(unittest.TestCase):
    def test_unanswered_and_recent_errors_outweigh_mastered_questions(self):
        new, wrong, strong = question(1), question(2,'SSSF'), question(3,'S'*30)
        new_weight, wrong_weight, strong_weight = question_weights([new,wrong,strong],now=NOW)
        self.assertGreater(new_weight,strong_weight)
        self.assertGreater(wrong_weight,strong_weight)
        # A mastered question remains eligible even in a difficult pool.
        self.assertGreaterEqual(strong_weight,.30/3)

    def test_error_frequency_matters_with_equal_attempts_and_trailing_successes(self):
        weak, strong = question(1,'FFFFFFSFSS'), question(2,'SSSSSSSFSS')
        weights=question_weights([weak,strong],now=NOW)
        self.assertGreater(weights[0],weights[1])

    def test_last_failure_has_extra_priority_with_equal_error_frequency(self):
        failed, recovering = question(1,'S'*9+'F'), question(2,'F'+'S'*9)
        weights=question_weights([failed,recovering],now=NOW)
        self.assertGreater(weights[0],weights[1])

    def test_older_answer_has_higher_priority_and_age_is_capped(self):
        weights=question_weights([question(1,'SS','2026-05-15'),question(2,'SS'),
                                  question(3,'SS','2000-01-01')],now=NOW)
        self.assertGreater(weights[0],weights[1])
        self.assertAlmostEqual(weights[0],weights[2])

    def test_low_attempt_count_matters_with_same_recent_history_and_streak(self):
        weights=question_weights([question(1,'FS'*5),question(2,'FS'*50)],now=NOW)
        self.assertGreater(weights[0],weights[1])

    def test_category_volume_is_not_cancelled_by_equal_topic_quotas(self):
        items=[question(i,'SS',category='Large' if i<10 else 'Small') for i in range(15)]
        weights=question_weights(items,now=NOW)
        self.assertAlmostEqual(sum(weights[:10]),2/3)
        self.assertAlmostEqual(sum(weights[10:]),1/3)

    def test_identical_histories_are_uniform_and_unseen_fallback_is_valid(self):
        for history in ('','SSSS','FFSS'):
            weights=question_weights([question(i,history) for i in range(7)],now=NOW)
            self.assertTrue(all(abs(weight-1/7)<1e-12 for weight in weights))

    def test_empty_singleton_and_missing_or_invalid_metadata(self):
        self.assertEqual(Shuffle_copy([],1),[])
        self.assertEqual(question_weights([]),[])
        single=question('001')
        self.assertEqual(Shuffle_copy([single],1),[single])
        items=[dict(id='1'),dict(id='2',repetition=None,last_review=None),
               dict(id='3',count_trailing_s='bad',last_review='not a date'),
               question('4','S? F\nS','2040-01-01'),
               question('5','SS','2026-11-14T12:00:00+00:00')]
        for now in (NOW,NOW.replace(tzinfo=timezone.utc)):
            weights=question_weights(items,now=now)
            self.assertTrue(all(isfinite(weight) and weight>0 for weight in weights))
            self.assertAlmostEqual(sum(weights),1)
        neutral=question_weights([question(1,'SS',''),question(2,'SS','bad'),
                                  question(3,'SS','2040-01-01')],now=NOW)
        self.assertTrue(all(abs(weight-1/3)<1e-12 for weight in neutral))

    def test_seeded_rounds_cover_each_id_once_and_never_mutate_source(self):
        items=[question(i,['','F','SSSS'][i%3]) for i in range(60)]
        original=deepcopy(items)
        orders=set()
        for seed in range(20):
            ordered=Shuffle_copy(items,1,rng=random.Random(seed),now=NOW)
            self.assertCountEqual([item['id'] for item in ordered],[item['id'] for item in items])
            orders.add(tuple(item['id'] for item in ordered))
        self.assertEqual(len(orders),20)
        self.assertEqual(items,original)
        self.assertEqual(Shuffle_copy(items,1,rng=random.Random(42),now=NOW),
                         Shuffle_copy(items,1,rng=random.Random(42),now=NOW))

    def test_seeded_empirical_first_question_matches_the_weights(self):
        items=[question(1),question(2,'SSSF'),question(3,'S'*25),question(4,'SS','2026-05-01')]
        expected=question_weights(items,now=NOW)
        generator=random.Random(4311)
        counts=Counter(Shuffle_copy(items,1,rng=generator,now=NOW)[0]['id'] for _ in range(12000))
        for item,weight in zip(items,expected):
            self.assertAlmostEqual(counts[item['id']]/12000,weight,delta=.018)
        self.assertGreater(counts['2'],counts['3'])
        self.assertGreater(counts['1'],counts['3'])

    def test_uniform_component_can_put_a_mastered_question_first(self):
        items=[question('weak','FFFF'),question('strong','S'*40)]
        generator=random.Random(2026)
        first={Shuffle_copy(items,1,rng=generator,now=NOW)[0]['id'] for _ in range(100)}
        self.assertEqual(first,{'weak','strong'})

    def test_answer_options_still_shuffle_independently_and_keep_correct_value(self):
        options=['yes','no','x','y']
        orders={tuple(Shuffle_copy(options,0,rng=random.Random(seed))) for seed in range(30)}
        self.assertGreater(len(orders),10)
        for order in orders:self.assertCountEqual(order,options)
        self.assertEqual(options,['yes','no','x','y'])


class ProgressTests(unittest.TestCase):
    def test_answer_progress_affects_next_round_without_mutating_input(self):
        items=[question('001','SS')];original=deepcopy(items)
        session=GrammarSession(items);session.advance()
        self.assertFalse(session.answer(session.options.index('no'),when='2026-11-15 11:00:00'))
        self.assertEqual(session.current['repetition'],'SS')
        self.assertEqual(session.progress['001']['repetition'],'SSF')
        session.restart();session.advance()
        self.assertEqual(session.current['repetition'],'SSF')
        self.assertEqual(session.current['last_review'],'2026-11-15 11:00:00')
        self.assertTrue(session.answer(session.options.index('yes'),when='2026-11-15 12:00:00'))
        self.assertEqual(session.progress['001']['repetition'],'SSFS')
        self.assertIsNone(session.answer(0))
        self.assertEqual(session.progress['001']['repetition'],'SSFS')
        self.assertEqual(items,original)

    def test_progress_survives_category_changes_but_other_sessions_are_independent(self):
        articles=[question('a',category='Articles')];tenses=[question('t',category='Tenses')]
        progress={}
        session=GrammarSession(articles,progress=progress);session.advance()
        session.answer(session.options.index('no'))
        filtered=GrammarSession(tenses,progress=progress)
        self.assertEqual(filtered.advance()['id'],'t')
        self.assertIsNone(filtered.advance())
        resumed=GrammarSession(articles,progress=progress)
        self.assertEqual(resumed.advance()['repetition'],'F')
        independent=GrammarSession(articles)
        self.assertEqual(independent.advance()['repetition'],'')

    def test_reveal_and_skip_do_not_create_persisted_or_local_answer_history(self):
        session=GrammarSession([question(1),question(2)])
        session.advance();session.reveal();session.advance();session.advance()
        self.assertEqual(session.progress,{})
        self.assertEqual((session.correct,session.incorrect),(0,1))

    def test_loader_age_and_deferred_deltas_round_trip_without_duplicate_history(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'English_gra.csv'
            path.write_text('\ufeffquestion_id;category;prompt;anchor;option_1;option_2;option_3;option_4;R;LR;custom\n'
                '001;Čas;Choose;Sentence;yes;no;x;y;S;2025-01-01 12:00:00;007\n',encoding='utf-8')
            before=path.read_bytes()
            items=Load_questions_from_csv(path)
            self.assertEqual(items[0]['last_review'],'2025-01-01 12:00:00')
            session=GrammarSession(items);pending=[]
            for result,answer in (('F','no'),('S','yes')):
                session.restart();session.advance();expected=session.current.copy()
                when='2026-11-15 12:00:00'
                pending.append(('001',result,expected,when))
                session.answer(session.options.index(answer),when=when)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(session.progress['001']['repetition'],'SFS')
            save_answers(path,pending)
            loaded=Load_questions_from_csv(path)
            self.assertEqual(loaded[0]['id'],'001')
            self.assertEqual(loaded[0]['repetition'],'SFS')
            self.assertEqual(loaded[0]['last_review'],'2026-11-15 12:00:00')
            self.assertIn(';007',path.read_text(encoding='utf-8'))
            path.write_text('question_id;prompt;anchor;option_1;option_2;option_3;option_4;R;LR\n'
                            '2;Choose;Sentence;yes;no;x;y\n',encoding='utf-8')
            self.assertEqual(Load_questions_from_csv(path)[0]['last_review'],'')

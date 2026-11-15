"""Lesson rules tested without Tk, files or sound devices."""
import unittest
from unittest.mock import patch
import pandas as pd
from app.grammar.session import GrammarSession
from app.conjugation.session import ConjugationSession
from app.conjugation.data import Verb


def question(identifier='1', trailing=0):
    return dict(id=identifier, prompt='Choose', anchor='Sentence',
                options=['yes', 'no', 'x', 'y'], correct_answer='yes',
                explanation='Reason', count_trailing_s=trailing)


class GrammarSessionTests(unittest.TestCase):
    def test_weighted_questions_and_independent_rounds(self):
        questions = [question('strong', 3), question('weak', 0)]
        with patch('app.grammar.data.random.random',return_value=.5):
            first, second = GrammarSession(questions), GrammarSession(questions)
        self.assertEqual(first.advance()['id'], 'weak')
        first.answer(first.options.index('yes'))
        self.assertEqual((first.correct, second.correct), (1, 0))
        self.assertEqual(len(second.remaining), 2)
        self.assertEqual(questions[0]['id'], 'strong')

    def test_success_streak_failure_and_duplicate_answer(self):
        state = GrammarSession([question(str(i)) for i in range(3)])
        for _ in range(2):
            state.advance()
            self.assertTrue(state.answer(state.options.index('yes')))
        self.assertEqual((state.correct, state.streak, state.best_streak), (2, 2, 2))
        state.advance()
        self.assertFalse(state.answer(state.options.index('no')))
        self.assertIsNone(state.answer(0))
        self.assertEqual((state.incorrect, state.streak, state.best_streak), (1, 0, 2))

    def test_reveal_counts_once_and_restart_resets_round(self):
        state = GrammarSession([question()])
        state.advance()
        self.assertTrue(state.reveal())
        self.assertFalse(state.reveal())
        self.assertIsNone(state.answer(0))
        self.assertEqual((state.correct, state.incorrect), (0, 1))
        self.assertIsNone(state.advance())
        self.assertFalse(state.reveal())
        state.restart()
        self.assertEqual((state.correct, state.incorrect, state.best_streak), (0, 0, 0))
        self.assertIsNotNone(state.advance())

    def test_next_can_skip_without_recording_an_answer(self):
        state = GrammarSession([question('1'), question('2')])
        state.advance()
        state.advance()
        self.assertEqual((state.correct, state.incorrect), (0, 0))


def conjugation_round():
    selection = pd.DataFrame({'ID': [1, 2], 'R': ['', ''], 'LR': ['', '']})
    verbs = [Verb(i, 'enseño', '', '', '', '', '', 'present', 'teach', 'enseñar') for i in (1, 2)]
    return ConjugationSession(selection, verbs, [('s1', 'Yo'), ('s2', 'Tú')])


class ConjugationSessionTests(unittest.TestCase):
    def test_wrong_then_revealed_confirmation_keeps_only_failure(self):
        state = conjugation_round()
        current = state.advance()
        self.assertFalse(state.confirm({'s1': 'wrong', 's2': ''}))
        self.assertTrue(state.revealed)
        self.assertTrue(state.confirm({'s1': 'enseño', 's2': ''}))
        self.assertIsNone(state.confirm({'s1': 'enseño', 's2': ''}))
        self.assertEqual(state.selection.loc[state.selection.ID == current.id, 'R'].iloc[0], 'F')
        self.assertEqual(state.completed, 1)
        self.assertIs(state.previous, current)

    def test_matching_and_success_preserve_missing_forms(self):
        state = conjugation_round()
        current = state.advance()
        self.assertTrue(state.confirm({'s1': ' ENSENO ', 's2': 'ignored'}))
        self.assertEqual(state.selection.loc[state.selection.ID == current.id, 'R'].iloc[0], 'S')
        self.assertFalse(state.revealed)

    def test_skip_does_not_write_history_or_increment_count(self):
        state = conjugation_round()
        first = state.advance()
        next_verb = state.advance(skip=True)
        self.assertIsNot(first, next_verb)
        self.assertEqual(state.selection.R.tolist(), ['', ''])
        self.assertEqual(state.completed, 0)
        self.assertIsNone(state.previous)
        self.assertIsNone(state.advance(skip=True))
        self.assertIsNone(state.confirm({'s1': 'enseño', 's2': ''}))

    def test_rounds_do_not_share_remaining_verbs_or_results(self):
        first, second = conjugation_round(), conjugation_round()
        second = ConjugationSession(first.selection, first.remaining, first.persons)
        first.advance()
        first.confirm({'s1': 'wrong', 's2': ''})
        self.assertEqual(second.selection.R.tolist(), ['', ''])
        self.assertEqual(len(second.remaining), 2)

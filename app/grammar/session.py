"""Grammar round state; no widgets, file writes or audio."""
from collections import deque
from datetime import datetime
from app.grammar.data import Shuffle_copy
from app.shared.learning_data import Count_trailing_s


class GrammarSession:
    def __init__(self, questions, *, progress=None):
        self.questions = tuple(questions)
        # Shared by a controller's filtered rounds, separate from source records
        # and the pending persistence deltas. No answer is written here.
        self.progress = progress if progress is not None else {}
        self.restart()

    def restart(self):
        records = [dict(question, **self.progress.get(question['id'], {}))
                   for question in self.questions]
        self.remaining = deque(Shuffle_copy(records, 1))
        self.current = None
        self.previous = None
        self.options = ()
        self.revealed = False
        self.correct = self.incorrect = self.streak = self.best_streak = 0
        self.recent_results = deque(maxlen=10)

    def advance(self):
        if self.current is not None and not self.revealed:self.streak=0
        if self.current is not None:
            self.previous = self.current
        self.current = self.remaining.popleft() if self.remaining else None
        self.revealed = False
        self.options = tuple(Shuffle_copy(self.current['options'], 0)) if self.current else ()
        return self.current

    @property
    def can_answer(self):
        return self.current is not None and not self.revealed

    def is_correct(self, index):
        return self.options[index] == self.current['correct_answer']

    def answer(self, index, *, when=None):
        if not self.can_answer:
            return None
        correct = self.is_correct(index)
        self.revealed = True
        self.recent_results.append(correct)
        if correct:
            self.correct += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.incorrect += 1
            self.streak = 0
        history = (self.current.get('repetition') or '') + ('S' if correct else 'F')
        self.progress[self.current['id']] = dict(repetition=history,
            count_trailing_s=Count_trailing_s(history),
            last_review=when if when is not None else datetime.now().isoformat(sep=' ', timespec='seconds'))
        return correct

    def reveal(self):
        if not self.can_answer:
            return False
        self.revealed = True
        self.incorrect += 1
        self.streak = 0
        self.recent_results.append(False)
        return True

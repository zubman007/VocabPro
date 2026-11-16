"""Question-level grammar streaks derived only from recorded S/F outcomes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GrammarQuestionProgress:
    unpractised: int = 0
    last_incorrect: int = 0
    streak_one: int = 0
    streak_two: int = 0
    streak_three_plus: int = 0

    @property
    def counts(self):
        return (self.unpractised, self.last_incorrect, self.streak_one,
                self.streak_two, self.streak_three_plus)

    @property
    def total(self):
        return sum(self.counts)


def grammar_question_progress(frame):
    """Count each question once; unrelated legacy characters are not answers.

    A streak ends at the most recent failure for that individual question.
    This does not infer session order, dates or the all-time session record.
    """
    counts = [0] * 5
    histories = frame['R'].fillna('').astype(str) if 'R' in frame else [''] * len(frame)
    for history in histories:
        practised, streak = False, 0
        for outcome in history:
            if outcome == 'S':
                practised = True
                streak = min(3, streak + 1)
            elif outcome == 'F':
                practised = True
                streak = 0
        bucket = 0 if not practised else 1 if not streak else streak + 1
        counts[bucket] += 1
    return GrammarQuestionProgress(*counts)

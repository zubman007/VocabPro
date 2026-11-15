"""Pure grammar question ordering; persistence lives in app.repositories.grammar."""
from datetime import datetime
from math import log1p, sqrt
import random

# Uniform, unseen, errors/mastery, age, and low attempt counts respectively.
# Each signal is normalised over the eligible questions before mixing.
SELECTION_MIX = (0.30, 0.20, 0.30, 0.10, 0.10)


def _history_signals(question):
    history = ''.join(value for value in str(question.get('repetition') or '').upper()
                      if value in 'SF')
    if not history and 'repetition' not in question:
        # Compatibility for callers providing only the older derived metadata.
        try:
            streak = max(0, int(question.get('count_trailing_s', 0)))
        except (TypeError, ValueError, OverflowError):
            streak = 0
        return streak, 0.0, False, streak
    recent = history[-10:]
    return (len(history), recent.count('F') / len(recent) if recent else 0.0,
            history.endswith('F'), len(history) - len(history.rstrip('S')))


def _age_weight(value, now):
    if not value:
        return 1.0
    try:
        reviewed = datetime.fromisoformat(str(value).strip())
        current = now.replace(tzinfo=None) if reviewed.tzinfo is None else now.astimezone()
        days = max(0.0, min(180.0, (current - reviewed).total_seconds() / 86400))
    except (TypeError, ValueError, OverflowError):
        return 1.0
    return 1.0 + sqrt(days)


def question_weights(questions, *, now=None):
    """Return initial selection probabilities for the already filtered questions.

    Mix uniform coverage, unseen questions, recent errors/mastery, age and low
    attempt counts. Missing age is neutral; an empty unseen pool is uniform.
    Category size contributes naturally through its number of eligible questions.
    """
    if not questions:
        return []
    now = now if now is not None else datetime.now()
    signals = [[] for _ in SELECTION_MIX]
    for question in questions:
        attempts, failures, last_failed, streak = _history_signals(question)
        values = (1.0, float(attempts == 0),
                  (1.0 + 2.0 * failures + 1.5 * last_failed) / sqrt(1 + streak),
                  _age_weight(question.get('last_review'), now), 1.0 / sqrt(1 + attempts))
        for column, value in zip(signals, values):
            column.append(value)
    weights = [0.0] * len(questions)
    for share, values in zip(SELECTION_MIX, signals):
        total = sum(values)
        for index, value in enumerate(values):
            weights[index] += share * (value / total if total else 1.0 / len(questions))
    return weights


def Shuffle_copy(items, questions, *, rng=None, now=None):
    """Keep the legacy entry point; options shuffle uniformly, questions by weight."""
    generator = rng if rng is not None else random
    if questions != 1:
        new_items = list(items)
        generator.shuffle(new_items)
        return new_items
    weights = question_weights(items, now=now)
    # Exponential-race keys produce a weighted permutation in O(n log n),
    # avoiding a full remaining-pool scan for every subsequent question.
    keys = [-log1p(-generator.random()) / weight for weight in weights]
    return [items[index] for index in sorted(range(len(items)), key=keys.__getitem__)]



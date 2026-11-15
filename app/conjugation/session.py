"""Conjugation round state and results, independent of Tk and persistence."""
import random
from app.conjugation.data import answers_match, record_result


class ConjugationSession:
    def __init__(self, selection, verbs, persons):
        self.selection = selection.copy(deep=True)
        self.remaining = list(verbs)
        self.persons = tuple(persons)
        self.current = self.previous = None
        self.revealed = False
        self.completed = 0

    def advance(self, skip=False):
        if skip and self.current in self.remaining:
            self.remaining.remove(self.current)
        self.current = random.choice(self.remaining) if self.remaining else None
        self.revealed = False
        return self.current

    def confirm(self, answers):
        if self.current is None or self.current not in self.remaining:
            return None
        if not answers_match(self.current, answers, self.persons):
            record_result(self.selection, self.current.id, 'F')
            self.revealed = True
            return False
        if not self.revealed:
            record_result(self.selection, self.current.id, 'S')
        self.completed += 1
        self.remaining.remove(self.current)
        self.previous = self.current
        return True

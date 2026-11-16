"""Conjugation round state and results, independent of Tk and persistence."""
import random
from app.conjugation.data import person_results, record_result
from app.conjugation.history import record_person_results


class ConjugationSession:
    def __init__(self, selection, verbs, persons):
        self.selection = selection.copy(deep=True)
        self.persons = tuple(persons)
        self.remaining = [verb for verb in verbs if any(getattr(verb,key,'').strip() for key,_ in self.persons)]
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
        results = person_results(self.current, answers, self.persons)
        if not results:return None
        if not self.revealed:
            record_person_results(self.selection, self.current.id, results)
        if not all(results.values()):
            if not self.revealed:record_result(self.selection, self.current.id, 'F')
            self.revealed = True
            return False
        if not self.revealed:
            record_result(self.selection, self.current.id, 'S')
        self.completed += 1
        self.remaining.remove(self.current)
        self.previous = self.current
        return True

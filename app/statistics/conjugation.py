"""Summaries of whole conjugation rounds; no inferred per-person outcomes."""
from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class VerbProgress:
    identifier: str
    verb: str
    description: str
    successes: int
    failures: int

    @property
    def accuracy(self):
        attempts = self.successes + self.failures
        return self.successes / attempts if attempts else None


def conjugation_progress(frame, language,config=None):
    if frame.empty:
        return dict(practised=0, unpractised=0, covered_forms=0, difficult=[])
    histories = frame['R'].fillna('').astype(str)
    successes, failures = histories.str.count('S'), histories.str.count('F')
    practised = (successes + failures).gt(0)
    keys=(p.id for p in config.active) if config is not None else ('s1','s2','s3','m1','m2','m3')
    forms = [c for c in keys if c in frame]
    populated = frame[forms].fillna('').astype(str).apply(lambda col: col.str.strip().ne(''))
    items = []
    for position in range(len(frame)):
        if practised.iloc[position]:
            row = frame.iloc[position]
            items.append(VerbProgress(str(row.get('ID', '')), str(row.get(language, '')),
                str(row.get('Description', '')), int(successes.iloc[position]), int(failures.iloc[position])))
    difficult = sorted((item for item in items if item.failures),
        key=lambda item: (item.accuracy, -item.failures, item.verb.casefold(), item.identifier))[:10]
    return dict(practised=int(practised.sum()), unpractised=int((~practised).sum()),
        covered_forms=int(populated.loc[practised].sum().sum()), difficult=difficult)


@dataclass(frozen=True)
class PersonStatistics:
    id: str
    label: str
    enabled: bool
    successes: int
    failures: int


def person_statistics(frame,config):
    from app.conjugation.history import HISTORY_COLUMN,decode_history
    totals={person.id:[0,0] for person in config.persons}
    for value in frame.get(HISTORY_COLUMN,[]):
        for key,history in decode_history(value).items():
            counts=totals.setdefault(key,[0,0]);counts[0]+=history.count('S');counts[1]+=history.count('F')
    return tuple(PersonStatistics(p.id,p.label,p.enabled,*totals[p.id]) for p in config.persons)


def progress_table(progress):
    columns = ['Verb', 'Description', 'Recorded answers', 'Incorrect answers', 'Review accuracy']
    return pd.DataFrame([
        [item.verb, item.description, item.successes + item.failures,
         item.failures, round(item.accuracy * 100, 2)] for item in progress['difficult']
    ], columns=columns)

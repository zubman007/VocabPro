"""Validated undirected synonym relations and optimistic CSV persistence."""
from datetime import date
from pathlib import Path
import csv
import pandas as pd
from app.shared.storage import file_revision,save_csv,FileChangedError
from app.vocabulary.synonyms import linked_ids,describe

COLUMNS = ['ID 1','ID 2','Date']


def relation_path(course):
    course = Path(course)
    return course.with_name(course.stem.removesuffix('_voc') + '_synonyms.csv')


def load(course, words):
    path = relation_path(course)
    revision = file_revision(path) if path.exists() else None
    if revision:
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, delimiter=';')
            if reader.fieldnames != COLUMNS:
                raise ValueError('Invalid synonyms columns.')
            frame = pd.DataFrame(list(reader), columns=COLUMNS)
    else:
        frame = pd.DataFrame(columns=COLUMNS)
    if list(frame.columns) != COLUMNS:
        raise ValueError('Invalid synonyms columns.')
    rows, pairs = [], set()
    valid = {int(value) for value in words.ID}
    for first, second, created in frame.itertuples(index=False, name=None):
        first, second = int(first), int(second)
        date.fromisoformat(created)
        if first == second:
            raise ValueError('A word cannot be its own synonym.')
        pair = tuple(sorted((first, second)))
        if pair in pairs:
            raise ValueError('Duplicate synonyms pair.')
        pairs.add(pair)
        # Deleted words must not produce broken links in the interface.
        if set(pair) <= valid:
            rows.append((*pair, created))
    if revision is not None and file_revision(path) != revision:
        raise FileChangedError('Synonyms changed. Reopen the window.')
    return pd.DataFrame(rows, columns=COLUMNS), revision


def replace_links(course, word_id, selected, revision):
    words = pd.read_csv(course, sep=';', dtype=str, keep_default_na=False)
    frame, current = load(course, words)
    if current != revision:
        raise FileChangedError('Synonyms changed. Reopen the window.')
    word_id, selected = int(word_id), {int(value) for value in selected}
    valid = {int(value) for value in words.ID}
    if word_id not in valid or not selected <= valid or word_id in selected:
        raise ValueError('Invalid synonym word ID.')
    old = {tuple(sorted((int(a), int(b)))): created for a,b,created in frame.itertuples(index=False,name=None)}
    frame = frame.loc[~(frame['ID 1'].eq(word_id) | frame['ID 2'].eq(word_id))]
    rows = []
    for target in sorted(selected):
        pair = tuple(sorted((word_id, target)))
        rows.append((*pair, old.get(pair, date.today().isoformat())))
    result = pd.concat([frame, pd.DataFrame(rows, columns=COLUMNS)], ignore_index=True)
    save_csv(result.sort_values(['ID 1', 'ID 2']), relation_path(course), sep=';', index=False, expected_revision=revision, expect_missing=revision is None)


def prune_deleted(course):
    if not relation_path(course).exists():return
    words = pd.read_csv(course,sep=';',dtype=str,keep_default_na=False)
    frame,revision = load(course,words)
    save_csv(frame,relation_path(course),sep=';',index=False,expected_revision=revision, expect_missing=revision is None)


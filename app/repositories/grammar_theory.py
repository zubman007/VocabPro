"""Add empty counterparts for new question categories without touching existing theory."""
import csv
import pandas as pd
from pathlib import Path
from app.grammar.theory_data import category_key
from app.shared.storage import file_revision, save_csv

THEORY_FIELDS = ('category', 'title', 'level', 'description', 'rules', 'examples', 'common_mistakes', 'subtopics')


def question_categories_for_theory(path):
    path=Path(path)
    language=path.stem.removesuffix('_gra_ex').rsplit('_',1)[-1]
    questions=path.with_name(f'{language}_gra.csv')
    if not questions.exists():return set()
    with questions.open(encoding='utf-8-sig',newline='') as stream:
        return {(row.get('category') or row.get('Category') or '').strip()
            for row in csv.DictReader(stream,delimiter=';')}- {''}


def ensure_theory_categories(path, categories):
    categories = list(dict.fromkeys(str(value).strip() for value in categories if str(value).strip()))
    if not categories:
        return 0
    path = Path(path)
    revision = file_revision(path) if path.exists() else None
    frame = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False) if revision is not None else pd.DataFrame(columns=THEORY_FIELDS)
    if 'category' not in frame:
        frame['category'] = ''
    known = set(frame.category.map(category_key))
    rows = []
    for category in categories:
        key = category_key(category)
        if key not in known:
            row = dict.fromkeys(frame.columns, '')
            row['category'] = category
            rows.append(row)
            known.add(key)
    if rows:
        result = pd.concat([frame, pd.DataFrame(rows)], ignore_index=True)
        save_csv(result, path, sep=';', index=False, expected_revision=revision, expect_missing=revision is None)
    return len(rows)


def load_theory(path):
    path = Path(path)
    if not path.exists():
        return {}
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = csv.DictReader(stream, delimiter=';')
        result = {}
        for row in rows:
            row = {str(key).strip().casefold(): (value or '').strip()
                   for key, value in row.items() if key is not None}
            key = category_key(row.get('category'))
            if key and any(row.get(field) for field in ('description', 'rules', 'examples', 'common_mistakes', 'subtopics')):
                result[key] = row
        return result


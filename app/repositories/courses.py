"""Course creation, lightweight counts and removal of unused empty CSVs."""
from pathlib import Path
import csv
import io
import pandas as pd
from app.shared.storage import save_csv


def vocabulary_columns(learned_by, language):
    headers = ['ID', language, 'Phonetic', learned_by, 'Audio', 'Description', 'Example',
               'Part of Speech', 'Tags', 'Created', 'Repetition', 'Next repetition']
    if language == 'Spanish':
        headers.remove('Phonetic')
    return headers


def ensure_course(files_dir, learned_by, language):
    files_dir = Path(files_dir)
    files_dir.mkdir(parents=True,exist_ok=True)
    path = files_dir / f'{learned_by}_{language}_voc.csv'
    if not path.exists():
        save_csv(pd.DataFrame(columns=vocabulary_columns(learned_by, language)), path, index=False, sep=';', expect_missing=True)


def remove_unused_empty_courses(files_dir, learned_by, languages):
    """Remove only unused, header-only vocabulary/synonym CSVs; keep all real data."""
    active = {f'{learned_by}_{language}' for language in languages}
    removed = []
    for path in Path(files_dir).glob('*_*.csv'):
        course, _, kind = path.stem.rpartition('_')
        if kind not in ('voc','synonyms') or course in active:continue
        try:
            revision = path.read_bytes()
            rows = csv.reader(revision.decode('utf-8-sig').splitlines(),delimiter=';')
            header = next(rows,[])
            required = {'ID','Repetition'} if kind=='voc' else {'ID 1','ID 2','Date'}
            if not required <= set(header):continue
            if any(any(cell.strip() for cell in row) for row in rows):continue
            if path.read_bytes()!=revision:continue
            path.unlink()
            removed.append(path.name)
        except (OSError,UnicodeError,csv.Error):
            continue
    return removed


def row_count(path):
    if not path.exists():
        return 0
    # Counts do not need the wide description, example or history columns.
    return len(pd.read_csv(path, sep=';', usecols=[0]))


def backup_files(files_dir):
    """Yield original bytes of nonempty data CSVs; never email settings/API keys."""
    for path in sorted(Path(files_dir).iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file() and path.name.endswith('_con_persons.json') and not path.is_symlink():
            from app.shared.languages import LANGUAGE_CODES
            from app.conjugation.persons import decode_configuration
            language=path.name.removesuffix('_con_persons.json')
            if language in LANGUAGE_CODES:
                data=path.read_bytes()
                decode_configuration(data.decode('utf-8-sig'),language)
                yield path.name,data
            continue
        if not path.is_file() or path.suffix.casefold() != '.csv' or path.name.casefold() == 'settings.csv':
            continue
        data = path.read_bytes()
        rows = csv.reader(io.StringIO(data.decode('utf-8-sig'), newline=''), delimiter=';')
        # Ignore blank lines before the header and fully empty/whitespace-only records.
        next((row for row in rows if any(cell.strip() for cell in row)), None)
        if any(any(cell.strip() for cell in row) for row in rows):
            yield path.name, data

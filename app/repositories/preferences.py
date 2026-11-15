"""Validated preference persistence, preserving concurrent scheduling metadata."""
from pathlib import Path
from datetime import datetime,timedelta
import pandas as pd
from app.preferences.data import PREFERENCES_FILE,validate_preferences,with_defaults
from app.shared.storage import file_revision
from app.repositories.csv_store import commit_document


def load_preferences(path=PREFERENCES_FILE):
    frame = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False)
    if not {"Name", "Type", "Value"}.issubset(frame.columns):
        raise ValueError("Preferences require Name, Type and Value columns")
    if frame["Name"].duplicated().any():
        raise ValueError("Duplicate preference names")
    if frame['Name'].str.strip().eq('').any():
        raise ValueError('Preference names must not be empty')
    return frame


def save_preferences(frame, values, path=PREFERENCES_FILE):
    path = Path(path)
    revision=file_revision(path) if path.exists() else None
    if path.exists():
        latest = load_preferences(path)
        if not latest.equals(frame):
            # Background backup may have changed only the scheduling metadata.
            metadata = ['Next backup','Saved grammar category filters']
            stable = lambda data: data.loc[~data.Name.isin(metadata)].reset_index(drop=True)
            if not stable(latest).equals(stable(frame)):
                raise ValueError('Settings changed on disk. Reopen settings before saving.')
            before = dict(zip(frame.Name, frame.Value)).get('Next backup', '')
            values = dict(values)
            if values.get('Next backup', before) == before:
                values['Next backup'] = dict(zip(latest.Name, latest.Value)).get('Next backup', '')
            frame = latest
    updated = validate_preferences(with_defaults(frame), values)
    maximum=int(dict(zip(updated.Name,updated.Value)).get('Maximum tags per word','10'))
    from app.vocabulary.tags_data import normalize_tags
    from app.preferences.data import PreferenceError
    if 'Maximum tags per word' in values:
        for course in path.parent.glob('*_voc.csv'):
            words=pd.read_csv(course,sep=';',dtype=str,keep_default_na=False)
            if any(len(normalize_tags(value).split(', '))>maximum for value in words.get('Tags',[]) if normalize_tags(value)):
                raise PreferenceError('Maximum tags per word','Existing words exceed this tag limit.')
    commit_document(path,updated,revision)
    return updated


def record_success(path, recipient, period, expected_next, now=None):
    """Only update scheduling metadata if its configuration is still current."""
    revision = file_revision(path)
    frame = load_preferences(path)
    values = dict(zip(frame.Name, frame.Value))
    if (values.get('Backup mail', '').strip() != recipient
            or int(values.get('Backup period (days)', 0)) != period
            or values.get('Next backup', '').strip()[:19] != expected_next):
        return None
    next_date = ((now or datetime.now())+timedelta(days=period)).replace(microsecond=0).isoformat(sep=' ')
    if 'Next backup' not in values:
        row = dict.fromkeys(frame.columns, '')
        row.update(Name='Next backup', Type='Str', Value=next_date)
        frame = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
    else:
        frame.loc[frame.Name.eq('Next backup'), 'Value'] = next_date
    commit_document(path,frame,revision)
    return next_date

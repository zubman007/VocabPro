"""Consistent CSV reads and revision-checked document transactions."""
from pathlib import Path
import pandas as pd
from app.shared.storage import file_revision,save_csv,FileChangedError


def read_csv(path, **options):
    options = {'sep': ';', 'dtype': str, 'keep_default_na': False, **options}
    return pd.read_csv(path, **options)


def read_document(path, *, optional=False, columns=None,
                  message='The file changed while it was being read.'):
    path = Path(path)
    revision = file_revision(path) if not optional or path.exists() else None
    frame = read_csv(path) if revision is not None else pd.DataFrame(columns=columns)
    if revision is not None and file_revision(path) != revision:
        raise FileChangedError(message)
    return frame, revision


def commit_document(path, frame, revision, *,
                    message='The file changed. Reopen it before saving.'):
    path = Path(path)
    if revision is None and path.exists():
        raise FileChangedError(message)
    save_csv(frame, path, sep=';', index=False, expected_revision=revision,
             expect_missing=revision is None)
    return file_revision(path)


def apply_delta(current, original, edited, columns, *, id_column='ID'):
    """Three-way field merge, preserving row order and rejecting the whole conflict."""
    frames = [frame.copy() for frame in (current, original, edited)]
    for frame in frames:
        frame[id_column] = frame[id_column].astype(str)
        if frame[id_column].eq('').any() or frame[id_column].duplicated().any():
            raise ValueError('Practice requires unique word IDs')
    result, before, changes = [frame.set_index(id_column, drop=False) for frame in frames]
    def value_of(value, column):
        if pd.isna(value):
            return ''
        if column in ('LR','Next repetition') and str(value):
            try:
                return str(pd.Timestamp(value))
            except (ValueError, TypeError):
                pass
        return str(value)

    for identifier, row in changes.iterrows():
        if identifier not in before.index or identifier not in result.index:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
        for column in columns:
            old = value_of(before.at[identifier, column], column)
            new = value_of(row[column], column)
            if old == new:
                continue
            if value_of(result.at[identifier, column], column) != old:
                raise FileChangedError('The course file changed. Reopen the editor before saving.')
            result.at[identifier, column] = new
    return result.reset_index(drop=True)

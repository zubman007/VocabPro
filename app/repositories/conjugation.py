"""Conjugation source validation and result persistence."""
import pandas as pd
from app.shared.storage import save_csv, file_revision
from app.repositories.csv_store import apply_delta
from app.shared.messages import UserMessageError


def load_source(path,language,learned_by):
    source=pd.read_csv(path,delimiter=';').fillna('')
    required={'ID','R','LR','s1','s2','s3','m1','m2','m3','Description',learned_by,language}
    missing=required.difference(source.columns)
    if missing:raise UserMessageError('Missing required CSV columns: {columns}', columns=', '.join(sorted(missing)))
    if source.ID.isna().any() or source.ID.eq('').any() or source.ID.duplicated().any():
        raise ValueError('Practice requires unique word IDs')
    return source


def save_results(all_df, selection, path):
    revision = file_revision(path)
    latest = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    updated = apply_delta(latest, all_df, selection, ('R', 'LR'))
    save_csv(updated, path, sep=";", index=False, expected_revision=revision)
    updated['ID'] = updated.ID.astype(all_df.ID.dtype)
    return updated

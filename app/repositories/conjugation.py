"""Conjugation source validation and result persistence."""
import pandas as pd
from app.shared.storage import save_csv, file_revision, FileChangedError
from app.repositories.csv_store import apply_delta
from app.shared.messages import UserMessageError
from app.conjugation.history import HISTORY_COLUMN, decode_history
from app.conjugation.persons import LEGACY_IDS
from app.repositories.csv_store import read_document, commit_document
from app.shared.atomic_bytes import save_bytes
from pathlib import Path
from uuid import uuid4


def conjugation_columns(language, learned_by, config):
    return ['ID', language, learned_by, 'Description', *(p.id for p in config.persons), 'R', 'LR', HISTORY_COLUMN]


def load_source(path,language,learned_by,config=None):
    source,revision=read_document(path)
    source_columns=tuple(source.columns)
    required={'ID','R','LR','Description',learned_by,language}
    if config is None:required.update(LEGACY_IDS)
    missing=required.difference(source.columns)
    if missing:raise UserMessageError('Missing required CSV columns: {columns}', columns=', '.join(sorted(missing)))
    if source.ID.isna().any() or source.ID.eq('').any() or source.ID.duplicated().any():
        raise ValueError('Practice requires unique word IDs')
    if config is not None:
        for person in config.persons:
            if person.id not in source:source[person.id]=''
    for value in source.get(HISTORY_COLUMN, []):decode_history(value)
    source.attrs['revision']=revision
    source.attrs['source_columns']=source_columns
    return source


def backup_legacy(path, original=None,*,suffix='.pre-persons.bak'):
    path=Path(path)
    backup=path.with_name(path.name+suffix)
    if backup.exists():return
    try:save_bytes(backup,path.read_bytes() if original is None else original,expect_missing=True)
    except FileChangedError:
        if not backup.exists():raise


class ConjugationDocument:
    """Editable forms only; opaque legacy histories and unknown columns survive."""
    def __init__(self,path,language,learned_by,config):
        self.path=Path(path)
        self.language,self.learned_by,self.config=language,learned_by,config
        self.frame=load_source(path,language,learned_by,config)
        self.revision=self.frame.attrs['revision']
        self.source_columns=self.frame.attrs['source_columns']
        self.fields=(language,learned_by,'Description',*(p.id for p in config.active))
        self.initial=self.frame.copy(deep=True)

    def verb(self,identifier):
        rows=self.frame.loc[self.frame.ID.eq(str(identifier))]
        if rows.empty:raise UserMessageError('Verb not found.')
        return rows.iloc[0].to_dict()

    def add(self):
        identifier=uuid4().hex
        while self.frame.ID.eq(identifier).any():identifier=uuid4().hex
        row=dict.fromkeys(self.frame.columns,'');row['ID']=identifier
        self.frame=pd.concat([self.frame,pd.DataFrame([row])],ignore_index=True)
        return identifier

    def update(self,identifier,values):
        original=self.verb(identifier)
        if not str(values.get(self.language,original[self.language])).strip():
            raise UserMessageError('Enter the verb in the learning language.')
        for key in self.fields:
            value=str(values.get(key,original.get(key,'')))
            # Preserve untouched legacy text, including its whitespace.
            if value!=original.get(key,''):value=value.strip()
            self.frame.loc[self.frame.ID.eq(str(identifier)),key]=value

    def delete(self,identifier):
        self.frame=self.frame.loc[self.frame.ID.ne(str(identifier))].reset_index(drop=True)

    def save(self):
        if self.frame[self.language].str.strip().eq('').any():
            raise UserMessageError('Enter the verb in the learning language.')
        if self.frame.ID.eq('').any() or self.frame.ID.duplicated().any():
            raise UserMessageError('Practice requires unique word IDs')
        if self.frame.equals(self.initial) and not (set(self.frame.columns)-set(self.source_columns)):return
        if not self.path.exists() or file_revision(self.path)!=self.revision:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
        for value in self.frame.get(HISTORY_COLUMN,[]):decode_history(value)
        if HISTORY_COLUMN not in self.frame:
            self.frame[HISTORY_COLUMN]=''
        if set(self.frame.columns)-set(self.source_columns):
            backup_legacy(self.path)
        self.revision=commit_document(self.path,self.frame,self.revision)
        self.initial=self.frame.copy(deep=True)
        self.source_columns=tuple(self.frame.columns)


def save_results(all_df, selection, path):
    revision = file_revision(path)
    latest = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    if file_revision(path)!=revision:
        raise FileChangedError('The course file changed. Reopen the editor before saving.')
    original=all_df.copy(deep=True)
    selected=selection.copy(deep=True)
    columns=['R','LR']
    if HISTORY_COLUMN in selected:
        for frame in (original,latest):
            if HISTORY_COLUMN not in frame:frame[HISTORY_COLUMN]=''
        for value in selected[HISTORY_COLUMN]:decode_history(value)
        columns.append(HISTORY_COLUMN)
    updated = apply_delta(latest, original, selected, columns)
    # A result belongs to the forms actually shown. Unrelated edits can merge,
    # but changing a practised form or deleting its row must reject the save.
    person_ids=all_df.attrs.get('person_ids',())
    before=original.assign(ID=original.ID.astype(str)).set_index('ID')
    current=latest.assign(ID=latest.ID.astype(str)).set_index('ID')
    for row in selected.to_dict('records'):
        identifier=str(row['ID'])
        if identifier not in before.index or identifier not in current.index:continue
        changed=any(str(row[column])!=str(before.at[identifier,column])
                    for column in columns if column!='LR')
        if changed:
            for key in person_ids:
                old=str(before.at[identifier,key]) if key in before else ''
                new=str(current.at[identifier,key]) if key in current else ''
                if old!=new:raise FileChangedError('The course file changed. Reopen the editor before saving.')
    # Skipping a lesson or retrying an already-saved snapshot does no disk work.
    schema_changed=HISTORY_COLUMN in selected and HISTORY_COLUMN not in all_df
    if schema_changed or not updated.equals(latest):
        if schema_changed:backup_legacy(path)
        save_csv(updated, path, sep=";", index=False, expected_revision=revision)
    updated['ID'] = updated.ID.astype(all_df.ID.dtype)
    updated.attrs=all_df.attrs.copy()
    return updated

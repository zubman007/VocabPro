"""Per-course tag catalog with stable IDs and revision-checked atomic saves."""
import csv
from pathlib import Path
from unicodedata import normalize

import pandas as pd

from app.shared.storage import FileChangedError, file_revision, save_csv, destination_lock


class TagValidationError(ValueError):
    def __init__(self, message, row):
        self.message, self.row = message, row
        super().__init__(message)


def catalog_columns(learned_by, language):
    return ['ID', learned_by, language, 'Note']


def validate_catalog(frame, learned_by, language):
    """Validate without mutating input; translations and notes may remain empty."""
    required = catalog_columns(learned_by, language)
    if not frame.columns.is_unique or not set(required) <= set(frame.columns):
        raise ValueError('Invalid tag catalog columns.')
    result = frame.fillna('').astype(str).reset_index(drop=True)
    identifiers, names = set(), set()
    for position, index in enumerate(result.index, 1):
        identifier = result.at[index, 'ID'].strip()
        if not identifier.isdecimal() or int(identifier) < 1 or int(identifier) in identifiers:
            raise TagValidationError('Invalid or duplicate tag ID on row {row}.', position)
        identifiers.add(int(identifier))
        result.at[index, 'ID'] = identifier
        for column in (learned_by, language):
            value = normalize('NFC', result.at[index, column].strip())
            if ',' in value or '\n' in value or '\r' in value:
                raise TagValidationError('Tag names cannot contain commas or line breaks (row {row}).', position)
            result.at[index, column] = value
        name = result.at[index, learned_by].casefold()
        if not name or name in names:
            raise TagValidationError('Missing or duplicate tag name on row {row}.', position)
        names.add(name)
    return result


def load_catalog(path, learned_by, language):
    """Opening an absent catalog does not create an unused empty CSV."""
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=catalog_columns(learned_by, language)), None
    revision = file_revision(path)
    try:
        with path.open(encoding='utf-8-sig', newline='') as stream:
            records = list(csv.reader(stream, delimiter=';', strict=True))
    except csv.Error as error:
        raise ValueError('Invalid tag catalog columns.') from error
    if not records or len(records[0]) != len(set(records[0])):
        raise ValueError('Invalid tag catalog columns.')
    header, *rows = records
    rows = [row for row in rows if row]
    if any(len(row) != len(header) for row in rows):
        raise ValueError('Invalid tag catalog columns.')
    result = validate_catalog(pd.DataFrame(rows, columns=header), learned_by, language)
    if file_revision(path) != revision:
        raise FileChangedError('The tag catalog changed. Reopen it before saving.')
    return result, revision


def _save_catalog(path, frame, learned_by, language, revision):
    result = validate_catalog(frame, learned_by, language)
    path=Path(path)
    if path.exists():
        original,_=load_catalog(path,learned_by,language)
        deleted=set(original.ID)-set(result.ID)
        course=path.with_name(path.stem.removesuffix('_tags')+'_voc.csv')
        if deleted and course.exists():
            words=pd.read_csv(course,sep=';',dtype=str,keep_default_na=False)
            names={str(row.ID):str(getattr(row,learned_by)) for row in original.itertuples(index=False)}
            from app.vocabulary.tags_data import normalize_tags
            for value in words.get('Tags',[]):
                assigned={tag.casefold() for tag in normalize_tags(value).split(', ')}
                if any(identifier in assigned or names[identifier].casefold() in assigned for identifier in deleted):
                    raise ValueError('Cannot delete a tag assigned to words.')
    try:
        save_csv(result, path, sep=';', index=False, expected_revision=revision,
                 expect_missing=revision is None)
    except FileChangedError as error:
        raise FileChangedError('The tag catalog changed. Reopen it before saving.') from error
    return result


def save_catalog(path,frame,learned_by,language,revision):
    path=Path(path)
    course=path.with_name(path.stem.removesuffix('_tags')+'_voc.csv')
    with destination_lock(course),destination_lock(path):
        return _save_catalog(path,frame,learned_by,language,revision)


def decode_tags(frame, path, learned_by, language, *, target=False):
    """Resolve persistent IDs at presentation boundaries; legacy names remain readable."""
    catalog,_=load_catalog(path,learned_by,language)
    if 'Tags' not in frame:return frame
    from app.vocabulary.tags_data import normalize_tags
    column=language if target else learned_by
    labels={row['ID']:(row[column] or row[learned_by]) for _,row in catalog.iterrows()}
    result=frame.copy()
    result['Tags']=result.Tags.map(lambda value:', '.join(labels.get(tag,tag) for tag in normalize_tags(value).split(', ') if tag))
    return result


def encode_tags(frame, catalog, learned_by, language, maximum=10, *, clean=False):
    """Accept names in either catalog language, persist only stable IDs."""
    from app.vocabulary.tags_data import normalize_tags, UnknownTagError
    result=frame.copy()
    if 'Tags' not in result:return result
    lookup={}
    for _,row in catalog.iterrows():
        for value in (row['ID'],row[learned_by],row[language]):
            if value:lookup.setdefault(value.casefold(),set()).add(row['ID'])
    values=[]
    for identifier,value in result[['ID','Tags']].itertuples(index=False,name=None):
        ids=[]
        for tag in normalize_tags(value).split(', '):
            if not tag:continue
            matches=lookup.get(tag.casefold(),set())
            if len(matches)!=1:
                if clean:continue
                raise UnknownTagError(tag,identifier)
            resolved=next(iter(matches))
            if resolved not in ids:ids.append(resolved)
        if len(ids)>maximum:raise ValueError('Maximum number of tags exceeded.')
        values.append(', '.join(ids))
    result['Tags']=values
    return result

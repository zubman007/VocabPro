"""Vocabulary editor loading, filtering, ID merges and save preparation."""
from datetime import datetime
from unicodedata import normalize
from app.vocabulary.tags_data import normalize_tags
import pandas as pd
from app.vocabulary.synonyms import COLUMNS as SYNONYM_COLUMNS
from app.shared.learning_data import Set_datatypes


def merge_table_edits(source, rows, headers, language, learned_by):
    """Merge by persistent ID, keeping rows hidden by the active filter."""
    edited=pd.DataFrame(rows,columns=headers)
    if edited.empty:
        return source.copy(), edited
    ids=pd.to_numeric(edited["ID"],errors="coerce")
    if ids.isna().any() or ids.duplicated().any() or (ids % 1 != 0).any():
        raise ValueError("Invalid or duplicate IDs in table")
    if source["ID"].duplicated().any():
        raise ValueError("Duplicate IDs in main DataFrame")
    Set_datatypes(edited,language,learned_by)
    if 'Tags' in edited:
        edited['Tags'] = edited['Tags'].map(normalize_tags)
    updated=source.set_index("ID").copy()
    indexed=edited.set_index("ID")
    new_ids=indexed.index.difference(updated.index)
    if len(new_ids):
        updated=pd.concat([updated,indexed.loc[new_ids]])
    updated.loc[indexed.index,indexed.columns]=indexed
    return updated.reset_index()[headers], edited


def filter_vocabulary(frame,column,operator,query):
    if operator in ('less','greater'):
        numeric=pd.to_numeric(frame[column],errors='coerce')
        number=float(query)
        return frame.loc[numeric.lt(number) if operator=='less' else numeric.gt(number)].copy().reset_index(drop=True)
    values=frame[column].astype(str).str.casefold()
    query=query.strip().casefold()
    if operator == "equals":
        mask=values == query
        if column == 'Tags' and query:
            tag_query = normalize('NFC', query)
            mask |= frame[column].map(lambda value: tag_query in normalize_tags(value).casefold().split(', '))
    else:
        mask=values.str.contains(query,regex=False,na=False)
        if operator == "excludes":
            mask=~mask
    return frame.loc[mask].copy().reset_index(drop=True)


def sort_vocabulary(frame,column,descending=False):
    """Sort display rows stably, with missing/invalid values at the end."""
    def key(values):
        if column in ('ID','Synonym count','Tag count'):
            return pd.to_numeric(values,errors='coerce')
        if column in ('Created','Next repetition'):
            return pd.to_datetime(values,format='ISO8601',errors='coerce',utc=True)
        if column=='Has synonyms':return values.eq('●').astype(int)
        return values.fillna('').astype(str).str.casefold()
    return frame.sort_values(column,key=key,ascending=not descending,kind='stable',na_position='last').reset_index(drop=True)


def prepare_save(edited, previous, now=None):
    """Preserve learning history and creation dates while saving edited text."""
    edited = edited.drop(columns=['Enabled','Tag count',*SYNONYM_COLUMNS], errors='ignore')
    if 'Tags' in edited:
        edited['Tags'] = edited['Tags'].map(normalize_tags)
    previous = previous.drop(columns=['Enabled','Tag count',*SYNONYM_COLUMNS], errors='ignore')
    metadata=["ID","Created","Repetition","Next repetition"]
    result=edited.drop(columns=["Next repetition","Repetition","Created"], errors='ignore').merge(
        previous[metadata],on="ID",how="left",validate="one_to_one")
    now=now or datetime.now().replace(microsecond=0)
    result["Created"]=result["Created"].fillna(now.strftime("%Y-%m-%d"))
    result["Repetition"]=result["Repetition"].fillna("")
    result["Next repetition"]=result["Next repetition"].fillna(now.strftime("%Y-%m-%d %H:%M:%S"))
    extra = [column for column in previous.columns if column not in result.columns]
    if extra:
        result = result.merge(previous[['ID', *extra]], on='ID', how='left', validate='one_to_one')
        result[extra] = result[extra].fillna('')
    for column in edited.columns:
        result[column] = result[column].replace(r'\s*;\s*', ' / ', regex=True)
    columns = list(previous.columns) + [column for column in result.columns if column not in previous.columns]
    return result[columns]

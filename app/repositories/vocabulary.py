"""Vocabulary loading and save transactions, including history and audio cleanup."""

import pandas as pd
from pathlib import Path
from app.shared.learning_data import Set_datatypes
from app.shared.storage import file_revision, save_csv, FileChangedError


def read_words(path):
    """Raw course values for practice and synonym lookup; preserve literal strings."""
    frame=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
    path=Path(path)
    catalog=path.with_name(path.stem.removesuffix('_voc')+'_tags.csv')
    if catalog.exists() and 'Tags' in frame:
        from app.repositories.tags import decode_tags
        learned_by,language=path.stem.removesuffix('_voc').split('_',1)
        frame=decode_tags(frame,catalog,learned_by,language)
    return frame


def load_vocabulary(path, language, learned_by):
    frame=read_words(path).drop(columns=["Created", "Enabled"],errors='ignore')
    if 'Tags' not in frame:
        frame['Tags'] = ''
    frame["Next repetition"]=pd.to_datetime(frame["Next repetition"],format='ISO8601',errors='coerce').dt.strftime("%Y-%m-%d %H:%M:%S").fillna('')
    Set_datatypes(frame,language,learned_by)
    return frame


def load_editor_snapshot(path,language,learned_by):
    revision=file_revision(path)
    frame=load_vocabulary(path,language,learned_by)
    if file_revision(path)!=revision:
        raise FileChangedError('The course file changed. Reopen the editor before saving.')
    return frame,revision


def save_practice(path, remaining, completed, headers, *, original=None, maximum_tags=10):
    """Save session fields by ID while preserving all unrelated vocabulary fields."""
    all_words=pd.concat([completed,remaining],ignore_index=True).copy()
    revision = file_revision(path) if Path(path).exists() else None
    previous=pd.read_csv(path,sep=";",dtype=str,keep_default_na=False)
    previous = previous.drop(columns=['Enabled'], errors='ignore')
    if original is not None:
        from app.repositories.csv_store import apply_delta
        fields=['Repetition','Next repetition','Audio','Description','Example']
        catalog_path=Path(path).with_name(Path(path).stem.removesuffix('_voc')+'_tags.csv')
        if catalog_path.exists() and 'Tags' in all_words and 'Tags' in original:
            from app.repositories.tags import load_catalog,encode_tags
            learned_by,language=Path(path).stem.removesuffix('_voc').split('_',1)
            catalog,_=load_catalog(catalog_path,learned_by,language)
            all_words=encode_tags(all_words,catalog,learned_by,language,maximum_tags)
            original=encode_tags(original,catalog,learned_by,language,100000)
            fields.append('Tags')
        merged = apply_delta(previous, original, all_words,
            fields)
        save_csv(merged,path,sep=';',index=False,expected_revision=revision)
        return
    previous['ID']=previous['ID'].astype(int)
    previous["Next repetition"]=pd.to_datetime(previous["Next repetition"])
    all_words["Next repetition"]=pd.to_datetime(all_words["Next repetition"])
    merged=previous.merge(all_words,on="ID",how="left",suffixes=("","_2"),validate="one_to_one")
    for column in ("Repetition","Next repetition","Audio","Description","Example"):
        merged[column]=merged[column+"_2"].combine_first(merged[column])
    save_csv(merged[list(previous.columns)],path,sep=";",index=False,expected_revision=revision)



def save_course(*args, **kwargs):
    """Compatibility entry point; orchestration belongs to the vocabulary workflow."""
    from app.vocabulary.save_workflow import save_course as save
    return save(*args, **kwargs)

"""Read-only lessons ordered by scheduled review; unlearned words remain unlearned."""
import pandas as pd
from app.repositories.tags import load_catalog,encode_tags,decode_tags


def tag_lesson(course,catalog_path,learned_by,language,tag_id):
    frame=pd.read_csv(course,sep=';',dtype=str,keep_default_na=False)
    catalog,_=load_catalog(catalog_path,learned_by,language)
    if str(tag_id) not in set(catalog.ID):return frame.iloc[:0].copy()
    encoded=encode_tags(frame,catalog,learned_by,language,maximum=100000)
    selected=encoded.Tags.map(lambda value:str(tag_id) in value.split(', '))
    result=frame.loc[selected].copy()
    dates=pd.to_datetime(result['Next repetition'],format='ISO8601',errors='coerce',utc=True)
    result=result.assign(_date=dates).sort_values('_date',kind='stable',na_position='first').drop(columns='_date')
    result=decode_tags(result,catalog_path,learned_by,language)
    result.attrs['ordered_lesson']=True
    return result

"""Remember category subsets per learning-language pair, separately from questions."""
import json
from app.shared.diagnostics import report_error
from pathlib import Path
import pandas as pd
from app.grammar.theory_data import category_key
from app.shared.storage import file_revision, save_csv

FILTER_SETTING = 'Saved grammar category filters'


def _read(path):
    if not Path(path).exists():return pd.DataFrame(columns=['Name','Type','Value'])
    frame = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    if not {'Name','Type','Value'}.issubset(frame.columns) or frame.Name.duplicated().any():
        raise ValueError('Invalid saved category filters.')
    return frame


def _filters(frame):
    row=frame.loc[frame.Name.eq(FILTER_SETTING)]
    result=json.loads(row.iloc[0].Value) if len(row) else {}
    if not isinstance(result,dict) or any(not isinstance(courses,dict) or any(
            not isinstance(values,list) or not all(isinstance(value,str) for value in values)
            for values in courses.values()) for courses in result.values()):
        raise ValueError('Invalid saved category filters.')
    return result


def load_filter(path, learned_by, language, available):
    try:
        frame = _read(path)
        selected = _filters(frame).get(learned_by,{}).get(language,[])
        if not isinstance(selected, list) or not all(isinstance(value, str) for value in selected):
            return None
        valid = {category_key(value) for value in selected} & set(available)
        return valid or None
    except (OSError, ValueError) as error:
        report_error(error, operation='saved grammar filter')
        return None


def save_filter(path, learned_by, language, selected, available):
    path = Path(path)
    revision = file_revision(path) if path.exists() else None
    frame = _read(path)
    filters = _filters(frame)
    before = json.dumps(filters,ensure_ascii=False,sort_keys=True)
    selected = {category_key(value) for value in selected} & set(available)
    if not selected:
        raise ValueError('Select at least one category.')
    if selected == set(available):
        # No stored restriction means that newly added categories are included too.
        filters.get(learned_by,{}).pop(language,None)
        if learned_by in filters and not filters[learned_by]:filters.pop(learned_by)
    else:
        filters.setdefault(learned_by,{})[language]=sorted(selected)
    encoded=json.dumps(filters,ensure_ascii=False,sort_keys=True)
    if encoded==before:return
    mask=frame.Name.eq(FILTER_SETTING)
    if mask.any():frame.loc[mask,'Value']=encoded
    else:
        row = dict.fromkeys(frame.columns, '')
        row.update(Name=FILTER_SETTING,Type='JSON',Value=encoded)
        frame = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
    save_csv(frame, path, sep=';', index=False, expected_revision=revision, expect_missing=revision is None)

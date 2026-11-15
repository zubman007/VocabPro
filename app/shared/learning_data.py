"""DataFrame normalization and repetition helpers, independent of the GUI."""
import pandas as pd

def Count_trailing_s(value):
    if pd.isna(value): return 0
    text = str(value).strip()
    if text == "": return 0
    return len(text) - len(text.rstrip('S'))

def Set_datatypes(df, lang_desc, learned_by):
    cols_to_str = ["Audio", "Description", "Example", learned_by, lang_desc]
    df["ID"] = df["ID"].astype(int)
    if lang_desc != "Spanish" and "Phonetic" in df.columns: cols_to_str.append("Phonetic")
    for col in cols_to_str: df[col] = df[col].astype(str)


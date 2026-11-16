"""Verb model, language persons, batch selection and result persistence."""
from datetime import datetime
import pandas as pd
from app.shared.learning_data import Count_trailing_s

class Verb:
    def __init__(self, id, s1='', s2='', s3='', m1='', m2='', m3='', desc='', base_lng='', targ_lng='', *, forms=None):
        self.id = id
        self.forms = dict(forms) if forms is not None else dict(zip(('s1','s2','s3','m1','m2','m3'), (s1,s2,s3,m1,m2,m3)))
        self.desc = desc
        self.base_lng = base_lng
        self.targ_lng = targ_lng
    def __getattr__(self, key):
        if key in self.__dict__.get('forms', {}):return self.forms[key]
        raise AttributeError(key)

    def copy(self, next_obj):
        self.__dict__.update(next_obj.__dict__)
        self.forms = dict(next_obj.forms)

PERSONS_MAP = {
    "Spanish": [("s1","Yo"),("s2","Tú"),("s3","Él/Ella"),("m1","Nosotros"),("m2","Vosotros"),("m3","Ellos/Ellas")],
    "English": [("s1","I"),("s2","You"),("s3","He/She/It"),("m1","We"),("m2","You"),("m3","They")],
    "French":  [("s1","Je"),("s2","Tu"),("s3","Il/Elle"),("m1","Nous"),("m2","Vous"),("m3","Ils/Elles")],
    "German":  [("s1","Ich"),("s2","Du"),("s3","Er/Sie/Es"),("m1","Wir"),("m2","Ihr"),("m3","Sie")],
    "Slovak":  [("s1","Ja"),("s2","Ty"),("s3","On/Ona/Ono"),("m1","My"),("m2","Vy"),("m3","Oni/Ony")],
    "Czech":   [("s1","Já"),("s2","Ty"),("s3","On/Ona/Ono"),("m1","My"),("m2","Vy"),("m3","Oni/Ony")],}

def select_verbs(all_df, sample_size):
    # Shuffle/sort only priorities, then copy the selected full rows once.
    priority = pd.DataFrame({
        'LR': pd.to_datetime(all_df['LR'], errors='coerce').to_numpy(),
        'trailing_s': all_df['R'].map(Count_trailing_s).to_numpy(),
    })
    positions = (priority.sample(frac=1)
        .sort_values(['trailing_s', 'LR'], ascending=[True, True], na_position='first')
        .head(sample_size).index)
    selection = all_df.iloc[positions].copy()
    selection['LR'] = priority.loc[positions, 'LR'].to_numpy()
    return selection

def build_verbs(df, lang, learned_by, persons=None):
    from app.conjugation.persons import LEGACY_IDS
    keys = [key for key, _ in persons] if persons is not None else LEGACY_IDS
    return [Verb(row['ID'], desc=row.get('Description',''), base_lng=row.get(learned_by,''),
                 targ_lng=row.get(lang,''), forms={key:row.get(key,'') for key in keys})
            for row in df.to_dict('records')]


def eligible_verbs(frame, persons):
    keys = [key for key, _ in persons if key in frame]
    if not keys:return frame.iloc[:0].copy()
    return frame.loc[frame[keys].fillna('').astype(str).apply(lambda col: col.str.strip().ne('')).any(axis=1)].copy()

def record_result(sel, verb_id, result_char):
    mask = sel["ID"] == verb_id
    sel.loc[mask, "R"] = sel.loc[mask, "R"].astype(str) + result_char
    sel.loc[mask, "LR"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def answers_match(verb, answers, persons):
    """Preserve existing matching rules: case and Spanish/Czech n variants."""
    return all(person_results(verb, answers, persons).values())


def person_results(verb, answers, persons):
    results = {}
    for key, _ in persons:
        expected = getattr(verb, key, '').strip()
        if expected:
            correct = expected.lower().replace('ñ', 'n')
            answer = answers.get(key, '').strip().lower().replace('ñ', 'n').replace('ň', 'n')
            results[key] = answer == correct
    return results



"""Home-page course selection without widgets or application globals."""
from datetime import datetime
from pathlib import Path
import pandas as pd
from app.shared.learning_data import Set_datatypes
from app.repositories.vocabulary import read_words
from app.repositories.courses import row_count


def course_overview(files_dir, learned_by, language, learn_batch, repeat_batch, now=None):
    files_dir = Path(files_dir)
    result = dict(rep_words=pd.DataFrame(), lrn_words=pd.DataFrame(), rep_count=0,
                  lrn_count=0, all_count=0, con_count=0, gra_count=0)
    path = files_dir / f'{learned_by}_{language}_voc.csv'
    if not path.exists():
        return result
    data = read_words(path).drop(columns=['Enabled'],errors='ignore')
    Set_datatypes(data, language, learned_by)
    data['Next repetition'] = pd.to_datetime(data['Next repetition'], format='ISO8601', errors='coerce')
    success_count = data['Repetition'].astype(str).str.count('S')
    due = data['Next repetition'].lt(now or datetime.now())
    repeat = data.loc[due & success_count.gt(4)].copy()
    learn = data.loc[due & success_count.le(4)].copy()
    result.update(all_count=len(data), rep_count=len(repeat), lrn_count=len(learn))
    if len(learn) > learn_batch:
        learn = learn.sample(n=learn_batch)
    if repeat.empty:
        repeat = data.loc[success_count.ge(4)].nsmallest(repeat_batch, 'Next repetition').copy()
    result.update(rep_words=repeat, lrn_words=learn,
        con_count=row_count(files_dir / f'{learned_by}_{language}_con.csv'),
        gra_count=row_count(files_dir / f'{language}_gra.csv'))
    return result

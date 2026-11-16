"""Per-language session record, independent of per-question answer histories."""
from contextlib import contextmanager
from pathlib import Path
import pandas as pd
from app.shared.storage import destination_lock, file_revision, save_csv, FileChangedError

COLUMNS = ('best_streak',)


def record_path(course):
    return Path(course).with_name(Path(course).stem+'_records.csv')


def load_record(course):
    path=record_path(course)
    if not path.exists():return 0
    frame=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
    if list(frame.columns)!=list(COLUMNS) or len(frame)>1:
        raise ValueError('Invalid grammar record file.')
    if frame.empty:return 0
    value=frame.best_streak.iloc[0]
    if not value.isascii() or not value.isdigit():raise ValueError('Invalid grammar record file.')
    return int(value)


@contextmanager
def update_record(course, candidate):
    """Roll the record back if saving the corresponding answers fails."""
    path=record_path(course)
    with destination_lock(path):
        existed=path.exists()
        revision=file_revision(path) if existed else None
        previous=load_record(course)
        changed=candidate>previous
        if changed:
            save_csv(pd.DataFrame({'best_streak':[candidate]}),path,sep=';',index=False,
                     expected_revision=revision,expect_missing=not existed)
            written_revision=file_revision(path)
        try:yield
        except Exception:
            if changed:
                if file_revision(path)!=written_revision:
                    raise FileChangedError('Invalid grammar record file.')
                if existed:
                    save_csv(pd.DataFrame({'best_streak':[previous]}),path,sep=';',index=False,
                             expected_revision=written_revision)
                else:path.unlink(missing_ok=True)
            raise

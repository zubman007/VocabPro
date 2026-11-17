"""Small, module/course-local records committed alongside answer saves."""
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
import pandas as pd
from app.shared.storage import destination_lock, file_revision, save_csv, FileChangedError
from app.shared.atomic_bytes import save_bytes
from app.shared.messages import UserMessageError


@dataclass(frozen=True)
class PracticeRecords:
    best_streak: int = 0
    best_correct: int | None = None


def record_path(course):
    course=Path(course)
    return course.with_name(course.stem+'_records.csv')


def load_records(course):
    path=record_path(course)
    if not path.exists():return PracticeRecords()
    frame=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
    if list(frame.columns) not in (['best_streak'],['best_streak','best_correct']) or len(frame)>1:
        raise UserMessageError('Invalid practice record file.')
    if frame.empty:return PracticeRecords()
    values={}
    for key in frame:
        value=frame.at[0,key]
        if key=='best_correct' and value=='':values[key]=None;continue
        if not value.isascii() or not value.isdigit():raise UserMessageError('Invalid practice record file.')
        values[key]=int(value)
    return PracticeRecords(**values)


@contextmanager
def update_records(course, best_streak, best_correct=None, *, enabled=True):
    if not enabled:
        yield
        return
    if type(best_streak) is not int:raise UserMessageError('Invalid practice record file.')
    for value in (best_streak,best_correct):
        if value is not None and (type(value) is not int or value<0):
            raise UserMessageError('Invalid practice record file.')
    path=record_path(course)
    with destination_lock(path):
        original=path.read_bytes() if path.exists() else None
        revision=sha256(original).digest() if original is not None else None
        previous=load_records(course)
        if original is not None and file_revision(path)!=revision:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
        updated=PracticeRecords(max(previous.best_streak,best_streak),
            max(previous.best_correct or 0,best_correct) if best_correct is not None else previous.best_correct)
        changed=updated!=previous
        if changed:
            save_csv(pd.DataFrame([dict(best_streak=updated.best_streak,
                best_correct='' if updated.best_correct is None else updated.best_correct)]),path,
                sep=';',index=False,expected_revision=revision,expect_missing=original is None)
            written=file_revision(path)
        try:yield
        except BaseException:
            if changed:
                if not path.exists() or file_revision(path)!=written:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.')
                if original is None:path.unlink()
                else:save_bytes(path,original,revision=written)
            raise

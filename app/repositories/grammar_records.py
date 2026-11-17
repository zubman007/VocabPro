"""Backward-compatible grammar API; shared record storage serves both modules."""
from app.repositories.practice_records import load_records, record_path, update_records

# Preserve the original empty schema; expand only on explicit save.
COLUMNS = ('best_streak',)


def load_record(course):
    return load_records(course).best_streak


def update_record(course,candidate,best_correct=None,*,enabled=True):
    return update_records(course,candidate,best_correct,enabled=enabled)

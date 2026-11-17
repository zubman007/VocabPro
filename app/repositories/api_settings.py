"""Read API settings only when the settings file changes."""
from app.paths import FILES_DIR
from pathlib import Path
from threading import RLock
from contextvars import ContextVar
from contextlib import contextmanager
from app.repositories.csv_store import read_csv

_audio_output = ContextVar('audio_output', default=None)


@contextmanager
def audio_output(folder):
    token = _audio_output.set(Path(folder))
    try:
        yield
    finally:
        _audio_output.reset(token)


SETTINGS_PATH = FILES_DIR / "settings.csv"
_signature = None
_values = {}
_lock = RLock()


def load_settings(path=None):
    global _signature, _values
    path=Path(path) if path is not None else SETTINGS_PATH
    with _lock:
        stat = path.stat()
        signature = (str(path), stat.st_mtime_ns, stat.st_size)
        if signature != _signature:
            frame = read_csv(path)
            values = {str(name): str(value) for name, value in zip(frame["Name"], frame["Value"])}
            _values, _signature = values, signature
        return dict(_values)


def audio_path(learning_by, language, word_id, settings_path=None):
    output = _audio_output.get()
    if output is not None:
        return output / f'{word_id}.mp3'
    path=Path(settings_path) if settings_path is not None else SETTINGS_PATH
    return path.parent / "audio" / f"{learning_by}_{language}" / f"{word_id}.mp3"

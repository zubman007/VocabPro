"""Crash-safe file persistence shared by application repositories."""
import os
import tempfile
import hashlib
from contextlib import contextmanager
from threading import RLock
from weakref import WeakValueDictionary
from pathlib import Path


def file_revision(path: str | os.PathLike) -> bytes:
    """Content revision for optimistic conflict checks, without retaining file data."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.digest()


class FileChangedError(OSError):
    pass


_locks = WeakValueDictionary()
_locks_guard = RLock()


def destination_lock(path: str | os.PathLike):
    """Serialize cooperating writers in this process; external changes use revisions."""
    key = str(Path(path).resolve())
    with _locks_guard:
        lock = _locks.get(key)
        if lock is None:
            lock = RLock()
            _locks[key] = lock
        return lock


@contextmanager
def atomic_output(destination, *, before_commit=None, expect_missing=False, **stream_options):
    """Stage, flush and close output before validating and publishing it atomically."""
    destination = Path(destination)
    temporary = None
    with destination_lock(destination):
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, dir=destination.parent,
                prefix=destination.name + ".", suffix=".tmp", **stream_options,
            ) as stream:
                temporary = Path(stream.name)
                yield stream
                stream.flush()
                os.fsync(stream.fileno())
            if before_commit is not None:
                before_commit()
            if expect_missing:
                try:
                    # Atomic create-if-absent: never overwrite a concurrently created file.
                    os.link(temporary, destination)
                except FileExistsError:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.') from None
            else:
                os.replace(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def save_csv(frame, destination, *, expected_revision=None, expect_missing=False, **options):
    destination = Path(destination)
    def check_revision():
        if expected_revision is not None and file_revision(destination) != expected_revision:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
    with atomic_output(destination, mode="w", encoding="utf-8", newline="",
                       before_commit=check_revision, expect_missing=expect_missing) as stream:
        frame.to_csv(stream, **options)

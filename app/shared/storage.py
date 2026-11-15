"""Crash-safe CSV persistence shared by application screens."""
import os
import tempfile
import hashlib
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


def save_csv(frame, destination, *, expected_revision=None, expect_missing=False, **options):
    with destination_lock(destination):
        _save_csv(frame, destination, expected_revision=expected_revision,
                  expect_missing=expect_missing, **options)


def _save_csv(frame, destination, *, expected_revision, expect_missing, **options):
    """Replace the destination only after writing and flushing the whole CSV."""
    destination = Path(destination)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", delete=False,
            dir=destination.parent, prefix=destination.name + ".", suffix=".tmp",
        ) as stream:
            temporary = Path(stream.name)
            frame.to_csv(stream, **options)
            stream.flush()
            os.fsync(stream.fileno())
        if expected_revision is not None and file_revision(destination) != expected_revision:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
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

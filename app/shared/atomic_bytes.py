"""Revision-checked atomic documents, including create-if-absent backups."""
import os
import tempfile
from pathlib import Path
from app.shared.storage import destination_lock, file_revision, FileChangedError


def save_bytes(path, data, *, revision=None, expect_missing=False):
    path = Path(path)
    temporary = None
    with destination_lock(path):
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            if revision is not None and (not path.exists() or file_revision(path) != revision):
                raise FileChangedError('The course file changed. Reopen the editor before saving.')
            if expect_missing:
                try:os.link(temporary, path)
                except FileExistsError:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.') from None
            else:
                os.replace(temporary, path)
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)

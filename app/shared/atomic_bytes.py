"""Revision-checked atomic documents, including create-if-absent backups."""
from pathlib import Path
from app.shared.storage import atomic_output, file_revision, FileChangedError


def save_bytes(path, data, *, revision=None, expect_missing=False):
    path = Path(path)
    if path.name.endswith('_con_persons.json'):
        from app.conjugation.persons import decode_configuration
        decode_configuration(data.decode('utf-8-sig'),path.stem.removesuffix('_con_persons'))
    def check_revision():
        from app.shared.integrity import check_writable
        check_writable(path)
        if revision is not None and (not path.exists() or file_revision(path) != revision):
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
    with atomic_output(path, before_commit=check_revision, expect_missing=expect_missing) as stream:
        stream.write(data)

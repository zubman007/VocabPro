"""Read-only legacy adaptation and explicit, atomic person configuration saves."""
import csv
from dataclasses import replace
from pathlib import Path
from app.conjugation.persons import default_configuration, decode_configuration, Person
from app.shared.languages import legacy_name
from app.shared.atomic_bytes import save_bytes
from app.shared.storage import file_revision, FileChangedError


def configuration_path(files, language):
    return Path(files)/f'{legacy_name(language)}_con_persons.json'


def load_configuration(files, language, course=None):
    path = configuration_path(files, language)
    columns = []
    if course is not None and Path(course).exists():
        with Path(course).open(encoding='utf-8-sig', newline='') as stream:
            columns = next(csv.reader(stream, delimiter=';'), [])
    revision = file_revision(path) if path.exists() else None
    if revision is None:
        config = default_configuration(language, legacy=all(key in columns for key in ('s1','s2','s3','m1','m2','m3')))
    else:
        config = decode_configuration(path.read_text(encoding='utf-8-sig'), language)
        if file_revision(path) != revision:
            raise FileChangedError('The course file changed. Reopen the editor before saving.')
    # Recovered legacy/custom columns remain accessible without changing the
    # user's practice selection or writing a migration merely by opening a file.
    from app.conjugation.persons import valid_person_id
    known = {p.id for p in config.persons}
    defaults = {p.id:p.label for p in default_configuration(language, legacy=True).persons}
    recovered = tuple(Person(key, defaults.get(key, key), False) for key in columns
                      if key not in known and valid_person_id(key))
    return replace(config, persons=config.persons+recovered).validate(), revision


def save_configuration(files, config, revision):
    path = configuration_path(files, config.language)
    save_bytes(path, config.to_json().encode('utf-8'), revision=revision, expect_missing=revision is None)
    return file_revision(path)

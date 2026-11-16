"""Prepare missing course assets; retire only known, demonstrably empty files."""
from contextlib import contextmanager
import csv
import logging
from pathlib import Path
import pandas as pd
from app.shared.languages import LanguagePair, legacy_name
from app.shared.storage import destination_lock, file_revision, save_csv
from app.repositories.courses import vocabulary_columns
from app.repositories.tags import catalog_columns
from app.repositories.synonyms import COLUMNS as SYNONYM_COLUMNS
from app.repositories.grammar_theory import THEORY_FIELDS
from app.repositories.grammar_records import COLUMNS as RECORD_COLUMNS
from app.grammar.editor_data import COLUMNS as GRAMMAR_COLUMNS
from dataclasses import replace
from app.conjugation.persons import default_configuration
from app.repositories.conjugation import conjugation_columns
from app.repositories.conjugation_persons import configuration_path, load_configuration, save_configuration

logger = logging.getLogger(__name__)


def resolve_conjugation_courses(files,source,courses):
    """Legacy auto-detection belongs to storage, not the settings JSON parser."""
    result=[]
    for course in courses:
        if course.conjugation_enabled is None:
            try:exists=(Path(files)/f'{LanguagePair(source,course.target).legacy_stem}_con.csv').exists()
            except (ValueError,KeyError):
                if course.enabled:raise
                exists=False
            course=replace(course,conjugation_enabled=exists)
        result.append(course)
    return tuple(result)


def course_assets(files, source, target):
    """Every path is derived from registered identities, never arbitrary input."""
    files = Path(files)
    pair = LanguagePair(source, target)
    source, target = legacy_name(pair.source), legacy_name(pair.target)
    stem = pair.legacy_stem
    return {
        'vocabulary': (files/f'{stem}_voc.csv', vocabulary_columns(source, target), {'ID', 'Repetition'}),
        'tags': (files/f'{stem}_tags.csv', catalog_columns(source, target), {'ID', source, target, 'Note'}),
        'synonyms': (files/f'{stem}_synonyms.csv', SYNONYM_COLUMNS, set(SYNONYM_COLUMNS)),
        'grammar': (files/f'{target}_gra.csv', GRAMMAR_COLUMNS,
                    {'question_id', 'prompt', 'anchor', 'option_1', 'option_2', 'option_3', 'option_4'}),
        'theory': (files/f'{stem}_gra_ex.csv', THEORY_FIELDS, {'category'}),
        'records': (files/f'{target}_gra_records.csv', RECORD_COLUMNS, set(RECORD_COLUMNS)),
        'conjugation': (files/f'{stem}_con.csv', conjugation_columns(target,source,default_configuration(target)), {'ID', 'R'}),
        'audio': files/'audio'/stem,
    }


def _local_path(path, files):
    return (not path.is_symlink() and not getattr(path, 'is_junction', lambda: False)()
            and path.resolve().is_relative_to(Path(files).resolve()))


def _empty_csv(path, required):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, delimiter=';', strict=True)
        header = next((row for row in reader if any(cell.strip() for cell in row)), None)
        if header is None:return True
        if not required <= set(header):return False
        return not any(any(cell.strip() for cell in row) for row in reader)


def _remove_empty_csv(path, required, files, *, revision=None):
    if not _local_path(path, files):return
    with destination_lock(path):
        if not path.exists() or not _empty_csv(path, required):return
        before = file_revision(path)
        if revision is not None and before != revision:return
        # Recheck after the first read; a concurrently populated file stays intact.
        if _empty_csv(path, required) and file_revision(path) == before:
            path.unlink()


def _remove_empty_directory(path, files):
    if _local_path(path, files) and path.is_dir() and not any(path.iterdir()):
        try:path.rmdir()  # Never recursive; files and nonempty subdirectories survive.
        except OSError:
            if path.is_dir() and any(path.iterdir()):return  # Concurrently filled.
            raise


@contextmanager
def prepared_course_files(files, source, courses):
    """Roll back only our unchanged, empty creations if preparation/save fails."""
    files = Path(files)
    files.mkdir(parents=True, exist_ok=True)
    created, directories, configurations = [], [], []
    try:
        for course in courses:
            if not course.enabled:continue
            assets = course_assets(files, source, course.target)
            kinds = ['vocabulary', 'tags', 'synonyms']
            if course.grammar_enabled:kinds.extend(('grammar', 'theory', 'records'))
            if course.conjugation_enabled is True:
                con_path=assets['conjugation'][0]
                config_path=configuration_path(files,course.target)
                with destination_lock(config_path):
                    config,revision=load_configuration(files,course.target,con_path)
                    if revision is None:
                        saved=save_configuration(files,config,None)
                        configurations.append((config_path,saved))
                assets['conjugation']=(con_path,conjugation_columns(course.language,legacy_name(source),config),{'ID','R'})
                kinds.append('conjugation')
            for kind in kinds:
                path, columns, required = assets[kind]
                with destination_lock(path):
                    if not path.exists():
                        save_csv(pd.DataFrame(columns=columns), path, sep=';', index=False, expect_missing=True)
                        created.append((path, required, file_revision(path)))
            for directory in (files/'audio', assets['audio']):
                if not directory.exists():
                    directory.mkdir()
                    directories.append(directory)
        yield
    except BaseException:
        for path, required, revision in reversed(created):
            try:_remove_empty_csv(path, required, files, revision=revision)
            except (OSError, UnicodeError, csv.Error):logger.warning('Could not roll back empty course asset %s', path.name)
        for directory in reversed(directories):
            try:_remove_empty_directory(directory, files)
            except OSError:logger.warning('Could not roll back empty course directory %s', directory.name)
        for path,revision in reversed(configurations):
            try:
                with destination_lock(path):
                    if _local_path(path,files) and path.exists() and file_revision(path)==revision:path.unlink()
            except OSError:logger.warning('Could not roll back course configuration %s',path.name)
        raise


def ensure_course_files(files, source, courses):
    with prepared_course_files(files, source, courses):pass


def retire_course_files(files, old_source, old_courses, source, courses):
    """Called only AFTER settings commit; return genuine filesystem failures."""
    active = {course.target for course in courses if course.enabled}
    grammar = {course.target for course in courses if course.enabled and course.grammar_enabled}
    candidates = {}
    for origin, entries in ((old_source, old_courses), (source, courses)):
        if not origin:continue
        for course in entries:
            try:assets = course_assets(files, origin, course.target)
            except (ValueError, KeyError):continue  # Inactive invalid legacy slots own no valid pair.
            same_source = legacy_name(origin) == legacy_name(source)
            retained = same_source and course.target in active
            kinds = [] if retained else ['vocabulary', 'tags', 'synonyms', 'conjugation', 'audio']
            if not retained or course.target not in grammar:kinds.append('theory')
            # Questions/records use the historical target-only filename. Another
            # active pair can still need it after changing the own language.
            if course.target not in grammar:kinds.extend(('grammar', 'records'))
            for kind in kinds:
                asset = assets[kind]
                path = asset if kind == 'audio' else asset[0]
                candidates[path] = (kind, asset)
    failed = []
    for path, (kind, asset) in candidates.items():
        try:
            if kind == 'audio':_remove_empty_directory(path, files)
            else:_remove_empty_csv(path, asset[2], files)
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError, csv.Error):
            # Saving settings succeeded. Preserve suspicious/locked assets and
            # report cleanup separately instead of claiming the save failed.
            failed.append(path.name)
            logger.warning('Could not retire empty course asset %s', path.name)
    return failed

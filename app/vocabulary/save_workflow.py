"""Prepare isolated enrichment, then commit related files with failure rollback.

Cancellation is honored until commit starts. No Tk objects are used here.
Rollback handles ordinary I/O failures, not power loss across multiple files.
"""
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
import pandas as pd
from app.repositories.api_settings import audio_output
from app.repositories import synonyms
from app.shared.background_task import check_cancelled
from app.shared.storage import file_revision, save_csv, FileChangedError, destination_lock
from app.vocabulary.editor_attributes import enrich_attributes, clean_audio_files
from app.vocabulary.editor_data import prepare_save
from app.repositories.tags import load_catalog, encode_tags

logger = logging.getLogger(__name__)


def _archive_audio(folder, word_ids):
    """Plan archives; actual replacement is performed in the commit section."""
    folder = Path(folder)
    return {folder/f'{word_id}.{suffix}': folder/'deleted'/f'{word_id}_{uuid4().hex}.{suffix}'
            for word_id in word_ids for suffix in ('mp3','wav')
            if (folder/f'{word_id}.{suffix}').is_file()}


def save_course(edited, path, language, audio_folder, revision, cancelled, progress, *, context=None):
    path, folder = Path(path), Path(audio_folder)
    check_cancelled(cancelled)
    if file_revision(path) != revision:
        raise FileChangedError('The course file changed. Reopen the editor before saving.')
    previous = pd.read_csv(path, sep=';', dtype=str, keep_default_na=False)
    previous['ID'] = previous.ID.astype(int)
    tag_path=path.with_name(path.stem.removesuffix('_voc')+'_tags.csv')
    tag_revision=None
    if 'Tags' in edited and edited.Tags.fillna('').astype(str).str.strip().ne('').any():
        learned_by=context.preferences.learned_by if context is not None else path.stem.removesuffix(f'_{language}_voc')
        catalog,tag_revision=load_catalog(tag_path,learned_by,language)
        encoded=encode_tags(edited,catalog,learned_by,language,getattr(getattr(context,'preferences',None),'maximum_tags',10))
    relation_file = synonyms.relation_path(path)
    relations, relation_revision = synonyms.load(path, previous)
    edited_ids, previous_ids = set(edited.ID), set(previous.ID)
    new_ids = edited_ids-previous_ids
    archive_ids = (previous_ids-edited_ids) | set(
        edited.loc[edited.ID.isin(new_ids) & edited.Audio.ne('Own'), 'ID'])
    folder.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.vocab-stage-', dir=folder) as directory:
        stage = Path(directory)
        originals = {}
        for identifier in previous_ids | edited_ids:
            for suffix in ('mp3','wav'):
                source = folder/f'{identifier}.{suffix}'
                originals[source] = file_revision(source) if source.is_file() else None
                if source.is_file():
                    if identifier in edited_ids and identifier not in archive_ids:
                        shutil.copy2(source, stage/source.name)
        with audio_output(stage):
            enriched = enrich_attributes(edited.copy(deep=True), language, stage,
                progress=progress, cancelled=cancelled, cleanup=False,
                **({'context':context} if context is not None else {}))
        result = prepare_save(enriched, previous)
        if tag_revision is not None:result['Tags']=encoded.set_index('ID').Tags.reindex(result.ID).values
        check_cancelled(cancelled)
        with destination_lock(path), destination_lock(relation_file), destination_lock(tag_path):
            if tag_revision is not None and file_revision(tag_path)!=tag_revision:
                raise FileChangedError('The tag catalog changed. Reopen it before saving.')
            if file_revision(path) != revision or (
                    file_revision(relation_file) if relation_file.exists() else None) != relation_revision:
                raise FileChangedError('The course file changed. Reopen the editor before saving.')
            for source, expected in originals.items():
                if (file_revision(source) if source.exists() else None) != expected:
                    raise FileChangedError('The course file changed. Reopen the editor before saving.')
            archives = _archive_audio(folder, archive_ids)
            changes = dict.fromkeys(archives)
            for row in enriched.itertuples(index=False):
                for suffix in ('mp3','wav'):
                    target = folder/f'{row.ID}.{suffix}'
                    staged = stage/target.name
                    # archive IDs are removed unless a fresh staged recording replaces them.
                    keep = (row.Audio != 'No audio' and not ('Automatic' in str(row.Audio) and suffix == 'wav')
                            and not (row.Audio == 'Own' and suffix == 'mp3' and (stage/f'{row.ID}.wav').exists()))
                    replacement = staged if keep and staged.exists() else None
                    if replacement is not None and originals.get(target) == file_revision(replacement):
                        continue
                    if replacement is not None or target.exists():
                        changes[target] = replacement
            backups, applied, created_archives = {}, [], []
            try:
                for target in changes:
                    if target.exists():
                        backup = stage/f'rollback-{uuid4().hex}'
                        shutil.copy2(target, backup)
                        backups[target] = backup
                for source, archive in archives.items():
                    archive.parent.mkdir(exist_ok=True)
                    shutil.copy2(source, archive)
                    created_archives.append(archive)
                for target, source in changes.items():
                    applied.append(target)
                    if source is None:
                        target.unlink(missing_ok=True)
                    else:
                        os.replace(source, target)
                # Remove stale links before recycled IDs become visible.
                valid = previous_ids & edited_ids
                trimmed = relations.loc[relations['ID 1'].isin(valid) & relations['ID 2'].isin(valid)]
                if relation_revision is not None and (new_ids or previous_ids-edited_ids):
                    backups[relation_file] = stage/'relations.rollback'
                    shutil.copy2(relation_file, backups[relation_file])
                    applied.append(relation_file)
                    save_csv(trimmed, relation_file, sep=';', index=False, expected_revision=relation_revision)
                save_csv(result, path, sep=';', index=False, expected_revision=revision)
            except Exception:
                rollback_errors = []
                for target in reversed(applied):
                    try:
                        if target in backups:
                            shutil.copy2(backups[target], target)
                        else:
                            target.unlink(missing_ok=True)
                    except OSError as error:
                        rollback_errors.append(error)
                if rollback_errors:
                    # Preserve originals for manual recovery even if restoration itself fails.
                    recovery = folder/f'.recovery-{uuid4().hex}'
                    os.replace(stage, recovery)
                    logger.error('Audio rollback failed; originals preserved in %s', recovery.name)
                    raise OSError('Audio recovery required: '+str(recovery)) from rollback_errors[0]
                for archive in created_archives:
                    archive.unlink(missing_ok=True)
                raise
        # The corresponding CSV is committed; cleanup touches staged copies only.
        for index in enriched.index:
            clean_audio_files(enriched, index, stage)
    return result

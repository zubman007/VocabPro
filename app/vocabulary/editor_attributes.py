"""Automatic attributes and audio cleanup; manual parts of speech stay untouched."""
import logging
from pathlib import Path
from app.services import api
from app.shared.background_task import check_cancelled

logger = logging.getLogger(__name__)


def enrich_attributes(main_df, lang_desc, audio_folder, *, progress=None, cancelled=None, cleanup=True, context=None):
    total = len(main_df)
    if progress:progress(0,total)
    for position, i in enumerate(main_df.index):
        check_cancelled(cancelled)
        clean_audio_files(main_df, i, audio_folder, destructive=cleanup)
        path = Path(audio_folder) / f"{main_df.at[i, 'ID']}.mp3"

        def needs_audio(dictionary=False):
            flag = str(main_df.at[i, 'Audio'])
            return 'Automatic' in flag and not path.exists() and (not dictionary or flag != 'Automatic - 11Labs')

        def needs_details():
            return (main_df.at[i, 'Description'] == '-' or main_df.at[i, 'Example'] == '-'
                    or (lang_desc == 'English' and main_df.at[i, 'Phonetic'] == '[]'))

        providers = []
        if lang_desc == 'English':
            providers.append((api.Dict_api, ()))
        if lang_desc in ('English', 'Spanish'):
            providers.append((api.MW, (lang_desc,)))
        for provider, arguments in providers:
            check_cancelled(cancelled)
            if needs_audio(dictionary=lang_desc == 'English') or needs_details():
                try:
                    main_df = provider(i,main_df,*arguments,**({'context':context} if context is not None else {}))
                except Exception:
                    # Provider exceptions can contain request URLs with API keys.
                    logger.warning('Dictionary provider %s failed for row %s', getattr(provider, '__name__', 'unknown'), i)
        check_cancelled(cancelled)
        if needs_audio():
            try:
                main_df = api.Eveleven_labs(i,main_df,lang_desc,**({'context':context} if context is not None else {}))
            except Exception:
                logger.warning('Speech provider failed for row %s', i)
        if lang_desc in ('English', 'Spanish'):
            for column in ('Description', 'Example'):
                if main_df.at[i, column] == '-':
                    main_df.at[i, column] = 'No found'
            if lang_desc == 'English' and main_df.at[i, 'Phonetic'] == '[]':
                main_df.at[i, 'Phonetic'] = '-'
        if needs_audio():
            main_df.at[i, 'Audio'] = 'No audio'
        check_cancelled(cancelled)
        if progress:progress(position+1,total)
    check_cancelled(cancelled)
    return main_df


def clean_audio_files(main_df, i, audio_folder, *, destructive=True):
    word_id, flag = main_df.at[i, 'ID'], str(main_df.at[i, 'Audio'])
    mp3 = Path(audio_folder) / f'{word_id}.mp3'
    wav = Path(audio_folder) / f'{word_id}.wav'
    try:
        if 'Automatic' in flag:
            if destructive:
                wav.unlink(missing_ok=True)
        elif flag == 'Own':
            if wav.exists() and destructive:
                mp3.unlink(missing_ok=True)
            elif not wav.exists() and not mp3.exists():
                main_df.at[i, 'Audio'] = 'No audio'
        elif flag == 'No audio' and destructive:
            for path in (wav, mp3):
                path.unlink(missing_ok=True)
    except OSError:
        logger.warning('Audio cleanup failed for word %s', word_id)

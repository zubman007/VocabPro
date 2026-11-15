"""Compatibility facade for editor integrations; provider code has no GUI imports."""
from app.core.context import get_context
from app.services.api_dictionary import dictionary_entry, merriam_entry
from app.services.api_speech import generate_audio


def Dict_api(i,df,*,context=None):
    context=get_context(context=context)
    return dictionary_entry(i,df,context.preferences.learned_by,settings_path=context.files_dir/'settings.csv')


def MW(i,df,lang,*,context=None):
    context=get_context(context=context)
    return merriam_entry(i,df,lang,context.preferences.learned_by,settings_path=context.files_dir/'settings.csv')


def Eveleven_labs(i,df,lang,*,context=None):
    context=get_context(context=context)
    return generate_audio(i,df,lang,context.preferences.learned_by,settings_path=context.files_dir/'settings.csv')

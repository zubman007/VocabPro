"""Cached translations backed by one UTF-8 JSON catalog per language.

Use translate(message_id, language). Message IDs remain stable English strings;
locales/*.json contains display text only, never persisted vocabulary values.
The read-only `translation[id][language]` view supports older callers.
"""
from app.paths import ROOT_DIR
from collections.abc import Mapping
from functools import lru_cache
import json
from types import MappingProxyType
from app.shared.languages import legacy_name

LOCALES_DIR = ROOT_DIR / 'locales'
# UI support is explicit: registering a learning language does not create a UI catalog.
UI_LANGUAGE_IDS = ('en', 'cs', 'sk', 'es', 'fr', 'de')
LANGUAGE_CODES = MappingProxyType({legacy_name(code): code for code in UI_LANGUAGE_IDS})
LANGUAGES = tuple(LANGUAGE_CODES)
_CODES = frozenset(LANGUAGE_CODES.values())


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate translation ID: {key!r}')
        result[key] = value
    return result


@lru_cache(maxsize=len(LANGUAGES))
def _load_catalog(code):
    try:
        with (LOCALES_DIR / f'{code}.json').open(encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=_unique_object)
    except FileNotFoundError:
        if code == 'en':
            raise
        # Cache absence too, rather than retrying the missing file per label.
        return MappingProxyType({})
    if not isinstance(data, dict) or any(not isinstance(value, str) for value in data.values()):
        raise ValueError(f'Translation catalog {code} must map message IDs to strings')
    return MappingProxyType(data)


def get_catalog(language='English'):
    """Load a language once; unknown languages or absent files use English."""
    code = LANGUAGE_CODES.get(language, language if language in _CODES else 'en')
    return _load_catalog(code) or _load_catalog('en')


def translate(message_id, language='English'):
    """Resolve a stable ID, falling back to English and then the original ID."""
    text = get_catalog(language).get(message_id)
    if text and text.strip():
        return text
    fallback = get_catalog('English').get(message_id)
    return fallback if fallback and fallback.strip() else message_id


class _MessageLanguages(Mapping):
    def __init__(self, message_id):
        self.message_id = message_id

    def __getitem__(self, language):
        if language not in LANGUAGE_CODES:
            raise KeyError(language)
        return translate(self.message_id, language)

    def __iter__(self):
        return iter(LANGUAGES)

    def __len__(self):
        return len(LANGUAGES)


class _LegacyTranslations(Mapping):
    def __getitem__(self, message_id):
        if message_id not in get_catalog('English'):
            raise KeyError(message_id)
        return _MessageLanguages(message_id)

    def __iter__(self):
        return iter(get_catalog('English'))

    def __len__(self):
        return len(get_catalog('English'))


translation = _LegacyTranslations()

"""Stable language IDs with lossless adapters to existing CSV names.

The registry describes identity, not provider capabilities. A provider may
support fewer languages than the application.
"""
from dataclasses import dataclass
from types import MappingProxyType


LANGUAGE_CODES = MappingProxyType({
    'English': 'en', 'Czech': 'cs', 'Slovak': 'sk',
    'Spanish': 'es', 'French': 'fr', 'German': 'de',
})
_NAMES = {code: name for name, code in LANGUAGE_CODES.items()}


def language_id(value):
    if value in _NAMES:
        return value
    return LANGUAGE_CODES[value]


def legacy_name(value):
    return _NAMES[language_id(value)]


@dataclass(frozen=True)
class LanguagePair:
    source: str
    target: str

    def __post_init__(self):
        object.__setattr__(self, 'source', language_id(self.source))
        object.__setattr__(self, 'target', language_id(self.target))
        if self.source == self.target:
            raise ValueError('Source and target languages must differ')

    @property
    def legacy_stem(self):
        return f'{legacy_name(self.source)}_{legacy_name(self.target)}'

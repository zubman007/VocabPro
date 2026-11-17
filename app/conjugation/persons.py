"""Small language-specific person definitions; labels never identify forms."""
from dataclasses import dataclass, replace
import json
import re
from uuid import uuid4
from app.shared.languages import language_id
from app.shared.messages import UserMessageError

LEGACY_IDS = ('s1', 's2', 's3', 'm1', 'm2', 'm3')
# Learning content: this pronoun must stay English when the UI language changes.
ENGLISH_YOU = 'you'
LABELS = {
    'es': ('yo', 'tú', 'él / ella / usted', 'nosotros / nosotras', 'vosotros / vosotras', 'ellos / ellas / ustedes'),
    'en': ('I', 'you (singular)', 'he / she / it', 'we', 'you (plural)', 'they'),
    'cs': ('já', 'ty', 'on / ona / ono', 'my', 'vy', 'oni / ony / ona'),
    'sk': ('ja', 'ty', 'on / ona / ono', 'my', 'vy', 'oni / ony'),
    'fr': ('je', 'tu', 'il / elle / on', 'nous', 'vous', 'ils / elles'),
    'de': ('ich', 'du', 'er / sie / es', 'wir', 'ihr', 'sie / Sie'),
}


def valid_person_id(value):
    return isinstance(value, str) and (value in LEGACY_IDS or re.fullmatch(r'p_[0-9a-f]{32}', value) is not None)


def unique_object(items):
    result = {}
    for key, value in items:
        if key in result:raise UserMessageError('Invalid conjugation person configuration.')
        result[key] = value
    return result


@dataclass(frozen=True)
class Person:
    id: str
    label: str
    enabled: bool = True

    @classmethod
    def create(cls, label):
        return cls('p_'+uuid4().hex, label.strip())


@dataclass(frozen=True)
class PersonConfiguration:
    language: str
    persons: tuple[Person, ...]
    practice_person_ids: tuple[str, ...]

    @property
    def active(self):
        return tuple(person for person in self.persons if person.enabled)

    @property
    def practice(self):
        return tuple((person.id, person.label) for person in self.persons
                     if person.enabled and person.id in self.practice_person_ids)

    def validate(self):
        if language_id(self.language) != self.language:
            raise UserMessageError('Invalid conjugation person configuration.')
        ids = [person.id for person in self.persons]
        if (len(set(ids)) != len(ids) or any(not valid_person_id(key) for key in ids)
                or any(type(person.enabled) is not bool or not isinstance(person.label, str)
                       or not person.label.strip() for person in self.persons)
                or len(set(self.practice_person_ids)) != len(self.practice_person_ids)
                or not set(self.practice_person_ids) <= {person.id for person in self.active}):
            raise UserMessageError('Invalid conjugation person configuration.')
        return self

    def to_json(self):
        self.validate()
        return json.dumps(dict(version=1, language=self.language,
            persons=[dict(id=p.id, label=p.label, enabled=p.enabled) for p in self.persons],
            practice_person_ids=list(self.practice_person_ids)), ensure_ascii=False, indent=2)+'\n'


def default_configuration(language, *, legacy=False):
    code = language_id(language)
    persons = tuple(Person(key, label) for key, label in zip(LEGACY_IDS, LABELS[code])
                    if legacy or code != 'en' or key != 'm2')
    if code == 'en' and not legacy:
        persons = tuple(replace(p, label=ENGLISH_YOU) if p.id == 's2' else p for p in persons)
    return PersonConfiguration(code, persons, tuple(p.id for p in persons))


def decode_configuration(text, language):
    try:
        data = json.loads(text, object_pairs_hook=unique_object)
        if (not isinstance(data, dict) or set(data) != {'version', 'language', 'persons', 'practice_person_ids'}
                or type(data['version']) is not int or data['version'] != 1
                or data['language'] != language_id(language) or not isinstance(data['persons'], list)
                or not isinstance(data['practice_person_ids'], list)):
            raise ValueError
        if any(not isinstance(item, dict) or set(item) != {'id', 'label', 'enabled'} for item in data['persons']):
            raise ValueError
        return PersonConfiguration(data['language'], tuple(Person(**item) for item in data['persons']),
                                   tuple(data['practice_person_ids'])).validate()
    except (ValueError, TypeError, KeyError):
        raise UserMessageError('Invalid conjugation person configuration.') from None

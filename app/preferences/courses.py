"""Versioned study-course settings; legacy slots are adapted without disk writes."""
from dataclasses import dataclass
import json
from app.shared.languages import language_id, legacy_name, LanguagePair

COURSE_FIELD = 'Study courses'
LEGACY_COURSE_FIELDS = ('First learning language', 'Second learning language',
                        'Enable second learning language')
LEGACY_TEST_PREFIXES = tuple(f'Percentage of type {kind} testing - {order}.lang '
                             for kind in (2, 3) for order in (1, 2))


def is_legacy_course_field(name):
    return name in LEGACY_COURSE_FIELDS or name.startswith(LEGACY_TEST_PREFIXES)


class CourseConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class StudyCourse:
    target: str
    enabled: bool = True
    context_percent: int = 0
    audio_percent: int = 0
    grammar_enabled: bool = True
    conjugation_enabled: bool | None = False

    @property
    def language(self):
        return legacy_name(self.target)


def legacy_courses(values):
    """Inactive duplicate/own-language slots stay in legacy CSV rows, not as courses."""
    result, seen = [], set()
    source = values.get('Learned by', '')
    for order, field in enumerate(LEGACY_COURSE_FIELDS[:2], 1):
        target = values.get(field, '')
        if not target:
            continue
        target = language_id(target)
        if target in seen or legacy_name(target) == source:
            continue
        seen.add(target)
        result.append(StudyCourse(target, order == 1 or values.get('Enable second learning language', '1') == '1',
            int(values.get(f'Percentage of type 2 testing - {order}.lang (description and use in a sentence)', 0)),
            int(values.get(f'Percentage of type 3 testing - {order}.lang (audio and options)', 0)),
            conjugation_enabled=None))
    return tuple(result)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CourseConfigurationError('Invalid study course configuration.')
        result[key] = value
    return result


def decode_courses(text, source):
    """Reject corrupt/future schemas instead of silently falling back to two slots."""
    try:
        data = json.loads(text, object_pairs_hook=_unique_object)
        if not isinstance(data, dict) or set(data) != {'version', 'source', 'courses'}:
            raise ValueError
        if type(data['version']) is not int or data['version'] not in (1, 2, 3):
            raise CourseConfigurationError('Unsupported study course configuration version.')
        if data['source'] != language_id(source):
            raise CourseConfigurationError('Study course source does not match your own language.')
        if not isinstance(data['courses'], list) or not data['courses']:
            raise ValueError
        result, seen = [], set()
        for item in data['courses']:
            fields = ({'target', 'enabled', 'context', 'audio'} | ({'grammar'} if data['version'] >= 2 else set())
                      | ({'conjugation'} if data['version'] == 3 else set()))
            if not isinstance(item, dict) or set(item) != fields:
                raise ValueError
            target = item['target']
            if language_id(target) != target or type(item['enabled']) is not bool:
                raise ValueError
            if target in seen:
                raise CourseConfigurationError('Each study language may appear only once.')
            seen.add(target)
            if type(item.get('grammar', True)) is not bool:
                raise ValueError
            if data['version']==3 and type(item['conjugation']) is not bool:raise ValueError
            for kind in ('context', 'audio'):
                if type(item[kind]) is not int or not 0 <= item[kind] <= 100:
                    raise CourseConfigurationError('Enter a percentage between 0 and 100.')
            if item['enabled'] and item['context'] + item['audio'] > 100:
                raise CourseConfigurationError('Test percentages for each language must total at most 100.')
            if item['enabled'] or data['version'] >= 2:
                try:
                    LanguagePair(source, target)
                except ValueError:
                    raise CourseConfigurationError('Your own language and all learned language need to be different.') from None
            result.append(StudyCourse(target,item['enabled'],item['context'],item['audio'],item.get('grammar',True),
                                      item.get('conjugation')))
        if not any(course.enabled for course in result):
            raise CourseConfigurationError('Enable at least one study course.')
        return tuple(result)
    except CourseConfigurationError:
        raise
    except (ValueError, KeyError, TypeError):
        raise CourseConfigurationError('Invalid study course configuration.') from None


def encode_courses(source, courses):
    """Encode one resolved snapshot, or retain a wholly legacy v2 snapshot.

    Mixed old/new callers first use repository.resolve_conjugation_courses;
    disk-dependent availability cannot be guessed by this pure serializer.
    """
    courses=tuple(courses)
    if any(c.conjugation_enabled is None for c in courses) and any(c.conjugation_enabled is not None for c in courses):
        raise CourseConfigurationError('Invalid study course configuration.')
    version=2 if any(course.conjugation_enabled is None for course in courses) else 3
    text = json.dumps({'version': version, 'source': language_id(source), 'courses': [
        dict(target=course.target, enabled=course.enabled, context=course.context_percent,
             audio=course.audio_percent, grammar=course.grammar_enabled,
             **({'conjugation':course.conjugation_enabled} if version==3 else {})) for course in courses]}, separators=(',', ':'))
    decode_courses(text, source)
    return text

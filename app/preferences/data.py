"""User-preference schema and validation, independent of the dialog."""
from app.paths import ROOT_DIR
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
from app.preferences.courses import (COURSE_FIELD, StudyCourse, CourseConfigurationError,
                                    decode_courses, legacy_courses, is_legacy_course_field)

PREFERENCES_FILE = ROOT_DIR / "files" / "settings.csv"
LANGUAGE_FIELDS = ("Learned by", "First learning language", "Second learning language")
BATCH_FIELDS = {"Random repeat batch - Vocabulary", "Random repeat batch - Conjugation", "Random repeat batch - Grammar", "Learn batch"}
TAG_DEPENDENT_FIELDS = ('Show tags during practice', 'Tag display language', 'Maximum tags per word')


def group_for(name):
    """Presentation groups within a tab; persisted preference names stay stable."""
    if name in ('Track personal records','Show personal records'):return 'Practice records'
    if name == 'Enable tags' or name in TAG_DEPENDENT_FIELDS:
        return 'Tags'
    if name in ('App sounds enabled', 'App sound volume'):
        return 'Settings sounds'
    if name in ('Remember grammar categories', 'Random repeat batch - Grammar'):
        return 'Grammar'
    if name in ('Random repeat batch - Conjugation', 'Remember conjugation categories'):
        return 'Conjugation'
    if name in ('Random repeat batch - Vocabulary', 'Learn batch', 'Autoplay pronunciation',
                'Automatically show synonyms in repeat', 'Letter hints') or name.startswith('Percentage'):
        return 'Vocabulary'
    return 'Settings general'


def with_defaults(frame):
    result = frame.copy(deep=True)
    for name, kind, value in (('App sounds enabled', 'Bool', '1'), ('App sound volume', 'Int', '100'),
                             ('Autoplay pronunciation', 'Bool', '1'), ('Remember grammar categories', 'Bool', '1'),
                             ('Automatically show synonyms in repeat', 'Bool', '1'),
                             ('Enable second learning language', 'Bool', '1'),
                             ('Letter hints', 'Options[Automatic,On request,Disabled]', 'On request'),
                             ('Enable tags','Bool','1'),('Show tags during practice','Bool','1'),
                             ('Tag display language','Options[Student language,Learning language]','Learning language'),
                             ('Maximum tags per word','Int','10'),
                             ('Track personal records','Bool','1'),('Show personal records','Bool','1'),
                             ('Remember conjugation categories','Bool','1'),
                             ('Random repeat batch - Grammar','Int','10'),
                             ('Random repeat batch - Conjugation','Int','10')):
        if name not in set(result['Name']):
            row = dict.fromkeys(result.columns, '')
            row.update(Name=name, Type=kind, Value=value)
            result = pd.concat([result, pd.DataFrame([row])], ignore_index=True)
    return result


@dataclass(frozen=True)
class RuntimePreferences:
    backup_mail: str
    backup_period: int
    next_backup: str
    repeat_batch: int
    conjugation_batch: int
    learn_batch: int
    learned_by: str
    first_language: str
    second_language: str
    app_language: str
    context_probabilities: tuple
    audio_probabilities: tuple
    sounds_enabled: bool = True
    sound_volume: int = 100
    autoplay_pronunciation: bool = True
    remember_grammar_categories: bool = True
    show_synonyms: bool = True
    letter_hints: str = 'On request'
    tags_enabled: bool = True
    show_practice_tags: bool = True
    tag_display_language: str = 'Learning language'
    maximum_tags: int = 10
    second_language_enabled: bool = True
    courses: tuple[StudyCourse, ...] | None = None
    track_personal_records: bool = True
    show_personal_records: bool = True
    remember_conjugation_categories: bool = True
    grammar_batch: int = 10

    @property
    def records_visible(self):
        return self.track_personal_records and self.show_personal_records

    @property
    def study_courses(self):
        if self.courses is not None:
            return self.courses
        values = {'Learned by': self.learned_by, 'First learning language': self.first_language,
                  'Second learning language': self.second_language,
                  'Enable second learning language': '1' if self.second_language_enabled else '0'}
        for index in range(2):
            values[f'Percentage of type 2 testing - {index + 1}.lang (description and use in a sentence)'] = self.context_probabilities[index]
            values[f'Percentage of type 3 testing - {index + 1}.lang (audio and options)'] = self.audio_probabilities[index]
        return legacy_courses(values)

    @property
    def learning_languages(self):
        return tuple(course.language for course in self.study_courses if course.enabled)

    @property
    def language_pairs(self):
        from app.shared.languages import LanguagePair
        return tuple(LanguagePair(self.learned_by, language) for language in self.learning_languages)

    def grammar_enabled(self, language):
        from app.shared.languages import language_id
        target = language_id(language)
        return any(course.target == target and course.enabled and course.grammar_enabled for course in self.study_courses)

    def testing_probabilities(self, language):
        """Resolve course settings by identity, regardless of list order or origin."""
        from app.shared.languages import legacy_name
        name = legacy_name(language)
        course = next((course for course in self.study_courses if course.enabled and course.language == name), None)
        if course is None:
            raise ValueError(language)
        return course.context_percent, course.audio_percent

    @classmethod
    def from_frame(cls, frame):
        validated = validate_preferences(frame, {})
        values = dict(zip(validated['Name'], validated['Value']))
        configured = decode_courses(values[COURSE_FIELD], values['Learned by']) if COURSE_FIELD in values else None
        active = tuple(course for course in configured if course.enabled) if configured is not None else ()
        for name in (('Learned by', 'App language') if COURSE_FIELD in values else (*LANGUAGE_FIELDS, 'App language')):
            if not values.get(name):
                raise PreferenceError(name, 'Choose a valid option.')
        def probabilities(kind, suffix):
            if configured is not None:
                settings = tuple(course.context_percent if kind == 2 else course.audio_percent for course in active[:2])
                return (settings + (0, 0))[:2]
            return tuple(int(values.get(f'Percentage of type {kind} testing - {order}.lang ({suffix})', 0))
                         for order in (1, 2))
        return cls(values.get('Backup mail', ''), int(values.get('Backup period (days)', 0)),
            values.get('Next backup', '')[:19], int(values.get('Random repeat batch - Vocabulary', 0)),
            int(values.get('Random repeat batch - Conjugation', 10)), int(values.get('Learn batch', 0)),
            values.get('Learned by', ''), active[0].language if active else values.get('First learning language', ''),
            active[1].language if len(active) > 1 else values.get('Second learning language', ''), values.get('App language', ''),
            probabilities(2, 'description and use in a sentence'), probabilities(3, 'audio and options'),
            values.get('App sounds enabled', '1') == '1', int(values.get('App sound volume', '100')),
            values.get('Autoplay pronunciation', '1') == '1', values.get('Remember grammar categories', '1') == '1',
            values.get('Automatically show synonyms in repeat','1') == '1',
            values.get('Letter hints','On request'),values.get('Enable tags','1')=='1',
            values.get('Show tags during practice','1')=='1',values.get('Tag display language','Learning language'),
            int(values.get('Maximum tags per word','10')),
            len(active) > 1 if configured is not None else values.get('Enable second learning language','1')=='1', configured,
            values.get('Track personal records','1')=='1',values.get('Show personal records','1')=='1',
            values.get('Remember conjugation categories','1')=='1',int(values.get('Random repeat batch - Grammar','10')))


class PreferenceError(ValueError):
    def __init__(self, field, message):
        self.field, self.message = field, message
        super().__init__(message)


def options_for(kind):
    if kind.startswith("Options[") and kind.endswith("]"):
        return [value.strip() for value in kind[8:-1].split(",")]
    return None


def section_for(name):
    if name in ('App sounds enabled', 'App sound volume'):
        return 'Learning'
    if name == "App language" or name in LANGUAGE_FIELDS or name in ('Enable second learning language', COURSE_FIELD):
        return "Languages"
    if name.startswith("Backup") or name == "Next backup":
        return "Backups"
    if "token" in name.casefold() or "api key" in name.casefold():
        return "API services"
    return "Learning"


def validate_preferences(frame, values):
    """Return a validated copy; never silently reset values or mutate the form."""
    result = frame.copy(deep=True)
    if COURSE_FIELD in values and COURSE_FIELD not in set(result.Name):
        row = dict.fromkeys(result.columns, '')
        row.update(Name=COURSE_FIELD, Type='JSON', Value=values[COURSE_FIELD])
        result = pd.concat([result, pd.DataFrame([row])], ignore_index=True)
    merged = dict(zip(result["Name"], result["Value"]))
    merged.update({name: str(value) for name, value in values.items() if name in merged})
    has_courses = COURSE_FIELD in merged
    if merged.get('Letter hints','On request') not in ('Automatic','On request','Disabled'):
        raise PreferenceError('Letter hints', 'Choose a valid option.')
    for field in ('App sounds enabled', 'Autoplay pronunciation', 'Remember grammar categories','Enable second learning language',
                  'Track personal records','Show personal records','Remember conjugation categories'):
        if has_courses and is_legacy_course_field(field):
            continue
        if merged.get(field, '1') not in ('0', '1'):
            raise PreferenceError(field, 'Choose a valid option.')
    volume = merged.get('App sound volume', '100')
    if not volume.isascii() or not volume.isdigit() or not 0 <= int(volume) <= 100:
        raise PreferenceError('App sound volume', 'Enter a volume between 0 and 100.')
    for row in result.itertuples(index=False):
        name, kind = row.Name, row.Type
        if has_courses and is_legacy_course_field(name):
            continue  # Retained for rollback; the versioned course list is authoritative.
        value = merged[name]
        choices = options_for(kind)
        if kind == "Int":
            if not value.isascii() or not value.isdigit():
                raise PreferenceError(name, "Enter a whole non-negative number.")
            number = int(value)
            if name in BATCH_FIELDS and number == 0:
                raise PreferenceError(name, "Batch size must be at least 1.")
            if name.startswith("Percentage") and number > 100:
                raise PreferenceError(name, "Enter a percentage between 0 and 100.")
        elif kind == "Bool" and value not in {"0", "1"}:
            raise PreferenceError(name, "Choose a valid option.")
        elif choices is not None and value not in choices:
            raise PreferenceError(name, "Choose a valid option.")
    if has_courses:
        try:
            if result.loc[result.Name.eq(COURSE_FIELD), 'Type'].tolist() != ['JSON']:
                raise CourseConfigurationError('Invalid study course configuration.')
            decode_courses(merged[COURSE_FIELD], merged.get('Learned by', ''))
        except CourseConfigurationError as error:
            raise PreferenceError(COURSE_FIELD, str(error)) from None
    else:
        if 'First learning language' in merged and not merged['First learning language'].strip():
            raise PreferenceError('First learning language','Choose a valid option.')
        second_enabled=merged.get('Enable second learning language','1')=='1'
        languages = [merged.get(name, "") for name in LANGUAGE_FIELDS[:2 if not second_enabled else 3]]
        if all(languages) and len(set(languages)) != len(languages):
            raise PreferenceError("First learning language", "Your own language and all learned language need to be different.")
        for order in (1, 2):
            if order==2 and not second_enabled:continue
            fields = [name for name in merged if name.startswith(("Percentage of type 2 testing", "Percentage of type 3 testing")) and f"{order}.lang" in name]
            if sum(int(merged[name]) for name in fields) > 100:
                raise PreferenceError(fields[0], "Test percentages for each language must total at most 100.")
    next_backup = merged.get("Next backup", "").strip()
    if 'Next backup' in merged:
        merged['Next backup'] = next_backup
    if next_backup:
        try:
            parsed = datetime.fromisoformat(next_backup)
            datetime.strptime(next_backup[:19], "%Y-%m-%d %H:%M:%S")
            if parsed.tzinfo is not None:
                raise ValueError("Use local time")
        except ValueError:
            raise PreferenceError("Next backup", "Use date and time in YYYY-MM-DD HH:MM:SS format.") from None
    email = merged.get("Backup mail", "").strip()
    if 'Backup mail' in merged:
        merged['Backup mail'] = email
    if email and ("@" not in email or any(char.isspace() for char in email)):
        raise PreferenceError("Backup mail", "Enter a valid email address.")
    result["Value"] = result["Name"].map(merged)
    return result



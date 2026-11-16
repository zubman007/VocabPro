"""User-preference schema and validation, independent of the dialog."""
from app.paths import ROOT_DIR
from datetime import datetime
from dataclasses import dataclass
import pandas as pd

PREFERENCES_FILE = ROOT_DIR / "files" / "settings.csv"
LANGUAGE_FIELDS = ("Learned by", "First learning language", "Second learning language")
BATCH_FIELDS = {"Random repeat batch - Vocabulary", "Random repeat batch - Conjugation", "Learn batch"}
TAG_DEPENDENT_FIELDS = ('Show tags during practice', 'Tag display language', 'Maximum tags per word')


def group_for(name):
    """Presentation groups within a tab; persisted preference names stay stable."""
    if name == 'Enable tags' or name in TAG_DEPENDENT_FIELDS:
        return 'Tags'
    if name in ('App sounds enabled', 'App sound volume'):
        return 'Settings sounds'
    if name == 'Remember grammar categories':
        return 'Grammar'
    if name == 'Random repeat batch - Conjugation':
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
                             ('Maximum tags per word','Int','10')):
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

    @property
    def learning_languages(self):
        return (self.first_language,self.second_language) if self.second_language_enabled else (self.first_language,)

    @property
    def language_pairs(self):
        from app.shared.languages import LanguagePair
        return tuple(LanguagePair(self.learned_by, language) for language in self.learning_languages)

    def testing_probabilities(self, language):
        """Resolve legacy ordinal preferences at the boundary, by language identity."""
        from app.shared.languages import legacy_name
        index = self.learning_languages.index(legacy_name(language))
        return self.context_probabilities[index], self.audio_probabilities[index]

    @classmethod
    def from_frame(cls, frame):
        validated = validate_preferences(frame, {})
        values = dict(zip(validated['Name'], validated['Value']))
        for name in (*LANGUAGE_FIELDS, 'App language'):
            if not values.get(name):
                raise PreferenceError(name, 'Choose a valid option.')
        def probabilities(kind, suffix):
            return tuple(int(values.get(f'Percentage of type {kind} testing - {order}.lang ({suffix})', 0))
                         for order in (1, 2))
        return cls(values.get('Backup mail', ''), int(values.get('Backup period (days)', 0)),
            values.get('Next backup', '')[:19], int(values.get('Random repeat batch - Vocabulary', 0)),
            int(values.get('Random repeat batch - Conjugation', 0)), int(values.get('Learn batch', 0)),
            values.get('Learned by', ''), values.get('First learning language', ''),
            values.get('Second learning language', ''), values.get('App language', ''),
            probabilities(2, 'description and use in a sentence'), probabilities(3, 'audio and options'),
            values.get('App sounds enabled', '1') == '1', int(values.get('App sound volume', '100')),
            values.get('Autoplay pronunciation', '1') == '1', values.get('Remember grammar categories', '1') == '1',
            values.get('Automatically show synonyms in repeat','1') == '1',
            values.get('Letter hints','On request'),values.get('Enable tags','1')=='1',
            values.get('Show tags during practice','1')=='1',values.get('Tag display language','Learning language'),
            int(values.get('Maximum tags per word','10')),values.get('Enable second learning language','1')=='1')


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
    if name == "App language" or name in LANGUAGE_FIELDS or name=='Enable second learning language':
        return "Languages"
    if name.startswith("Backup") or name == "Next backup":
        return "Backups"
    if "token" in name.casefold() or "api key" in name.casefold():
        return "API services"
    return "Learning"


def validate_preferences(frame, values):
    """Return a validated copy; never silently reset values or mutate the form."""
    result = frame.copy(deep=True)
    merged = dict(zip(frame["Name"], frame["Value"]))
    merged.update({name: str(value) for name, value in values.items() if name in merged})
    if merged.get('Letter hints','On request') not in ('Automatic','On request','Disabled'):
        raise PreferenceError('Letter hints', 'Choose a valid option.')
    for field in ('App sounds enabled', 'Autoplay pronunciation', 'Remember grammar categories','Enable second learning language'):
        if merged.get(field, '1') not in ('0', '1'):
            raise PreferenceError(field, 'Choose a valid option.')
    volume = merged.get('App sound volume', '100')
    if not volume.isascii() or not volume.isdigit() or not 0 <= int(volume) <= 100:
        raise PreferenceError('App sound volume', 'Enter a volume between 0 and 100.')
    for row in frame.itertuples(index=False):
        name, kind = row.Name, row.Type
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



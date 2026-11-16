"""Explicit application dependencies shared by controllers and entry points."""
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable,TYPE_CHECKING
from app.paths import ROOT_DIR
from app.preferences.data import RuntimePreferences
from app.shared.translations import translate
from app.shared.languages import LanguagePair, legacy_name

if TYPE_CHECKING:
    from pandas import DataFrame


def initial_preferences():
    # Bootstrap only: saved settings are loaded before the home screen is built.
    return RuntimePreferences('',0,'',10,10,10,'','Spanish','English','English',(0,0),(0,0))


@dataclass
class AppContext:
    preferences: RuntimePreferences = field(default_factory=initial_preferences)
    root_dir: Path = ROOT_DIR
    files_dir: Path | None = None
    on_home: Callable[[], None] | None = None
    preferences_frame: 'DataFrame | None' = field(default=None,repr=False)
    selected_course: LanguagePair | None = None

    def __post_init__(self):
        self.root_dir=Path(self.root_dir)
        self.files_dir=Path(self.files_dir) if self.files_dir is not None else self.root_dir/'files'

    def translate(self,message):
        return translate(message,self.preferences.app_language)

    def vocabulary_path(self,language):
        return self.files_dir/f'{self.language_pair(language).legacy_stem}_voc.csv'

    def language_pair(self, language):
        return LanguagePair(self.preferences.learned_by, language)

    def tags_path(self,language):
        return self.files_dir/f'{self.language_pair(language).legacy_stem}_tags.csv'

    def conjugation_path(self,language):
        return self.files_dir/f'{self.language_pair(language).legacy_stem}_con.csv'

    def grammar_path(self,language):
        return self.files_dir/f'{legacy_name(language)}_gra.csv'

    def theory_path(self,language):
        return self.files_dir/f'{self.language_pair(language).legacy_stem}_gra_ex.csv'

    def audio_folder(self,language):
        return self.files_dir/'audio'/self.language_pair(language).legacy_stem

    def go_home(self):
        if self.on_home is None:
            raise RuntimeError('Home navigation has not been configured.')
        return self.on_home()

    def bind(self,owner):
        owner.app_context=self
        _active.set(self)
        return self


# Compatibility for shared presentation helpers without an owner argument.
# Controllers resolve their own context once; they never import app.main.
_active=ContextVar('vocabpro_context',default=None)


def get_context(owner=None,context=None):
    if context is not None:
        if owner is not None:context.bind(owner)
        return context
    current=owner
    while current is not None:
        candidate=vars(current).get('app_context')
        if isinstance(candidate,AppContext):
            _active.set(candidate)
            return candidate
        current=vars(current).get('master')
    context=_active.get()
    if context is None:
        context=AppContext()
        _active.set(context)
    return context

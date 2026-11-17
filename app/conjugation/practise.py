"""Conjugation screen controller; no module-level lesson state."""
from app.shared.messages import error_text
from app.core.context import get_context
from app.shared.diagnostics import report_error
from pathlib import Path
from os.path import exists
from app.ui import messagebox
import customtkinter as cst
from app.shared.audio_effects import play_effect
from app.conjugation.data import select_verbs, build_verbs, eligible_verbs, person_results, PERSONS_MAP
from app.repositories.conjugation_persons import load_configuration
from app.repositories.conjugation import save_results,load_source
from app.conjugation.layout import build as build_layout
from app.conjugation.session import ConjugationSession
from app.repositories.practice_records import load_records, update_records, PracticeRecords
from app.ui.learning_review import open_verb_review
from app.core.screen_controller import ScreenController
from app.ui import learning_layout as ui
from app.shared import settings as s


class ConjugationController:
    def __init__(self, app, source, selection, verbs, persons, path, on_back, *, context=None):
        self.context=get_context(app,context)
        self.translate=self.context.translate
        self.app, self.source = app, source
        self.path, self.on_back = Path(path), on_back
        self.session = ConjugationSession(selection, verbs, persons)
        self.records=load_records(self.path) if self.context.preferences.show_personal_records else PracticeRecords()
        self._initial_selection=self.session.selection.copy(deep=True)
        s.Clear_frames(app)
        self.view = build_layout(app, persons, self.confirm, self.skip, self.save, self.exit_app, self.back)
        self.lifecycle = ScreenController(app,self.view.root,{
            '<Return>': self.confirm,
            '<Escape>':self.back,
            '<Control-s>': self.save, '<Control-S>': self.save,
            '<Control-r>': self.review, '<Control-R>': self.review,
            '<KeyRelease-Control_L>': self.close_review,
        },context=self.context,on_window_close=self.exit_app)
        self.bindings=self.lifecycle.bindings
        self.lifecycle.add_cleanup(self._close_review_dialog)
        self.next_verb()

    def next_verb(self, skip=False):
        if self.bindings.closed:
            return
        verb = self.session.advance(skip)
        self._refresh_records()
        if verb is None:
            self.save()
            return
        self.view.verb.configure(text=f'{verb.targ_lng} / {verb.base_lng}')
        self.view.description.configure(text=verb.desc)
        first_entry = None
        for key, _ in self.session.persons:
            self.view.variables[key].set('')
            available = bool(getattr(verb,key,'').strip())
            entry = self.view.entries[key]
            entry.configure(state='normal' if available else 'disabled',
                            fg_color=ui.SURFACE if available else ui.PAGE)
            if available and first_entry is None:
                first_entry = entry
        if first_entry is not None:
            first_entry.focus()

    def skip(self):
        self.next_verb(skip=True)

    def confirm(self, event=None):
        if self.bindings.closed:
            return
        answers = {key: variable.get() for key, variable in self.view.variables.items()}
        previously_revealed = self.session.revealed
        correct = self.session.confirm(answers)
        self._refresh_records()
        if correct is None:
            return
        if correct:
            if not previously_revealed:
                play_effect('success.FLAC')
            self.view.count.configure(text=str(self.session.completed))
            self.next_verb()
        else:
            play_effect('wrong.wav')
            self._reveal_answers(answers)

    def _reveal_answers(self, answers):
        results=person_results(self.session.current,answers,self.session.persons)
        for key, _ in self.session.persons:
            expected = getattr(self.session.current,key,'')
            if not expected.strip():
                value, color = '', ui.PAGE
            elif not results[key]:
                value, color = expected, ui.ERROR
            else:
                value, color = answers[key], ui.SURFACE
            self.view.variables[key].set(value)
            self.view.entries[key].configure(state='disabled', fg_color=color)

    def _refresh_records(self):
        if not self.context.preferences.show_personal_records:
            self.view.records.grid_remove();return
        streak=self.records.best_streak;correct=self.records.best_correct
        if self.context.preferences.track_personal_records:
            streak=max(streak,self.session.best_streak)
            if self.session.correct:correct=max(correct or 0,self.session.correct)
        self.view.records.configure(text=self.translate('Session: {correct} correct · streak {streak}').format(
            correct=self.session.correct,streak=self.session.streak)+'\n'+
            self.translate('All-time best streak: {count}').format(count=streak)+' · '+
            self.translate('Most correct in one session: {count}').format(count=correct if correct is not None else '—'))

    def review(self, event=None):
        if self.bindings.closed or self.session.previous is None:
            return
        if not any(isinstance(widget, cst.CTkToplevel) for widget in self.app.winfo_children()):
            self._review_dialog=open_verb_review(self.app,self.session.previous,self.session.persons)

    def close_review(self, event=None):
        if not self.bindings.closed:
            s.Clear_tops(self.app)

    def save(self,event=None,*,close=True):
        if self.bindings.closed:
            return
        try:
            with update_records(self.path,self.session.best_streak,
                                self.session.correct if self.session.correct else None,
                                enabled=self.context.preferences.track_personal_records):
                updated = save_results(self.source, self.session.selection, self.path)
        except Exception as error:
            report_error(error, operation='conjugation screen')
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=error_text(error, self.translate))
            return False
        self.source = updated
        self._initial_selection=self.session.selection.copy(deep=True)
        if self.session.completed:
            play_effect('saved')
        if close:self.lifecycle.finish(self.on_back)
        return True

    def back(self,event=None):
        if self.bindings.closed:return
        if self._can_leave():self.lifecycle.finish(self.on_back)

    def _can_leave(self):
        return self.lifecycle.can_leave(not self.session.selection.equals(self._initial_selection),
            lambda:self.save(close=False),message='Save this practice session before going back?')

    def exit_app(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def _close_review_dialog(self):
        dialog=getattr(self,'_review_dialog',None)
        if dialog is not None and dialog.winfo_exists():dialog.destroy()


def Conjugation(app_input,lang_input,*,context=None):
    """Load a lesson before replacing the current screen, as before."""
    context=get_context(app_input,context)
    config=context.preferences
    if not context.conjugation_enabled(lang_input):return None
    from app.shared.languages import legacy_name
    lang_input=legacy_name(lang_input)
    path=context.conjugation_path(lang_input)
    if not exists(path):
        messagebox.showerror(parent=app_input, title=context.translate('Error'),
                             message=f"{context.translate('Something got wrong.')}\n{path}")
        return None
    try:
        people,_=load_configuration(context.files_dir,lang_input,path)
        source=load_source(path,lang_input,config.learned_by,people)
        source.attrs['person_ids']=tuple(key for key,_ in people.practice)
        selection = select_verbs(eligible_verbs(source,people.practice),config.conjugation_batch)
        verbs = build_verbs(selection,lang_input,config.learned_by,people.practice)
    except (OSError,ValueError,KeyError) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error, context.translate))
        return None
    if not verbs:
        return None
    try:
        return ConjugationController(app_input, source, selection, verbs,
            people.practice,path,context.go_home,context=context)
    except (OSError,ValueError) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error,context.translate))
        return None

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
from app.conjugation.categories import load_catalog, category_options, category_ids, filter_categories
from app.conjugation.history import HISTORY_COLUMN
from types import SimpleNamespace
import pandas as pd


class ConjugationController:
    def __init__(self, app, source, selection, verbs, persons, path, on_back, *, context=None,category_labels=None,
                 catalog=None, language=None, initial_categories=None, remember_filter=None):
        self.context=get_context(app,context)
        self.translate=self.context.translate
        self.app, self.source = app, source
        self.path, self.on_back = Path(path), on_back
        self.category_labels=category_labels or {}
        self.language=language or self.path.stem.split('_')[-2]
        self.catalog=catalog if catalog is not None else load_catalog(self.path,source)[0]
        self.categories=category_options(eligible_verbs(source,persons),self.catalog)
        available={key for key,_,_ in self.categories}
        self.selected_categories=available if initial_categories is None else available & set(initial_categories)
        self.remember_filter=remember_filter
        self._filter_window=None
        self._working=source.copy(deep=True)
        self.session = ConjugationSession(selection, verbs, persons)
        self.records=load_records(self.path) if self.context.preferences.track_personal_records else PracticeRecords()
        self.record_best_streak=self.record_best_correct=0
        self._initial_selection=self.session.selection.copy(deep=True)
        s.Clear_frames(app)
        self.view = build_layout(app, persons, self.confirm, self.skip, self.save, self.exit_app, self.back,self.open_filter)
        self.lifecycle = ScreenController(app,self.view.root,{
            '<Return>': self.confirm,
            '<Escape>':self.back,
            '<Control-s>': self.save, '<Control-S>': self.save,
            '<Control-r>': self.review, '<Control-R>': self.review,
            '<KeyRelease-Control_L>': self.close_review,
            '<Control-f>':self.open_filter, '<Control-F>':self.open_filter,
        },context=self.context,on_window_close=self.exit_app)
        self.bindings=self.lifecycle.bindings
        self.lifecycle.add_cleanup(self._close_review_dialog)
        self._refresh_filter_status()
        self.next_verb()

    def _collect_progress(self):
        identifiers=self._working.ID.astype(str)
        selected=self.session.selection.copy()
        selected.index=selected.ID.astype(str)
        mask=identifiers.isin(selected.index)
        for column in ('R','LR',HISTORY_COLUMN):
            if column not in selected:continue
            if column not in self._working:self._working[column]=''
            self._working[column]=self._working[column].astype(object)
            self._working.loc[mask,column]=identifiers[mask].map(selected[column]).to_numpy(dtype=object)

    def _pending_selection(self):
        self._collect_progress()
        changed=pd.Series(False,index=self._working.index)
        for column in ('R',HISTORY_COLUMN):
            if column not in self._working:continue
            before=self.source.get(column,pd.Series('',index=self.source.index)).fillna('').astype(str)
            changed |= self._working[column].fillna('').astype(str).ne(before)
        return self._working.loc[changed].copy()

    def open_filter(self,event=None):
        if self.bindings.closed:return 'break'
        if self._filter_window is not None and self._filter_window.winfo_exists():
            self._filter_window.lift();return 'break'
        from app.grammar.category_filter import CategoryFilterDialog
        self._filter_window=CategoryFilterDialog(self.app,self.categories,self.selected_categories,self.apply_filter,
                                                title_key='Verb categories',count_caption='Number of verbs')
        return 'break'

    def apply_filter(self,selected):
        selected=set(selected)&{key for key,_,_ in self.categories}
        if not selected or self.bindings.closed:return False
        if selected!=self.selected_categories:
            self._refresh_records()
            self._collect_progress()
            pool=filter_categories(eligible_verbs(self._working,self.session.persons),self.catalog,selected)
            selection=select_verbs(pool,self.context.preferences.conjugation_batch or len(pool))
            if selection.empty:return False
            verbs=build_verbs(selection,self.language,self.context.preferences.learned_by,self.session.persons)
            self.session=ConjugationSession(selection,verbs,self.session.persons)
            self.selected_categories=selected
            self._refresh_filter_status()
            self.next_verb()
        self._remember_filter()
        return True

    def _remember_filter(self):
        if self.remember_filter is None:return
        try:self.remember_filter(self.selected_categories)
        except (OSError,ValueError) as error:
            report_error(error,operation='saved conjugation filter')
            parent=self._filter_window if self._filter_window is not None and self._filter_window.winfo_exists() else self.app
            messagebox.showerror(parent=parent,title=self.translate('Verb categories'),
                                 message=self.translate('Category filter applied but could not be remembered.'))

    def _refresh_filter_status(self):
        self.view.filter_status.configure(text=self.translate('Filtered categories')+': '+
            f'{len(self.selected_categories)} / {len(self.categories)}')

    def next_verb(self, skip=False):
        if self.bindings.closed:
            return
        verb = self.session.advance(skip)
        self._refresh_records()
        if verb is None:
            self.save()
            return
        self.view.verb.configure(text=f'{verb.targ_lng} / {verb.base_lng}')
        category=self.category_labels.get(str(verb.id),'')
        description=verb.desc
        if category and description.split(',',1)[0].strip().casefold()!=category.casefold():
            description=category+('\n'+description if description.strip() else '')
        self.view.description.configure(text=description)
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
        if self.bindings.closed or (event is not None and self.app.grab_current() is not None):
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
        state=self.session
        self.view.count.configure(text=self.translate('Completed verbs: {count}').format(
            count=f'{state.completed} / {len(state.selection)}'))
        self.view.score.configure(text=f'{self.translate("Correct answers")}: {state.correct}\n'
            f'{self.translate("Incorrect answers")}: {state.incorrect}\n'
            f'{self.translate("Streak")}: {state.streak}\n{self.translate("Best streak")}: {state.best_streak}')
        if self.context.preferences.track_personal_records:
            self.record_best_streak=max(self.record_best_streak,state.best_streak)
            self.record_best_correct=max(self.record_best_correct,state.correct)
        if not self.context.preferences.records_visible:
            self.view.records_panel.grid_remove();return
        self.view.records_panel.grid()
        candidate=SimpleNamespace(best_streak=self.record_best_streak,correct=self.record_best_correct,streak=state.streak)
        self.view.records_panel.set_state(candidate,self.records,True)

    def review(self, event=None):
        if self.bindings.closed or self.session.previous is None:
            return
        if not any(isinstance(widget, cst.CTkToplevel) for widget in self.app.winfo_children()):
            self._review_dialog=open_verb_review(self.app,self.session.previous,self.session.persons)

    def close_review(self, event=None):
        if not self.bindings.closed:
            self._close_review_dialog()

    def save(self,event=None,*,close=True):
        if self.bindings.closed:
            return
        try:
            pending=self._pending_selection()
            with update_records(self.path,self.record_best_streak,
                                self.record_best_correct if self.record_best_correct else None,
                                enabled=self.context.preferences.track_personal_records):
                updated = save_results(self.source, pending, self.path)
        except Exception as error:
            report_error(error, operation='conjugation screen')
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=error_text(error, self.translate))
            return False
        self.source = updated
        self._working=updated.copy(deep=True)
        self._initial_selection=self.session.selection.copy(deep=True)
        if self.session.completed:
            play_effect('saved')
        if close:self.lifecycle.finish(self.on_back)
        return True

    def back(self,event=None):
        if self.bindings.closed:return
        if self._can_leave():self.lifecycle.finish(self.on_back)

    def _can_leave(self):
        return self.lifecycle.can_leave(not self._pending_selection().empty,
            lambda:self.save(close=False),message='Save this practice session before going back?')

    def exit_app(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def _close_review_dialog(self):
        dialog=getattr(self,'_review_dialog',None)
        if dialog is not None and dialog.winfo_exists():dialog.destroy()


def Conjugation(app_input,lang_input,*,context=None,categories=None,on_back=None):
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
        from app.conjugation.categories import category_names
        catalog,_=load_catalog(path,source)
        labels=dict(zip(source.ID.astype(str),category_names(source,catalog)))
        eligible=eligible_verbs(source,people.practice)
        available_ids={key for key,_,_ in category_options(eligible,catalog)}
        explicit_categories=categories is not None
        remember=None
        if config.remember_conjugation_categories and config.learned_by:
            from app.repositories.conjugation_filters import load_filter,save_filter
            filter_path=context.files_dir/'settings.csv'
            remember=lambda selected:save_filter(filter_path,config.learned_by,lang_input,selected,available_ids)
            if categories is None:categories=load_filter(filter_path,config.learned_by,lang_input,available_ids)
        available=filter_categories(eligible,catalog,categories)
        selected_ids=None if categories is None else set(category_ids(available,catalog))
        selection = select_verbs(available,config.conjugation_batch)
        verbs = build_verbs(selection,lang_input,config.learned_by,people.practice)
    except (OSError,ValueError,KeyError) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error, context.translate))
        return None
    if not verbs:
        return None
    try:
        controller=ConjugationController(app_input, source, selection, verbs,
            people.practice,path,on_back if on_back is not None else context.go_home,context=context,category_labels=labels,
            catalog=catalog,language=lang_input,initial_categories=selected_ids,remember_filter=remember)
        if remember is not None and explicit_categories:controller._remember_filter()
        return controller
    except (OSError,ValueError) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error,context.translate))
        return None

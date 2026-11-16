"""Grammar question editor controller; changes reach CSV only on explicit save."""
from app.shared.messages import error_text
from app.core.context import get_context
from app.ui import messagebox
import customtkinter as cst
from app.shared import settings as s
from app.grammar.editor_data import GrammarDocument, QuestionValidationError
from app.grammar.editor_layout import build
from app.core.screen_controller import ScreenController
from app.shared.audio_effects import play_effect
from app.grammar.editor_navigation import open_editor
from app.shared.diagnostics import report_error


class GrammarEditor:
    document_type = GrammarDocument
    theory_mode = False
    title_key = 'Edit grammar questions'
    add_key = 'Add question'
    delete_key = 'Delete question'
    apply_prompt = 'Apply changes to the current question?'
    delete_prompt = 'Delete this question and its answer history?'
    count_key = 'Number of questions'

    def __init__(self, app, language, path, on_back, *, context=None):
        self.context=get_context(app,context)
        self.translate=self.context.translate
        self.app, self.on_back = app, on_back
        self.language = language
        self.document = self.document_type(path)
        self._initial_document=self.document.frame.copy(deep=True)
        self.learned_by = self.context.preferences.learned_by
        if not self.theory_mode and self.learned_by:
            self._sync_theory()
        self.current = None
        self._loaded = None
        s.Clear_frames(app)
        self.view = build(app, language, dict(save=self.save, back=self.back, exit=self.close_app,filter=self.filter,
            select=self.select, add=self.add, delete=self.delete, apply=self.apply,
            related=self.open_related), theory=self.theory_mode)
        self.lifecycle=ScreenController(app,self.view.root,{'<Control-s>':self.save,'<Control-S>':self.save,'<Escape>':lambda event:self.back()},
            context=self.context,on_window_close=self.close_app)
        self.bindings=self.lifecycle.bindings
        self.refresh()
        play_effect('edit')

    def _values(self):
        result = {}
        for key, widget in self.view.fields.items():
            result[key] = widget.get('1.0', 'end-1c') if isinstance(widget, cst.CTkTextbox) else widget.get()
        return result, self.view.correct.get()

    def _form_changed(self):
        return self.current is not None and self._values() != self._loaded

    def _show(self, identifier):
        self.current = identifier
        values = self.document.question(identifier) if identifier is not None else dict.fromkeys(self.document.fields, '')
        for key, widget in self.view.fields.items():
            if isinstance(widget, cst.CTkTextbox):
                widget.delete('1.0', 'end')
                widget.insert('1.0', values[key])
            elif isinstance(widget, cst.CTkComboBox):
                widget.set(values[key])
            else:
                widget.delete(0, 'end')
                widget.insert(0, values[key])
        self.view.correct.set(0)
        self.view.form_title.configure(text=(values['category'] or self.translate(self.add_key)) if self.theory_mode
            else f"{self.translate('Question ID')}: {identifier}" if identifier else self.translate(self.add_key))
        self._loaded = self._values()

    def refresh(self, preferred=None):
        frame = self.document.frame
        categories = sorted(set(frame.category) - {''}, key=str.casefold)
        selected_category = self.view.category_filter.get()
        choices = [self.translate('All categories'), *categories]
        self.view.category_filter.configure(values=choices)
        if selected_category not in choices:
            self.view.category_filter.set(self.translate('All categories'))
        self.view.fields['category'].configure(values=categories or [''])
        query = self.view.query.get().strip().casefold()
        category = self.view.category_filter.get()
        rows = frame
        if category != self.translate('All categories'):
            rows = rows.loc[rows.category.eq(category)]
        if query:
            mask = rows[list(self.document.fields)+[self.document.id_column]].apply(
                lambda column: column.str.casefold().str.contains(query, regex=False)).any(axis=1)
            rows = rows.loc[mask]
        tree = self.view.tree
        tree.delete(*tree.get_children())
        for row in rows.to_dict('records'):
            identifier = row[self.document.id_column]
            tree.insert('', 'end', iid=identifier, values=(identifier, row['category'], row[self.document.summary_column]))
        ids = list(rows[self.document.id_column])
        identifier = preferred if preferred in ids else self.current if self.current in ids else ids[0] if ids else None
        self._show(identifier)
        if identifier is not None:
            tree.selection_set(identifier)
            tree.see(identifier)
        self.view.count.configure(text=f"{len(rows)} / {len(frame)}  ·  {self.translate(self.count_key)}")
        self._applied_filter = (self.view.query.get(), self.view.category_filter.get())

    def _leave_question(self):
        if not self._form_changed():
            return True
        answer = messagebox.askyesnocancel(parent=self.app, title=self.translate(self.title_key),
            message=self.translate(self.apply_prompt))
        return self.apply(refresh=False) if answer is True else answer is False

    def select(self, event=None):
        selection = self.view.tree.selection()
        if not selection or selection[0] == self.current:
            return
        if self._leave_question():
            self._show(selection[0])
        elif self.current is not None:
            self.view.tree.selection_set(self.current)

    def filter(self):
        if self._leave_question():
            self.refresh()
        else:
            query, category = self._applied_filter
            self.view.query.delete(0, 'end')
            self.view.query.insert(0, query)
            self.view.category_filter.set(category)

    def apply(self, refresh=True):
        if self.current is None:
            return True
        try:
            values, correct = self._values()
            self.document.update(self.current, values, correct)
            if self.view.tree.exists(self.current):
                row = self.document.question(self.current)
                self.view.tree.item(self.current, values=(self.current, row['category'], row[self.document.summary_column]))
        except ValueError as error:
            self._error(QuestionValidationError(self.current, str(error)) if not self.theory_mode else error)
            return False
        if refresh:
            self.refresh(self.current)
        else:
            self._loaded = self._values()
        return True

    def add(self):
        if not self._leave_question():
            return
        identifier = self.document.add()
        self.view.query.delete(0, 'end')
        self.view.category_filter.set(self.translate('All categories'))
        self.refresh(identifier)
        self.view.fields['category'].focus_set()

    def delete(self):
        if self.current is not None and messagebox.askyesno(parent=self.app, title=self.translate(self.delete_key),
                message=self.translate(self.delete_prompt)):
            self.document.delete(self.current)
            self.current = None
            self.refresh()

    def save(self, event=None, *, close=True):
        if self.lifecycle.closed:return False
        if self._form_changed() and not self.apply(refresh=False):
            return False
        try:
            self.document.save()
            self._initial_document=self.document.frame.copy(deep=True)
            if not self.theory_mode and self.learned_by:
                self._sync_theory()
        except Exception as error:
            self._error(error)
            return False
        self.refresh(self.current)
        play_effect('saved')
        if close:
            self.back()
        return True

    def _can_leave(self):
        if self.lifecycle.closed:return False
        dirty=not self.document.frame.equals(self._initial_document) or self._form_changed()
        return self.lifecycle.can_leave(dirty,lambda:self.save(close=False),title=self.title_key)

    def back(self):
        if self._can_leave():
            self.lifecycle.finish(self.on_back)

    def close_app(self):
        if self._can_leave():
            self.lifecycle.finish(self.app.destroy)

    def _error(self, error):
        report_error(error, operation='grammar editor')
        prefix = ''
        if isinstance(error, QuestionValidationError):
            if error.identifier != self.current or not self._form_changed():
                self.view.query.delete(0, 'end')
                self.view.category_filter.set(self.translate('All categories'))
                self.refresh(error.identifier)
            prefix = f"{self.translate('Question ID')}: {error.identifier}\n\n"
            self.view.fields['option_1'].focus_set()
        messagebox.showerror(parent=self.app, title=self.translate(self.title_key), message=prefix+error_text(error, self.translate))

    def _sync_theory(self):
        from app.repositories.grammar_theory import ensure_theory_categories
        path = self.document.path.with_name(f'{self.learned_by}_{self.language}_gra_ex.csv')
        ensure_theory_categories(path, self.document.frame.category)

    def open_related(self):
        if self._can_leave():
            try:
                open_editor(self.app, self.language, theory=not self.theory_mode, context=self.context)
            except Exception as error:
                self._error(error)


def Edit_grammar(app,language,*,context=None):
    context=get_context(app,context)
    if not context.preferences.grammar_enabled(language):return
    return GrammarEditor(app,language,context.grammar_path(language),context.go_home,context=context)

"""Table-based tag catalog editor; catalog changes never rewrite vocabulary."""
from tkinter import messagebox

import customtkinter as cst
import pandas as pd
import tksheet

from app.repositories.tags import TagValidationError, load_catalog, save_catalog
from app.shared.diagnostics import report_error
from app.shared import settings as s
from app.ui.components.app_dialog import AppDialog
from app.ui.components.shortcut_hint import ShortcutHint
from app.ui.module_style import SESSION, tool_button
from app.vocabulary.editor_layout import sheet_options


class TagsDialog(AppDialog):
    def __init__(self, owner, language, *, context=None):
        if context is not None:
            context.bind(owner)
        super().__init__(owner)
        self.translate = self.app_context.translate
        self.language = language
        self.learned_by = self.app_context.preferences.learned_by
        self.path = self.app_context.tags_path(language)
        try:
            self.original, self.revision = load_catalog(self.path, self.learned_by, language)
        except (OSError, ValueError, UnicodeError):
            self.destroy()
            raise
        self.columns = list(self.original.columns)
        self.title(self.translate('Manage tags'))
        self.geometry('980x680')
        self.minsize(700, 480)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.add_heading(self.translate('Tag catalog') + ' · ' + self.translate(language),
            self.translate('Edit tag names and translations. Words can have multiple tags separated by commas.'))
        body = cst.CTkFrame(self, fg_color='#ded4bf', corner_radius=18)
        body.grid(row=1, sticky='nsew', padx=20, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self.table = tksheet.Sheet(body, headers=[self.translate(column) for column in self.columns],
            data=self.original.values.tolist(), **sheet_options(s.tbl_set))
        self.table.grid(row=0, sticky='nsew', padx=12, pady=12)
        self.table.enable_bindings(s.tbl_bind)
        self.table.readonly_columns(columns=[0])
        self.table.bind('<Control-s>', self.save)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-S>', self.save)
        self.table.bind('<Escape>', lambda event: self.close())
        self.bind('<Escape>', lambda event: self.close())
        self.protocol('WM_DELETE_WINDOW', self.close)
        controls = cst.CTkFrame(self, fg_color=SESSION, corner_radius=16)
        controls.grid(row=2, sticky='ew', padx=20, pady=8)
        controls.grid_columnconfigure(0, weight=1)
        self.hint = ShortcutHint(controls,'Manage tags',self.translate)
        self.hint.grid(row=0, column=0, sticky='ew', padx=14, pady=12)
        for column, (caption, callback) in enumerate((('Add tag', self.add_tag), ('Delete tag', self.delete_tags)), 1):
            button = tool_button(cst.CTkButton(controls, text=self.translate(caption), command=callback))
            button.grid(row=0, column=column, padx=(0,12), pady=8)
        self.add_actions(self, [('Close', self.close), ('Save', self.save)], self.translate, row=3, pady=(8,20))
        self.apply_background('editor_warm_v1.png')
        self.table.bind('<Configure>', self._resize_columns, add='+')
        self.after(50, lambda: self.present(modal=True))

    def _resize_columns(self, event=None):
        available = max(560, self.table.winfo_width() - 64)
        widths = [65, max(150, int(available * .28)), max(150, int(available * .28))]
        widths += [max(150, available - sum(widths))] * (len(self.columns) - 3)
        for column, width in enumerate(widths):
            self.table.column_width(column, width=width, redraw=False)
        self.table.refresh()

    def snapshot(self):
        self.table.close_text_editor(set_data=True)
        return pd.DataFrame(self.table.get_sheet_data(), columns=self.columns).fillna('').astype(str)

    def add_tag(self):
        frame = self.snapshot()
        identifiers = pd.to_numeric(pd.concat([frame.ID,self.original.ID]), errors='coerce')
        identifier = int(identifiers.max()) + 1 if identifiers.notna().any() else 1
        row = [''] * len(self.columns)
        row[0] = str(identifier)
        self.table.insert_row(row)
        self.table.readonly_columns(columns=[0])
        index = self.table.get_total_rows() - 1
        self.table.select_cell(index, 1)
        self.table.see(index, 1)

    def delete_tags(self):
        self.table.close_text_editor(set_data=True)
        selected = set(self.table.get_selected_rows())
        selected.update(row for row, _ in self.table.get_selected_cells())
        if selected:
            rows = [row for index, row in enumerate(self.table.get_sheet_data()) if index not in selected]
            from app.repositories.vocabulary import read_words
            course=self.app_context.vocabulary_path(self.language)
            if course.exists():
                from app.vocabulary.tags_data import normalize_tags
                used=set(tag.casefold() for value in read_words(course).get('Tags',[]) for tag in normalize_tags(value).split(', '))
                if any(str(self.table.get_cell_data(index,self.columns.index(self.learned_by))).casefold() in used for index in selected):
                    messagebox.showerror(parent=self,title=self.translate('Manage tags'),message=self.translate('Cannot delete a tag assigned to words.'))
                    return
            self.table.set_sheet_data(rows, reset_col_positions=False)

    def save(self, event=None):
        try:
            save_catalog(self.path, self.snapshot(), self.learned_by, self.language, self.revision)
        except (OSError, ValueError) as error:
            report_error(error, operation='save tag catalog')
            message = (self.translate(error.message).format(row=error.row)
                       if isinstance(error, TagValidationError) else self.translate(str(error)))
            messagebox.showerror(parent=self, title=self.translate('Manage tags'), message=message)
            return 'break'
        self.destroy()
        return 'break'

    def close(self):
        if not self.snapshot().equals(self.original.astype(str)):
            choice = messagebox.askyesnocancel(parent=self, title=self.translate('Manage tags'),
                message=self.translate('Save changes before leaving?'))
            if choice is None:
                return
            if choice:
                self.save()
                return
        self.destroy()

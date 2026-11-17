"""Conjugation spreadsheets: bulk verb forms and a course category catalog."""
import customtkinter as cst
import pandas as pd
import tksheet
from app.core.context import get_context
from app.core.screen_controller import ScreenController
from app.repositories.conjugation import ConjugationDocument, conjugation_columns
from app.repositories.conjugation_persons import load_configuration
from app.conjugation.categories import ConjugationTables, CATEGORY_COLUMN
from app.shared.storage import save_csv
from app.shared.messages import error_text
from app.ui import messagebox
from app.ui import learning_layout as ui
from app.ui.training_layout import shell
from app.ui.surfaces import surface
from app.ui.sections import SectionTabs
from app.ui.components.editor_toolbar import EditorToolbar
from app.ui.components.search_filter_panel import SearchFilterPanel
from app.vocabulary.editor_layout import sheet_options


class ConjugationEditor:
    def __init__(self,app,language,*,context=None):
        self.context=get_context(app,context);self.translate=self.context.translate
        self.app,self.language=app,language
        path=self.context.conjugation_path(language)
        self.config,_=load_configuration(self.context.files_dir,language,path)
        if not path.exists():
            save_csv(pd.DataFrame(columns=conjugation_columns(language,self.context.preferences.learned_by,self.config)),
                     path,sep=';',index=False,expect_missing=True)
        self.document=ConjugationDocument(path,language,self.context.preferences.learned_by,self.config)
        self.tables=ConjugationTables(self.document)
        self.applied_query='';self.visible_ids=set()
        self._build(app)
        self.lifecycle=ScreenController(app,self.view.root,{'<Control-s>':self.save,'<Control-S>':self.save,
            '<Escape>':self.back},context=self.context,on_window_close=self.exit_app)
        self.refresh()

    def _build(self,app):
        from app.shared import settings as s
        s.Clear_frames(app)
        view=shell(app,'Edit conjugation','conjugation_background_v1.png',
                   [('save',self.save),('close',self.back),('exit',self.exit_app)])
        self.view=view
        view.header.title_label.configure(text=self.translate('Edit conjugation')+' / '+self.translate(self.language))
        view.body.grid_rowconfigure(1,weight=1)
        view.filters=SearchFilterPanel(view.body,self.translate,placeholder='Search',on_apply=self.filter)
        view.filters.grid(row=0,sticky='ew',pady=(0,8));view.query=view.filters.query
        view.tabs=SectionTabs(view.body);view.tabs.grid(row=1,sticky='nsew')
        labels={self.language:self.translate('Verb'),self.document.learned_by:self.translate('Translation'),
                CATEGORY_COLUMN:self.translate('Category'),'Description':self.translate('Description'),
                **{p.id:p.label for p in self.config.active}}
        view.sheets={}
        for key,caption,headers in (('verbs','Verbs',['ID',*(labels[field] for field in self.tables.fields)]),
                                    ('categories','Categories',['ID',self.translate('Category'),self.translate('Description')])):
            panel=view.tabs.add(self.translate(caption))
            panel.grid_rowconfigure(0,weight=1);panel.grid_columnconfigure(0,weight=1)
            sheet=tksheet.Sheet(panel,headers=headers,expand_sheet_if_paste_too_big=True,
                               default_row_index_width=44,**sheet_options(s.tbl_set))
            sheet.grid(sticky='nsew',padx=12,pady=12)
            sheet.enable_bindings(('single_select','drag_select','select_all','column_select','row_select',
                'column_width_resize','row_height_resize','double_click_column_resize','arrowkeys',
                'copy','cut','paste','delete','undo','edit_cell'))
            sheet.readonly_columns(columns=[0]);sheet.hide_columns([0])
            sheet.set_all_column_widths(width=170)
            sheet.popup_menu_add_command(self.translate('Delete selected rows'),self.delete,
                                        index_menu=True,header_menu=False)
            sheet.bind('<Control-s>',self.save);sheet.bind('<Control-S>',self.save)
            view.sheets[key]=sheet
        view.sheet=view.sheets['verbs'];view.category_sheet=view.sheets['categories']
        view.tools=EditorToolbar(view.body,'Conjugation editors',self.translate,action_columns=3)
        view.tools.grid(row=2,sticky='ew',pady=(8,0));view.tools.attach_background(view.layer)
        view.tools.set_help(self.translate('Conjugation spreadsheet help'))
        for key,caption,command in (('add','Add row',self.add),('delete','Delete selected rows',self.delete),('apply','Apply',self.apply)):
            view.tools.add_action(key,caption,command)
        surface(view.tabs,view.layer)

    def refresh(self):
        rows=self.tables.verb_rows(self.applied_query)
        self.visible_ids={row[0] for row in rows}
        self.view.sheet.set_sheet_data(rows,reset_col_positions=False,reset_row_positions=True)
        self.view.category_sheet.set_sheet_data(self.tables.catalog[['ID','Name','Description']].values.tolist(),
                                                reset_col_positions=False,reset_row_positions=True)
        self.view.sheet.readonly_columns(columns=[0]);self.view.category_sheet.readonly_columns(columns=[0])
        self.view.sheet.hide_columns([0]);self.view.category_sheet.hide_columns([0])
        self.view.sheet.dropdown_column(self.tables.fields.index(CATEGORY_COLUMN)+1,
            values=['',*self.tables.catalog.Name.tolist()],validate_input=False)
        self._displayed_verbs=self.view.sheet.get_sheet_data(return_copy=True)
        self._displayed_categories=self.view.category_sheet.get_sheet_data(return_copy=True)
        self.view.tools.count.configure(text=f'{len(rows)} / {len(self.document.frame)} - '+self.translate('Number of verbs'))

    def _end_editing(self):
        for sheet in self.view.sheets.values():
            sheet.close_text_editor(set_data=True)

    def apply(self,event=None):
        self._end_editing()
        try:
            self.tables.apply(self.view.sheet.get_sheet_data(return_copy=True),self.visible_ids,
                              self.view.category_sheet.get_sheet_data(return_copy=True))
        except (ValueError,KeyError) as error:self.error(error);return False
        self.refresh();return True

    def filter(self):
        if self.apply():
            self.applied_query=self.view.query.get().strip();self.refresh()
        else:
            self.view.query.delete(0,'end');self.view.query.insert(0,self.applied_query)

    def _active_sheet(self):
        return self.view.sheet if self.view.tabs.get()==self.translate('Verbs') else self.view.category_sheet

    def add(self):
        sheet=self._active_sheet()
        row=sheet.get_total_rows();sheet.insert_row(row=['']*len(sheet.headers()),idx='end')
        sheet.select_cell(row,1);sheet.see(row,1)

    def delete(self):
        sheet=self._active_sheet()
        rows=set(sheet.get_selected_rows())|{row for row,column in sheet.get_selected_cells()}
        if not rows:return
        if messagebox.askyesno(parent=self.app,title=self.translate('Delete selected rows'),
                              message=self.translate('Delete selected conjugation rows?')):
            sheet.delete_rows(rows=sorted(rows))

    def save(self,event=None,*,close=True):
        if self.lifecycle.closed:return False
        if not self.apply():return False
        try:self.tables.save()
        except (OSError,ValueError) as error:self.error(error);return False
        if close:self.lifecycle.finish(self.context.go_home)
        return True

    def _can_leave(self):
        if self.lifecycle.closed:return False
        self._end_editing()
        dirty=(self.tables.dirty or self.view.sheet.get_sheet_data(return_copy=True)!=self._displayed_verbs
               or self.view.category_sheet.get_sheet_data(return_copy=True)!=self._displayed_categories)
        return self.lifecycle.can_leave(dirty,lambda:self.save(close=False))

    def back(self,event=None):
        if self._can_leave():self.lifecycle.finish(self.context.go_home)

    def exit_app(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def error(self,error):
        messagebox.showerror(parent=self.app,title=self.translate('Error'),message=error_text(error,self.translate))


def Edit_conjugation(app,language,*,context=None):
    context=get_context(app,context)
    if not context.conjugation_enabled(language):return None
    from app.shared.languages import legacy_name
    try:return ConjugationEditor(app,legacy_name(language),context=context)
    except (OSError,ValueError,KeyError) as error:
        messagebox.showerror(parent=app,title=context.translate('Error'),message=error_text(error,context.translate))
        return None

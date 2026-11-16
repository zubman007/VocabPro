"""Screen controller with per-instance state; menu entry point preserved."""
from app.shared.messages import error_text
from app.vocabulary.editor_audio import AudioRecorderPlayer
from app.shared.background_task import BackgroundTask, CancelledError
from app.shared.audio_effects import play_effect
from app.vocabulary.save_workflow import save_course
from app.vocabulary.id_sequence import next_word_id
from app.vocabulary.editor_localization import display_frame,canonical_rows
from app.vocabulary.editor_synonym_columns import add_columns, SynonymCounts, COLUMNS as SYNONYM_COLUMNS
SYNONYM_COLUMNS=tuple(SYNONYM_COLUMNS)+('Tag count',)
from app.repositories.vocabulary import load_editor_snapshot
from app.vocabulary.editor_data import merge_table_edits, filter_vocabulary, sort_vocabulary
from app.vocabulary.editor_filter import VocabularyFilter, filterable_headers
from app.vocabulary.editor_layout import arrange_editor, sheet_options, READONLY_BACKGROUND, restore_after_save_error, fit_editor_columns, configure_editor_dropdowns, color_editor_columns
from app.shared import settings as s
from app.core.context import get_context
from app.shared.diagnostics import report_error
from dataclasses import replace
import pandas as pd
import customtkinter as cst
from tkinter import *
from app.ui import messagebox
import tksheet
from functools import partial
from app.ui.components.module_header import ModuleHeader
from app.ui.components.app_dialog import AppDialog
from app.ui.components.save_progress import SaveProgress
from app.core.screen_controller import ScreenController
from os.path import exists
import pygame
import pywinstyles
import os
from pathlib import Path

class EditorController:
    """Owns one screen, its widgets and editing/learning state."""

    def __init__(self, app, lang, *, context=None):
        self.context=get_context(app,context)
        self.translate=self.context.translate
        self.learned_by = self.context.preferences.learned_by
        self.app = app
        self.lang_desc = lang
        self.audio_folder = str(self.context.audio_folder(lang))
        self.file_voc = self.context.vocabulary_path(lang)
        self.main_df,self._revision=load_editor_snapshot(self.file_voc,lang,self.learned_by)
        if self.context.preferences.tag_display_language=='Learning language':
            from app.repositories.tags import load_catalog
            from app.vocabulary.tags_data import translated_tags
            catalog,_=load_catalog(self.context.tags_path(lang),self.learned_by,lang)
            mapping=dict(zip(catalog[self.learned_by].str.casefold(),catalog[lang]))
            self.main_df['Tags']=self.main_df.Tags.map(lambda value:translated_tags(value,mapping).replace(' · ', ', '))
        self._next_id = next_word_id(self.file_voc, self.main_df)
        self._saving = False
        self._task = None
        self._close_after_save = False
        self._mixer_active = False
        s.Clear_frames(app)
        self.filt_flag = 0
        self._sort_spec = None
        self._filter_job = None
        self._resetting_filter = False
        self.edit_frm = cst.CTkFrame(app, fg_color=s.clr_bg)
        action_frm = cst.CTkFrame(self.edit_frm, fg_color=s.clr_bg)
        self.head_frm=ModuleHeader(self.edit_frm,
            self.translate('Edit course') + ' · ' + self.translate(self.lang_desc), translate=self.translate)
        self.edit_tbl = tksheet.Sheet(action_frm, expand_sheet_if_paste_too_big=True, default_row_index_width=50, **sheet_options(s.tbl_set), rounded_boxes=True)
        self.edit_tbl.enable_bindings(s.tbl_bind)
        self.headers = ['ID', self.lang_desc, 'Phonetic', self.learned_by, 'Audio', 'Description', 'Example', 'Part of Speech', 'Tags', 'Repetition', 'Next repetition']
        self.default_vals = ['', '', '[]', '', 'Automatic', '-', '-', '-', '', '', self.translate('Now')]
        if self.lang_desc == 'Spanish':
            self.dropdown_set = [[3, ['Automatic', 'Automatic - 11Labs', 'Own', 'No audio']], [6, ['-'] + s.PoS_types]]
            self.headers = [i for i in self.headers if i != 'Phonetic']
            self.default_vals = [i for i in self.default_vals if i != '[]']
        else:
            self.dropdown_set = [[4, ['Automatic', 'Automatic - 11Labs', 'Own', 'No audio']], [7, ['-'] + s.PoS_types]]
        index=self.headers.index('Repetition')
        self.headers[index:index]=SYNONYM_COLUMNS
        self.default_vals[index:index]=['—',0,0]
        defaults=dict(zip(self.headers,self.default_vals))
        self.headers=[name for name in self.headers if name not in ('Description','Example')]
        index=self.headers.index('Repetition')
        self.headers[index:index]=['Description','Example']
        self.headers.remove('Tag count')
        self.headers.insert(self.headers.index('Tags')+1, 'Tag count')
        self.default_vals=[defaults[name] for name in self.headers]
        self.dropdown_set=[[self.headers.index('Audio'),['Automatic','Automatic - 11Labs','Own','No audio']],
                           [self.headers.index('Part of Speech'),['-']+s.PoS_types]]
        self._synonym_counts = SynonymCounts()
        self.main_df = add_columns(self.main_df,self.file_voc,self._synonym_counts)
        self.transl_headers = [self.translate(i) for i in self.headers]
        self.edit_tbl.headers(self.transl_headers)
        self.edit_tbl.popup_menu_add_command(self.translate('Record audio (ctrl+r)'), partial(self.Record_audio, app, ''), index_menu=False, header_menu=False)
        self.edit_tbl.popup_menu_add_command(self.translate('Play audio (ctrl+p)'), partial(self.Play_audio, app, ''), index_menu=False, header_menu=False)
        self.edit_tbl.popup_menu_add_command(self.translate('Delete audio'), self.Delete_audio, index_menu=False, header_menu=False)
        self.edit_tbl.popup_menu_add_command(self.translate('Delete selected words'), self.Delete_words, index_menu=True, header_menu=False)
        self.edit_tbl.popup_menu_add_command(self.translate('Synonyms'), self.Open_synonyms, index_menu=True, header_menu=False)
        self.edit_tbl.popup_menu_add_command(self.translate('Sort'),self.Sort,index_menu=False,header_menu=True)
        self.Load()
        self._initial_words=self._editor_snapshot()
        self.lifecycle=ScreenController(self.app,self.edit_frm,{'<Escape>':lambda event:self.Cancel(self.app),
            '<Control-h>':lambda event:self.Open_synonyms(),'<Control-H>':lambda event:self.Open_synonyms()},
            context=self.context,on_window_close=lambda:self.Exit(self.app))
        self.bindings=self.lifecycle.bindings
        for sequence in ('<Control-t>','<Control-T>'):
            self.bindings.bind(sequence,lambda event:self.Tag_shortcut())
        for sequence in ('<Control-Shift-t>','<Control-Shift-T>'):
            self.bindings.bind(sequence,lambda event:self.Tag_shortcut(manage=True))
        self.lifecycle.add_cleanup(self._dispose)
        if self.edit_tbl.get_total_rows():
            self.edit_tbl.see(self.edit_tbl.get_total_rows() - 1, 0)
        configure_editor_dropdowns(self.edit_tbl, self.dropdown_set)
        color_editor_columns(self.edit_tbl, self.headers, self.lang_desc, self.learned_by)
        fit_editor_columns(self.edit_tbl, self.headers, self.lang_desc, self.learned_by)
        self.save_progress=SaveProgress(self.head_frm,self.translate)
        self.save_btn=self.head_frm.add_action('save',partial(self.Save,app,''))
        self.back_btn=self.head_frm.add_action('close',partial(self.Cancel,app))
        self.exit_btn=self.head_frm.add_action('exit',partial(self.Exit,app))
        sign_list = [self.translate('like'), self.translate('not like'), '=']
        self.sign_var = StringVar(master=self.app, value=self.translate('like'))
        self.filt_entry_var = StringVar(master=self.app)
        self.filt_col_var = StringVar(master=self.app, value=self.translate(self.lang_desc))
        filter_columns=[self.translate(name) for name in filterable_headers(self.headers,self.context.preferences.tags_enabled)]
        self.filt_frm = VocabularyFilter(self.head_frm, filter_columns, sign_list, self.filt_col_var, self.sign_var,
            self.filt_entry_var, self.translate, self.Filter, self.Reset_filter, self.Open_tag_filter, self._schedule_filter)
        self.lifecycle.trace(self.filt_col_var,'write',self._filter_column_changed)
        self.lifecycle.trace(self.sign_var,'write',self._schedule_filter)
        self.edit_tbl.MT.bind('<Double-Button-1>', self._add_row_below_table, add='+')
        self.edit_tbl.bind('<Control-p>', partial(self.Play_audio, app))
        self.edit_tbl.bind('<Control-r>', partial(self.Record_audio, app))
        self.edit_tbl.bind('<Control-s>', partial(self.Save, app))
        self.edit_tbl.extra_bindings('end_paste', self.Trace_multi_paste)
        self.edit_tbl.edit_validation(self.Validate_tag_cell)
        self.edit_tbl.readonly_columns(columns=[0], redraw=True)
        self.edit_tbl.extra_bindings('edit_cell', partial(self.Sync_changes, 0))
        arrange_editor(self.edit_frm, self.head_frm, action_frm, self.filt_frm, self.edit_tbl, {'wait': self.save_progress, 'save': self.save_btn, 'back': self.back_btn, 'exit': self.exit_btn, 'delete': self.Delete_words, 'synonyms': self.Open_synonyms, 'sort': self.Sort, 'unsort': self.Unsort, 'manage_tags':self.Open_tags, 'word_tags':self.Open_word_tags})
        self.edit_tbl.popup_menu_add_command(self.translate('Word tags'),self.Open_word_tags,index_menu=True,header_menu=False)
        self.edit_tbl.bind('<<SheetSelect>>',self._update_synonyms_button,add='+')
        self._update_status()
        if not self.context.preferences.tags_enabled:
            self.edit_tbl.hide_columns([self.headers.index('Tags'),self.headers.index('Tag count')],redraw=True)
            self.edit_frm._word_tags_button.grid_remove()
            self.edit_frm._manage_tags_button.grid_remove()
        play_effect('edit')

    def Validate_tag_cell(self,event):
        if event.column!=self.headers.index('Tags'):return event.value
        try:
            from app.repositories.tags import load_catalog,encode_tags,decode_tags
            catalog,_=load_catalog(self.context.tags_path(self.lang_desc),self.learned_by,self.lang_desc)
            frame=pd.DataFrame({'ID':[self.edit_tbl.get_cell_data(event.row,0)],'Tags':[event.value]})
            encoded=encode_tags(frame,catalog,self.learned_by,self.lang_desc,self.context.preferences.maximum_tags)
            decoded=decode_tags(encoded,self.context.tags_path(self.lang_desc),self.learned_by,self.lang_desc,
                target=self.context.preferences.tag_display_language=='Learning language')
            return decoded.Tags.iloc[0]
        except ValueError as error:
            message=error_text(error, self.translate)
            if hasattr(error,'tag'):message=message.format(tag=error.tag,word_id=error.word_id)
            messagebox.showerror(parent=self.app,title=self.translate('Tags'),message=message)
            return None

    def Delete_audio(self):
        if getattr(self, '_saving', False):
            return
        sel = self.edit_tbl.get_selected_cells()
        if not sel:
            return
        try:
            pygame.mixer.quit()
            rows = set((cell[0] for cell in sel))
            for row in rows:
                val = self.edit_tbl.get_cell_data(row, 0)
                if val in ('', None):
                    continue
                path_wav = Path(self.audio_folder) / f'{val}.wav'
                path_mp3 = Path(self.audio_folder) / f'{val}.mp3'
                for path in [path_mp3, path_wav]:
                    if exists(path):
                        os.remove(path)
                self.main_df.loc[self.main_df['ID'] == int(val), 'Audio'] = 'No audio'
                self.filt_df.loc[self.filt_df['ID'] == int(val), 'Audio'] = 'No audio'
                self.edit_tbl.set_cell_data(row, self.headers.index('Audio'), 'No audio')
        except Exception as e:
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=error_text(e, self.translate))
        finally:
            pygame.mixer.init()

    def Delete_words(self):
        if self._saving:
            return
        self.edit_tbl.close_text_editor(set_data=True)
        self.Sync_changes(1, '')
        rows = set(self.edit_tbl.get_selected_rows())
        rows.update(cell[0] for cell in self.edit_tbl.get_selected_cells())
        ids = {int(self.edit_tbl.get_cell_data(row, 0)) for row in rows
               if row < self.edit_tbl.get_total_rows() and self.edit_tbl.get_cell_data(row, 0) not in ('', None)}
        if not ids or not messagebox.askyesno(parent=self.app, title=self.translate('Delete selected words'),
                message=self.translate('Delete selected words? The change takes effect after saving.')):
            return
        self.main_df = self.main_df.loc[~self.main_df.ID.isin(ids)].reset_index(drop=True)
        self.main_df = add_columns(self.main_df,self.file_voc,self._synonym_counts)[self.headers]
        self.filt_df = self.filt_df.loc[~self.filt_df.ID.isin(ids)].reset_index(drop=True)
        if self.filt_flag:
            self.filt_df = self.main_df.loc[self.main_df.ID.isin(self.filt_df.ID)].copy()
        shown = self.filt_df if self.filt_flag else self.main_df
        self.edit_tbl.set_sheet_data(display_frame(shown[self.headers],self.translate).values.tolist(), reset_col_positions=False)
        self._update_status()

    def _selected_word_row(self):
        rows = set(self.edit_tbl.get_selected_rows())
        rows.update(cell[0] for cell in self.edit_tbl.get_selected_cells())
        return next((row for row in sorted(rows) if 0<=row<self.edit_tbl.get_total_rows()
            and self.edit_tbl.get_cell_data(row,0) not in ('',None)),None)

    def _update_synonyms_button(self,event=None):
        self._update_sort_button()
        if not hasattr(self.edit_frm,'_synonyms_button'):return
        state='normal' if not self._saving and self._selected_word_row() is not None else 'disabled'
        button=self.edit_frm._synonyms_button
        if button.cget('state')!=state:button.configure(state=state)
        if hasattr(self.edit_frm,'_word_tags_button'):
            self.edit_frm._word_tags_button.configure(state=state)

    def Open_synonyms(self):
        if self._saving:return
        row=self._selected_word_row()
        if row is None:return
        try:
            from app.vocabulary.editor_synonyms import SynonymsDialog
            SynonymsDialog(self.app, self.file_voc, self.edit_tbl.get_cell_data(row, 0),
                           self.lang_desc, self.learned_by, on_changed=self._synonyms_changed)
        except (OSError, ValueError) as error:
            messagebox.showerror(parent=self.app, title=self.translate('Synonyms'), message=error_text(error, self.translate))

    def Open_tags(self):
        if self._saving or not self.context.preferences.tags_enabled:return
        try:
            from app.vocabulary.editor_tags import TagsDialog
            dialog=getattr(self, '_tags_dialog', None)
            if dialog is not None and dialog.winfo_exists():
                dialog.lift()
                return
            self._tags_dialog=TagsDialog(self.app,self.lang_desc,context=self.context)
        except (OSError, ValueError, UnicodeError) as error:
            report_error(error,operation='open tag catalog')
            message=(self.translate(error.message).format(row=error.row)
                     if hasattr(error,'message') and hasattr(error,'row') else error_text(error, self.translate))
            messagebox.showerror(parent=self.app,title=self.translate('Manage tags'),message=message)

    def Tag_shortcut(self, *, manage=False):
        if self._saving or self.lifecycle.closed or not self.context.preferences.tags_enabled:
            return 'break'
        if self.app.grab_current() is None and not any(
                isinstance(window,cst.CTkToplevel) and window.winfo_viewable()
                for window in self.app.winfo_children()):
            if manage:self.Open_tags()
            else:self.Open_word_tags()
        return 'break'

    def Open_word_tags(self):
        if self._saving or not self.context.preferences.tags_enabled:return
        row=self._selected_word_row()
        if row is None:return
        try:
            from app.vocabulary.editor_tag_picker import WordTagsDialog
            self.edit_tbl.close_text_editor(set_data=True)
            self.Sync_changes(1,'')
            identifier=int(self.edit_tbl.get_cell_data(row,0))
            word=self.main_df.set_index('ID').loc[identifier]
            def apply(value):
                if self._saving or self.lifecycle.closed:return
                self.Sync_changes(1,'')
                self.main_df.loc[self.main_df.ID.eq(identifier),'Tags']=value
                for display_row,data in enumerate(self.edit_tbl.get_sheet_data()):
                    if str(data[0])==str(identifier):
                        self.edit_tbl.set_cell_data(display_row,self.headers.index('Tags'),value)
                if self.filt_flag:self.Filter()
                else:self.Refresh()
            WordTagsDialog(self.app,self.lang_desc,identifier,str(word[self.lang_desc]),
                           word['Tags'],apply,context=self.context)
        except (OSError,ValueError) as error:
            message=error_text(error, self.translate)
            if hasattr(error,'row'):message=message.format(row=error.row)
            messagebox.showerror(parent=self.app,title=self.translate('Word tags'),message=message)

    def _filter_column_changed(self,*args):
        self.filt_frm.set_tag_mode(self.filt_col_var.get()==self.translate('Tags'))
        if self.filt_col_var.get()!=self.translate('Tags'):
            operators=['<','=','>'] if self.filt_col_var.get()==self.translate('Tag count') else [self.translate('like'),self.translate('not like'),'=']
            self.filt_frm.operator.configure(values=operators)
            if self.sign_var.get() not in operators:self.sign_var.set('=' if len(operators) and operators[0]=='<' else operators[0])
        self.filt_frm.query.configure(placeholder_text=self.translate('Synonym filter: 1 = yes, 0 = no')
            if self.filt_col_var.get()==self.translate('Has synonyms') else self.translate('Search'))
        self._schedule_filter()

    def _cancel_filter(self):
        if self._filter_job is not None:
            self.lifecycle.cancel_after(self._filter_job)
            self._filter_job = None

    def _schedule_filter(self, *_):
        if self._resetting_filter or self._saving or self.lifecycle.closed:return
        self._cancel_filter()
        def apply():
            self._filter_job = None
            # A half-entered numeric condition should not display an error popup.
            if self.filt_col_var.get()==self.translate('Tag count'):
                value=self.filt_entry_var.get().strip()
                if not value.isascii() or not value.isdigit():return
            self.Filter()
        self._filter_job = self.lifecycle.after(250, apply)

    def Reset_filter(self):
        if self._saving:return
        self._cancel_filter()
        self._resetting_filter=True
        try:
            self.filt_entry_var.set('')
            self.filt_frm.set_tag_selection('')
            self.sign_var.set(next(iter(self.filt_frm.tag_operators)) if self.filt_frm.tag_mode else
                '=' if self.filt_col_var.get()==self.translate('Tag count') else self.translate('like'))
            self.Refresh()
        finally:
            self._resetting_filter=False

    def Open_tag_filter(self):
        if self._saving or not self.context.preferences.tags_enabled:return
        try:
            from app.vocabulary.editor_tag_picker import WordTagsDialog
            def apply(value):
                if self._saving or self.lifecycle.closed:return
                self.filt_frm.set_tag_selection(value)
                self.Filter()
            dialog=WordTagsDialog(self.app,self.lang_desc,'','',self.filt_frm.tag_selection,
                apply,context=self.context,selection_only=True)
            self.lifecycle.own_dialog(dialog)
        except (OSError,ValueError) as error:
            message=error_text(error, self.translate)
            if hasattr(error,'row'):message=message.format(row=error.row)
            messagebox.showerror(parent=self.app,title=self.translate('Filter tags'),message=message)

    def _synonyms_changed(self):
        if self._saving or not self.edit_frm.winfo_exists():return
        if self.filt_flag:self.Filter()
        else:self.Refresh()

    def Exit(self, app):
        if self.lifecycle.closed:return
        if self._saving:
            self._close_after_save = True
            self._cancel_save()
            return
        if self._can_leave(save_for_exit=True):self.lifecycle.finish(app.destroy)

    def Filter(self):
        if self._saving:
            return
        self._cancel_filter()
        self.Sync_changes(1, '')
        val = self.filt_entry_var.get().strip().casefold()
        if self.filt_col_var.get() not in self.transl_headers:
            raise ValueError('Selected column not found')
        idx = self.transl_headers.index(self.filt_col_var.get())
        column = self.headers[idx]
        if column=='Has synonyms':
            val={'1':'●','true':'●','0':'—','false':'—'}.get(val,val)
        if column=='Tag count' and (not val.isascii() or not val.isdigit()):
            messagebox.showerror(parent=self.app,title=self.translate('Tags'),message=self.translate('Enter a whole non-negative number.'))
            return
        if column=='Tags':
            from app.vocabulary.tags_data import filter_by_tags
            mode=self.filt_frm.tag_operators.get(self.sign_var.get())
            if mode is None:return
            matched=filter_by_tags(self.main_df,self.filt_frm.tag_selection,mode)
        else:
            operator = {'=': 'equals','<':'less','>':'greater', self.translate('like'): 'contains', self.translate('not like'): 'excludes'}.get(self.sign_var.get())
            if operator is None:return
            matched = filter_vocabulary(display_frame(self.main_df,self.translate), column, operator, val)
        self.filt_df = self.main_df.loc[self.main_df.ID.isin(matched.ID)].copy()
        if self._sort_spec:self.filt_df=sort_vocabulary(self.filt_df,*self._sort_spec)
        self.filt_flag = 1
        self.edit_tbl.set_sheet_data(display_frame(self.filt_df,self.translate).values.tolist(), reset_col_positions=False)
        if self.edit_tbl.get_total_rows():self.edit_tbl.see(0,0)
        self._update_status()

    def Sort(self, descending=None):
        if self._saving:return
        selected=self.edit_tbl.get_currently_selected()
        index=getattr(selected,'column',None) if getattr(selected,'type_',None) in ('cell','cells','column','columns') else None
        if index is None:
            columns=sorted(self.edit_tbl.get_selected_columns())
            cells=sorted(self.edit_tbl.get_selected_cells())
            index=columns[0] if columns else cells[0][1] if cells else self.headers.index(self._sort_spec[0]) if self._sort_spec else self.transl_headers.index(self.filt_col_var.get())
        column=self.headers[index]
        if descending is None:
            from app.ui.sorting import next_sort
            state=next_sort(self._sort_spec,column)
            if state is None:
                self.Unsort()
                return
            descending=state[1]
        self.Sync_changes(1,'')
        self._sort_spec=(column,descending)
        shown=self.filt_df if self.filt_flag else self.main_df
        self.filt_df=sort_vocabulary(shown,column,descending)
        self.filt_flag=1
        self.edit_tbl.set_sheet_data(display_frame(self.filt_df[self.headers],self.translate).values.tolist(),reset_col_positions=False)
        self.edit_tbl.select_column(index)
        if len(self.filt_df):self.edit_tbl.see(0,0)
        self._update_status()

    def Refresh(self):
        if self._saving:
            return
        self.Sync_changes(1, '')
        self.filt_flag = 0
        self._sort_spec = None
        self.filt_df = self.main_df.copy()
        self.edit_tbl.set_sheet_data(display_frame(self.main_df,self.translate).values.tolist(), reset_col_positions=False)
        if self.edit_tbl.get_total_rows() > 0:
            self.edit_tbl.see(self.edit_tbl.get_total_rows() - 1, 0)
        self.edit_tbl.update_idletasks()
        self._update_status()

    def Unsort(self):
        if self._saving or self._sort_spec is None:return
        self.Sync_changes(1,'')
        self._sort_spec=None
        visible=set(self.filt_df.ID) if self.filt_flag else set(self.main_df.ID)
        self.filt_df=self.main_df.loc[self.main_df.ID.isin(visible)].copy()
        self.edit_tbl.set_sheet_data(display_frame(self.filt_df[self.headers],self.translate).values.tolist(),reset_col_positions=False)
        self._update_status()

    def Sync_changes(self, run_force, event):
        if self._saving:
            return
        if self.filt_flag != 1 and run_force != 1:
            return
        self.main_df, updated = merge_table_edits(self.main_df, canonical_rows(self.edit_tbl.get_sheet_data(),self.headers,self.translate), self.headers, self.lang_desc, self.learned_by)
        self.main_df = add_columns(self.main_df,self.file_voc,self._synonym_counts)[self.headers]
        updated = self.main_df.set_index('ID').loc[updated.ID].reset_index()[self.headers]
        if self.filt_flag == 1:
            self.filt_df = updated

    def _add_row_below_table(self, event):
        if self.edit_tbl.MT.identify_row(y=event.y, allow_end=False) is None:
            self.New_row(event)
        elif self.edit_tbl.identify_column(event,allow_end=False)==self.headers.index('Tags'):
            self.edit_tbl.select_cell(self.edit_tbl.MT.identify_row(y=event.y,allow_end=False),self.headers.index('Tags'))
            self.Open_word_tags()
            return 'break'

    def New_row(self, event):
        if self._saving:
            return
        self.Sync_changes(1, '')
        new_row = {col: self.default_vals[idx] for idx, col in enumerate(self.headers)}
        new_row['ID'] = self._next_id
        self._next_id += 1
        upd_data = self.edit_tbl.get_sheet_data()
        upd_data.append([new_row[col] for col in self.headers])
        self.filt_df = pd.DataFrame(upd_data, columns=self.headers)
        self.edit_tbl.set_sheet_data(display_frame(self.filt_df,self.translate).values.tolist(), reset_col_positions=False)
        self.edit_tbl.see(self.edit_tbl.get_total_rows() - 1, 0)
        self.Sync_changes(1, '')
        self._update_status()

    def Cancel(self, app):
        if self.lifecycle.closed:return
        if self._saving:
            self._cancel_save()
            return
        if self._can_leave():self.lifecycle.finish(self._return_home)

    def _can_leave(self,*,save_for_exit=False):
        if self.lifecycle.closed:return False
        self.Sync_changes(1,'')
        def save():
            self.Save(self.app,'')
            self._close_after_save=save_for_exit and self._saving
        return self.lifecycle.can_leave(not self._editor_snapshot().equals(self._initial_words),save)

    def _return_home(self):
        self.edit_frm.destroy()
        self.context.go_home()

    def _editor_snapshot(self):
        return self.main_df.drop(columns=list(SYNONYM_COLUMNS),errors='ignore').sort_values('ID').reset_index(drop=True).astype(str)

    def Trace_multi_paste(self, event):
        if self._saving:
            return
        if len(event.added.rows) > 0:
            new_rows = sorted(event.added.rows['table'].keys())
            for k, i in enumerate(new_rows):
                for j in range(len(self.headers)):
                    if str(self.edit_tbl.get_cell_data(i, j)) == '' and self.default_vals[j] != '':
                        self.edit_tbl.set_cell_data(i, j, value=self.default_vals[j])
                self.edit_tbl.set_cell_data(i, 0, value=self._next_id)
                self._next_id += 1
        if len(event.added.columns) > 0:
            new_cols = sorted(event.added.columns['table'].keys(), reverse=True)
            for i in new_cols:
                self.edit_tbl.del_column(i)
        self.Sync_changes(1, '')
        self._update_status()

    def Save(self, app, event):
        if self.lifecycle.closed or self._saving:
            return
        try:
            self.edit_tbl.close_text_editor(set_data=True)
            self.Sync_changes(1, '')
            from app.repositories.tags import load_catalog
            from app.vocabulary.tags_data import validate_word_tags
            catalog,_=load_catalog(self.context.tags_path(self.lang_desc),self.learned_by,self.lang_desc)
            self.main_df=validate_word_tags(self.main_df,catalog,self.learned_by)
            exclude_cols = ['Part of Speech', 'Tags', 'ID', 'Repetition', 'Next repetition',*SYNONYM_COLUMNS]
            cols_to_check = [c for c in self.main_df.columns if c not in exclude_cols]
            if not self.main_df[cols_to_check].ne('').all().all():
                messagebox.showerror(parent=app, title=self.translate('Error'), message=self.translate('All columns gotta be filled.'))
                return
            snapshot = self.main_df.drop(columns=list(SYNONYM_COLUMNS)).copy(deep=True)
            self._set_saving(True)
            worker_context=replace(self.context,on_home=None,preferences_frame=None)
            self._task = BackgroundTask(self.edit_frm,
                lambda cancelled, progress: save_course(snapshot, self.file_voc, self.lang_desc,
                    self.audio_folder,self._revision,cancelled,progress,context=worker_context),
                self._save_succeeded, self._save_failed, self._save_progress).start()
        except Exception as error:
            report_error(error, operation='vocabulary screen')
            if self._saving:
                self._set_saving(False)
            message=error_text(error, self.translate)
            if hasattr(error,'tag'):message=message.format(tag=error.tag,word_id=error.word_id)
            messagebox.showerror(parent=app, title=self.translate('Error'), message=message)

    def _set_saving(self, saving):
        self._saving = saving
        self._update_synonyms_button()
        self.edit_frm._manage_tags_button.configure(state='disabled' if saving else 'normal')
        self.edit_frm._delete_button.configure(state='disabled' if saving else 'normal')
        if saving:
            self.save_btn.grid_remove()
            self.filt_frm.grid_remove()
            self.head_frm.refresh_action('close',text=self.translate('Stop saving'),command=self._cancel_save)
            self.save_progress.update_progress(0,len(self.main_df))
            self.save_progress.grid()
            self.edit_tbl.disable_bindings()
            self.exit_btn.configure(state='disabled')
            self._mixer_active = bool(pygame.mixer.get_init())
            pygame.mixer.quit()
        else:
            self.save_progress.grid_remove()
            self.head_frm.refresh_action('close',text=self.translate('Close'),command=partial(self.Cancel,self.app),state='normal')
            self.exit_btn.configure(state='normal')
            self.edit_tbl.enable_bindings(s.tbl_bind)
            restore_after_save_error(self.save_btn, self.back_btn, self.filt_frm)
            if self._mixer_active:
                try:
                    pygame.mixer.init()
                except pygame.error:
                    pass

    def _save_progress(self, completed, total):
        self.save_progress.update_progress(completed,total)

    def _cancel_save(self):
        if self._task is not None:
            self._task.cancel()
            self.back_btn.configure(state='disabled')

    def _save_succeeded(self, result):
        self._set_saving(False)
        self._initial_words=self._editor_snapshot()
        play_effect('saved')
        if self._close_after_save:
            self.Exit(self.app)
        else:
            self.Cancel(self.app)

    def _save_failed(self, error):
        self._set_saving(False)
        self._close_after_save=False
        if not isinstance(error, CancelledError):
            message=error_text(error, self.translate)
            if hasattr(error,'tag'):message=message.format(tag=error.tag,word_id=error.word_id)
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=message)

    def _dispose(self, event=None):
        if self._task is not None:
            self._task.close()

    def Load(self):
        self.main_df = self.main_df.loc[:, self.headers].copy()
        self.edit_tbl.set_sheet_data(display_frame(self.main_df,self.translate).values.tolist(), reset_col_positions=False)
        col_1 = self.main_df.columns.get_loc('Next repetition')
        col_2 = self.main_df.columns.get_loc('Repetition')
        self.edit_tbl.highlight_columns(columns=[col_1, col_2], bg=READONLY_BACKGROUND, fg='#48615f')
        self.edit_tbl.readonly_columns(columns=[0, col_1, col_2])
        self.filt_df = self.main_df.copy()

    def Record_audio(self, app, event):
        if self._saving:
            return
        sel = self.edit_tbl.get_selected_cells()
        if not sel:
            return
        try:
            row = min((cell[0] for cell in sel))
            id = self.edit_tbl.get_cell_data(row, 0)
            lbl_1 = self.edit_tbl.get_cell_data(row, 1)
            lbl_2 = self.edit_tbl.get_cell_data(row, 2)
            lbl_3 = '' if self.lang_desc == 'Spanish' else self.edit_tbl.get_cell_data(row, 3)
            s.Clear_tops(app)
            top=AppDialog(app)
            pywinstyles.apply_style(top, 'dark')
            AudioRecorderPlayer(top, lbl_1, lbl_2, lbl_3, id, row, self.edit_tbl, self.main_df, self.audio_folder, self.lang_desc)
        except Exception as error:
            report_error(error, operation='vocabulary screen')
            messagebox.showerror(parent=app, title=self.translate('Error'), message=error_text(error, self.translate))

    def Play_audio(self, app, event):
        if self._saving:
            return
        try:
            sel = self.edit_tbl.get_selected_cells(get_rows=False)
            if len(sel) != 0:
                row_idx = min((cell[0] for cell in sel))
                val = self.edit_tbl.get_cell_data(row_idx, 0)
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.stop()
                for ext in ['mp3', 'wav']:
                    file = str(Path(self.audio_folder) / f'{val}.{ext}')
                    if exists(file):
                        pygame.mixer.music.load(file)
                        pygame.mixer.music.play()
                        break
                else:
                    messagebox.showerror(parent=app, title=self.translate('Error'), message=self.translate('Audio-error'))
        except (OSError, pygame.error) as error:
            messagebox.showerror(parent=app, title=self.translate('Error'), message=self.translate('Audio-error') + '\n' + error_text(error, self.translate))

    def _update_sort_button(self):
        if hasattr(self.edit_frm,'_sort_button'):
            from app.ui.sorting import sort_arrow
            key=self._sort_spec[0] if self._sort_spec else None
            selected=bool(self.edit_tbl.get_selected_cells() or self.edit_tbl.get_selected_columns()
                          or self.edit_tbl.get_selected_rows())
            self.edit_frm._sort_button.configure(text=self.translate('Sort')+' '+sort_arrow(self._sort_spec,key),
                state='normal' if not self._saving and (selected or self._sort_spec is not None) else 'disabled')

    def _update_status(self):
        self._update_synonyms_button()
        self.edit_tbl.headers([self.translate(name)+(' '+('↓' if self._sort_spec[1] else '↑')
            if self._sort_spec and self._sort_spec[0]==name else '') for name in self.headers])
        if hasattr(self.edit_frm, '_row_count'):
            self.edit_frm._row_count.configure(text=f"{self.edit_tbl.get_total_rows()} / {len(self.main_df)}  ·  {self.translate('Number of words')}")

def Edit(app, lang, *, context=None):
    return EditorController(app,lang,context=context)

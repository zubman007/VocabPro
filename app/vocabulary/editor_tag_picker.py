"""Searchable multiple selection of a word's tags from the saved catalog."""
from tkinter import messagebox
import customtkinter as cst

from app.repositories.tags import load_catalog
from app.vocabulary.tags_data import normalize_tags, validate_word_tags
from app.ui.components.app_dialog import AppDialog
from app.ui.components.search_filter_panel import SearchFilterPanel
from app.ui.components.shortcut_hint import ShortcutHint
from app.ui.theme import FONT, TEXT
import pandas as pd


class WordTagsDialog(AppDialog):
    def __init__(self, owner, language, word_id, heading, value, on_apply, *, context=None, selection_only=False):
        if context is not None:context.bind(owner)
        super().__init__(owner)
        self.translate=self.app_context.translate
        self.language,self.word_id,self.on_apply=language,word_id,on_apply
        self.learned_by=self.app_context.preferences.learned_by
        try:
            self.catalog,_=load_catalog(self.app_context.tags_path(language),self.learned_by,language)
        except (OSError,ValueError):
            self.destroy()
            raise
        self.selected={tag.casefold() for tag in normalize_tags(value).split(', ') if tag}
        for _,row in self.catalog.iterrows():
            if row[self.language].casefold() in self.selected:self.selected.add(row[self.learned_by].casefold())
        self.selection_only=selection_only
        self.title(self.translate('Filter tags' if selection_only else 'Word tags'))
        self.geometry('820x650')
        self.minsize(620,480)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.add_heading(self.translate('Filter tags') if selection_only else self.translate('Word tags')+' · '+heading,
            self.translate('Select tags, then choose the matching rule and press Filter in the editor.' if selection_only
                else 'Select any number of tags. Apply replaces the tags for this word; save the vocabulary to keep changes.'))
        self.query=cst.StringVar(master=self)
        self.search=SearchFilterPanel(self,self.translate,placeholder='Search tags',query_var=self.query,on_change=self.render)
        self.search.grid(row=1,sticky='ew',padx=20,pady=8)
        self.list=cst.CTkScrollableFrame(self,fg_color='#e9e0cd',corner_radius=18)
        self.list.grid(row=2,sticky='nsew',padx=20,pady=8)
        self.list.grid_columnconfigure(0,weight=1)
        self.list._parent_canvas.bind('<Configure>',self._resize,add='+')
        self.shortcuts=ShortcutHint(self,'Word tags',self.translate,rounded=True)
        self.shortcuts.grid(row=3,sticky='ew',padx=20,pady=(0,4))
        self.add_actions(self,[('Clear selection',self.clear),('Close',self.destroy),('Apply',self.apply)],
                         self.translate,row=4,pady=(10,20))
        for sequence in ('<Control-f>','<Control-F>'):
            self.bind(sequence,self.focus_search)
        self.bind('<Control-Return>',self.apply)
        self.search.query.bind('<Control-Return>',self.apply)
        self.apply_background('editor_warm_v1.png')
        self.render()
        self.after(50,lambda:self.present(modal=True))

    def render(self):
        for widget in self.list.winfo_children():widget.destroy()
        self.checkboxes=[]
        query=self.query.get().strip().casefold()
        ordered=self.catalog.assign(_selected=self.catalog[self.learned_by].str.casefold().isin(self.selected)).sort_values(['_selected','ID'],ascending=[False,True],key=lambda col:pd.to_numeric(col) if col.name=='ID' else col)
        for _, row in ordered.iterrows():
            name,translation=row[self.learned_by],row[self.language]
            if query and query not in name.casefold() and query not in translation.casefold():continue
            variable=cst.BooleanVar(master=self,value=name.casefold() in self.selected)
            def toggle(key=name.casefold(),variable=variable):
                if variable.get():self.selected.add(key)
                else:self.selected.discard(key)
            label=(translation+' — '+name if translation and self.app_context.preferences.tag_display_language=='Learning language'
                   else name+(' — '+translation if translation else ''))
            checkbox=cst.CTkCheckBox(self.list,text=label,variable=variable,command=toggle,
                font=(FONT,16),text_color=TEXT,fg_color='#567b63')
            checkbox.grid(row=len(self.checkboxes),sticky='ew',padx=14,pady=8)
            checkbox._text_label.configure(justify='left')
            self.checkboxes.append(checkbox)
        if not self.checkboxes:
            cst.CTkLabel(self.list,text=self.translate('No tags found. Add tags in Manage tags.'),
                text_color=TEXT,fg_color='transparent',wraplength=450).grid(padx=14,pady=14)
        self.list.update_idletasks()
        self.list._parent_canvas.yview_moveto(0)
        self._resize()

    def _resize(self,event=None):
        width=self.list._parent_canvas.winfo_width()
        if width>80:
            wrap=max(100,width-80)
            for checkbox in self.checkboxes:
                if int(checkbox._text_label.cget('wraplength'))!=wrap:
                    checkbox._text_label.configure(wraplength=wrap)

    def clear(self):
        self.selected.clear()
        self.render()

    def focus_search(self,event=None):
        self.search.query.focus_set()
        return 'break'

    def apply(self,event=None):
        try:
            # Reload so a label deleted externally cannot slip through an older window.
            catalog,_=load_catalog(self.app_context.tags_path(self.language),self.learned_by,self.language)
            labels=[name for name in self.catalog[self.learned_by] if name.casefold() in self.selected]
            frame=pd.DataFrame({'ID':[self.word_id],'Tags':[', '.join(labels)]})
            value=validate_word_tags(frame,catalog,self.learned_by).Tags.iloc[0]
            if self.app_context.preferences.maximum_tags<len(labels) and not self.selection_only:
                raise ValueError('Maximum number of tags exceeded.')
            if self.app_context.preferences.tag_display_language=='Learning language':
                from app.vocabulary.tags_data import translated_tags
                mapping=dict(zip(catalog[self.learned_by].str.casefold(),catalog[self.language]))
                value=translated_tags(value,mapping).replace(' · ', ', ')
            self.on_apply(value)
        except (OSError,ValueError) as error:
            message=self.translate(str(error))
            if hasattr(error,'tag'):message=message.format(tag=error.tag,word_id=error.word_id)
            elif hasattr(error,'row'):message=message.format(row=error.row)
            messagebox.showerror(parent=self,title=self.translate('Word tags'),message=message)
            return 'break'
        self.destroy()
        return 'break'

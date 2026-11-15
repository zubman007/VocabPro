"""Common learning-session sidebar; lesson state belongs to its controller."""
import customtkinter as cst
from app.ui.theme import TEXT
from app.ui.module_style import (session_content,tool_button,SESSION_PAD,
    SESSION_HEADING,SESSION_TITLE_FONT,SESSION_COUNT_FONT)
from app.ui.components.shortcut_hint import ShortcutHint


class SessionPanel(cst.CTkFrame):
    def __init__(self,parent,translate,*,progress=False):
        super().__init__(parent)
        self.translate=translate
        self.content=session_content(self)
        self.heading=cst.CTkLabel(self.content,text=translate('Session overview'),
            font=SESSION_TITLE_FONT,text_color=SESSION_HEADING,anchor='w')
        self.heading.grid(row=0,sticky='ew',padx=SESSION_PAD,pady=(14,4))
        self.count=cst.CTkLabel(self.content,text='0',font=SESSION_COUNT_FONT,text_color=TEXT,anchor='w')
        self.count.grid(row=1,sticky='ew',padx=SESSION_PAD)
        self.progress=None
        if progress:
            self.progress=cst.CTkProgressBar(self.content,progress_color='#567b63',fg_color='#d8d4bf',height=8)
            self.progress.grid(row=3,sticky='ew',padx=SESSION_PAD,pady=(0,16))
            self.progress.set(0)

    def set_progress(self,completed,total):
        self.count.configure(text=f'{completed} / {total}')
        if self.progress is not None:self.progress.set(completed/total if total else 0)

    def add_action(self,caption,callback,*,row):
        button=tool_button(cst.CTkButton(self.content,text=self.translate(caption),command=callback))
        button.grid(row=row,sticky='ew',padx=SESSION_PAD,pady=4)
        return button

    def add_shortcuts(self,section,*,row,show_synonyms=True):
        hint=ShortcutHint(self.content,section,self.translate,show_synonyms,vertical=True)
        hint.grid(row=row,sticky='ew',padx=SESSION_PAD,pady=(6,12))
        return hint

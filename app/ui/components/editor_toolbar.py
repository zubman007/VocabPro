"""Shared editor count, contextual actions, shortcut hint and optional help."""
import customtkinter as cst
from app.ui.module_style import SESSION,tool_button
from app.ui.theme import FONT,TEXT,MUTED
from app.ui.components.shortcut_hint import ShortcutHint
from app.ui.surfaces import surface


class EditorToolbar(cst.CTkFrame):
    def __init__(self,parent,section,translate,*,action_columns=None,compact=False,tags_enabled=True):
        super().__init__(parent,fg_color=SESSION,corner_radius=16)
        self.translate=translate
        self.buttons={}
        self.action_columns=action_columns
        self.compact=compact
        self._compact_active=False
        self.grid_columnconfigure(0,weight=1)
        self.count=cst.CTkLabel(self,text='',font=(FONT,16),text_color=TEXT,anchor='w',justify='left')
        self.count.grid(row=0,column=0,sticky='ew',padx=12,pady=4)
        self.actions=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        self.actions.grid(row=0,column=1,sticky='e',padx=6,pady=8)
        self.shortcuts=ShortcutHint(self,section,translate,tags_enabled=tags_enabled)
        self.shortcuts.grid(row=1,column=0,columnspan=2,sticky='ew',padx=12,pady=(0,2))
        self.help=None
        self.bind('<Configure>',self._resize,add='+')

    def add_action(self,key,caption,callback,*,state='normal'):
        button=tool_button(cst.CTkButton(self.actions,text=self.translate(caption),command=callback,state=state))
        scale=button._get_widget_scaling()
        font=cst.CTkFont(family=FONT,size=round(14*scale))
        button.configure(width=max(140,font.measure(button.cget('text'))/scale+28))
        button.grid_propagate(False)
        columns=self.action_columns or len(self.buttons)+1
        button.grid(row=len(self.buttons)//columns,column=len(self.buttons)%columns,sticky='nsew',padx=6,pady=3 if self.action_columns else 0)
        self.buttons[key]=button
        return button

    def set_help(self,text):
        if self.help is None:
            self.help=cst.CTkLabel(self,font=(FONT,12),text_color=MUTED,justify='left',anchor='w')
            self.help.grid(row=2,column=0,columnspan=1 if self._compact_active else 2,sticky='ew',padx=12,pady=(0,4))
        self.help.configure(text=text)

    def attach_background(self,provider):
        return surface(self,provider)

    def _resize(self,event):
        if event.widget is not self._canvas:return
        scale=self._get_widget_scaling()
        width=max(120,int((event.width-self.actions.winfo_reqwidth())/scale)-36)
        compact=self.compact and width>=520
        if compact!=self._compact_active:
            self._compact_active=compact
            self.actions.grid_configure(rowspan=3 if compact else 1,pady=6 if compact else 8)
            self.shortcuts.grid_configure(columnspan=1 if compact else 2)
            self.shortcuts.configure(pady=2 if compact else 6)
            self.count.grid_configure(pady=(8,0) if compact else 4)
            if self.help is not None:self.help.grid_configure(columnspan=1 if compact else 2)
        if self.count.cget('wraplength')!=width:self.count.configure(wraplength=width)
        if self.help is not None:
            wrap=width if compact else max(120,int(event.width/scale)-24)
            if self.help.cget('wraplength')!=wrap:self.help.configure(wraplength=wrap)

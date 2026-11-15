"""Reusable search/filter controls, including working variable-backed placeholders."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT
from app.ui.module_style import tool_button
from app.ui.components.filter_option_menu import FilterOptionMenu


class SearchEntry(cst.CTkEntry):
    """CTk suppresses placeholders with textvariable; synchronize it explicitly."""
    def __init__(self,parent,variable,changed=None,**kwargs):
        self.variable,self.changed=variable,changed
        super().__init__(parent,**kwargs)
        self._trace=variable.trace_add('write',self._sync)
        self.bind('<KeyRelease>',self.read_value)
        self._paste_job=None
        for event in ('<<Paste>>','<<Cut>>'):
            self.bind(event,self._paste,add='+')
        self._sync(notify=False)

    def read_value(self,event=None):
        if self.variable.get()!=self.get():self.variable.set(self.get())

    def _paste(self,event=None):
        if self._paste_job is not None:self.after_cancel(self._paste_job)
        def read():
            self._paste_job=None
            self.read_value()
        self._paste_job=self.after_idle(read)

    def _sync(self,*_,notify=True):
        value=self.variable.get()
        if self.get()!=value:
            self.delete(0,'end')
            if value:self.insert(0,value)
        if notify and self.changed is not None:self.changed()

    def destroy(self):
        self.variable.trace_remove('write',self._trace)
        if self._paste_job is not None:self.after_cancel(self._paste_job)
        super().destroy()


class SearchFilterPanel(cst.CTkFrame):
    def __init__(self,parent,translate,*,placeholder='Search',query_var=None,
                 on_apply=None,on_change=None,on_reset=None,stacked=False):
        super().__init__(parent,fg_color='#ded4bf',corner_radius=16,border_width=0)
        self.translate,self.on_apply,self.stacked=translate,on_apply,stacked
        self.choices={}
        self.query_var=query_var if query_var is not None else cst.StringVar(master=self)
        self.query=SearchEntry(self,self.query_var,on_change,placeholder_text=translate(placeholder),
            height=40,width=260,font=(FONT,17),fg_color='#eee4d0',text_color=TEXT,
            border_color='#d6bea0',border_width=1,corner_radius=12)
        self.query.bind('<Return>',lambda event:self._submit())
        self.apply=(tool_button(cst.CTkButton(self,text=translate('Filter'),command=self._submit)) if on_apply else None)
        self.reset=(tool_button(cst.CTkButton(self,text=translate('Refresh'),command=on_reset)) if on_reset else None)
        self._layout()

    def add_choice(self,key,values,*,variable=None,kind='option',command=None,width=180,dropdown_font=None):
        options=dict(values=list(values),width=width,height=40,font=(FONT,17),text_color=TEXT,
            fg_color='#e8d7b5',dropdown_fg_color='#ded4bf',dropdown_text_color=TEXT,
            dropdown_hover_color='#c5d4bc',dropdown_font=dropdown_font or (FONT,19),corner_radius=12)
        if kind=='combo':
            widget=cst.CTkComboBox(self,state='readonly',command=command,button_color='#49736b',**options)
        else:
            widget=FilterOptionMenu(self,variable=variable,command=command,button_color='#cab38b',
                button_hover_color='#d9c39d',dynamic_resizing=False,**options)
        if values:
            selected=variable.get() if variable is not None else None
            widget.set(selected if selected in values else values[0])
        self.choices[key]=widget
        self._layout()
        return widget

    def _submit(self):
        if self.on_apply is not None:self.on_apply()
        return 'break'

    def _layout(self):
        count=len(self.choices)
        for column in range(self.grid_size()[0]):self.grid_columnconfigure(column,weight=0)
        for column,widget in enumerate(self.choices.values()):widget.grid(row=0,column=column,sticky='ew',padx=8,pady=12)
        column=count if self.stacked else count+1
        for widget in (self.apply,self.reset):
            if widget is not None:
                widget.grid(row=0,column=column,sticky='nsew',padx=8,pady=12)
                column+=1
        if self.stacked:
            self.query.grid(row=1,column=0,columnspan=max(1,column),sticky='ew',padx=8,pady=(0,12))
            self.grid_columnconfigure(0,weight=1)
        else:
            self.query.grid(row=0,column=count,sticky='ew',padx=8,pady=12)
            self.grid_columnconfigure(count,weight=1)

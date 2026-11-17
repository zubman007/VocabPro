"""Retained individual accuracy bars; zero observations have unknown accuracy."""
import customtkinter as cst
from app.core.context import get_context
from app.shared.localization_format import percent
from app.ui.theme import FONT,TEXT,SECTION_SURFACE
from app.statistics.components import DETAIL_ROW_COLORS


class ConjugationPersonsPanel(cst.CTkFrame):
    def __init__(self,parent,translate):
        super().__init__(parent,fg_color=SECTION_SURFACE,corner_radius=24)
        self.translate=translate;self._snapshot=None;self.labels=[]
        self.grid_columnconfigure(0,weight=1)
        self.title=cst.CTkLabel(self,text=translate('Accuracy by grammatical person'),font=(FONT,24,'bold'),
            text_color=TEXT,anchor='w',justify='left',height=0)
        self.title.grid(row=0,sticky='ew',padx=24,pady=(18,8))
        self.description=cst.CTkLabel(self,text=translate('Conjugation person statistics help'),font=(FONT,14),
            text_color='#665d48',anchor='w',justify='left',height=0)
        self.description.grid(row=1,sticky='ew',padx=24,pady=(0,12))
        self.body=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        self.body.grid(row=2,sticky='ew',padx=24,pady=(0,16));self.body.grid_columnconfigure(0,weight=1)
        self.bind('<Configure>',self._resize,add='+')

    def _resize(self,event):
        if event.widget is not self._canvas:return
        width=max(120,int(event.width/self._get_widget_scaling())-48)
        for label in (self.title,self.description,*self.labels):
            if label.cget('wraplength')!=width:label.configure(wraplength=width)

    def set_data(self,items):
        items=tuple(items or ())
        language=get_context(self).preferences.app_language
        snapshot=(items,language)
        if self._snapshot==snapshot:return
        for child in self.body.winfo_children():child.destroy()
        self.labels=[]
        if not items:
            label=cst.CTkLabel(self.body,text=self.translate('No individual results yet.'),font=(FONT,15),text_color=TEXT)
            label.grid(sticky='w');self.labels.append(label)
        for index,item in enumerate(items):
            attempts=item.successes+item.failures
            name=item.label+(' · '+self.translate('Inactive person') if not item.enabled else '')
            rate=percent(item.successes/attempts,language) if attempts else '—'
            text=(name+' · '+rate+' · '+self.translate('Recorded answers')+f': {attempts} · '+
                  self.translate('Correct answers')+f': {item.successes} · '+self.translate('Incorrect answers')+f': {item.failures}')
            row=cst.CTkFrame(self.body,fg_color=DETAIL_ROW_COLORS[index%2],corner_radius=16)
            row.grid(row=index,sticky='ew',pady=2);row.grid_columnconfigure(0,weight=1)
            label=cst.CTkLabel(row,text=text,font=(FONT,14),text_color=TEXT,anchor='w',justify='left',height=0,wraplength=700)
            label.grid(row=0,sticky='ew',padx=18,pady=(8,5));self.labels.append(label)
            bar=cst.CTkProgressBar(row,height=6,corner_radius=3,fg_color='#b5ad97',progress_color='#417766')
            bar.grid(row=1,sticky='ew',padx=18,pady=(0,8));bar.set(item.successes/attempts if attempts else 0)
        self._snapshot=snapshot

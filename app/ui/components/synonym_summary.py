"""Reusable, plain synonym rows with distinct source and translation typography."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT,MUTED


class SynonymSummary(cst.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color='transparent',corner_radius=0)
        self.grid_columnconfigure(0,weight=1)
        self.rows=[]
        self.value=None
        self.bind('<Configure>',self._resize,add='+')

    def set_text(self,value):
        if value==self.value:return
        self.value=value
        lines=value.splitlines()
        while len(self.rows)<len(lines):
            word=cst.CTkLabel(self,text='',height=0,font=(FONT,16,'bold'),text_color=TEXT,anchor='w',justify='left')
            translation=cst.CTkLabel(self,text='',height=0,font=(FONT,14),text_color=MUTED,anchor='w',justify='left')
            self.rows.append((word,translation))
        for index,(word,translation) in enumerate(self.rows):
            if index>=len(lines):
                word.grid_remove();translation.grid_remove();continue
            source,separator,target=lines[index].partition(' — ')
            word.configure(text=source)
            translation.configure(text=target)
            word.grid(row=index*2,column=0,sticky='ew',pady=(5,0))
            if separator:translation.grid(row=index*2+1,column=0,sticky='ew',pady=(0,4))
            else:translation.grid_remove()
        self._resize()

    def _resize(self,event=None):
        width=max(80,round(self.winfo_width()/self._get_widget_scaling())-4)
        for pair in self.rows:
            for label in pair:
                if label.cget('wraplength')!=width:label.configure(wraplength=width)

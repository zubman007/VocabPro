"""Compact editor progress card; counts processed rows before the final commit."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT,MUTED
from app.ui.module_style import SESSION,HEADER


class SaveProgress(cst.CTkFrame):
    def __init__(self,parent,translate):
        super().__init__(parent,fg_color=SESSION,bg_color=HEADER,corner_radius=16)
        self.translate=translate
        self.completed=self.total=0
        self.grid_columnconfigure((0,1),weight=1,uniform='progress')
        self.heading=cst.CTkLabel(self,text=translate('Saving and generating automatic attributes'),
            font=(FONT,16,'bold'),text_color=TEXT,fg_color='transparent',anchor='w',justify='left')
        self.heading.grid(row=0,column=0,columnspan=2,sticky='ew',padx=16,pady=(10,2))
        self.processed=cst.CTkLabel(self,font=(FONT,14),text_color=TEXT,fg_color='transparent',anchor='w',justify='left')
        self.processed.grid(row=1,column=0,sticky='ew',padx=(16,8),pady=(0,6))
        self.remaining=cst.CTkLabel(self,font=(FONT,14),text_color=MUTED,fg_color='transparent',anchor='e',justify='right')
        self.remaining.grid(row=1,column=1,sticky='ew',padx=(8,16),pady=(0,6))
        self.bar=cst.CTkProgressBar(self,height=8,fg_color='#becbb2',progress_color='#58766b',corner_radius=4)
        self.bar.grid(row=2,column=0,columnspan=2,sticky='ew',padx=16,pady=(0,12))
        self.bind('<Configure>',self._resize,add='+')
        self.update_progress(0,0)

    def update_progress(self,completed,total):
        self.total=max(0,int(total))
        self.completed=max(0,min(int(completed),self.total))
        self.processed.configure(text=f"{self.translate('Words processed')}: {self.completed} / {self.total}")
        self.remaining.configure(text=f"{self.translate('Words remaining')}: {self.total-self.completed}")
        self.bar.set(self.completed/self.total if self.total else 0)

    def _resize(self,event):
        if event.widget is not self._canvas:return
        width=max(120,int(event.width/self._get_widget_scaling())-32)
        self.heading.configure(wraplength=width)
        for label in (self.processed,self.remaining):label.configure(wraplength=max(60,width//2-8))

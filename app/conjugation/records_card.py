"""A compact, responsive record card with persistent new-record emphasis."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT


class ConjugationRecordsCard(cst.CTkFrame):
    def __init__(self,parent,translate):
        super().__init__(parent,fg_color='#dbe1cb',corner_radius=18,border_width=1,border_color='#a7b49a')
        self.translate=translate;self.new_record=False;self._snapshot=None
        self.grid_columnconfigure(0,weight=1)
        self.heading=cst.CTkLabel(self,text=translate('Practice records'),font=(FONT,15,'bold'),
            text_color='#355e59',anchor='w',height=0,justify='left')
        self.heading.grid(row=0,sticky='ew',padx=16,pady=(12,5))
        self.report=cst.CTkLabel(self,text='',font=(FONT,14),text_color=TEXT,anchor='w',height=0,justify='left')
        self.report.grid(row=1,sticky='ew',padx=16,pady=(0,12))
        self.bind('<Configure>',self._resize,add='+')

    def _resize(self,event):
        if event.widget is not self._canvas:return
        width=max(100,int(event.width/self._get_widget_scaling())-32)
        for label in (self.heading,self.report):
            if label.cget('wraplength')!=width:label.configure(wraplength=width)

    def set_state(self,session,baseline,tracking):
        streak=baseline.best_streak;correct=baseline.best_correct
        if tracking:
            streak=max(streak,session.best_streak)
            if session.correct:correct=max(correct or 0,session.correct)
        new=tracking and (session.best_streak>baseline.best_streak or session.correct>(baseline.best_correct or 0))
        snapshot=(session.correct,session.streak,streak,correct,new)
        if snapshot==self._snapshot:return
        self.new_record=new
        self.configure(fg_color='#f1dfad' if new else '#dbe1cb',border_color='#b78943' if new else '#a7b49a',
                       border_width=2 if new else 1)
        self.heading.configure(text=self.translate('New personal record') if new else self.translate('Practice records'),
                               text_color='#86551f' if new else '#355e59')
        self.report.configure(text=self.translate('All-time best streak: {count}').format(count=streak)+'\n'+
            self.translate('Most correct in one session: {count}').format(count=correct if correct is not None else '—'))
        self._snapshot=snapshot

"""Explicit language-person settings, separate from course switch drafts."""
from dataclasses import replace
from pathlib import Path
import customtkinter as cst
from app.conjugation.persons import Person, PersonConfiguration
from app.repositories.conjugation_persons import load_configuration, save_configuration
from app.shared.languages import LanguagePair
from app.shared.messages import error_text
from app.ui import messagebox
from app.ui.components.app_dialog import AppDialog
from app.ui.theme import FONT, TEXT, SECTION_SURFACE, SECTION_CONTROL


class PersonsDialog(AppDialog):
    def __init__(self,owner,language,*,files,source,translate):
        course=Path(files)/f'{LanguagePair(source,language).legacy_stem}_con.csv'
        config,revision=load_configuration(files,language,course)
        super().__init__(owner)
        self.translate,self.files=translate,Path(files)
        self.config,self.revision=config,revision
        self.initial=self.config
        self.saved=False
        self.rows=[]
        self.title(translate('Grammatical persons'))
        self.geometry('940x650');self.minsize(740,480)
        self.grid_columnconfigure(0,weight=1);self.grid_rowconfigure(1,weight=1)
        self.add_heading(translate('Grammatical persons'),translate('Conjugation person settings help'))
        self.body=cst.CTkScrollableFrame(self,fg_color=SECTION_SURFACE,corner_radius=18)
        self.body.grid(row=1,sticky='nsew',padx=20,pady=8)
        self.body.grid_columnconfigure(0,weight=1)
        self.error=cst.CTkLabel(self,text='',font=(FONT,14),text_color='#963f32',wraplength=700,justify='left')
        self.error.grid(row=2,sticky='ew',padx=24)
        footer=cst.CTkFrame(self,fg_color='transparent');footer.grid(row=3,sticky='ew',padx=20,pady=(4,16))
        self.add_actions(footer,[('Add person',self.add),('Save',self.save),('Close',self.close)],translate)
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.bind('<Escape>',lambda event:self.close())
        self.bind('<Control-s>',lambda event:self.save());self.bind('<Control-S>',lambda event:self.save())
        self.render()

    def configuration(self):
        persons=tuple(replace(row['person'],label=row['label'].get().strip(),enabled=row['enabled'].get()) for row in self.rows)
        selected=tuple(row['person'].id for row in self.rows if row['enabled'].get() and row['practice'].get())
        return PersonConfiguration(self.config.language,persons,selected)

    def render(self):
        for child in self.body.winfo_children():child.destroy()
        self.rows=[]
        for index,person in enumerate(self.config.persons):
            card=cst.CTkFrame(self.body,fg_color='#eee4d0',corner_radius=14)
            card.grid(row=index,sticky='ew',pady=4,padx=4);card.grid_columnconfigure(0,weight=1)
            label=cst.StringVar(value=person.label);enabled=cst.BooleanVar(value=person.enabled)
            practice=cst.BooleanVar(value=person.id in self.config.practice_person_ids)
            entry=cst.CTkEntry(card,textvariable=label,font=(FONT,17),text_color=TEXT,
                fg_color='#fffaef',border_color='#b7ac91',height=34)
            entry.grid(row=0,column=0,sticky='ew',padx=10,pady=10)
            active=cst.CTkCheckBox(card,text=self.translate('Active person'),variable=enabled,
                font=(FONT,14),text_color=TEXT,width=120)
            active.grid(row=0,column=1,padx=8)
            selected=cst.CTkCheckBox(card,text=self.translate('Practise'),variable=practice,
                font=(FONT,14),text_color=TEXT,width=120)
            selected.grid(row=0,column=2,padx=8)
            def toggle(enabled=enabled,practice=practice,selected=selected):
                if not enabled.get():practice.set(False)
                selected.configure(state='normal' if enabled.get() else 'disabled')
            active.configure(command=toggle);toggle()
            for column,(symbol,delta) in enumerate((('↑',-1),('↓',1)),3):
                cst.CTkButton(card,text=symbol,width=34,height=32,fg_color=SECTION_CONTROL,
                    command=lambda index=index,delta=delta:self.move(index,delta),
                    state='normal' if 0<=index+delta<len(self.config.persons) else 'disabled').grid(row=0,column=column,padx=(0,8))
            self.rows.append(dict(person=person,label=label,enabled=enabled,practice=practice,entry=entry))

    def add(self):
        config=self.configuration()
        person=Person.create('')
        self.config=replace(config,persons=(*config.persons,person))
        self.render();self.rows[-1]['entry'].focus_set()

    def move(self,index,delta):
        config=self.configuration();items=list(config.persons)
        if not 0<=index+delta<len(items):return
        items[index],items[index+delta]=items[index+delta],items[index]
        self.config=replace(config,persons=tuple(items));self.render()

    def save(self):
        try:
            config=self.configuration().validate()
            self.revision=save_configuration(self.files,config,self.revision)
        except (OSError,ValueError) as error:
            self.error.configure(text=error_text(error,self.translate));return False
        self.config=self.initial=config;self.saved=True
        self.destroy();return True

    def close(self):
        if self.configuration()!=self.initial:
            choice=messagebox.askyesnocancel(parent=self,title=self.translate('Grammatical persons'),
                                             message=self.translate('Save changes before leaving?'))
            if choice is None:return
            if choice:return self.save()
        self.destroy()


def open_persons(owner,language,*,files,source,translate):
    dialog=None
    try:
        dialog=PersonsDialog(owner,language,files=files,source=source,translate=translate)
        dialog.after(250,lambda:dialog.present(modal=True))
        owner.wait_window(dialog)
        return dialog.saved
    except (OSError,ValueError) as error:
        if dialog is not None and dialog.winfo_exists():dialog.destroy()
        messagebox.showerror(parent=owner,title=translate('Error'),message=error_text(error,translate))
        return False
    finally:
        if owner.winfo_exists() and isinstance(owner,AppDialog):owner.grab_set()

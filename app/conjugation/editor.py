"""Dynamic conjugation form editor with stable IDs and explicit saves."""
from tkinter import ttk
import customtkinter as cst
import pandas as pd
from app.core.context import get_context
from app.core.screen_controller import ScreenController
from app.repositories.conjugation import ConjugationDocument, conjugation_columns
from app.repositories.conjugation_persons import load_configuration
from app.shared.storage import save_csv
from app.shared.messages import error_text
from app.ui import messagebox
from app.ui import learning_layout as ui
from app.ui.training_layout import shell
from app.ui.surfaces import surface
from app.ui.components.editor_toolbar import EditorToolbar
from app.ui.components.search_filter_panel import SearchFilterPanel


class ConjugationEditor:
    def __init__(self,app,language,*,context=None):
        self.context=get_context(app,context);self.translate=self.context.translate
        self.app,self.language=app,language
        path=self.context.conjugation_path(language)
        self.config,_=load_configuration(self.context.files_dir,language,path)
        if not path.exists():
            save_csv(pd.DataFrame(columns=conjugation_columns(language,self.context.preferences.learned_by,self.config)),
                     path,sep=';',index=False,expect_missing=True)
        self.document=ConjugationDocument(path,language,self.context.preferences.learned_by,self.config)
        self.current=None;self.loaded={};self.applied_query=''
        ui_root=self._build_before_replace(app)
        self.view=ui_root
        self.lifecycle=ScreenController(app,self.view.root,{'<Control-s>':self.save,'<Control-S>':self.save,
            '<Escape>':self.back},context=self.context,on_window_close=self.exit_app)
        self.refresh()

    def _build_before_replace(self,app):
        from app.shared import settings as s
        s.Clear_frames(app)
        view=shell(app,'Edit conjugation','conjugation_background_v1.png',
                   [('save',self.save),('close',self.back),('exit',self.exit_app)])
        view.header.title_label.configure(text=self.translate('Edit conjugation')+' · '+self.translate(self.language))
        view.body.grid_columnconfigure(0,weight=2);view.body.grid_columnconfigure(1,weight=3)
        view.body.grid_rowconfigure(0,weight=1)
        listing=cst.CTkFrame(view.body,fg_color=ui.SURFACE,corner_radius=24)
        listing.grid(row=0,column=0,sticky='nsew',padx=(0,12))
        listing.grid_columnconfigure(0,weight=1);listing.grid_rowconfigure(1,weight=1)
        surface(listing,view.layer)
        filters=SearchFilterPanel(listing,self.translate,placeholder='Search',on_apply=self.filter,stacked=True)
        filters.grid(row=0,sticky='ew',padx=14,pady=12);view.query=filters.query
        holder=cst.CTkFrame(listing,fg_color='transparent');holder.grid(row=1,sticky='nsew',padx=14,pady=(0,14))
        holder.grid_columnconfigure(0,weight=1);holder.grid_rowconfigure(0,weight=1)
        style=ttk.Style(holder)
        style.configure('ConjugationEditor.Treeview',background='#eee4d0',fieldbackground='#eee4d0',
                        foreground=ui.TEXT,rowheight=34,font=(ui.FONT,13))
        view.tree=ttk.Treeview(holder,columns=('verb','translation'),show='headings',selectmode='browse',
                              style='ConjugationEditor.Treeview')
        for key,caption in (('verb','Verb'),('translation','Translation')):
            view.tree.heading(key,text=self.translate(caption));view.tree.column(key,width=160,minwidth=70)
        view.tree.grid(row=0,column=0,sticky='nsew')
        scrollbar=ttk.Scrollbar(holder,orient='vertical',command=view.tree.yview)
        scrollbar.grid(row=0,column=1,sticky='ns');view.tree.configure(yscrollcommand=scrollbar.set)
        horizontal=ttk.Scrollbar(holder,orient='horizontal',command=view.tree.xview)
        horizontal.grid(row=1,column=0,sticky='ew');view.tree.configure(xscrollcommand=horizontal.set)
        view.tree.bind('<<TreeviewSelect>>',self.select)
        view.form=cst.CTkScrollableFrame(view.body,fg_color=ui.SURFACE,corner_radius=24)
        view.form.grid(row=0,column=1,sticky='nsew');view.form.grid_columnconfigure(0,weight=1)
        surface(view.form._parent_frame,view.layer)
        view.fields={}
        captions={self.language:self.translate('Verb'),self.document.learned_by:self.translate('Translation'),
                  'Description':self.translate('Description'),**{p.id:p.label for p in self.config.active}}
        for index,key in enumerate(self.document.fields):
            cst.CTkLabel(view.form,text=captions[key],font=(ui.FONT,15),text_color=ui.TEXT,
                         anchor='w',justify='left',wraplength=420).grid(row=index*2,sticky='ew',padx=18,pady=(10,2))
            widget=cst.CTkEntry(view.form,font=(ui.FONT,17),height=36,fg_color='#fffaef',text_color=ui.TEXT)
            widget.grid(row=index*2+1,sticky='ew',padx=18,pady=(0,4));view.fields[key]=widget
        def resize_form(event):
            width=max(100,int(event.width/view.form._get_widget_scaling())-36)
            for child in view.form.winfo_children():
                if isinstance(child,cst.CTkLabel):child.configure(wraplength=width)
        view.form.bind('<Configure>',resize_form,add='+')
        view.tools=EditorToolbar(view.body,'Conjugation editors',self.translate,action_columns=3)
        view.tools.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(10,0))
        view.tools.attach_background(view.layer)
        for key,caption,callback in (('add','Add verb',self.add),('delete','Delete verb',self.delete),('apply','Apply',self.apply)):
            view.tools.add_action(key,caption,callback)
        return view

    def values(self):return {key:widget.get() for key,widget in self.view.fields.items()}

    def show(self,identifier):
        self.current=identifier
        row=self.document.verb(identifier) if identifier is not None else dict.fromkeys(self.document.fields,'')
        for key,widget in self.view.fields.items():
            widget.delete(0,'end');widget.insert(0,row.get(key,''))
        self.loaded=self.values()
        for key in ('delete','apply'):self.view.tools.buttons[key].configure(state='normal' if identifier is not None else 'disabled')

    def refresh(self,preferred=None):
        query=self.view.query.get().strip().casefold()
        self.applied_query=self.view.query.get()
        frame=self.document.frame
        if query:
            frame=frame.loc[frame[list(self.document.fields)].apply(lambda col:col.str.casefold().str.contains(query,regex=False)).any(axis=1)]
        tree=self.view.tree;tree.delete(*tree.get_children())
        for row in frame.to_dict('records'):
            tree.insert('','end',iid=row['ID'],values=(row[self.language],row[self.document.learned_by]))
        ids=list(frame.ID)
        identifier=preferred if preferred in ids else self.current if self.current in ids else ids[0] if ids else None
        self.show(identifier)
        if identifier is not None:tree.selection_set(identifier);tree.see(identifier)
        self.view.tools.count.configure(text=f'{len(frame)} / {len(self.document.frame)} · '+self.translate('Number of verbs'))

    def _leave_form(self):
        if self.current is None or self.values()==self.loaded:return True
        choice=messagebox.askyesnocancel(parent=self.app,title=self.translate('Edit conjugation'),
                                          message=self.translate('Apply changes to the current verb?'))
        return self.apply(refresh=False) if choice is True else choice is False

    def apply(self,event=None,*,refresh=True):
        if self.current is None:return True
        try:self.document.update(self.current,self.values())
        except ValueError as error:self.error(error);return False
        self.loaded=self.values()
        if refresh:self.refresh(self.current)
        return True

    def select(self,event=None):
        selection=self.view.tree.selection()
        if selection and selection[0]!=self.current:
            if self._leave_form():self.show(selection[0])
            elif self.current is not None:self.view.tree.selection_set(self.current)

    def filter(self):
        if self._leave_form():self.refresh()
        else:
            self.view.query.delete(0,'end');self.view.query.insert(0,self.applied_query)

    def add(self):
        if not self._leave_form():return
        identifier=self.document.add();self.view.query.delete(0,'end');self.refresh(identifier)
        self.view.fields[self.language].focus_set()

    def delete(self):
        if self.current is not None and messagebox.askyesno(parent=self.app,title=self.translate('Delete verb'),
                message=self.translate('Delete this verb and its answer history?')):
            self.document.delete(self.current);self.current=None;self.refresh()

    def save(self,event=None,*,close=True):
        if self.lifecycle.closed:return False
        if self.current is not None and self.values()!=self.loaded and not self.apply(refresh=False):return False
        try:self.document.save()
        except (OSError,ValueError) as error:self.error(error);return False
        if close:self.lifecycle.finish(self.context.go_home)
        return True

    def _can_leave(self):
        if self.lifecycle.closed:return False
        dirty=not self.document.frame.equals(self.document.initial) or self.values()!=self.loaded
        return self.lifecycle.can_leave(dirty,lambda:self.save(close=False))

    def back(self,event=None):
        if self._can_leave():self.lifecycle.finish(self.context.go_home)

    def exit_app(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def error(self,error):
        messagebox.showerror(parent=self.app,title=self.translate('Error'),message=error_text(error,self.translate))


def Edit_conjugation(app,language,*,context=None):
    context=get_context(app,context)
    if not context.conjugation_enabled(language):return None
    from app.shared.languages import legacy_name
    language=legacy_name(language)
    try:return ConjugationEditor(app,language,context=context)
    except (OSError,ValueError,KeyError) as error:
        messagebox.showerror(parent=app,title=context.translate('Error'),message=error_text(error,context.translate))
        return None

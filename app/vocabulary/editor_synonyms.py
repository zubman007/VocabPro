"""Searchable synonym editor with explicit saving and navigation between words."""
from app.shared.messages import error_text
from app.ui import messagebox
import customtkinter as cst
from app.shared import settings as s
from app.ui import learning_layout as ui
from app.repositories import synonyms
from app.repositories.vocabulary import read_words
from app.ui.components.app_dialog import AppDialog
from app.ui.components.search_filter_panel import SearchFilterPanel


class SynonymsDialog(AppDialog):
    def __init__(self, owner, course, word_id, language, learned_by, on_changed=None,
                 heading=None, allow_navigation=True,show_translation=True):
        self.on_changed = on_changed
        self.allow_navigation = allow_navigation
        self.show_translation = show_translation
        words = read_words(course)
        words['ID'] = words.ID.astype(int)
        relations, revision = synonyms.load(course, words)
        if int(word_id) not in set(words.ID):
            raise ValueError('Save the vocabulary before editing synonyms.')
        super().__init__(owner, fg_color='#ded4bf')
        self.withdraw()
        self.course, self.language, self.learned_by = course, language, learned_by
        self.words = words
        self._words_by_id=words.set_index('ID')
        self._search_target=words[language].str.casefold()
        self._search_translation=words[learned_by].str.casefold()
        self.relations, self.revision = relations, revision
        self.word_id = int(word_id)
        self.hidden_ids=set()
        if not allow_navigation:
            from app.vocabulary.practise_data import answers_match
            source_word=self._words_by_id.loc[self.word_id,language]
            self.hidden_ids={int(identifier) for identifier,target in self.words[['ID',language]].itertuples(index=False,name=None)
                             if answers_match(source_word,target)}
        self.selected = synonyms.linked_ids(self.relations, self.word_id)
        self.title(s.T('Synonyms'))
        self.geometry('850x640')
        self.minsize(650, 480)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        word = self._words_by_id.loc[self.word_id]
        caption=self.add_heading(f"{s.T('Synonyms')} · {word[language] if heading is None else heading}")
        self.heading_frame,self.heading_label=caption.frame,caption.title
        self.query = cst.StringVar(master=self)
        self.search_panel=SearchFilterPanel(self,s.T,placeholder='Search word or translation',
            query_var=self.query,on_change=self.render)
        self.search_panel.grid(row=1,sticky='ew',padx=20,pady=8)
        self.search_entry=self.search_panel.query
        self.list = cst.CTkScrollableFrame(self, fg_color='#e9e0cd', corner_radius=18)
        self.list.grid(row=2, sticky='nsew', padx=20, pady=8)
        self.list.grid_columnconfigure(0,weight=1)
        self.list._parent_canvas.bind('<Configure>',self._resize_rows,add='+')
        self.add_actions(self,[('Close',self.destroy),('Save',self.save)],s.T,row=3,pady=(12,20))
        self.apply_background('editor_warm_v1.png')
        self.render()
        self.after(100,self.present)

    def render(self):
        for child in self.list.winfo_children():child.destroy()
        query = self.query.get().strip().casefold()
        matches=(self._search_target.str.contains(query,regex=False)
                 | self._search_translation.str.contains(query,regex=False))
        rows = self.words.loc[self.words.ID.ne(self.word_id) & ~self.words.ID.isin(self.hidden_ids) & matches]
        rows = rows.assign(_linked=rows.ID.isin(self.selected)).sort_values(
            ['_linked','ID'],ascending=[False,True])
        visible=rows.head(200)
        self._row_checkboxes=[]
        self._navigation_width=85 if self.allow_navigation and visible.ID.isin(self.selected).any() else 0
        for position, (identifier,target,translation) in enumerate(visible[['ID',self.language,self.learned_by]].itertuples(index=False,name=None)):
            word_id = int(identifier)
            variable = cst.BooleanVar(master=self, value=word_id in self.selected)
            def toggle(value=variable, target=word_id):
                if value.get():self.selected.add(target)
                else:self.selected.discard(target)
            label=str(target)
            if self.show_translation:label+=' — '+str(translation)
            checkbox = cst.CTkCheckBox(self.list,text=f"{label}  ·  ID {word_id}",
                variable=variable,command=toggle,text_color=ui.TEXT,font=(ui.FONT,16),fg_color='#567b63',
                width=380)
            checkbox._text_label.configure(justify='left')
            checkbox.grid(row=position,column=0,sticky='ew',padx=12,pady=6)
            self._row_checkboxes.append(checkbox)
            if word_id in self.selected and self.allow_navigation:
                cst.CTkButton(self.list,text=s.T('Open'),width=65,fg_color='#355e59',
                    command=lambda target=word_id:self.navigate(target)).grid(row=position,column=1,padx=10)
        if len(rows)>200:
            cst.CTkLabel(self.list,text=s.T('Refine your search to see more words.'),text_color=ui.MUTED).grid(row=201,sticky='w',padx=12,pady=10)
        self._resize_rows()
        self.list.update_idletasks()
        self.list._parent_canvas.yview_moveto(0)

    def _resize_rows(self,event=None):
        width=self.list._parent_canvas.winfo_width()/self.list._get_widget_scaling()
        if width<50:return
        wrap=round(max(100,width-70-getattr(self,'_navigation_width',0))*self.list._get_widget_scaling())
        for checkbox in getattr(self,'_row_checkboxes',()):
            if int(checkbox._text_label.cget('wraplength'))!=wrap:
                checkbox._text_label.configure(wraplength=wrap)

    def navigate(self, target):
        if not self.allow_navigation:return
        changed = self.selected != synonyms.linked_ids(self.relations,self.word_id)
        if changed and not messagebox.askyesno(parent=self,title=s.T('Synonyms'),
                message=s.T('Save changes before opening another word?')):
            return
        if not changed or self.save(close=False):
            SynonymsDialog(self.master,self.course,target,self.language,self.learned_by,on_changed=self.on_changed)
            self.destroy()

    def save(self, close=True):
        try:
            synonyms.replace_links(self.course,self.word_id,self.selected,self.revision)
            self.relations,self.revision = synonyms.load(self.course,self.words)
            if self.on_changed is not None:self.on_changed()
        except (OSError,ValueError) as error:
            messagebox.showerror(parent=self,title=s.T('Synonyms'),message=error_text(error, s.T))
            return False
        if close:self.destroy()
        return True

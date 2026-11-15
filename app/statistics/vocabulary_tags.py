"""Weighted tag statistics and a compact, paginated vocabulary panel."""
from dataclasses import dataclass
import customtkinter as cst

from app.ui.theme import FONT, TEXT, SECTION_SURFACE
from app.vocabulary.tags_data import normalize_tags
from app.ui.sorting import next_sort, sort_arrow
from app.statistics.components import DETAIL_ROW_COLORS, detail_sort_button, detail_practise_button


@dataclass(frozen=True)
class TagStatistics:
    name: str
    words: int
    successes: int
    failures: int
    tag_id: str = ''

    @property
    def attempts(self):
        return self.successes + self.failures

    @property
    def accuracy(self):
        return self.successes / self.attempts if self.attempts else None


def tag_statistics(frame, outcomes):
    """Count all tagged words, using the same post-learning outcomes as the summary."""
    if 'Tags' not in frame:
        return []
    groups = {}
    results = outcomes[['Success', 'Failure']].reindex(frame.index, fill_value=0)
    for value, (success, failure) in zip(frame.Tags, results.itertuples(index=False, name=None)):
        normalized = normalize_tags(value)
        for tag in normalized.split(', ') if normalized else ():
            entry = groups.setdefault(tag.casefold(), [tag, 0, 0, 0])
            entry[1] += 1
            entry[2] += int(success)
            entry[3] += int(failure)
    return sorted((TagStatistics(*values) for values in groups.values()),
                  key=lambda item: (-item.words, item.name.casefold()))


class VocabularyTagsPanel(cst.CTkFrame):
    page_size = 15

    def __init__(self, parent, translate,on_practise=None):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self.translate, self.items, self.page = translate, [], 0
        self.sort_key = None
        self.sort_descending = True
        self.on_practise=on_practise
        self.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Vocabulary by tag'), font=(FONT,24,'bold'),
            text_color=TEXT, anchor='w').grid(row=0,sticky='ew',padx=24,pady=(16,4))
        self.description=cst.CTkLabel(self,text=translate('Tag statistics description'),font=(FONT,14),
            text_color='#665d48',anchor='w',justify='left',width=0,wraplength=900)
        self.description.grid(row=1,sticky='ew',padx=24,pady=(0,8))
        self.bind('<Configure>',self._resize,add='+')
        toolbar=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        toolbar.grid(row=2,sticky='ew',padx=24,pady=(0,8));toolbar.grid_columnconfigure(0,weight=1)
        self.search=cst.CTkEntry(toolbar,placeholder_text=translate('Search tags'),width=220,height=32,
            font=(FONT,15),fg_color='#eee4d0',text_color=TEXT,border_color='#b7ac91')
        self.search.grid(row=0,column=0,sticky='w')
        self.search.bind('<KeyRelease>',self._search_changed)
        self.count=cst.CTkLabel(toolbar,text='',font=(FONT,14),text_color=TEXT)
        self.count.grid(row=0,column=3,padx=12)
        self.previous=cst.CTkButton(toolbar,text='←',width=36,height=30,fg_color='#355e59',command=lambda:self.turn(-1))
        self.previous.grid(row=0,column=4,padx=3)
        self.next=cst.CTkButton(toolbar,text='→',width=36,height=30,fg_color='#355e59',command=lambda:self.turn(1))
        self.next.grid(row=0,column=5,padx=3)
        sortbar=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        sortbar.grid(row=3,sticky='ew',padx=16,pady=(0,6))
        sortbar.grid_columnconfigure((0,1,2),weight=1,uniform='sort')
        headers=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        headers.grid(row=4,sticky='ew',padx=16,pady=(0,2))
        headers.grid_columnconfigure(0,weight=1)
        self.sort_buttons={}
        cst.CTkLabel(headers,text=translate('Tags'),anchor='w',text_color=TEXT,font=(FONT,14,'bold')).grid(row=0,column=0,sticky='ew',padx=(16,4))
        for column, (key, caption, width) in enumerate((('words','Tagged words',100),
                ('attempts','Review answers',140),('accuracy','Review accuracy',200)),1):
            button=detail_sort_button(cst.CTkButton(sortbar,text=translate(caption),
                command=lambda key=key:self.sort(key)))
            button.grid(row=0,column=column-1,sticky='ew',padx=4)
            self.sort_buttons[key]=(button,caption)
            cst.CTkLabel(headers,text=translate(caption),width=width,font=(FONT,13),
                         text_color='#5e6655').grid(row=0,column=column,padx=3)
        if on_practise is not None:
            cst.CTkLabel(headers,text='',width=120).grid(row=0,column=4,padx=(0,12))
        self.rows=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        self.rows.grid(row=5,sticky='ew',padx=16,pady=(0,12))
        self.rows.grid_columnconfigure(0,weight=1)
        self.visible=[]

    def set_items(self, items):
        self.items=list(items)
        self.page=0
        self.sort_key=None
        self.sort_descending=True
        self.search.delete(0,'end')
        self.render()

    def _resize(self,event):
        if event.widget is self._canvas:
            width=max(100,int(event.width/self._get_widget_scaling())-48)
            if self.description.cget('wraplength')!=width:self.description.configure(wraplength=width)

    def _search_changed(self,event=None):
        self.page=0
        self.render()

    def sort(self,key):
        state=next_sort((self.sort_key,self.sort_descending) if self.sort_key else None,key)
        self.sort_key,self.sort_descending=state if state else (None,False)
        self.page=0
        self.render()

    def turn(self,direction):
        self.page+=direction
        self.render()

    def render(self):
        query=self.search.get().strip().casefold()
        items=[item for item in self.items if query in item.name.casefold()]
        def order(item):
            value=getattr(item,self.sort_key)
            direction=-1 if self.sort_descending else 1
            return (value is None,direction*value if value is not None else 0,
                    direction*item.attempts,direction*item.words,item.name.casefold())
        if self.sort_key:items.sort(key=order)
        self.page=max(0,min(self.page,max(0,(len(items)-1)//self.page_size)))
        start=self.page*self.page_size
        self.visible=items[start:start+self.page_size]
        for child in self.rows.winfo_children():child.destroy()
        if not self.visible:
            cst.CTkLabel(self.rows,text=self.translate('No tagged words found.'),text_color=TEXT,
                font=(FONT,16)).grid(sticky='w',pady=12)
        for index,item in enumerate(self.visible):
            row=cst.CTkFrame(self.rows,fg_color=DETAIL_ROW_COLORS[index%2],corner_radius=16)
            row.grid(row=index,sticky='ew',pady=2);row.grid_columnconfigure(0,weight=1)
            name=cst.CTkLabel(row,text=item.name,width=0,anchor='w',text_color=TEXT,font=(FONT,15,'bold'))
            name.grid(row=0,column=0,sticky='ew',padx=(16,4))
            name.bind('<Configure>',lambda event,label=name,text=item.name:self._fit_name(label,text),add='+')
            for column,value,width in ((1,item.words,100),(2,item.attempts,140)):
                cst.CTkLabel(row,text=str(value),width=width,text_color=TEXT,font=(FONT,15)).grid(row=0,column=column,padx=3)
            rate=cst.CTkFrame(row,width=200,height=30,fg_color='transparent',corner_radius=0)
            rate.grid(row=0,column=3,padx=3);rate.grid_propagate(False)
            bar=cst.CTkProgressBar(rate,width=100,height=7,fg_color='#b5ad97',progress_color='#417766')
            bar.grid(row=0,column=0,padx=(8,6),pady=11);bar.set(item.accuracy or 0)
            cst.CTkLabel(rate,text=f'{item.accuracy:.1%}' if item.accuracy is not None else '—',width=70,
                text_color=TEXT,font=(FONT,15,'bold')).grid(row=0,column=1)
            if self.on_practise is not None:
                detail_practise_button(cst.CTkButton(row,text=self.translate('Repeat'),
                    state='normal' if item.words else 'disabled',
                    command=lambda item=item:self.on_practise(item.tag_id))).grid(row=0,column=4,padx=(0,12),pady=3)
        self.count.configure(text=f'{start+1 if items else 0}–{min(start+self.page_size,len(items))} / {len(items)}')
        active=('#355e59','#fffcf5')
        inactive=('#d0d7c1',TEXT)
        state=(self.sort_key,self.sort_descending) if self.sort_key else None
        for key,(button,caption) in self.sort_buttons.items():
            selected=key==self.sort_key
            background,foreground=active if selected else inactive
            button.configure(text=self.translate(caption)+' '+sort_arrow(state,key),fg_color=background,text_color=foreground,
                hover_color='#426357' if selected else '#b5c3a4')
        self.previous.configure(state='normal' if self.page else 'disabled')
        self.next.configure(state='normal' if start+self.page_size<len(items) else 'disabled')

    def _fit_name(self,label,text):
        font=cst.CTkFont(family=FONT,size=round(15*self._get_widget_scaling()),weight='bold')
        width=max(20,label.winfo_width()-8)
        shown=text
        if font.measure(text)>width:
            while shown and font.measure(shown+'…')>width:shown=shown[:-1]
            shown+='…'
        if label.cget('text')!=shown:label.configure(text=shown)

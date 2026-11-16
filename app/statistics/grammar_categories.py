"""Read-only grammar category summaries and a compact comparison panel."""
from dataclasses import dataclass
from app.shared.localization_format import percent
from app.core.context import get_context
import customtkinter as cst
from app.ui.theme import FONT, TEXT, SECTION_SURFACE
from app.statistics.components import DETAIL_ROW_COLORS, detail_sort_button, detail_practise_button

SORT_OPTIONS = (('questions', 'Number of questions'), ('practised', 'Practised questions'),
                ('accuracy', 'Review accuracy'))


@dataclass(frozen=True)
class GrammarCategory:
    name: str
    questions: int
    practised: int
    successes: int
    failures: int

    @property
    def attempts(self):
        return self.successes + self.failures

    @property
    def accuracy(self):
        return self.successes / self.attempts if self.attempts else None


def order_categories(items, key='accuracy', descending=False):
    """Sort numeric metrics; unknown accuracy stays last in either direction."""
    if key not in {name for name, _ in SORT_OPTIONS}:
        raise ValueError(f'Unknown grammar category sort: {key}')
    def order(item):
        value = getattr(item, key)
        return (value is None, (-value if descending else value) if value is not None else 0,
                -item.attempts if key == 'accuracy' else 0, item.name.casefold(), item.name)
    return sorted(items, key=order)


def grammar_categories(frame):
    """Weight accuracy by answers; count coverage by questions with valid history."""
    category_column = next((c for c in frame.columns if str(c).strip().casefold() == 'category'), None)
    if category_column is None:
        return []
    categories = frame[category_column].fillna('').astype(str).str.strip()
    histories = frame['R'].fillna('').astype(str) if 'R' in frame else [''] * len(frame)
    groups = {}
    for name, history in zip(categories, histories):
        successes, failures = history.count('S'), history.count('F')
        values = groups.setdefault(name, [0, 0, 0, 0])
        values[0] += 1
        values[1] += bool(successes + failures)
        values[2] += successes
        values[3] += failures
    result = [GrammarCategory(name, *values) for name, values in groups.items()]
    return order_categories(result)


class GrammarCategoriesPanel(cst.CTkFrame):
    def __init__(self, parent, translate, on_practise=None):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self.translate = translate
        self.on_practise = on_practise
        self.sort_key, self.descending = None, False
        self.items, self.visible, self._category_rows = (), [], []
        self.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Grammar by category'), font=(FONT, 24, 'bold'),
                     text_color=TEXT, anchor='w').grid(row=0, sticky='ew', padx=24, pady=(16, 4))
        self.description=cst.CTkLabel(self,text=translate('Grammar category statistics description'),font=(FONT,14),
                     text_color='#665d48',anchor='w',justify='left',wraplength=850)
        self.description.grid(row=1,sticky='ew',padx=24,pady=(0,8))
        self.category_count=cst.CTkLabel(self,text='',font=(FONT,13),text_color='#665d48',anchor='w',justify='left',height=0)
        self.category_count.grid(row=2,sticky='ew',padx=24,pady=(0,8))
        self.bind('<Configure>',self._resize_description,add='+')
        totals=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        totals.grid(row=3,sticky='ew',padx=16,pady=(0,8))
        totals.grid_columnconfigure((0,1,2),weight=1,uniform='totals')
        self.summary_counts={}
        self.summary_labels=[]
        for column,(caption,color,background) in enumerate((('Recorded answers',TEXT,'#dedac3'),
                ('Correct answers','#355e59','#d0d7c1'),('Incorrect answers','#976042','#ead7c3'))):
            card=cst.CTkFrame(totals,fg_color=background,corner_radius=14)
            card.grid(row=0,column=column,sticky='nsew',padx=4)
            card.grid_columnconfigure(0,weight=1)
            value=cst.CTkLabel(card,text='0',font=(FONT,23,'bold'),text_color=color,anchor='w')
            value.grid(row=0,sticky='ew',padx=14,pady=(6,0))
            label=cst.CTkLabel(card,text=translate(caption),font=(FONT,14),text_color=color,
                anchor='w',justify='left',height=0,wraplength=180)
            label.grid(row=1,sticky='ew',padx=14,pady=(0,6))
            self.summary_counts[caption]=value
            self.summary_labels.append(label)
        toolbar=cst.CTkFrame(self,fg_color='transparent',corner_radius=0)
        toolbar.grid(row=4,sticky='ew',padx=16,pady=(0,6))
        toolbar.grid_columnconfigure((0,1,2),weight=1,uniform='sort')
        self.sort_buttons={}
        for column,(key,caption) in enumerate(SORT_OPTIONS):
            button=detail_sort_button(cst.CTkButton(toolbar,text=translate(caption)+' ↕',
                command=lambda key=key:self.sort(key)))
            button.grid(row=0,column=column,sticky='ew',padx=4)
            self.sort_buttons[key]=button
        self.rows = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.rows.grid(row=5, sticky='ew', padx=16, pady=(0, 12))
        self.rows.grid_columnconfigure(0, weight=1)
        self._order_rows()

    def sort(self,key):
        if key not in self.sort_buttons:raise ValueError(f'Unknown grammar category sort: {key}')
        from app.ui.sorting import next_sort
        state=next_sort((self.sort_key,self.descending) if self.sort_key else None,key)
        self.sort_key,self.descending=state if state else (None,False)
        self._order_rows()

    def _order_rows(self):
        self.visible=order_categories(self.items,self.sort_key,self.descending) if self.sort_key else list(self.items)
        positions={id(item):index for index,item in enumerate(self.visible)}
        for item,row in self._category_rows:
            index=positions[id(item)]
            row.grid_configure(row=index)
            color=DETAIL_ROW_COLORS[index%2]
            if row.cget('fg_color')!=color:row.configure(fg_color=color)
        for key,caption in SORT_OPTIONS:
            active=key==self.sort_key
            arrow=('↓' if self.descending else '↑') if active else '↕'
            self.sort_buttons[key].configure(text=self.translate(caption)+' '+arrow,
                fg_color='#355e59' if active else '#d0d7c1',
                hover_color='#426357' if active else '#b5c3a4',
                text_color='#fffcf5' if active else TEXT,
                state='normal' if self.items else 'disabled')

    def _resize_description(self,event):
        if event.widget is not self._canvas:return
        width=max(80,int(event.width/self._get_widget_scaling())-48)
        if self.category_count.cget('wraplength')!=width:self.category_count.configure(wraplength=width)
        if self.description.cget('wraplength')!=width:self.description.configure(wraplength=width)
        for label in getattr(self,'summary_labels',()):label.configure(wraplength=max(60,(width-92)//3))

    def set_data(self, frame):
        history=frame['R'].fillna('').astype(str) if 'R' in frame else None
        summary=(len(frame),int(history.str.count('S').sum()),int(history.str.count('F').sum())) if history is not None else (len(frame),0,0)
        self.set_items(grammar_categories(frame),summary=summary)

    def set_items(self,items,*,summary=None):
        items=tuple(items)
        self.category_count.configure(text=self.translate('Total categories: {count}').format(count=len(items)))
        unchanged=items==self.items and bool(self.rows.winfo_children())
        if not unchanged:
            self.items=items
        if summary is None:summary=(sum(item.questions for item in items),sum(item.successes for item in items),sum(item.failures for item in items))
        _,successes,failures=summary
        for caption,value in (('Recorded answers',successes+failures),('Correct answers',successes),('Incorrect answers',failures)):
            self.summary_counts[caption].configure(text=str(value))
        if unchanged:
            return
        for child in self.rows.winfo_children():
            child.destroy()
        self._category_rows=[]
        if not items:
            cst.CTkLabel(self.rows, text=self.translate('No grammar categories available.'),
                         font=(FONT, 18), text_color=TEXT).grid(padx=12, pady=16, sticky='w')
        for index, item in enumerate(items):
            row = cst.CTkFrame(self.rows, fg_color=DETAIL_ROW_COLORS[index%2], corner_radius=16)
            row.grid(row=index, sticky='ew', pady=2)
            row.grid_columnconfigure(0, weight=1)
            self._category_rows.append((item,row))
            name = cst.CTkLabel(row, text=item.name or self.translate('Uncategorised'),
                font=(FONT, 18, 'bold'), text_color=TEXT, anchor='w', justify='left', wraplength=650, height=24)
            name.grid(row=0, column=0, sticky='ew', padx=18, pady=(5, 0))
            text=f'{item.practised} / {item.questions}  {self.translate("Practised questions")}'
            coverage=cst.CTkLabel(row,text=text,font=(FONT,14),text_color='#5e6655',anchor='w',justify='left',height=20)
            coverage.grid(row=1,column=0,columnspan=2,sticky='ew',padx=18,pady=(0,2))
            results=cst.CTkFrame(row,fg_color='transparent',corner_radius=0)
            results.grid(row=2,column=0,columnspan=2,sticky='ew',padx=18,pady=(0,3))
            results.grid_columnconfigure((0,1,2),weight=1,uniform='results')
            result_labels=[]
            for column,(caption,value,color) in enumerate((('Recorded answers',item.attempts,TEXT),
                    ('Correct answers',item.successes,'#355e59'),('Incorrect answers',item.failures,'#976042'))):
                label=cst.CTkLabel(results,text=f'{self.translate(caption)}: {value}',font=(FONT,13),
                    text_color=color,anchor='w',justify='left',height=0)
                label.grid(row=0,column=column,sticky='ew',padx=(0,8))
                result_labels.append(label)
            def resize(event,widget=row,title=name,coverage=coverage,labels=result_labels):
                if event.widget is not widget._canvas:return
                width=event.width/widget._get_widget_scaling()
                title.configure(wraplength=max(120,width-(340 if self.on_practise else 180)))
                available=max(120,width-(180 if self.on_practise else 36))
                coverage.configure(wraplength=available)
                for label in labels:label.configure(wraplength=max(60,available/3-16))
            row.bind('<Configure>',resize,add='+')
            cst.CTkLabel(row, text=percent(item.accuracy, get_context(self).preferences.app_language) if item.attempts else '—',
                font=(FONT, 21, 'bold'), text_color='#976042' if item.attempts and item.accuracy < .6 else '#355e59',
                width=90, height=24).grid(row=0, column=1, padx=18, pady=(4, 0))
            bar = cst.CTkProgressBar(row, height=6, corner_radius=3,
                fg_color='#b5ad97', progress_color='#417766')
            bar.grid(row=3, column=0, columnspan=2, sticky='ew', padx=18, pady=(2, 6))
            bar.set(item.accuracy if item.attempts else 0)
            if self.on_practise is not None:
                detail_practise_button(cst.CTkButton(row, text=self.translate('Practise category'),
                    command=lambda name=item.name: self.on_practise(name))).grid(
                        row=0, column=2, rowspan=4, padx=(0, 16), pady=8)
        self._order_rows()

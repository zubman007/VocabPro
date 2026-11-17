"""Multi-category selection; opening/cancelling never changes the active round."""
from collections import Counter
import customtkinter as cst
from app.grammar.theory_data import category_key
from app.shared import settings as s
from app.ui.theme import FONT, TEXT
from app.ui.module_style import SESSION,tool_button
from app.ui.surfaces import surface
from app.ui.components.app_dialog import AppDialog
from app.ui.components.search_filter_panel import SearchFilterPanel


def category_options(questions):
    names = {}
    counts = Counter()
    for question in questions:
        name = str(question.get('category') or '').strip()
        key = category_key(name)
        names.setdefault(key, name)
        counts[key] += 1
    return [(key, names[key], counts[key]) for key in sorted(names, key=lambda key: names[key].casefold())]


class CategoryFilterDialog(AppDialog):
    def __init__(self, owner, options, selected, apply, *, title='Question categories', count_caption='Number of questions'):
        super().__init__(owner, fg_color='#eee9df')
        self.withdraw()
        self.title(s.T(title))
        self.count_caption=count_caption
        self.geometry('620x670')
        self.minsize(480, 450)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.options, self.apply_callback = options, apply
        caption=self.add_heading(s.T(title),s.T('Category filter starts a new round.'),rowspan=2)
        self.header,self.heading,self.description=caption.frame,caption.title,caption.description
        self.search_text=cst.StringVar(master=self)
        self.search_panel=SearchFilterPanel(self,s.T,placeholder='Search categories',
            query_var=self.search_text,on_change=self._search)
        self.search_panel.grid(row=2,sticky='ew',padx=24,pady=(0,12))
        self.query=self.search_panel.query
        body = cst.CTkScrollableFrame(self, fg_color='#ded4bf', corner_radius=20)
        body.grid(row=3, sticky='nsew', padx=24)
        body.grid_columnconfigure(0, weight=1)
        self.body=body
        self.variables, self.checkboxes = {}, {}
        for row, (key, name, count) in enumerate(options):
            variable = cst.BooleanVar(value=key in selected)
            checkbox = cst.CTkCheckBox(body, text=f'{name or s.T("Uncategorised")}  ·  {count}',
                variable=variable, command=self._refresh, font=(FONT, 17), text_color=TEXT,
                fg_color='#49736b', hover_color='#355e59', border_color='#8d947d')
            checkbox.grid(row=row, sticky='w', padx=16, pady=10)
            checkbox._text_label.configure(wraplength=460, justify='left')
            self.variables[key], self.checkboxes[key] = variable, checkbox
        actions = cst.CTkFrame(self, fg_color='transparent')
        actions.grid(row=4, sticky='ew', padx=24, pady=12)
        actions.grid_columnconfigure((0,1),weight=1,uniform='actions')
        for column, (label, value) in enumerate((('Select all', True), ('Clear selection', False))):
            tool_button(cst.CTkButton(actions,text=s.T(label),command=lambda state=value:self._select_all(state),
                width=150)).grid(row=0,column=column,sticky='ew',padx=(0,6) if column==0 else (6,0))
        count_frame=cst.CTkFrame(self,fg_color=SESSION,corner_radius=14)
        count_frame.grid(row=5,sticky='ew',padx=24)
        self.count = cst.CTkLabel(count_frame, text='', font=(FONT, 15), text_color=TEXT,fg_color='transparent')
        self.count.pack(anchor='w',padx=12,pady=6)
        footer = cst.CTkFrame(self, fg_color='transparent')
        footer.grid(row=6, sticky='ew', padx=24,pady=(8,16))
        cancel,self.apply_button=self.add_actions(footer,[('Close',self.destroy),('Apply filter',self._apply)],s.T)
        self.bind('<Configure>', self._resize, add='+')
        self.apply_background('sections_warm_v1.png')
        for container in (actions,footer):
            for button in container.winfo_children():
                if isinstance(button,cst.CTkButton):surface(button,container._surface)
        self._refresh()
        self.after(250, lambda: self.present(modal=True))

    def _refresh(self):
        count = sum(count for key, _, count in self.options if self.variables[key].get())
        self.count.configure(text=f'{s.T(self.count_caption)}: {count}')
        self.apply_button.configure(state='normal' if count else 'disabled')

    def _resize(self, event):
        if event.widget is not self:
            return
        for checkbox in self.checkboxes.values():
            label = checkbox._text_label
            desired = max(150, round(event.width-140*checkbox._get_widget_scaling()))
            if int(label.cget('wraplength')) != desired:
                label.configure(wraplength=desired)

    def _select_all(self, value):
        for variable in self.variables.values():variable.set(value)
        self._refresh()

    def _search(self, event=None):
        query = self.search_text.get().strip().casefold()
        for key, name, _ in self.options:
            if query in (name or s.T('Uncategorised')).casefold():self.checkboxes[key].grid()
            else:self.checkboxes[key].grid_remove()
        self.body.update_idletasks()
        canvas=self.body._parent_canvas
        canvas.configure(scrollregion=canvas.bbox('all'))
        canvas.yview_moveto(0)

    def _apply(self):
        selected = {key for key, variable in self.variables.items() if variable.get()}
        if selected and self.apply_callback(selected):self.destroy()

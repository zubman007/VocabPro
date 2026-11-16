"""Read-only statistics explorer with search, header sorting and pagination."""
from app.ui.theme import FONT
from tkinter import ttk
import customtkinter as cst
import pandas as pd
from numbers import Real, Integral
from app.shared.localization_format import number
from app.core.context import get_context
from app.statistics.components import detail_sort_button
from app.ui.sorting import sort_arrow
from app.ui.theme import SECTION_SURFACE as SURFACE, SECTION_CONTROL as HEADER, TEXT, TITLE_FONT


class StatisticsTable(cst.CTkFrame):
    page_size = 25

    def __init__(self, parent, translate, *, sort_columns=()):
        super().__init__(parent, fg_color=SURFACE, corner_radius=24)
        self.translate = translate
        self.frame = pd.DataFrame()
        self.page = 0
        self.sort_column = None
        self.ascending = True
        self.grid_columnconfigure(0, weight=1)
        self.title_label = cst.CTkLabel(self, text=translate('Statistic table'),
            font=(FONT, 24, 'bold'), text_color=TEXT, anchor='w')
        self.title_label.grid(row=0, column=0, sticky='ew', padx=18, pady=(16, 0))
        toolbar = cst.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=18, pady=(16, 12))
        toolbar.grid_columnconfigure(0, weight=1)
        self.search = cst.CTkEntry(toolbar, placeholder_text=translate("Filter"),
            fg_color="#eee4d0", border_color="#b7ac91", text_color=TEXT, width=320,
            height=36, font=(FONT, 18))
        self.search.grid(row=0, column=0, sticky="w")
        self.search.bind("<KeyRelease>", self._search_changed)
        self.count = cst.CTkLabel(toolbar, text="", text_color=TEXT, font=(FONT, 18))
        self.count.grid(row=0, column=1, padx=16)
        self.previous = cst.CTkButton(toolbar, text="←", width=44, command=lambda: self._turn(-1),
            fg_color=HEADER, hover_color="#315347")
        self.previous.grid(row=0, column=2, padx=3)
        self.next = cst.CTkButton(toolbar, text="→", width=44, command=lambda: self._turn(1),
            fg_color=HEADER, hover_color="#315347")
        self.next.grid(row=0, column=3, padx=3)
        self.sort_buttons = {}
        if sort_columns:
            sorts = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
            sorts.grid(row=2, sticky='ew', padx=18, pady=(0, 12))
            sorts.grid_columnconfigure(tuple(range(len(sort_columns))), weight=1, uniform='sort')
            for position, column in enumerate(sort_columns):
                button = detail_sort_button(cst.CTkButton(sorts, text=translate(column),
                    command=lambda column=column: self.sort(column)))
                button.grid(row=0, column=position, sticky='ew', padx=4)
                self.sort_buttons[column] = button
        holder = cst.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        holder.grid(row=3 if sort_columns else 2, column=0, sticky="ew", padx=18, pady=(0, 18))
        holder.grid_columnconfigure(0, weight=1)
        style = ttk.Style(self)
        style.configure("VocabStats.Treeview", background="#eee4d0", fieldbackground="#eee4d0",
            foreground=TEXT, rowheight=34, font=(FONT, 14), borderwidth=0)
        style.configure("VocabStats.Treeview.Heading", background="#c8d0b6", foreground=TEXT,
            font=(FONT, 15, "bold"), padding=(10, 12), borderwidth=1,
            bordercolor='#b7b995', lightcolor='#c8d0b6', darkcolor='#c8d0b6')
        # Windows' native heading ignores background colors. Clone only this
        # component's heading border, leaving the application's ttk theme alone.
        if 'VocabStats.heading.border' not in style.element_names():
            style.element_create('VocabStats.heading.border', 'from', 'clam', 'Treeheading.border')
        style.layout('VocabStats.Treeview.Heading', [('VocabStats.heading.border', {
            'sticky': 'nswe', 'children': [('Treeheading.padding', {
                'sticky': 'nswe', 'children': [('Treeheading.text', {'sticky': 'we'})]})]})])
        style.map('VocabStats.Treeview.Heading', background=[('active', '#b5c3a4')])
        style.map("VocabStats.Treeview", background=[("selected", "#b5c3a4")],
            foreground=[("selected", TEXT)])
        self.tree = ttk.Treeview(holder, show="headings", height=12, style="VocabStats.Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure("even", background="#eee4d0")
        self.tree.tag_configure("odd", background="#ded4bf")
        horizontal = ttk.Scrollbar(holder, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        def horizontal_range(first, last):
            horizontal.set(first, last)
            if float(first) <= 0 and float(last) >= 1:
                horizontal.grid_remove()
            else:
                horizontal.grid()
        self.tree.configure(xscrollcommand=horizontal_range)
        self.tree.bind('<MouseWheel>', self._scroll_page)

    def _scroll_page(self, event):
        """The table has no vertical viewport; scroll its enclosing statistics page."""
        from app.ui.widgets import VerticalScrolledFrame_class
        parent = self.master
        while parent is not None:
            if isinstance(parent, VerticalScrolledFrame_class):
                parent.canvas.yview_scroll(-int(event.delta / 120), 'units')
                return 'break'
            parent = parent.master
        return 'break'

    def set_data(self, frame):
        self.frame = frame.copy()
        self.page = 0
        self.search.delete(0, "end")
        self.sort_column = "Next repetition" if "Next repetition" in frame else None
        self.ascending = True
        columns = list(frame.columns)
        self.tree.configure(columns=columns)
        for column in columns:
            self.tree.column(column, width=250 if column == "Next repetition" else 160,
                minwidth=100, anchor="e" if column in ("Total", "Success", "Failure", 'Recorded answers', 'Incorrect answers', 'Review accuracy') else "w")
        self.refresh()

    def _search_changed(self, event=None):
        self.page = 0
        self.refresh()

    def _turn(self, direction):
        self.page += direction
        self.refresh()

    def sort(self, column):
        from app.ui.sorting import next_sort
        state=next_sort((self.sort_column,not self.ascending) if self.sort_column else None,column)
        self.sort_column,self.ascending=(state[0],not state[1]) if state else (None,True)
        self.page = 0
        self.refresh()

    def refresh(self):
        view = self.frame
        query = self.search.get().strip().casefold()
        if query and len(view):
            mask = view.fillna("").astype(str).apply(
                lambda series: series.str.casefold().str.contains(query, regex=False)).any(axis=1)
            view = view.loc[mask]
        if self.sort_column in view.columns:
            view = view.sort_values(self.sort_column, ascending=self.ascending, kind="stable")
        total = len(view)
        self.page = max(0, min(self.page, max(0, (total - 1) // self.page_size)))
        start = self.page * self.page_size
        self.tree.configure(height=max(1, min(self.page_size, total-start)))
        items = self.tree.get_children()
        if items:
            self.tree.delete(*items)
        ui_language = get_context(self).preferences.app_language
        for index, row in enumerate(view.iloc[start:start+self.page_size].fillna("").itertuples(index=False, name=None)):
            shown = [number(value, ui_language, 2)
                     if isinstance(value, Real) and not isinstance(value, Integral) else value for value in row]
            self.tree.insert("", "end", values=shown, tags=("even" if index % 2 == 0 else "odd",))
        for column in view.columns:
            arrow = (" ↑" if self.ascending else " ↓") if column == self.sort_column else ""
            unit = ' (%)' if column == 'Review accuracy' else ''
            self.tree.heading(column, text=self.translate(column) + unit + arrow,
                command=lambda selected=column: self.sort(selected))
        self.count.configure(text=f"{start + 1 if total else 0}–{min(start+self.page_size, total)} / {total}")
        self.previous.configure(state="normal" if self.page else "disabled")
        self.next.configure(state="normal" if start + self.page_size < total else "disabled")
        state = (self.sort_column, not self.ascending) if self.sort_column else None
        for column, button in self.sort_buttons.items():
            active = self.sort_column == column
            button.configure(text=self.translate(column) + ' ' + sort_arrow(state, column),
                fg_color='#355e59' if active else '#d0d7c1',
                hover_color='#426357' if active else '#b5c3a4',
                text_color='#fffcf5' if active else TEXT,
                state='normal' if column in self.frame and len(self.frame) else 'disabled')
        self.tree.yview_moveto(0)

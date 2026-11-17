"""Conjugation coverage presented with the same cards as other statistics."""
import customtkinter as cst
from app.ui.theme import FONT, TEXT, SECTION_SURFACE


class ConjugationProgressPanel(cst.CTkFrame):
    def __init__(self, parent, translate):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Overview'), font=(FONT, 24, 'bold'),
                     text_color=TEXT, anchor='w').grid(row=0, sticky='ew', padx=24, pady=(16, 8))
        cards = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        cards.grid(row=1, sticky='ew', padx=16, pady=(0, 8))
        cards.grid_columnconfigure((0, 1, 2), weight=1, uniform='coverage')
        self.values, self.labels = {}, {}
        for column, (key, caption, color, fill) in enumerate((
                ('practised', 'Practised conjugation rounds', '#416d58', '#d4dcc6'),
                ('unpractised', 'Unpractised conjugation rounds', '#9b6543', '#e7d0b9'),
                ('covered_forms', 'Forms in practised rounds', '#977338', '#e7dcbb'))):
            card = cst.CTkFrame(cards, fg_color=fill, corner_radius=14)
            card.grid(row=0, column=column, sticky='nsew', padx=4)
            card.grid_columnconfigure(0, weight=1)
            value = cst.CTkLabel(card, text='0', font=(FONT, 23, 'bold'), text_color=color, anchor='w')
            value.grid(row=0, sticky='ew', padx=14, pady=(6, 0))
            label = cst.CTkLabel(card, text=translate(caption), font=(FONT, 14), text_color=TEXT,
                                 anchor='w', justify='left', height=0, wraplength=260)
            label.grid(row=1, sticky='ew', padx=14, pady=(0, 6))
            self.values[key], self.labels[key] = value, label
        self.description = cst.CTkLabel(self, text=translate('Conjugation statistics explanation'),
            font=(FONT, 14), text_color='#665d48', anchor='w', justify='left', height=0, wraplength=900)
        self.description.grid(row=2, sticky='ew', padx=24, pady=(0, 18))
        self.bind('<Configure>', self._resize, add='+')

    def _resize(self, event):
        if event.widget is not self._canvas:
            return
        width = max(100, int(event.width / self._get_widget_scaling()) - 48)
        if self.description.cget('wraplength') != width:
            self.description.configure(wraplength=width)
        label_width = max(80, (width - 72) // 3)
        for label in self.labels.values():
            if label.cget('wraplength') != label_width:
                label.configure(wraplength=label_width)

    def set_data(self, progress):
        for key, label in self.values.items():
            value = str(progress[key]) if progress is not None else '-'
            if label.cget('text') != value:
                label.configure(text=value)

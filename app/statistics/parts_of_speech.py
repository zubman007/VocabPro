"""Horizontal, retained vocabulary distribution with per-category practice."""
import customtkinter as cst
from app.core.context import get_context
from app.shared.localization_format import percent
from app.statistics.components import detail_practise_button
from app.ui.theme import FONT, TEXT

SURFACE = '#e2e4ce'
ACTUAL, TARGET = '#557b61', '#b58a54'


class PartsOfSpeechPanel(cst.CTkFrame):
    def __init__(self, parent, translate, on_practise):
        super().__init__(parent, fg_color=SURFACE, corner_radius=24)
        self.translate, self.on_practise = translate, on_practise
        self.rows, self._snapshot = {}, None
        self.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Vocabulary by Part of Speech'), font=(FONT, 24, 'bold'),
                     text_color='#60794e', anchor='w').grid(row=0, sticky='ew', padx=24, pady=(18, 8))
        legend = cst.CTkFrame(self, fg_color='transparent')
        legend.grid(row=1, sticky='w', padx=24, pady=(0, 10))
        for column, (key, color) in enumerate((('Real', ACTUAL), ('Ideal', TARGET))):
            cst.CTkFrame(legend, width=20, height=10, corner_radius=4, fg_color=color).grid(row=0, column=column*2, padx=(0, 6))
            cst.CTkLabel(legend, text=translate(key), font=(FONT, 15), text_color=TEXT).grid(row=0, column=column*2+1, padx=(0, 22))
        self.body = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.body.grid(row=2, sticky='ew', padx=20, pady=(0, 8))
        self.body.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Percentage of words') + ' · ' + translate('Number of words') + ' · 0–100 %',
                     font=(FONT, 13), text_color='#5e6655').grid(row=3, sticky='w', padx=24, pady=(0, 14))

    def set_data(self, data):
        if self._snapshot is not None and all(old.equals(new) for old, new in zip(self._snapshot, data)):
            return
        percentages, counts = data
        keys = list(percentages.index)
        if list(self.rows) != keys:
            for child in self.body.winfo_children():
                child.destroy()
            self.rows.clear()
            for position, key in enumerate(keys):
                row = cst.CTkFrame(self.body, fg_color=SURFACE, corner_radius=0)
                row.grid(row=position, sticky='ew', pady=5)
                row.grid_columnconfigure(1, weight=1, minsize=80)
                cst.CTkLabel(row, text=self.translate(key), width=180, wraplength=170,
                    font=(FONT, 17, 'bold'), text_color=TEXT, anchor='w', justify='left').grid(
                        row=0, column=0, rowspan=2, sticky='w', padx=(4, 14))
                bars, values = {}, {}
                for index, (series, color) in enumerate((('Real', ACTUAL), ('Ideal', TARGET))):
                    bars[series] = cst.CTkProgressBar(row, height=11, width=120, corner_radius=5,
                        fg_color='#cbd0b6', progress_color=color)
                    bars[series].grid(row=index, column=1, sticky='ew', pady=7)
                    values[series] = cst.CTkLabel(row, text='', width=190, font=(FONT, 14),
                        text_color=color, anchor='e')
                    values[series].grid(row=index, column=2, sticky='e', padx=(12, 18))
                button = detail_practise_button(cst.CTkButton(row, text=self.translate('Repeat'),
                    command=lambda key=key: self.on_practise(key)))
                button.grid(row=0, column=3, rowspan=2, padx=(0, 4))
                self.rows[key] = (bars, values, button)
        language = get_context(self).preferences.app_language
        for key, (bars, values, button) in self.rows.items():
            for series in ('Real', 'Ideal'):
                value = float(percentages.at[key, series])
                bars[series].set(max(0, min(1, value / 100)))
                values[series].configure(text=percent(value / 100, language, 1) + ' · ' + str(int(counts.at[key, series])))
            button.configure(state='normal' if counts.at[key, 'Real'] > 0 else 'disabled')
        self._snapshot = [frame.copy(deep=True) for frame in data]

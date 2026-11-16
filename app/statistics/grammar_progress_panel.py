"""Retained grammar streak bars and a separate session-record card."""
import customtkinter as cst
from app.core.context import get_context
from app.shared.localization_format import number, percent
from app.statistics.grammar_progress import GrammarQuestionProgress
from app.ui.theme import FONT, TEXT, SECTION_SURFACE


class GrammarRecordPanel(cst.CTkFrame):
    def __init__(self, parent, translate):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self.translate = translate
        self.grid_columnconfigure(0, weight=1)
        self.record = cst.CTkLabel(self, text='', font=(FONT, 21, 'bold'),
            text_color='#815632', anchor='w', justify='left', height=0)
        self.record.grid(row=0, sticky='ew', padx=24, pady=(14, 4))
        self.description = cst.CTkLabel(self, text=translate('Grammar best streak explanation'),
            font=(FONT, 13), text_color='#665d48', anchor='w', justify='left', height=0)
        self.description.grid(row=1, sticky='ew', padx=24, pady=(0, 14))
        self.bind('<Configure>', self._resize, add='+')
        self.set_record(0)

    def _resize(self, event):
        if event.widget is self._canvas:
            width = max(80, int(event.width / self._get_widget_scaling()) - 48)
            for label in (self.record, self.description):
                if label.cget('wraplength') != width:
                    label.configure(wraplength=width)

    def set_record(self, count):
        text = self.translate('All-time best streak: {count}').format(count=count)
        if self.record.cget('text') != text:
            self.record.configure(text=text)


class GrammarProgressPanel(cst.CTkFrame):
    """Five fixed bars on a common 0–100% scale, with no scroll callbacks."""
    def __init__(self, parent, translate):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self._snapshot = None
        self.grid_columnconfigure(0, weight=1)
        self.title = cst.CTkLabel(self, text=translate('Current grammar question streaks'),
            font=(FONT, 24, 'bold'), text_color=TEXT, anchor='w', justify='left', height=0)
        self.title.grid(row=0, sticky='ew', padx=24, pady=(18, 8))
        self.description = cst.CTkLabel(self, text=translate('Grammar question streaks explanation'),
            font=(FONT, 14), text_color='#665d48', anchor='w', justify='left', height=0)
        self.description.grid(row=1, sticky='ew', padx=24, pady=(0, 14))
        self.body = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.body.grid(row=2, sticky='ew', padx=24)
        self.body.grid_columnconfigure(0, weight=1)
        self.rows = []
        for index, (caption, color) in enumerate((
                ('Not practised yet', '#9a9075'),
                ('Last answer incorrect', '#aa7356'),
                ('1 correct in a row', '#89a180'),
                ('2 correct in a row', '#628b70'),
                ('3+ correct in a row', '#417766'))):
            row = cst.CTkFrame(self.body, fg_color='transparent', corner_radius=0)
            row.grid(row=index, sticky='ew', pady=(0, 12))
            row.grid_columnconfigure(0, weight=1)
            label = cst.CTkLabel(row, text=translate(caption), font=(FONT, 15),
                text_color=TEXT, anchor='w', justify='left', height=0)
            label.grid(row=0, column=0, sticky='ew', padx=(0, 12), pady=(0, 5))
            value = cst.CTkLabel(row, text='', font=(FONT, 14, 'bold'),
                text_color=TEXT, anchor='e', height=0)
            value.grid(row=0, column=1, sticky='e', pady=(0, 5))
            bar = cst.CTkProgressBar(row, height=12, corner_radius=6,
                fg_color='#c9c6af', progress_color=color)
            bar.grid(row=1, column=0, columnspan=2, sticky='ew')
            self.rows.append((label, value, bar))
        language = get_context(self).preferences.app_language
        self.scale = cst.CTkLabel(self, text=translate('Share of all grammar questions') + ' · 0–' + percent(1, language),
            font=(FONT, 13), text_color='#665d48', anchor='w', justify='left', height=0)
        self.scale.grid(row=3, sticky='ew', padx=24, pady=(0, 16))
        self.bind('<Configure>', self._resize, add='+')
        self.set_data(GrammarQuestionProgress())

    def _resize(self, event):
        if event.widget is not self._canvas:
            return
        width = max(80, int(event.width / self._get_widget_scaling()) - 48)
        for label in (self.title, self.description, self.scale):
            if label.cget('wraplength') != width:
                label.configure(wraplength=width)
        for label, value, _ in self.rows:
            available = max(60, width - value.winfo_reqwidth() / self._get_widget_scaling() - 12)
            if label.cget('wraplength') != available:
                label.configure(wraplength=available)

    def set_data(self, progress):
        progress = progress or GrammarQuestionProgress()
        language = get_context(self).preferences.app_language
        snapshot = (progress, language)
        if snapshot == self._snapshot:
            return
        for (_, value, bar), count in zip(self.rows, progress.counts):
            share = count / progress.total if progress.total else 0
            value.configure(text=number(count, language) + ' · ' + percent(share, language, 1))
            bar.set(share)
        self._snapshot = snapshot

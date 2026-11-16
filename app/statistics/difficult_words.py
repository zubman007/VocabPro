"""Read-only recent difficulty ranking and its compact answer-history cards."""
from dataclasses import dataclass
from app.shared.localization_format import percent
from app.core.context import get_context
import customtkinter as cst
from app.ui.theme import FONT, TEXT, SECTION_SURFACE


@dataclass(frozen=True)
class DifficultWord:
    word: str
    translation: str
    history: str

    @property
    def errors(self):
        return self.history.count('F')


def difficult_words(frame, language, learned_by, limit=6):
    candidates = []
    for word, translation, history in frame[[language, learned_by, 'Repetition']].fillna('').itertuples(index=False, name=None):
        recent = []
        for result in reversed(str(history)):
            if result in 'SF':
                recent.append(result)
                if len(recent) == 10:
                    break
        history = ''.join(reversed(recent))
        if len(history) >= 5 and history.count('F') >= 2:
            candidates.append(DifficultWord(str(word), str(translation), history))
    candidates.sort(key=lambda item: (-item.errors, -item.errors / len(item.history), item.word.casefold()))
    return candidates[:limit], len(candidates)


class DifficultWordsPanel(cst.CTkFrame):
    def __init__(self, parent, translate):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=24)
        self.translate = translate
        self.grid_columnconfigure(0, weight=1)
        header = cst.CTkFrame(self, fg_color='#355e59', corner_radius=18)
        header.grid(row=0, sticky='ew', padx=12, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(header, text=translate('Words needing attention'), font=(FONT, 25, 'bold'),
                     text_color='#fff0d3', anchor='w').grid(row=0, column=0, sticky='ew', padx=18, pady=(10, 2))
        cst.CTkLabel(header, text=translate('Difficulty ranking rules'), font=(FONT, 16),
                     text_color='#e5dec8', anchor='w', justify='left', wraplength=900).grid(
                         row=1, column=0, sticky='ew', padx=18, pady=(0, 10))
        self.count = cst.CTkLabel(header, text='0', font=(FONT, 28, 'bold'), text_color='#e5bf7e', width=80)
        self.count.grid(row=0, column=1, rowspan=2, padx=20)
        self.rows = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.rows.grid(row=1, sticky='ew', padx=12, pady=(0, 6))
        self.rows.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Answer strip legend'), font=(FONT, 15), text_color='#665d48').grid(
            row=2, sticky='w', padx=24, pady=(2, 10))

    def set_data(self, frame, language, learned_by):
        self.set_items(*difficult_words(frame, language, learned_by))

    def set_items(self, items, count):
        self.count.configure(text=str(count))
        for child in self.rows.winfo_children():
            child.destroy()
        if not items:
            cst.CTkLabel(self.rows, text=self.translate('No repeatedly missed words yet.'),
                         font=(FONT, 20), text_color=TEXT).grid(row=0, sticky='w', padx=16, pady=26)
        for index, item in enumerate(items):
            row = cst.CTkFrame(self.rows, fg_color='#eee4d0' if index % 2 == 0 else '#d7ddc8', corner_radius=16)
            row.grid(row=index, sticky='ew', pady=2)
            row.grid_columnconfigure(1, weight=1)
            cst.CTkLabel(row, text=f'{index+1:02}', width=50, font=(FONT, 22, 'bold'), text_color='#9b6543').grid(
                        row=0, column=0, rowspan=2, padx=12, pady=6)
            cst.CTkLabel(row, text=item.word, font=(FONT, 19, 'bold'), text_color=TEXT,
                         anchor='w', justify='left', wraplength=480).grid(row=0, column=1, sticky='ew', pady=(4, 0))
            cst.CTkLabel(row, text=item.translation, font=(FONT, 15), text_color='#60664f',
                         anchor='w', justify='left', wraplength=480).grid(row=1, column=1, sticky='ew', pady=(0, 4))
            strip = cst.CTkFrame(row, fg_color='transparent', corner_radius=0)
            strip.grid(row=0, column=2, padx=20, pady=(8, 0))
            for position in range(10):
                result = item.history[position] if position < len(item.history) else ''
                cst.CTkFrame(strip, width=12, height=18, corner_radius=4,
                    fg_color='#416d58' if result == 'S' else '#ad6548' if result == 'F' else '#c7bfa9').grid(
                        row=0, column=position, padx=2)
            cst.CTkLabel(row, text=f'{item.errors}/{len(item.history)}  ·  '
                         + percent(item.errors / len(item.history), get_context(self).preferences.app_language) + '  '
                         + self.translate('Errors'), font=(FONT, 16, 'bold'), text_color='#8d4d34').grid(
                             row=1, column=2, padx=20, pady=(0, 5))

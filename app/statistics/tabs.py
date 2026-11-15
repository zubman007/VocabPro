"""Statistics sections with natural height instead of a fixed tab viewport."""
import customtkinter as cst
from app.ui.theme import FONT, TEXT


class StatisticsTabs(cst.CTkFrame):
    def __init__(self, parent, translate, on_change=None):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.on_change = on_change
        labels = {translate(key): key for key in ('Vocabulary', 'Grammar', 'Conjugation')}
        self.navigation = cst.CTkSegmentedButton(self, values=list(labels),
            command=lambda label: self.select(labels[label]), font=(FONT, 20), height=44,
            fg_color='#ded1b4', selected_color='#b5c3a4', selected_hover_color='#a3b48f',
            unselected_color='#ded1b4', unselected_hover_color='#cdbb98',
            text_color=TEXT, text_color_disabled='#fff0d3', corner_radius=12)
        self.navigation.grid(row=0, column=0, pady=(8, 18))
        self.panels = {}
        self.labels = {key: label for label, key in labels.items()}
        for key in self.labels:
            panel = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
            panel.grid_columnconfigure((0, 1), weight=1)
            self.panels[key] = panel
        self.selected = None
        self.select('Vocabulary')

    def set_conjugation_available(self, available):
        keys = ['Vocabulary', 'Grammar', 'Conjugation'] if available else ['Vocabulary', 'Grammar']
        values = [self.labels[key] for key in keys]
        if self.navigation.cget('values') != values:
            self.navigation.configure(values=values)
            # CTk recreates segmented buttons when a language has different tabs.
            # Newly created buttons need the same image-backed rounded corners.
            provider=getattr(self.navigation,'_surface',None)
            if provider is not None:
                from app.ui.surfaces import surface
                for button in self.navigation.winfo_children():
                    if isinstance(button,cst.CTkButton) and not hasattr(button,'_surface'):
                        surface(button,provider)
                provider.request()
        if self.selected not in keys:
            self.select('Vocabulary')
        else:
            self.navigation.set(self.labels[self.selected])

    def select(self, key):
        if self.labels[key] not in self.navigation.cget('values'):
            return
        if key == self.selected:
            return
        for name, panel in self.panels.items():
            if name == key:
                panel.grid(row=1, column=0, sticky='ew')
            else:
                panel.grid_remove()
        self.selected = key
        self.navigation.set(self.labels[key])
        if self.on_change:
            self.on_change()

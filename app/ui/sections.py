"""Shared section headings and generously sized dialog tabs."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT,RADIUS
from app.ui.theme import SECTION_SURFACE


class SectionTabs(cst.CTkTabview):
    _button_height = 42

    def __init__(self, parent):
        self._transparent_panels = False
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=RADIUS,
                         segmented_button_fg_color='#ded1b4',
                         segmented_button_selected_color='#b5c3a4',
                         segmented_button_selected_hover_color='#a3b48f',
                         segmented_button_unselected_color='#ded1b4',
                         segmented_button_unselected_hover_color='#cdbb98', text_color=TEXT)
        self._segmented_button.configure(font=(FONT, 20), corner_radius=12)

    def enable_transparent_panels(self):
        self._transparent_panels = True
        self.configure(fg_color='transparent')

    def _draw(self, no_color_updates=False):
        tabs = tuple(getattr(self, '_tab_dict', {}).values())
        if not self.winfo_exists() or any(not tab.winfo_exists() for tab in tabs):
            return
        super()._draw(no_color_updates)
        if self._transparent_panels:
            for tab in tabs:
                if tab.winfo_exists() and tab.cget('fg_color') != 'transparent':
                    tab.configure(fg_color='transparent')

    def _grid_forget_all_tabs(self, exclude_name=None):
        # A pending CTk callback may refer to a tab that has since changed.
        if not self.winfo_exists():
            return
        super()._grid_forget_all_tabs(exclude_name=self.get())

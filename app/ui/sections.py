"""Shared section headings and generously sized dialog tabs."""
import customtkinter as cst
from app.ui.theme import FONT,TEXT,RADIUS
from app.ui.theme import SECTION_SURFACE
from app.ui.surfaces import surface


class EditorTabs(cst.CTkSegmentedButton):
    """Header tabs with optional body pages and composited rounded backgrounds."""
    def __init__(self, parent, values, command=None):
        self.pages = {}
        super().__init__(parent, values=values, command=command, font=(FONT, 18), height=38,
            corner_radius=12, fg_color='#d2c39f', selected_color='#a77732',
            selected_hover_color='#8b683c', unselected_color='#d2c39f',
            unselected_hover_color='#c4b18a', text_color=TEXT)

    def add_page(self, name, panel):
        self.pages[name] = panel
        self.set(self.get() or name)

    def set(self, value, **kwargs):
        super().set(value, **kwargs)
        for name, panel in self.pages.items():
            if name == value:panel.grid()
            else:panel.grid_remove()

    def attach_background(self, provider):
        layer = surface(self, provider, rasterize_frame=True)
        for button in self._buttons_dict.values():
            surface(button, layer)
        return layer


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

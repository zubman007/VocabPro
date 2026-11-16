"""Reusable summary cards; no statistics calculations."""
from app.ui.theme import FONT
import customtkinter as cst
import tkinter as tk
from app.ui.legacy_styles import lbl_set_07
from PIL import Image, ImageDraw, ImageTk
from app.ui.theme import PAGE, TEXT

CARD_STYLES = [("#d4dcc6", "#416d58"), ("#e7d0b9", "#9b6543"), ("#e7dcbb", "#977338")]
DETAIL_ROW_COLORS = ('#dedac3', '#d0d7c1')


def detail_sort_button(button):
    """Same size and caption fitting for the category/tag metric controls."""
    from app.ui.module_style import tool_button
    return tool_button(button)


def detail_practise_button(button):
    """Compact practice action shared by tag rows and grammar cards."""
    from app.ui.module_style import tool_button
    tool_button(button)
    button.configure(width=120,height=32,fg_color='#49736b',hover_color='#355e59',
                     text_color='#fff4dc')
    button._caption_minimum=32
    return button


def ring_image(diameter, line, surface, accent, rate=None):
    """Render at four times the physical size, then antialias the edges."""
    size = max(1, round(diameter + line + 4))
    factor = 4
    image = Image.new('RGB', (size * factor, size * factor), surface)
    draw = ImageDraw.Draw(image)
    inset = 2 * factor
    box = (inset, inset, size * factor - inset, size * factor - inset)
    stroke = max(1, round(line * factor))
    draw.ellipse(box, outline='#bdbca5' if rate is None else '#b98770', width=stroke)
    if rate is not None and rate > 0:
        draw.arc(box, start=-90, end=-90 + min(100, rate) * 3.6,
                 fill=accent, width=stroke)
    return image.resize((size, size), Image.Resampling.LANCZOS)


class SuccessRing(cst.CTkFrame):
    """Lightweight doughnut matching the accuracy chart, without extra figures."""
    def __init__(self, parent):
        super().__init__(parent, fg_color=parent._summary_surface, height=156)
        self.accent = parent._summary_accent
        self.surface = parent._summary_surface
        self.value, self.attempts, self.caption = '-', 0, ''
        self.pack_propagate(False)
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, background=self.surface)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', self._draw_ring)

    def configure(self, **kwargs):
        if 'text' in kwargs:
            self.value = str(kwargs.pop('text'))
            self.attempts = kwargs.pop('attempts', 1)
            if hasattr(self, 'canvas'):
                self._draw_ring()
        super().configure(**kwargs)

    def _draw_ring(self, event=None):
        self.canvas.delete('all')
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 5 or height < 5:
            return
        scale = self._get_widget_scaling()
        diameter = min(112 * scale, height - 36 * scale)
        center_x, center_y = width / 2, diameter / 2 + 6 * scale
        line = 13 * scale
        rate = None
        if self.value.endswith('%') and self.attempts:
            rate = max(0, min(100, float(self.value[:-1].strip().replace(',', '.'))))
        self._ring_photo = ImageTk.PhotoImage(
            ring_image(diameter, line, self.surface, self.accent, rate), master=self.canvas)
        self.canvas.create_image(center_x, center_y, image=self._ring_photo)
        self.canvas.create_text(center_x, center_y, text=self.value, fill=TEXT,
                                font=(FONT, -round(20*scale), 'bold'))
        self.canvas.create_text(center_x, height-13*scale, text=self.caption.rstrip(' :'), fill=TEXT,
                                font=(FONT, -round(15*scale)), width=max(20, width-20*scale))


def arrange_success_ring(ring, caption):
    ring.caption = caption.cget('text')
    caption.grid_remove()
    ring.grid_configure(column=0, columnspan=2, sticky='ew', padx=12, pady=(18, 10))


def summary_metrics(parent, captions, *, first_row=0):
    """Build the five identical summary fields, keeping captions module-specific."""
    values, labels = [], []
    for offset, caption in enumerate(captions):
        label = cst.CTkLabel(parent, text=caption, **lbl_set_07)
        value = SuccessRing(parent) if offset == 4 else cst.CTkLabel(parent, **lbl_set_07)
        label.grid(row=first_row+offset, column=0, padx=5, pady=5)
        value.grid(row=first_row+offset, column=1, padx=5, pady=5)
        labels.append(label)
        values.append(value)
    cst.CTkFrame(parent,height=2,fg_color='#b6b49a',corner_radius=0).grid(
        row=first_row+5,column=0,padx=50,pady=5,columnspan=2,sticky='we')
    return values, labels[-1]


def summary_cards(parent, titles):
    container = cst.CTkFrame(parent, fg_color=PAGE, corner_radius=0)
    container.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 16))
    interiors = []
    for column, (title, (surface, accent)) in enumerate(zip(titles, CARD_STYLES)):
        container.grid_columnconfigure(column, weight=1, uniform="summary")
        card = cst.CTkFrame(container, fg_color=surface, border_width=1,
                            border_color=surface, corner_radius=24)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 0))
        card.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(card, text=title, text_color=accent, fg_color="transparent",
                     font=(FONT, 25, "bold"), anchor="w").grid(
                         row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        cst.CTkFrame(card, height=3, fg_color=accent, corner_radius=2).grid(
            row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        inner = cst.CTkFrame(card, fg_color=surface, corner_radius=0)
        inner.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 14))
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=0)
        inner._summary_surface, inner._summary_accent = surface, accent
        interiors.append(inner)
    return container, interiors


def style_summary_cards(interiors):
    for inner in interiors:
        for label in inner.winfo_children():
            if not isinstance(label, cst.CTkLabel):
                continue
            value = int(label.grid_info().get("column", 0)) == 1
            label.configure(bg_color=inner._summary_surface, fg_color="transparent",
                text_color=inner._summary_accent if value else TEXT,
                corner_radius=0, font=(FONT, 25, "bold") if value else (FONT, 17),
                height=42, justify="left", anchor="e" if value else "w", wraplength=245 if not value else 130)
            label.grid_configure(sticky="ew", padx=6, pady=5)

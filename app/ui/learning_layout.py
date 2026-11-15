"""Shared visual language for vocabulary, grammar and conjugation screens."""
from app.paths import ROOT_DIR
import customtkinter as cst
from PIL import Image
from app.ui.surfaces import BackdropSurface
from app.ui.theme import PAGE, SURFACE, TEXT, MUTED, TEAL, HONEY, SUCCESS, ERROR, FONT


def background(frame, filename='practice_warm_v4.png'):
    frame.configure(fg_color=PAGE)
    with Image.open(ROOT_DIR / 'images' / filename) as source:
        ratio = source.width / source.height
        photo = cst.CTkImage(source.copy(), size=(1280, 720))
    label = cst.CTkLabel(frame, text='', image=photo)
    label.place(x=0, y=0, relwidth=1, relheight=1)
    label._surface = BackdropSurface(frame, photo.cget('light_image'))
    current_asset = filename
    images = {filename: photo.cget('light_image')}
    # Resize the image only when the available size actually changes.
    def resize(event=None):
        if event is not None and isinstance(frame, (cst.CTk, cst.CTkToplevel)) and event.widget is not frame:
            return
        scale = label._get_widget_scaling()
        width = max(1, frame.winfo_width() / scale)
        height = max(1, frame.winfo_height() / scale)
        size = (round(max(width, height * ratio)), round(max(height, width / ratio)))
        if photo.cget('size') != size:
            # Reassign through the public API: CTk drops obsolete size variants.
            photo.configure(light_image=photo.cget('light_image'), size=size)
        label._surface.refresh()
    pending = None
    def request_resize(event=None):
        nonlocal pending
        if event is not None and isinstance(frame, (cst.CTk, cst.CTkToplevel)) and event.widget is not frame:
            return
        if pending is None:
            pending = frame.after(24, paint_resize)
    def paint_resize():
        nonlocal pending
        pending = None
        resize()
    def cleanup(event):
        nonlocal pending
        if event.widget is label._canvas and pending is not None:
            frame.after_cancel(pending)
            pending = None
    frame.bind('<Configure>', request_resize, add='+')
    label.bind('<Destroy>', cleanup, add='+')
    def switch_asset(filename):
        nonlocal ratio, current_asset
        if filename == current_asset:
            return
        if filename not in images:
            with Image.open(ROOT_DIR / 'images' / filename) as source:
                images[filename] = source.copy()
        source = images[filename]
        ratio = source.width / source.height
        photo.configure(light_image=source)
        label._surface.source = source
        current_asset = filename
        resize()
    label.switch_asset = switch_asset
    return label


def _base_color(widget):
    parent = widget.master
    while parent is not None:
        try:
            color = parent.cget('fg_color')
            if color != 'transparent':
                return color
        except (ValueError, AttributeError):
            pass
        parent = getattr(parent, 'master', None)
    return PAGE


def label(widget, size=21, color=TEXT, bold=False):
    widget.configure(fg_color='transparent', bg_color=_base_color(widget),
                     text_color=color, font=(FONT, size, 'bold' if bold else 'normal'))


def button(widget, accent=TEAL, secondary=False):
    widget.configure(fg_color=SURFACE if secondary else accent,
                     hover_color='#e4e6d9' if secondary else '#315e59',
                     text_color=TEXT if secondary else SURFACE,
                     text_color_disabled=MUTED, corner_radius=16,
                     border_width=1, border_color='#d7d9cb',
                     font=(FONT, 19), height=48,
                     bg_color=_base_color(widget))


def entry(widget):
    widget.configure(fg_color=SURFACE, text_color=TEXT, border_color='#b3c9bd',
                     corner_radius=14, border_width=2, font=(FONT, 25), height=52,
                     bg_color=_base_color(widget))


def card(frame, color=SURFACE):
    frame.configure(fg_color=color, bg_color=_base_color(frame), corner_radius=24,
                    border_width=1, border_color='#d5d9cc')



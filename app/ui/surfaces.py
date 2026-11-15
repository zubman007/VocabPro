"""Image-backed UI surfaces and continuous backgrounds around rounded widgets.

Assets remain unchanged. Pillow composites only the live widget backgrounds;
Tk retains control of entries, focus, button hover and keyboard interaction.
"""
from app.paths import ROOT_DIR
import tkinter as tk
import weakref
import customtkinter as cst
from PIL import Image, ImageDraw, ImageOps, ImageTk

IMAGES = ROOT_DIR / 'images'


def _crop_region(image,box):
    """Geometry can briefly exceed its parent's cached image during a tab change."""
    left,top,right,bottom=box
    if 0<=left<right<=image.width and 0<=top<bottom<=image.height:return image.crop(box)
    color=image.getpixel((min(max(left,0),image.width-1),min(max(top,0),image.height-1)))
    result=Image.new(image.mode,(right-left,bottom-top),color)
    bounds=(max(0,left),max(0,top),min(right,image.width),min(bottom,image.height))
    if bounds[2]>bounds[0] and bounds[3]>bounds[1]:
        result.paste(image.crop(bounds),(bounds[0]-left,bounds[1]-top))
    return result


def _rgb(widget, color):
    # Tk theme colors also include names such as gray17 and SystemButtonFace.
    return tuple(channel // 257 for channel in widget.winfo_rgb(color))


class BackdropSurface:
    def __init__(self, widget, image):
        self.widget, self.source = widget, image
        self.revision = 0
        self._signature, self._image = None, None
        self.children = weakref.WeakSet()

    def refresh(self):
        signature = (self.widget.winfo_width(), self.widget.winfo_height(), id(self.source))
        if signature != self._signature:
            self._signature, self._image = signature, None
            self.revision += 1
            for child in list(self.children):
                child.request()

    def region(self, widget):
        self.refresh()
        if self._image is None:
            self._image = ImageOps.fit(self.source, (max(1, self._signature[0]), max(1, self._signature[1])))
        x, y = widget.winfo_rootx()-self.widget.winfo_rootx(), widget.winfo_rooty()-self.widget.winfo_rooty()
        return _crop_region(self._image,(x, y, x+max(1, widget.winfo_width()), y+max(1, widget.winfo_height())))


class PanelSurface:
    def __init__(self, widget, parent, filename=None, wash=0.65):
        self.widget, self.parent, self.wash = widget, parent, wash
        self.canvas = widget._canvas
        self.source = None
        if filename:
            with Image.open(IMAGES / filename) as image:
                self.source = image.convert('RGB')
        self.revision = 0
        self.children = weakref.WeakSet()
        self._pending = self._photo = self._image = self._key = self._item = self._background = None
        self._dead = False
        self._painted_key, self._announced_revision = None, -1
        self._underlay = None
        parent.children.add(self)
        original_draw = widget._draw
        def draw(*args, **kwargs):
            original_draw(*args, **kwargs)
            self.request()
        widget._draw = draw
        self.canvas.bind('<Configure>', lambda event=None: self.request(), add='+')
        # CTk forwards bind() to its canvas, which misses position-only moves.
        tk.Misc.bind(widget, '<Configure>', lambda event=None: self.request(), add='+')
        self.canvas.bind('<Destroy>', lambda event=None: self.close(), add='+')
        self.request()

    def request(self):
        if not self._dead and self._pending is None:
            self._pending = self.widget.after(24, self.paint)

    def _render(self):
        widget = self.widget
        size = max(1, widget.winfo_width()), max(1, widget.winfo_height())
        if isinstance(self.parent, BackdropSurface):
            self.parent.refresh()
        else:
            self.parent._render()
        color = widget._apply_appearance_mode(widget.cget('fg_color'))
        scale = widget._get_widget_scaling()
        radius = round(widget.cget('corner_radius') * scale)
        border = round(widget.cget('border_width') * scale) if hasattr(widget, '_border_width') else 0
        if isinstance(widget, cst.CTkSegmentedButton):
            border = 0  # Its "border" is spacing between buttons, not an outline.
        border_color = getattr(widget, '_border_color', color)
        # Moving a whole scroll subtree does not change its children's pixels.
        origin = self.parent.widget
        key = (size, widget.winfo_rootx()-origin.winfo_rootx(), widget.winfo_rooty()-origin.winfo_rooty(), self.parent.revision, color, radius, border,
               border_color if border else None)
        if self._key == key:
            return self._background
        background = self.parent.region(widget)
        self._background = background
        self._key = key
        self._image = background.copy().convert('RGB')
        if color != 'transparent':
            fill = Image.new('RGB', size, _rgb(widget, color))
            if self.source is not None:
                fill = Image.blend(ImageOps.fit(self.source, size), fill, self.wash)
            # Supersampling applies to the UI corner mask, never to an asset file.
            mask = Image.new('L', (size[0]*2, size[1]*2))
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0]*2-1, size[1]*2-1), radius=radius*2, fill=255)
            mask = mask.resize(size, Image.Resampling.LANCZOS)
            self._image.paste(fill, (0, 0), mask)
            if border:
                ImageDraw.Draw(self._image).rounded_rectangle(
                    (border//2, border//2, size[0]-1-border//2, size[1]-1-border//2),
                    radius=max(0, radius-border//2), width=border,
                    outline=_rgb(widget, widget._apply_appearance_mode(border_color)))
        self.revision += 1
        return background

    def paint(self):
        if self._pending is not None:
            self.widget.after_cancel(self._pending)
        self._pending = None
        if self._dead or self.widget.winfo_width() < 2 or self.widget.winfo_height() < 2:
            return
        background = self._render()
        if self._painted_key != self._key:
            self._photo = ImageTk.PhotoImage(self._image if self.source is not None else background, master=self.widget)
            if self._item is None:
                self._item = self.canvas.create_image(0, 0, anchor='nw', image=self._photo)
            else:
                self.canvas.itemconfigure(self._item, image=self._photo)
            self._painted_key = self._key
        # Tabview's canvas starts below its tab buttons, unlike a plain frame.
        self.canvas.coords(self._item, -self.canvas.winfo_x(), -self.canvas.winfo_y())
        if self.canvas.winfo_x() or self.canvas.winfo_y():
            if self._underlay is None:
                self._underlay = tk.Canvas(self.widget, bd=0, highlightthickness=0)
                self._underlay.place(x=0, y=0, relwidth=1, relheight=1)
                self.widget.tk.call('lower', str(self._underlay))
            self._underlay.delete('all')
            self._underlay.create_image(0, 0, anchor='nw', image=self._photo)
        if self.source is None:
            self.canvas.tag_lower(self._item)
            self.canvas.itemconfigure('inner_parts', state='hidden' if self.widget.cget('fg_color') == 'transparent' else 'normal')
            self.canvas.itemconfigure('background_parts', state='hidden')
        else:
            self.canvas.tag_raise(self._item)
        if self._announced_revision != self.revision:
            self._announced_revision = self.revision
            for child in list(self.children):
                child.request()

    def region(self, widget):
        self._render()
        x, y = widget.winfo_rootx()-self.widget.winfo_rootx(), widget.winfo_rooty()-self.widget.winfo_rooty()
        return _crop_region(self._image,(x, y, x+max(1, widget.winfo_width()), y+max(1, widget.winfo_height())))

    def close(self):
        self._dead = True
        if self._pending is not None:
            try:
                self.widget.after_cancel(self._pending)
            except tk.TclError:
                pass
        self._pending = self._photo = self._image = self._background = None
        self.source = None
        self.parent.children.discard(self)


def surface(widget, parent, filename=None, wash=0.65):
    """Attach once; flat children retain their native rounded edges and hover."""
    provider = getattr(parent, '_surface', parent)
    widget._surface = PanelSurface(widget, provider, filename, wash)
    return widget._surface

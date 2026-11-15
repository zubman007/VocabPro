"""Scroll-stable statistics texture: Tk moves cached pixels instead of repainting."""
import tkinter as tk
import weakref
from PIL import Image, ImageTk
from app.ui.surfaces import BackdropSurface, surface


class ScrollSurface(BackdropSurface):
    """Repeat one viewport-sized tile in content coordinates, without a giant bitmap."""
    def __init__(self, scroller, backdrop):
        self.widget = scroller.interior
        self.viewport, self.backdrop = scroller.canvas, backdrop._surface
        self.children = weakref.WeakSet()
        self.revision = 0
        self._key = self._image = None

    def refresh(self):
        self.backdrop.refresh()
        key = (self.viewport.winfo_width(), self.viewport.winfo_height(), self.backdrop.revision,
               self.viewport.winfo_rootx()-self.backdrop.widget.winfo_rootx(),
               self.viewport.winfo_rooty()-self.backdrop.widget.winfo_rooty())
        if key != self._key:
            self._image = self.backdrop.region(self.viewport).convert('RGB')
            self._key = key
            self.revision += 1
            for child in list(self.children):
                child.request()

    def region(self, widget):
        self.refresh()
        x = widget.winfo_rootx()-self.widget.winfo_rootx()
        y = widget.winfo_rooty()-self.widget.winfo_rooty()
        width, height = max(1, widget.winfo_width()), max(1, widget.winfo_height())
        result = Image.new('RGB', (width, height))
        tile_width, tile_height = self._image.size
        for left in range(-(x % tile_width), width, tile_width):
            for top in range(-(y % tile_height), height, tile_height):
                result.paste(self._image, (left, top))
        return result


class StatisticsBackdrop:
    def __init__(self, scroller, backdrop):
        self.scroller, self.backdrop = scroller, backdrop
        self.panels = []
        self._pending = self._photo = self._key = None
        self._dead = False
        self.surface = ScrollSurface(scroller, backdrop)
        self.layer = tk.Canvas(scroller.interior, bd=0, highlightthickness=0)
        self.layer.place(x=0, y=0, width=1, height=1)
        self.layer.tk.call('lower', str(self.layer))
        scroller.canvas.configure(yscrollcommand=self._scroll_changed)
        scroller.canvas.bind('<Configure>', lambda event: self.request(), add='+')
        scroller.interior.bind('<Configure>', lambda event: self.request(), add='+')
        self.layer.bind('<Destroy>', lambda event: self.close(), add='+')
        self.request()

    def add_panel(self, widget, parent=None):
        ancestor = widget
        while ancestor is not None and ancestor is not self.scroller.interior:
            ancestor = getattr(ancestor, 'master', None)
        provider = self.surface if ancestor is self.scroller.interior else self.backdrop
        panel = surface(widget, parent if parent is not None else provider)
        self.panels.append(panel)
        return panel

    def _scroll_changed(self, first, last):
        self.scroller.vscrollbar.set(first, last)
        if self._dead:
            return
        # Tk scrolls the existing images. Scrolling schedules no Pillow/Tk image work.

    def request(self):
        if not self._dead and self._pending is None:
            self._pending = self.layer.after(24, self.paint)

    def paint(self):
        if self._pending is not None:
            self.layer.after_cancel(self._pending)
        self._pending = None
        if self._dead:
            return
        viewport = self.scroller.canvas
        width, height = viewport.winfo_width(), viewport.winfo_height()
        if width < 2 or height < 2:
            return
        provider = self.surface
        provider.refresh()
        content_height = max(height, self.scroller.interior.winfo_height())
        key = (width, height, content_height, provider.revision)
        if key != self._key:
            self._photo = ImageTk.PhotoImage(provider._image, master=self.layer)
            self.layer.delete('all')
            for y in range(0, content_height, height):
                self.layer.create_image(0, y, anchor='nw', image=self._photo)
            self._key = key
        self.layer.place_configure(y=0, width=width, height=content_height)
        top, bottom = viewport.winfo_rooty(), viewport.winfo_rooty()+height
        for panel in self.panels:
            widget = panel.widget
            if not panel._dead and widget.winfo_ismapped() and widget.winfo_rooty() < bottom \
                    and widget.winfo_rooty()+widget.winfo_height() > top:
                panel.request()

    def close(self):
        self._dead = True
        if self._pending is not None:
            self.layer.after_cancel(self._pending)
        self._pending = self._photo = None
        self.surface._image = None
        self.surface.children.clear()
        self.panels.clear()

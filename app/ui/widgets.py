"""Scrollable statistics viewport and mousewheel lifecycle."""
from tkinter import Canvas, Text, Listbox, TclError, VERTICAL, RIGHT, LEFT, Y, BOTH, NW
from tkinter import ttk
from app.ui.theme import PAGE as clr_bg_stats

class VerticalScrolledFrame_class(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)
        ttk.Style().configure("Stats.TFrame", background=clr_bg_stats)
        self.vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self,bd=0,highlightthickness=0,background=clr_bg_stats,yscrollcommand=self.vscrollbar.set,)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.interior = ttk.Frame(self.canvas, style="Stats.TFrame")
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
        self._scroll_region = None
        self.interior.bind("<Configure>", self.configure_interior)
        self.canvas.bind("<Configure>", self.configure_canvas)
        self._wheel_owner = self.winfo_toplevel()
        self._wheel_binding = self._wheel_owner.bind("<MouseWheel>", self.on_mousewheel, add="+")
    def configure_interior(self, event=None):
        width = self.interior.winfo_reqwidth()
        height = self.interior.winfo_reqheight()
        region = (0, 0, width, height)
        if region != self._scroll_region:
            self.canvas.config(scrollregion=region)
            self._scroll_region = region
        if width != self.winfo_width(): self.canvas.config(width=width)
    def configure_canvas(self, event=None):
        width = self.winfo_width()
        if self.interior.winfo_reqwidth() != width: self.canvas.itemconfigure(self.interior_id, width=width)
    def on_mousewheel(self, event, scroll=None):
        hovered = self.winfo_containing(event.x_root, event.y_root)
        while hovered is not None and hovered is not self:
            if isinstance(hovered, (ttk.Treeview, Text, Listbox)):
                return
            hovered = hovered.master
        if hovered is None:
            return
        delta = int(-1 * (event.delta / 120))
        if self.interior.winfo_y() < 0 or delta > 0: self.canvas.yview_scroll(delta, "units")
        return "break"

    def destroy(self):
        try:
            self._wheel_owner.unbind("<MouseWheel>", self._wheel_binding)
        except TclError:
            pass
        super().destroy()

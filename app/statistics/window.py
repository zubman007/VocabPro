"""Statistics window lifecycle: present loading first, reveal prepared content."""
import logging
from tkinter import messagebox
import customtkinter as cst
from app.shared import settings as s
from app.ui.theme import PAGE, SECTION_SURFACE as SURFACE, TEXT, FONT

logger = logging.getLogger(__name__)


class StatisticsWindow(cst.CTkToplevel):
    def __init__(self, owner):
        super().__init__(owner, fg_color=PAGE)
        self.withdraw()
        self._jobs = set()
        self._closing = self._building = False
        self._next_builder = None
        self.ready = False
        self.content = cst.CTkFrame(self, fg_color=PAGE, corner_radius=0)
        self.content.place(x=0, y=0, relwidth=1, relheight=1)
        self.cover = None
        self._show_cover()
        self.bind('<Escape>', lambda event: self.destroy())

    def _later(self, delay, callback):
        def invoke():
            self._jobs.discard(token)
            if not self._closing:
                callback()
        token = self.after(delay, invoke)
        self._jobs.add(token)

    def _show_cover(self):
        if self.cover is None:
            self.cover = cst.CTkFrame(self, fg_color=PAGE, corner_radius=0)
            self.cover.place(x=0, y=0, relwidth=1, relheight=1)
            card = cst.CTkFrame(self.cover, fg_color=SURFACE, corner_radius=24,
                                border_width=1, border_color='#c7b995')
            card.place(relx=.5, rely=.5, anchor='center')
            cst.CTkLabel(card, text=s.T('Loading statistics'), font=(FONT, 26, 'bold'),
                         text_color=TEXT).pack(padx=40, pady=30)
        self.cover.lift()

    def begin(self, builder):
        # Let CTk finish its deferred Windows titlebar setup before mapping.
        def present():
            self.deiconify()
            self.state('zoomed')
            self.lift()
            self.update_idletasks()
            self.load(builder)
        self._later(250, present)

    def load(self, builder):
        if self._closing:
            return
        if self._building:
            self._next_builder = builder
            return
        self.ready = False
        self._building = True
        self._show_cover()
        self._later(60, lambda: self._build(builder))

    def _build(self, builder):
        try:
            deferred = builder() is False
            self.content.update_idletasks()
        except Exception as error:
            logger.exception('Statistics preparation failed')
            messagebox.showerror(parent=self, title=s.T('Statistics'), message=str(error))
            self.destroy()
            return
        if not deferred:
            self.complete()

    def complete(self):
        if not self._closing:
            self._later(120, self._reveal)

    def fail(self, error):
        if self._closing:
            return
        logger.error('Statistics preparation failed: %s', type(error).__name__)
        messagebox.showerror(parent=self, title=s.T('Statistics'), message=s.T(str(error)))
        self.destroy()

    def _reveal(self):
        if self._next_builder is not None:
            builder, self._next_builder = self._next_builder, None
            self._building = False
            self.load(builder)
            return
        self.content.update_idletasks()
        if hasattr(self.content, '_surface'):
            self.content._surface.paint()
        backdrop = getattr(self, '_statistics_backdrop', None)
        if backdrop is not None:
            backdrop.paint()
            for panel in backdrop.panels:
                if not panel._dead and panel.widget.winfo_ismapped():
                    panel.paint()
        self.content.update_idletasks()
        self.cover.destroy()
        self.cover = None
        self.ready = True
        self._building = False

    def destroy(self):
        if self._closing:
            return
        self._closing = True
        self._next_builder = None
        controller = getattr(self, 'controller', None)
        if controller is not None:
            controller.close()
        for token in self._jobs:
            self.after_cancel(token)
        self._jobs.clear()
        super().destroy()

"""Spreadsheet-owned timers must end before Tk deletes their callback commands."""
import tkinter as tk
import tksheet


class Spreadsheet(tksheet.Sheet):
    def destroy(self):
        # tksheet schedules redraw/tooltip work on child canvases. Tk destroys
        # their commands but leaves timers queued, allowing later command reuse.
        for owner in (self, self.MT, self.CH, self.RI):
            for attribute in ('after_redraw_id', 'tooltip_after_id'):
                token = getattr(owner, attribute, None)
                if token is not None:
                    try:owner.after_cancel(token)
                    except tk.TclError:pass
                    setattr(owner, attribute, None)
        super().destroy()

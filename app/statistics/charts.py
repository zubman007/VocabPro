"""Chart rendering and lifecycle, separate from statistics calculations."""
from app.statistics.chart_style import STYLES, style_chart
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import tkinter as tk
from app.shared.localization_format import number, percent, date_pattern, date_text
from matplotlib.ticker import FuncFormatter


class _HoverBlit:
    """Cache static figure pixels; invalidate them on every full draw/resize."""
    def __init__(self, canvas, annotation):
        self.canvas, self.annotation = canvas, annotation
        self.background = None
        self.enabled = canvas.supports_blit
        annotation.set_animated(self.enabled)
        self.callbacks = [canvas.mpl_connect('draw_event', self._capture),
                          canvas.mpl_connect('resize_event', self._invalidate)]

    def _capture(self, event):
        if self.enabled:
            self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
            if self.annotation.get_visible():
                self.canvas.figure.draw_artist(self.annotation)

    def _invalidate(self, event):
        self.background = None

    def paint(self):
        if not self.enabled or self.background is None:
            self.canvas.draw_idle()
            return
        self.canvas.restore_region(self.background)
        if self.annotation.get_visible():
            self.canvas.figure.draw_artist(self.annotation)
        self.canvas.blit(self.canvas.figure.bbox)

    def close(self):
        for callback in self.callbacks:
            self.canvas.mpl_disconnect(callback)
        self.callbacks.clear()
        self.background = None
        self.annotation.set_animated(False)


def _release_chart(chart_frm, *, destroying=False):
    """Release callbacks, scheduled redraws and the figure owned by a chart."""
    canvas = getattr(chart_frm, "_chart_canvas", None)
    if canvas is None:
        return
    chart_frm._chart_canvas = None
    chart_frm._chart_snapshot = None
    for owner, sequence, token in getattr(chart_frm, '_chart_tk_bindings', ()):
        if not destroying:
            owner.unbind(sequence, token)
            continue
        # Destroy dispatch may already hold a snapshot of the toplevel binding
        # script. Remove the binding now, but keep its Tcl command alive until
        # that dispatch finishes. A Tcl-only idle job also survives destruction
        # of the owning window without creating a stale Python after callback.
        script = owner.bind(sequence) or ''
        prefix = f'if {{"[{token} '
        owner.tk.call('bind', owner._w, sequence,
                      '\n'.join(line for line in script.split('\n') if not line.startswith(prefix)))
        if token in (owner._tclCommands or ()):
            owner._tclCommands.remove(token)
        cleanup = owner.tk.call('list', 'catch', owner.tk.call('list', 'rename', token, ''))
        owner.tk.call('after', 'idle', cleanup)
    chart_frm._chart_tk_bindings = ()
    hover_blit = getattr(chart_frm, '_chart_blit', None)
    if hover_blit is not None:
        hover_blit.close()
        chart_frm._chart_blit = None
    callback = getattr(chart_frm, "_chart_hover_id", None)
    if callback is not None:
        canvas.mpl_disconnect(callback)
        chart_frm._chart_hover_id = None
    widget = canvas.get_tk_widget()
    for attribute in ("_idle_draw_id", "_event_loop_id"):
        pending = getattr(canvas, attribute, None)
        if pending is not None:
            widget.after_cancel(pending)
            setattr(canvas, attribute, None)
    canvas.figure.clear()
    if widget.winfo_exists():
        widget.destroy()


def _fit_chart_inset(frame):
    """Tk canvases are rectangular; keep them inside CTk's scaled corner arcs."""
    canvas = getattr(frame, '_chart_canvas', None)
    if canvas is None:
        return
    inset = max(1, round(frame.cget('corner_radius') * frame._get_widget_scaling()))
    if getattr(frame, '_chart_inset', None) != inset:
        canvas.get_tk_widget().grid_configure(padx=inset, pady=inset)
        frame._chart_inset = inset


def Generate_chart(data, chart_frm, name, chart_row):
    from app.shared import settings as s
    from app.core.context import get_context
    ui_language = get_context(chart_frm).preferences.app_language
    signature = (name, chart_row, ui_language)
    snapshot = getattr(chart_frm, '_chart_snapshot', None)
    values = data if isinstance(data, list) else [data]
    if snapshot is not None and snapshot[0] == signature and len(snapshot[1]) == len(values):
        if all(old.equals(new) for old, new in zip(snapshot[1], values)):
            chart_frm.grid()
            return
    _release_chart(chart_frm)
    if not getattr(chart_frm, '_chart_cleanup_bound', False):
        tk.Misc.bind(chart_frm, '<Destroy>',
            lambda event, frame=chart_frm: _release_chart(frame, destroying=True) if event.widget is frame else None, add='+')
        tk.Misc.bind(chart_frm, '<Configure>',
            lambda event, frame=chart_frm: _fit_chart_inset(frame) if event.widget is frame else None, add='+')
        chart_frm._chart_cleanup_bound = True
    if len(data) == 0:
        chart_frm.grid_remove()
        return
    def show(x, y, text):
        if annot.get_visible() and annot.get_text() == text and annot.xy == (x, y):
            return
        annot.xy = (x, y)
        annot.set_text(text)
        annot.set_position((-100, 10))
        annot.get_bbox_patch().set_alpha(1)
        annot.set_visible(True)
        chart_frm._chart_blit.paint()
    def hide():
        if annot.get_visible():
            annot.set_visible(False)
            chart_frm._chart_blit.paint()
    def hover(event):
        if event.inaxes != ax: hide(); return
        if name == "Number of words to review next days":
            cont, ind = scat.contains(event)
            if not cont: hide(); return
            i = ind["ind"][0]
            x, y = x_nz[i], y_nz[i]
            show(x, y, f"{date_text(x, ui_language)}\n{s.T('Number of words')}: {int(y)}")
            return
        if name == "Growth of the vocabulary":
            cont, ind = scat.contains(event)
            if not cont:
                hide()
                return
            i = ind["ind"][0]
            x, y = x_pts[i], y_pts[i]
            show(x, y, f"{date_text(x, ui_language)}\n{s.T('Number of words')}: {int(y)}")
            return
        for p, (lbl, ser_name, y) in patch_info.items():
            hit, _ = p.contains(event)
            if not hit: continue
            x = p.get_x() + p.get_width() / 2
            if name == "Vocabulary by Part of Speech": show(x, y, f"{percent(y / 100, ui_language, 2)}\n{int(df_nom.loc[lbl, ser_name])}"); return
            if name == "Conjugation trailing successes": show(x, y, f"{lbl}\n{s.T('Number of verbs')}: {int(y)}"); return
            if name == "Vocabulary trailing successes": show(x, y, f"{lbl}\n{s.T('Number of words')}: {int(y)}"); return
        hide()
    fig = Figure(figsize=(14, 4.8), dpi=100)
    ax = fig.add_subplot(111)
    annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
        bbox=dict(boxstyle="round", fc="#fff6e6", ec="#92704a", alpha=1),
        arrowprops=dict(arrowstyle="->"), zorder=100)
    annot.set_visible(False)
    patch_info, scat, x_nz, y_nz = {}, None, None, None
    ser = data.copy()
    chart_frm.grid(row = chart_row, column = 0, sticky = "NWES", padx = 20, pady = 12, columnspan = 2)
    if name == "Number of words to review next days":
        full_idx = pd.date_range(ser.index.min(), ser.index.max(), freq="D")
        ser = ser.reindex(full_idx, fill_value=0)
        x_num = mdates.date2num(ser.index)
        y_vals = ser.values.astype(float)
        x_s = np.linspace(x_num.min(), x_num.max(), len(x_num) * 10)
        # Linear interpolation preserves samples without introducing overshoot.
        y_s = np.maximum(np.interp(x_s, x_num, y_vals), 0)
        ax.plot(mdates.num2date(x_s), y_s, color="#416d58", linewidth=2)
        ax.fill_between(mdates.num2date(x_s), y_s, alpha=0.12, color=STYLES[name][0])
        mask = (ser.values != 0) & (~pd.isna(ser.values))
        x_nz, y_nz = ser.index[mask], ser.values[mask]
        scat = ax.scatter(x_nz, y_nz, picker=False, color=STYLES[name][0])
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_pattern(ui_language)))
        ax.margins(x=0.01)
        ax.set_xlabel(s.T("Date"), fontsize=14)
        ax.set_ylabel(s.T("Number of words"), fontsize=14)
        x_lbl_size = 10
    elif name == "Growth of the vocabulary":
        full_idx = pd.date_range(ser.index.min(), ser.index.max(), freq="D")
        ser = ser.reindex(full_idx).ffill().fillna(0)
        x_num = mdates.date2num(ser.index)
        y_vals = ser.values.astype(float)
        ax.plot(ser.index, y_vals, linewidth=2, color="#416d58")
        ax.fill_between(ser.index, y_vals, alpha=0.12, color=STYLES[name][0])
        x_pts, y_pts = ser.index, y_vals
        scat = ax.scatter(x_pts, y_pts, s=7, picker=False, color=STYLES[name][0])
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_pattern(ui_language)))
        ax.margins(x=0.01)
        ax.set_xlabel(s.T("Date"), fontsize=14)
        ax.set_ylabel(s.T("Number of words"), fontsize=14)
        x_lbl_size = 10
    elif name == "Vocabulary by Part of Speech":
        df_pct, df_nom = data
        df_pct = df_pct.rename(index=s.T,columns=s.T)
        df_nom = df_nom.rename(index=s.T,columns=s.T)
        df_pct.plot(kind="bar", ax=ax, color=["#557b61", "#b58a54"], edgecolor="white")
        lbls = [str(i) for i in df_pct.index]
        ser_names = list(df_pct.columns)
        for i, p in enumerate(ax.patches):
            cat_i, ser_i = i % len(lbls), i // len(lbls)
            lbl = lbls[cat_i]
            ser_name = ser_names[ser_i]
            y = float(p.get_height())
            patch_info[p] = (lbl, ser_name, y)
            p.set_picker(False)
        ax.set_xlabel(s.T("Part of Speech"), fontsize=14)
        ax.set_ylabel(s.T("Percentage of words"), fontsize=14)
        x_lbl_size = 20
    elif name in ("Conjugation trailing successes"):
        ser.plot(kind="bar", ax=ax, color="#557b61", edgecolor="white")
        lbls = [str(i) for i in ser.index]
        for i, p in enumerate(ax.patches):
            patch_info[p] = (lbls[i] if i < len(lbls) else "", "Real", float(p.get_height()))
            p.set_picker(False)
        ax.set_xlabel(s.T("Number of trailing successful attempts"), fontsize=14)
        ax.set_ylabel(s.T("Number of verbs"), fontsize=14)
        x_lbl_size = 12
    elif name == "Vocabulary trailing successes":
        ser.plot(kind="bar", ax=ax, color="#557b61", edgecolor="white")
        lbls = [str(i) for i in ser.index]
        for i, p in enumerate(ax.patches):
            patch_info[p] = (lbls[i] if i < len(lbls) else "", "Real", float(p.get_height()))
            p.set_picker(False)
        ax.set_xlabel(s.T("Number of trailing successful attempts"), fontsize=14)
        ax.set_ylabel(s.T("Number of words"), fontsize=14)
        x_lbl_size = 12

    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, position:
        number(value, ui_language, 0 if float(value).is_integer() else 2)))
    style_chart(fig, ax, name, s.T(name), x_lbl_size)
    chart_frm.configure(fg_color=STYLES[name][1], border_width=0, corner_radius=12)
    for w in chart_frm.winfo_children(): w.destroy()
    owner = chart_frm.winfo_toplevel()
    before = set(owner._tclCommands or ())
    canvas = FigureCanvasTkAgg(fig, master=chart_frm)
    # TkAgg installs callbacks on the toplevel. Remove these explicitly when
    # replacing a chart, rather than waiting for weakref cleanup during destroy.
    created = set(owner._tclCommands or ()) - before
    chart_frm._chart_tk_bindings = [(owner, sequence, token)
        for sequence in ('<MouseWheel>', '<Destroy>')
        for token in created if token in (owner.bind(sequence) or '')]
    chart_frm._chart_canvas = canvas
    chart_frm._chart_blit = _HoverBlit(canvas, annot)
    chart_frm._chart_hover_id = canvas.mpl_connect("motion_notify_event", hover)
    chart_frm._chart_inset = None
    canvas.get_tk_widget().grid(row=0, column=0, sticky="NWES")
    _fit_chart_inset(chart_frm)
    # Coalesce the first draw with Tk's final geometry instead of drawing twice.
    canvas.draw_idle()
    chart_frm._chart_snapshot = (signature, [value.copy(deep=True) for value in values])


"""Hover pixels, cache lifecycle, fallback and forecast interpolation contracts."""
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import ast
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backend_bases import ResizeEvent
from app.statistics.charts import _HoverBlit


class ChartRenderingTests(TestCase):
    def test_destroying_chart_host_does_not_delete_commands_during_tcl_dispatch(self):
        import customtkinter as cst
        import pandas as pd
        from app.statistics.charts import Generate_chart
        root = cst.CTk()
        root.tk.eval('set ::chart_errors {}; proc bgerror {message} {lappend ::chart_errors $message}')
        try:
            for _ in range(3):
                host = cst.CTkFrame(root)
                Generate_chart(pd.Series([1, 2]), host, 'Vocabulary trailing successes', 0)
                root.update()
                tokens = [token for _, _, token in host._chart_tk_bindings]
                host.destroy()
                root.update()
                for token in tokens:
                    self.assertFalse(root.tk.call('info', 'commands', token))
            self.assertFalse(root.tk.call('set', '::chart_errors'))
        finally:
            for job in root.tk.call('after', 'info'): root.tk.call('after', 'cancel', job)
            root.destroy()

    def test_real_tk_hover_show_hide_and_release(self):
        import customtkinter as cst
        import pandas as pd
        from matplotlib.backend_bases import MouseEvent
        from app.statistics.charts import Generate_chart, _release_chart
        root=cst.CTk();root.geometry('800x500')
        try:
            frame=cst.CTkFrame(root);frame.pack(fill='both',expand=True)
            host=cst.CTkFrame(frame);host.grid_columnconfigure(0,weight=1)
            Generate_chart(pd.Series([2,4],index=[0,1]),host,'Vocabulary trailing successes',0)
            root.update();canvas=host._chart_canvas;canvas.draw()
            axes=canvas.figure.axes[0];bar=axes.patches[0]
            x,y=axes.transData.transform((bar.get_x()+bar.get_width()/2,1))
            manager=host._chart_blit
            with patch.object(canvas,'draw_idle') as full:
                canvas.callbacks.process('motion_notify_event',MouseEvent('motion_notify_event',canvas,x,y))
                self.assertTrue(manager.annotation.get_visible())
                canvas.callbacks.process('motion_notify_event',MouseEvent('motion_notify_event',canvas,-5,-5))
                self.assertFalse(manager.annotation.get_visible())
                full.assert_not_called()
            _release_chart(host)
            self.assertIsNone(manager.background)
            self.assertIsNone(host._chart_blit)
        finally:
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()

    def make_chart(self):
        figure=Figure(figsize=(5,3),dpi=100);canvas=FigureCanvasAgg(figure)
        axes=figure.subplots();axes.plot([0,1,2],[0,1,0])
        annotation=axes.annotate('detail',xy=(1,.5),bbox={'fc':'white'})
        annotation.set_visible(False)
        manager=_HoverBlit(canvas,annotation);self.addCleanup(manager.close)
        canvas.draw()
        return canvas,annotation,manager

    def test_hover_restores_exact_static_pixels_and_does_not_redraw_axes(self):
        canvas,annotation,manager=self.make_chart()
        before=np.asarray(canvas.buffer_rgba()).copy()
        with patch.object(canvas,'draw_idle') as full:
            annotation.set_visible(True);manager.paint()
            self.assertFalse(np.array_equal(before,np.asarray(canvas.buffer_rgba())))
            annotation.set_visible(False);manager.paint()
            np.testing.assert_array_equal(before,np.asarray(canvas.buffer_rgba()))
            full.assert_not_called()

    def test_resize_discards_old_cache_and_draw_refreshes_it(self):
        canvas,annotation,manager=self.make_chart()
        canvas.figure.set_size_inches(6,4)
        canvas.callbacks.process('resize_event',ResizeEvent('resize_event',canvas))
        self.assertIsNone(manager.background)
        annotation.set_visible(True);manager.paint()
        self.assertIsNotNone(manager.background)
        annotation.set_visible(False);manager.paint()
        self.assertEqual(np.asarray(canvas.buffer_rgba()).shape,(400,600,4))

    def test_backend_without_blitting_uses_full_redraw(self):
        canvas,annotation,old=self.make_chart();old.close()
        with patch.object(canvas,'supports_blit',False):
            manager=_HoverBlit(canvas,annotation)
        self.addCleanup(manager.close)
        with patch.object(canvas,'draw_idle') as redraw:manager.paint();redraw.assert_called_once()
        self.assertFalse(annotation.get_animated())

    def test_close_disconnects_callbacks_and_releases_pixels(self):
        canvas,annotation,manager=self.make_chart();tokens=list(manager.callbacks)
        manager.close();manager.close()
        self.assertIsNone(manager.background)
        self.assertFalse(annotation.get_animated())
        for callbacks in canvas.callbacks.callbacks.values():
            self.assertTrue(set(tokens).isdisjoint(callbacks))

    def test_forecast_no_longer_imports_scipy_and_interpolation_has_no_overshoot(self):
        path=Path(__file__).resolve().parents[1]/'statistics/charts.py'
        tree=ast.parse(path.read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(n,ast.ImportFrom) and (n.module or '').startswith('scipy') for n in ast.walk(tree)))
        for x,y in (([0],[3]),([0,1],[0,4]),([0,1,2],[3,0,8])):
            samples=np.linspace(x[0],x[-1],30)
            values=np.interp(samples,x,y)
            self.assertTrue(np.isfinite(values).all())
            self.assertGreaterEqual(values.min(),min(y))
            self.assertLessEqual(values.max(),max(y))

    def test_hover_raster_benchmark(self):
        canvas,annotation,manager=self.make_chart();annotation.set_visible(True)
        start=perf_counter()
        for _ in range(20):canvas.draw()
        full=perf_counter()-start
        start=perf_counter()
        for _ in range(20):manager.paint()
        partial=perf_counter()-start
        print(f'PERF hover raster 20 updates: full {full*1000:.2f} ms; blit {partial*1000:.2f} ms')

"""Read-only UI profile: python -B -m app.statistics.profile_scroll.

Uses existing course files without opening practice or running backup services.
"""
import cProfile
import pstats
import ast
import inspect
import subprocess
import argparse
from time import perf_counter
from statistics import median
import customtkinter as cst
from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import load_preferences
from app.statistics.viewer import Stats
from app.ui.widgets import VerticalScrolledFrame_class


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true', help='Use painting methods from Git HEAD for comparison')
    parser.add_argument('--compare', action='store_true', help='Measure baseline then optimized methods in one window')
    options = parser.parse_args()
    overrides = []
    if options.baseline or options.compare:
        from app.ui.surfaces import PanelSurface
        from app.statistics.background import StatisticsBackdrop
        for cls, method, path in (
                (PanelSurface, 'paint', 'app/ui/surfaces.py'),
                (StatisticsBackdrop, 'paint', 'app/statistics/background.py')):
            overrides.append((cls, method, getattr(cls, method)))
            source = subprocess.run(['git', 'show', 'HEAD:' + path], check=True,
                                    capture_output=True, encoding='utf-8').stdout
            tree = ast.parse(source)
            old_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls.__name__)
            function = next(node for node in old_class.body if isinstance(node, ast.FunctionDef) and node.name == method)
            namespace = dict(vars(inspect.getmodule(cls)))
            exec(compile(ast.Module(body=[function], type_ignores=[]), path, 'exec'), namespace)
            setattr(cls, method, namespace[method])
    import faulthandler
    faulthandler.dump_traceback_later(120)
    root = cst.CTk()
    context = AppContext(preferences=RuntimePreferences.from_frame(load_preferences()))
    window = Stats(root, context=context)
    deadline = perf_counter() + 90
    try:
        while not window.ready:
            root.update()
            if perf_counter() > deadline:
                raise TimeoutError('Statistics did not become ready')
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        scroller = next(w for w in descendants(window) if isinstance(w, VerticalScrolledFrame_class))
        root.after(250, root.quit)
        root.mainloop()
        phases = ('baseline', 'optimized') if options.compare else (('baseline' if options.baseline else 'optimized'),)
        for phase in phases:
            if options.compare and phase == 'optimized':
                for cls, method, original in overrides:
                    setattr(cls, method, original)
            scroller.canvas.yview_moveto(0)
            root.after(250, root.quit)
            root.mainloop()
            timings = []
            profile = cProfile.Profile()
            profile.enable()
            for index in range(100):
                start = perf_counter()
                scroller.canvas.yview_moveto((index % 20) / 20)
                root.update()
                timings.append((perf_counter() - start) * 1000)
            profile.disable()
            print(f'PERF {phase} scroll 100 steps: median {median(timings):.2f} ms; max {max(timings):.2f} ms; total {sum(timings):.2f} ms')
            pstats.Stats(profile).strip_dirs().sort_stats('cumulative').print_stats(25)
    finally:
        faulthandler.cancel_dump_traceback_later()
        window.destroy()
        for job in root.tk.call('after', 'info'):
            root.tk.call('after', 'cancel', job)
        root.destroy()


if __name__ == '__main__':
    main()

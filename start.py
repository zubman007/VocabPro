"""Entry point for the desktop application."""
from app.paths import ROOT_DIR
import logging
import os
import sys
from app.version import __version__

if __name__ == '__main__' and '--version' in sys.argv:
    print(__version__)
    raise SystemExit(0)

if __name__ == '__main__' and '--release-smoke' not in sys.argv:
    import atexit
    from app.release_runtime import distribution_lock
    _run_lock = distribution_lock()
    _run_lock.__enter__()
    atexit.register(_run_lock.__exit__, None, None, None)

os.environ.setdefault("SDL_AUDIODRIVER", "directsound")

import customtkinter as cst
import pygame
import pywinstyles
from app import main
from app.core.context import AppContext
from app.shared import settings as s
from app.ui.brand import set_window_icon

logger = logging.getLogger(__name__)
BASE_DIR = ROOT_DIR


def run():
    app = cst.CTk()

    def close():
        pygame.mixer.quit()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", close)
    set_window_icon(app)
    pywinstyles.apply_style(app, "dark")
    app.minsize(min(1600, app.winfo_screenwidth()),
                min(850, max(400, app.winfo_screenheight() - 80)))
    app.title(s.app_name)
    app.state("zoomed")
    app._state_before_windows_set_titlebar_color = "zoomed"
    try:
        pygame.mixer.init()
    except pygame.error:
        logger.warning("Audio device unavailable at startup", exc_info=True)
    try:
        main.main_proc(app,AppContext())
        from app.shared.audio_effects import play_effect
        play_effect('start.wav')
        app.mainloop()
    finally:
        pygame.mixer.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    if '--release-smoke' in sys.argv:
        from app.release_check import check
        raise SystemExit(check(sys.argv[sys.argv.index('--release-smoke')+1]))
    run()

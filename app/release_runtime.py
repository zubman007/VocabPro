"""Hold the same external update lock as the release script while EXE runs."""
from contextlib import contextmanager
from app.paths import ROOT_DIR, COMPILED


@contextmanager
def distribution_lock():
    if not COMPILED:
        yield
        return
    import msvcrt
    path=ROOT_DIR.parent/'.VocabPro_exe.update.lock'
    with path.open('a+b') as stream:
        if not path.stat().st_size:stream.write(b'1');stream.flush()
        stream.seek(0)
        try:msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:
            import ctypes
            from app.shared.translations import translate
            from app.repositories.preferences import load_preferences
            from app.preferences.data import RuntimePreferences
            try:language=RuntimePreferences.from_frame(load_preferences()).app_language
            except (OSError,ValueError,KeyError):language='English'
            ctypes.windll.user32.MessageBoxW(None,translate(
                'VocabPro is running or being updated. Try again after closing it.',language),'VocabPro',0x30)
            raise SystemExit(1) from None
        try:yield
        finally:stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)

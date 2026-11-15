"""Accidental side-effect guards for the full test runner, local to its process."""
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest.mock import patch
import builtins
import io
import os
from app.paths import ROOT_DIR, FILES_DIR, IMAGES_DIR, LOCALES_DIR


def check_write(path):
    if isinstance(path, int):
        return
    resolved = Path(os.fsdecode(path)).resolve()
    protected = (FILES_DIR, IMAGES_DIR, LOCALES_DIR)
    if any(resolved == folder or folder in resolved.parents for folder in protected) or resolved in (
            ROOT_DIR/'sandbox.py', ROOT_DIR/'Activation_standalone.py'):
        raise AssertionError(f'Tests must not modify application data: {resolved.name}')


@contextmanager
def isolated_services():
    """Nested mocks in individual tests may replace these defaults with fakes."""
    def forbidden(*args, **kwargs):
        raise AssertionError('Real network, microphone or playback is forbidden in tests.')

    def guarded_open(original):
        def open_file(file, mode='r', *args, **kwargs):
            if any(flag in mode for flag in 'wax+'):
                check_write(file)
            return original(file, mode, *args, **kwargs)
        return open_file

    original_os_open = os.open
    def os_open(file, flags, *args, **kwargs):
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            check_write(file)
        return original_os_open(file, flags, *args, **kwargs)

    def guarded_remove(original):
        def remove(path, *args, **kwargs):
            check_write(path)
            return original(path, *args, **kwargs)
        return remove

    def guarded_move(original):
        def move(source, target, *args, **kwargs):
            check_write(source);check_write(target)
            return original(source, target, *args, **kwargs)
        return move

    with ExitStack() as stack:
        stack.enter_context(patch('app.services.mail_credentials.load_credentials',return_value=None))
        stack.enter_context(patch('app.services.mail_credentials.save_credentials',side_effect=forbidden))
        for target in ('requests.sessions.Session.request', 'smtplib.SMTP_SSL',
                       'socket.create_connection', 'socket.socket.connect', 'socket.socket.connect_ex',
                       'smtplib.SMTP', 'pyaudio.PyAudio',
                       'pygame.mixer.music.load', 'pygame.mixer.music.play', 'pygame.mixer.Channel'):
            stack.enter_context(patch(target, side_effect=forbidden))
        stack.enter_context(patch('pygame.mixer.init'))
        stack.enter_context(patch('pygame.mixer.get_init', return_value=None))
        stack.enter_context(patch('builtins.open', guarded_open(builtins.open)))
        stack.enter_context(patch('io.open', guarded_open(io.open)))
        stack.enter_context(patch('os.open', os_open))
        for name in ('unlink', 'remove', 'rmdir'):
            stack.enter_context(patch('os.'+name, guarded_remove(getattr(os, name))))
        for name in ('replace', 'rename'):
            stack.enter_context(patch('os.'+name, guarded_move(getattr(os, name))))
        yield

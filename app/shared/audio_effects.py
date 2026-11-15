"""Optional feedback sounds must never interrupt scoring or persistence."""
from app.paths import ROOT_DIR
from functools import lru_cache
from time import monotonic
import pygame

SOUNDS = ROOT_DIR / 'files' / 'audio' / 'Sounds'
ALIASES = {'success.flac': 'ui_success.wav', 'wrong.wav': 'ui_retry.wav',
           'start.wav': 'ui_start.wav', 'saved': 'ui_saved.wav', 'edit': 'edit_start.mp3'}
_last_played = {}
_enabled = True
_volume = 1.0
_current_gain = .75


def configure(enabled=True, volume=100):
    """User volume affects only the UI channel, never pronunciation/music."""
    global _enabled, _volume
    _enabled, _volume = bool(enabled), max(0, min(100, int(volume))) / 100
    if pygame.mixer.get_init():
        try:
            channel = pygame.mixer.Channel(0)
            if not _enabled or not _volume:
                channel.stop()
            channel.set_volume(_volume * _current_gain)
        except pygame.error:
            pass


@lru_cache(maxsize=8)
def _load_sound(filename, mixer_format):
    return pygame.mixer.Sound(str(SOUNDS / filename))


def play_effect(filename):
    global _current_gain
    if not _enabled or not _volume:
        return False
    mixer_format = pygame.mixer.get_init()
    if not mixer_format:
        return False
    filename = ALIASES.get(filename.casefold(), filename)
    try:
        # Pronunciation has priority; UI feedback never interrupts or overlaps it.
        if pygame.mixer.music.get_busy():
            return False
        now = monotonic()
        cooldown = 1.0 if filename == 'edit_start.mp3' else .12
        if now - _last_played.get(filename, -10) < cooldown:
            return False
        sound = _load_sound(filename, mixer_format)
        # One reusable channel prevents a pile-up of feedback sounds.
        channel = pygame.mixer.Channel(0)
        _current_gain = 1.0 if filename == 'edit_start.mp3' else .75
        channel.set_volume(_volume * _current_gain)
        channel.play(sound)
        _last_played[filename] = now
    except (OSError, pygame.error):
        return False
    return True

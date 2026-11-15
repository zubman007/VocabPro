"""Practice audio paths and playback, independent of session widgets."""
from app.paths import ROOT_DIR
from pathlib import Path
import pygame
from app.shared.audio_effects import play_effect

BASE_DIR=ROOT_DIR


class PracticeAudio:
    def __init__(self,learned_by,language,*,folder=None):
        self.folder=Path(folder) if folder is not None else BASE_DIR/'files'/'audio'/f'{learned_by}_{language}'

    def paths(self,word_id):
        return tuple(self.folder/f'{word_id}.{extension}' for extension in ('mp3','wav'))

    def available(self,word_id):
        return any(path.is_file() for path in self.paths(word_id))

    def play(self,word_id,fallback=None):
        paths=list(self.paths(word_id))
        for path in paths:
            if path.is_file():
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play()
                return True
        return play_effect(fallback) if fallback not in (None,'None','') else False

    def delete(self,word_id):
        was_initialized=pygame.mixer.get_init()
        pygame.mixer.quit()
        try:
            for path in self.paths(word_id):
                path.unlink(missing_ok=True)
        finally:
            if was_initialized:
                pygame.mixer.init()

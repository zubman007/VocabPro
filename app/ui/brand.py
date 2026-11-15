"""One transparent brand asset for every header and window icon."""
from app.paths import ROOT_DIR
from functools import lru_cache
import customtkinter as cst
from PIL import Image

IMAGE_PATH = ROOT_DIR / 'images' / 'vocabpro_logo_v2.png'
ICON_PATH = IMAGE_PATH.with_suffix('.ico')


@lru_cache(maxsize=1)
def _source():
    with Image.open(IMAGE_PATH) as image:
        return image.convert('RGBA')


def logo_image(size=72):
    # Cache pixels only; Tk images must belong to their own live interpreter.
    return cst.CTkImage(light_image=_source(), dark_image=_source(), size=(size, size))


def set_window_icon(window):
    window.iconbitmap(str(ICON_PATH))

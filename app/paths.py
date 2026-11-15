"""Resource paths independent of module location and working directory."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = ROOT_DIR / "files"
IMAGES_DIR = ROOT_DIR / "images"
LOCALES_DIR = ROOT_DIR / "locales"

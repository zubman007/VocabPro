"""Resource paths independent of module location and working directory."""
from pathlib import Path
import os
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
COMPILED = '__compiled__' in globals()
if COMPILED:
    ROOT_DIR = Path(sys.executable).resolve().parent
FILES_DIR = Path(os.environ['VOCABPRO_DATA_DIR']).resolve() if os.environ.get('VOCABPRO_DATA_DIR') else (
    ROOT_DIR.parent / 'VocabPro_data' / 'files' if COMPILED else ROOT_DIR / 'files')
IMAGES_DIR = ROOT_DIR / "images"
LOCALES_DIR = ROOT_DIR / "locales"

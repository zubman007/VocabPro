"""Optional, read-only theory indexed by category and learning language."""
import unicodedata


def category_key(value):
    return unicodedata.normalize('NFC', str(value or '')).strip().casefold()



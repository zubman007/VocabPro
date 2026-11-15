"""Shared three-click sorting cycle for tables and statistics."""


def next_sort(current, key):
    """Return ascending, descending, then the original order for one key."""
    if current is None or current[0] != key:
        return key, False
    return (key, True) if not current[1] else None


def sort_arrow(current, key):
    return ('↓' if current[1] else '↑') if current is not None and current[0] == key else '↕'

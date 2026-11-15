"""Compatibility exports for existing screens.

User preferences: files/settings.csv. Learning defaults: app.shared.config.
Original styles: app.ui.legacy_styles. New styles: app.ui.theme.
Shared widgets/helpers are re-exported here; data utilities are imported directly.
"""
from app.shared.config import *
from app.ui.legacy_styles import *
from app.ui.widgets import VerticalScrolledFrame_class
from app.ui.helpers import Grid_ratio, Clear_frames, Clear_tops


def T(val):
    from app.core.context import get_context
    return get_context().translate(val)

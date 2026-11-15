"""Shared application colors and statistics component styling."""
PAGE = '#eee9df'
SURFACE = '#fffcf5'
TEXT = '#244743'
MUTED = '#657671'
TEAL = '#397d77'
HONEY = '#a77732'
LAVENDER = '#8272aa'
SUCCESS = '#d9eadc'
ERROR = '#f3ddd5'
FONT = 'Segoe UI Variable Text'
TITLE_FONT = (FONT, 30, 'bold')
RADIUS = 24

HEADER = "#397f86"
SECTION_SURFACE = '#e1d6bf'
SECTION_CONTROL = '#40695b'
EDITOR_HEADER = "#aecbcf"


def style_statistics(table_title):
    table_title.configure(bg_color=PAGE, fg_color="transparent", text_color=TEXT,
                          font=TITLE_FONT)

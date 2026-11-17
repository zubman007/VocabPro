"""Vocabulary editor appearance and layout; no editing or persistence logic."""
from app.ui.theme import PAGE, TEXT
from app.ui.theme import RADIUS
from app.ui.learning_layout import background
from app.ui.surfaces import surface
# Keep the original sheet_options import path available to existing callers.
from app.ui.module_style import HEADER as EDITOR_INK, EDITOR_SURFACE, sheet_options
from app.ui.components.editor_toolbar import EditorToolbar

READONLY_BACKGROUND = "#efe5d5"


def arrange_editor(editor, header, body, filters, table, widgets):
    editor.configure(fg_color=PAGE)
    backdrop = background(editor, 'editor_warm_v1.png')
    header.lift()
    body.lift()
    body.configure(fg_color=EDITOR_SURFACE, corner_radius=RADIUS)
    filters.configure(fg_color=EDITOR_SURFACE, bg_color=EDITOR_INK, border_width=0, corner_radius=16)
    editor.grid_rowconfigure(0, weight=0)
    editor.grid_rowconfigure(1, weight=1)
    editor.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(0, weight=1)
    body.grid_rowconfigure(0, weight=1)
    filters.grid_columnconfigure(2, weight=1)
    editor.pack(side="bottom", fill="both", expand=True)
    header.grid_standard()
    body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(16, 8))
    table.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
    from app.shared import settings as s
    from app.core.context import get_context
    footer=EditorToolbar(editor,'Vocabulary',s.T,action_columns=4,compact=True,
                         tags_enabled=get_context(editor).preferences.tags_enabled)
    footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,18))
    footer.attach_background(backdrop)
    editor._row_count=footer.count
    editor._delete_button=footer.add_action('delete','Delete selected words',widgets['delete'])
    editor._synonyms_button=footer.add_action('synonyms','Synonyms',widgets['synonyms'],state='disabled')
    editor._word_tags_button=footer.add_action('word_tags','Word tags',widgets['word_tags'],state='disabled')
    editor._manage_tags_button=footer.add_action('manage_tags','Manage tags',widgets['manage_tags'])
    editor._sort_button=footer.add_action('sort','Sort',widgets['sort'])
    editor._shortcut_hint=footer.shortcuts
    footer.set_help(s.T('Add words: double-click below the table or paste from Excel/CSV (Ctrl+V).')
                    + '  ' + s.T('Tags: select a word and choose Word tags.'))
    header.place_extension(filters)
    header.place_extension(widgets['wait'])
    widgets['wait'].grid_remove()
    header.attach_background(backdrop)
    surface(body, backdrop)


def restore_after_save_error(save, back, filters):
    save.grid()
    back.grid()
    filters.grid()


def fit_editor_columns(table, headers, language, learned_by):
    """Keep long examples from expanding a column to the longest sentence."""
    widths = {"ID": 60, language: 220, learned_by: 240, "Phonetic": 130,
              "Audio": 160, "Description": 280, "Example": 340,
              "Part of Speech": 175, "Tags": 240, "Repetition": 160,
              "Next repetition": 220, 'Has synonyms':150, 'Synonym count':155}
    for index, column in enumerate(headers):
        table.column_width(column=index, width=widths.get(column, 180), redraw=False)
    table.refresh()

def configure_editor_dropdowns(table, definitions):
    from app.shared import settings as s
    for column, values in definitions:
        span=table.span(None,column,None,column+1)
        table.dropdown(span, values=[s.T(value) for value in values], state="normal", validate_input=True,
                       edit_data=False, redraw=False)


def color_editor_columns(table, headers, language, learned_by):
    computed = [headers.index(name) for name in ('Has synonyms','Synonym count','Tag count') if name in headers]
    if computed:
        table.readonly_columns(columns=computed)
        table.highlight_columns(columns=computed,bg='#e1eadc',fg='#277646',redraw=False)
    for names, background in (((language,learned_by), "#fff0d5"),
                              (("Part of Speech",), "#f8e5da")):
        table.highlight_columns(columns=[headers.index(name) for name in names],
                                bg=background, fg=TEXT, redraw=False)

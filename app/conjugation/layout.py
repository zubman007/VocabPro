"""Conjugation form and the shared learning-session sidebar."""
import customtkinter as cst
from app.ui import learning_layout as ui
from app.ui.training_layout import shell, text, action
from app.ui.surfaces import surface
from app.ui.module_style import primary_action, HEADER, QUESTION, QUESTION_BORDER, SESSION_PAD
from app.ui.components.session_panel import SessionPanel
from app.conjugation.records_card import ConjugationRecordsCard
from app.core.context import get_context


def build(app, persons, confirm, next_verb, save, exit_app, back, category_filter=None):
    translate = get_context(app).translate
    view = shell(app, 'Verb Conjugation', 'conjugation_background_v1.png',
                 [('save', save), ('close', back), ('exit', exit_app)])
    body = view.body
    body.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(1, weight=0, minsize=300)
    body.grid_rowconfigure(0, weight=1)
    view.session_frame = SessionPanel(body, translate)
    view.session_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=(18, 0))
    sidebar = view.session_panel = view.session_frame.content
    view.count = view.session_frame.count
    view.count.configure(font=(ui.FONT, 18, 'bold'), wraplength=225)
    view.score = text(sidebar, size=15, color=ui.MUTED)
    view.score.configure(wraplength=225)
    view.score.grid(row=2, sticky='ew', padx=SESSION_PAD, pady=(8, 10))
    view.category_filter = view.session_frame.add_action('Verb categories', category_filter, row=3)
    view.filter_status = text(sidebar, size=13, color=ui.MUTED)
    view.filter_status.configure(wraplength=225)
    view.filter_status.grid(row=4, sticky='ew', padx=SESSION_PAD, pady=(2, 6))
    view.records_panel = ConjugationRecordsCard(sidebar, translate)
    view.records_panel.grid(row=5, sticky='ew', padx=16, pady=(10, 6))
    view.records = view.records_panel.report
    view.shortcuts = view.session_frame.add_shortcuts('Conjugation', row=6)
    surface(view.session_frame, view.layer)

    card = view.card = cst.CTkFrame(body, fg_color=QUESTION, corner_radius=24,
                                    border_width=1, border_color=QUESTION_BORDER)
    card.grid(row=0, column=0, sticky='nsew', pady=(0, 12))
    card.grid_columnconfigure(0, weight=1)
    card.grid_rowconfigure(2, weight=1)
    view.verb = text(card, size=32, bold=True, color=HEADER)
    view.verb.grid(row=0, sticky='ew', padx=24, pady=(18, 4))
    view.description = text(card, size=19, color=ui.MUTED)
    view.description.grid(row=1, sticky='ew', padx=24, pady=(0, 12))
    fields = view.fields = cst.CTkScrollableFrame(card, fg_color=QUESTION, corner_radius=0)
    fields.grid(row=2, sticky='nsew', padx=16, pady=(0, 12))
    fields.grid_columnconfigure(0, weight=1, uniform='forms')
    fields.grid_columnconfigure(1, weight=3, uniform='forms')
    view.variables, view.entries, view.person_labels = {}, {}, {}
    for row, (key, person) in enumerate(persons):
        label = text(fields, person, size=19)
        label.configure(wraplength=180, width=0, justify='left')
        label.grid(row=row, column=0, sticky='ew', padx=(12, 8), pady=6)
        variable = cst.StringVar(master=fields)
        entry = cst.CTkEntry(fields, textvariable=variable)
        ui.entry(entry)
        entry.configure(width=140)
        entry.grid(row=row, column=1, sticky='ew', padx=(8, 12), pady=6)
        view.variables[key], view.entries[key], view.person_labels[key] = variable, entry, label
    surface(card, view.layer)
    footer = view.footer = cst.CTkFrame(body, fg_color='transparent', corner_radius=0)
    footer.grid(row=1, column=0, sticky='ew')
    footer.grid_columnconfigure((0, 1), weight=1, uniform='actions')
    layer = surface(footer, view.layer)
    for column, (title, command) in enumerate((('OK', confirm), ('Next verb', next_verb))):
        button = action(footer, title, command, HEADER, column == 1)
        primary_action(button, column)
        surface(button, layer)

    def resize(event):
        if event.widget is not card._canvas:return
        width = max(120, int(event.width / card._get_widget_scaling()) - 48)
        for label in (view.verb, view.description):
            if label.cget('wraplength') != width:label.configure(wraplength=width)
        person_width = max(60, (width - 48) // 4)
        for label in view.person_labels.values():
            if label.cget('wraplength') != person_width:label.configure(wraplength=person_width)
    card.bind('<Configure>', resize, add='+')
    return view

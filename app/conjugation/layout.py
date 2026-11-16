"""Conjugation form layout; no matching, scheduling or persistence."""
import customtkinter as cst
from app.ui import learning_layout as ui
from app.ui.training_layout import shell, text, action
from app.ui.surfaces import surface
from app.ui.module_style import primary_action, HEADER,QUESTION,QUESTION_BORDER


def build(app, persons, confirm, next_verb, save, exit_app, back):
    view = shell(app, 'Verb Conjugation', 'conjugation_background_v1.png',
                 [('save', save), ('close', back), ('exit', exit_app)])
    card = cst.CTkFrame(view.body, fg_color=QUESTION, corner_radius=24,
        border_width=1,border_color=QUESTION_BORDER)
    card.grid(row=0, sticky='nsew', pady=(0, 18))
    view.body.grid_rowconfigure(0, weight=1)
    card.grid_columnconfigure(0, weight=1)
    card.grid_columnconfigure(1, weight=3)
    view.card = card
    view.verb = text(card, size=32, bold=True, color=HEADER)
    view.verb.grid(row=0, column=0, columnspan=2, sticky='w', padx=28, pady=(20, 4))
    view.count = text(card, size=20, bold=True, color=HEADER)
    view.count.grid(row=0, column=2, padx=28, pady=20)
    view.description = text(card, size=21, color=ui.MUTED)
    view.description.grid(row=1, column=0, columnspan=3, sticky='ew', padx=28, pady=(0, 16))
    fields=card
    offset=2
    if len(persons)>6:
        fields=cst.CTkScrollableFrame(card,fg_color='transparent',corner_radius=0)
        fields.grid(row=2,column=0,columnspan=3,sticky='nsew',padx=16,pady=(0,12))
        card.grid_rowconfigure(2,weight=1)
        fields.grid_columnconfigure(0,weight=1);fields.grid_columnconfigure(1,weight=3)
        offset=0
    view.variables, view.entries = {}, {}
    for row, (key, person) in enumerate(persons, offset):
        fields.grid_rowconfigure(row, weight=1 if fields is card else 0)
        label=text(fields,person,size=22)
        label.configure(wraplength=280,justify='left')
        label.grid(row=row,column=0,sticky='w',padx=28,pady=6)
        variable = cst.StringVar(master=fields)
        entry = cst.CTkEntry(fields, textvariable=variable)
        ui.entry(entry)
        entry.grid(row=row, column=1, columnspan=2, sticky='ew', padx=(12, 28), pady=6)
        view.variables[key], view.entries[key] = variable, entry
    card.grid_rowconfigure(len(persons) + 2, minsize=16)
    footer = cst.CTkFrame(view.body, fg_color='transparent', corner_radius=0)
    footer.grid(row=1, sticky='ew')
    footer.grid_columnconfigure((0, 1), weight=1,uniform='actions')
    layer = surface(footer, view.layer)
    for column, (title, command) in enumerate((('OK', confirm), ('Next verb', next_verb))):
        button = action(footer, title, command, HEADER, column == 1)
        primary_action(button,column)
        surface(button, layer)
    surface(card, view.layer)
    from app.ui.components.shortcut_hint import ShortcutHint
    from app.shared import settings as s
    view.shortcuts=ShortcutHint(footer,'Conjugation',s.T,rounded=True)
    view.shortcuts.grid(row=1,column=0,columnspan=2,sticky='ew',padx=12,pady=8)
    surface(view.shortcuts,layer)

    def resize(event):
        if event.widget in (view.root,view.root._canvas):
            width = max(240, event.width / view.root._get_widget_scaling() - 160)
            view.verb.configure(wraplength=width - 100)
            view.description.configure(wraplength=width)
    view.root.bind('<Configure>', resize, add='+')
    return view

"""Conjugation form layout; no matching, scheduling or persistence."""
import customtkinter as cst
from app.ui import learning_layout as ui
from app.ui.training_layout import shell, text, action
from app.ui.surfaces import surface
from app.ui.module_style import primary_action, HEADER,QUESTION,QUESTION_BORDER
from app.conjugation.records_card import ConjugationRecordsCard
from app.core.context import get_context


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
    view.description = text(card, size=21, color=ui.MUTED)
    view.description.grid(row=1, column=0, columnspan=3, sticky='ew', padx=28, pady=(0, 16))
    view.records_panel=ConjugationRecordsCard(card,get_context(app).translate)
    view.records=view.records_panel.report
    fields=cst.CTkScrollableFrame(card,fg_color=QUESTION,corner_radius=0)
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
    footer = cst.CTkFrame(view.body, fg_color='transparent', corner_radius=0)
    footer.grid(row=1, sticky='ew')
    footer.grid_columnconfigure((0, 1), weight=1,uniform='actions')
    layer = surface(footer, view.layer)
    for column, (title, command) in enumerate((('OK', confirm), ('Next verb', next_verb))):
        button = action(footer, title, command, HEADER, column == 1)
        primary_action(button,column)
        button.grid_configure(row=1)
        surface(button, layer)
    counter=cst.CTkFrame(footer,fg_color='#d7dfca',corner_radius=12)
    counter.grid(row=0,column=1,sticky='e',padx=12,pady=(0,6))
    view.count=text(counter,size=14,color=ui.MUTED)
    view.count.grid(row=0,sticky='ew',padx=12,pady=4)
    surface(counter,layer)
    surface(card, view.layer)
    from app.ui.components.shortcut_hint import ShortcutHint
    from app.shared import settings as s
    view.shortcuts=ShortcutHint(footer,'Conjugation',s.T,rounded=True)
    view.shortcuts.grid(row=2,column=0,columnspan=2,sticky='ew',padx=12,pady=8)
    surface(view.shortcuts,layer)

    def reflow(width):
        show=get_context(app).preferences.show_personal_records
        wide=width>=1000
        card.grid_columnconfigure(2,minsize=round(360*card._get_widget_scaling()) if wide and show else 0)
        view.records_panel.grid_remove()
        fields.grid(row=2 if wide or not show else 3,column=0,columnspan=3,sticky='nsew',padx=16,pady=(0,12))
        card.grid_rowconfigure(2,weight=1 if wide or not show else 0)
        card.grid_rowconfigure(3,weight=0 if wide or not show else 1)
        if show:
            view.records_panel.grid(row=0 if wide else 2,column=2 if wide else 0,
                rowspan=2 if wide else 1,columnspan=1 if wide else 3,sticky='new',padx=(12,24) if wide else 24,pady=(16,10))
            view.records_panel.configure(width=330)
        view.description.grid_configure(columnspan=2 if show and wide else 3)
        view.verb.configure(wraplength=max(220,width-(460 if show and wide else 140)))
        view.description.configure(wraplength=max(220,width-(460 if show and wide else 100)))

    def resize(event):
        if event.widget in (view.root,view.root._canvas):
            reflow(max(240,event.width/view.root._get_widget_scaling()-56))
    view.root.bind('<Configure>', resize, add='+')
    reflow(1100)
    return view

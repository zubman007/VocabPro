"""Practice visual composition and session overview; no learning decisions."""
import customtkinter as cst
from app.shared import settings as s
from app.ui import learning_layout as ui
from app.ui.surfaces import surface
from app.ui.module_style import (choice_button,SESSION_TEXT_FONT,SESSION_SECTION_FONT,
    SESSION_WORD_FONT,SESSION_HEADING,SESSION_PAD)
from app.ui.components.session_panel import SessionPanel
from app.core.context import get_context
from app.ui.components.synonym_summary import SynonymSummary

INK = '#3c5e53'
SEA = '#567b63'


class PracticeSidebar(SessionPanel):
    def __init__(self, parent, review):
        super().__init__(parent,s.T,progress=True)
        body=self.content
        body.grid_columnconfigure(0, weight=1)
        self.previous_heading=cst.CTkLabel(body,text=s.T('Previous word'),font=SESSION_SECTION_FONT,
                     text_color=SESSION_HEADING,anchor='w')
        self.previous_heading.grid(row=4,sticky='ew',padx=SESSION_PAD,pady=(6,6))
        self.word = cst.CTkLabel(body, text='—', font=SESSION_WORD_FONT,
                                text_color=ui.TEXT, wraplength=210, justify='left', anchor='w')
        self.word.grid(row=5, sticky='ew', padx=24)
        self.translation = cst.CTkLabel(body, text='', font=SESSION_TEXT_FONT,
                                       text_color=ui.MUTED, wraplength=210, justify='left', anchor='w')
        self.translation.grid(row=6, sticky='ew', padx=SESSION_PAD, pady=(4, 12))
        self.tags=cst.CTkLabel(body,text='',font=(ui.FONT,14),text_color='#567b63',
            wraplength=210,justify='left',anchor='w')
        self.tags.grid(row=7,sticky='ew',padx=SESSION_PAD,pady=(0,8))
        self.tags.grid_remove()
        self.review=self.add_action('Review',review,row=11)
        self.synonym_title=cst.CTkLabel(body,text=s.T('Synonyms'),font=SESSION_SECTION_FONT,
            text_color=SESSION_HEADING,anchor='w')
        self.synonym_title.grid(row=9,sticky='ew',padx=SESSION_PAD,pady=(6,2))
        self.synonyms = cst.CTkFrame(body, fg_color='transparent', corner_radius=0)
        self.synonyms.grid(row=10,sticky='new',padx=24,pady=(0,12))
        self.synonyms.grid_columnconfigure(0,weight=1)
        self.synonym_list=SynonymSummary(self.synonyms)
        self.synonym_list.grid(sticky='ew',padx=0,pady=0)
        self.shortcuts=self.add_shortcuts('Repeat',row=12,show_synonyms=get_context(parent).preferences.show_synonyms)

    def update_session(self, previous, current, completed, total, synonyms='', tags=''):
        self.set_progress(completed,total)
        valid = previous.id not in ('', current.id)
        self.word.configure(text=previous.word if valid else '—')
        self.translation.configure(text=previous.tr if valid else '')
        self.review.configure(state='normal' if valid else 'disabled')
        self.tags.configure(text=tags if valid else '')
        if valid and tags:self.tags.grid()
        else:self.tags.grid_remove()
        self.synonym_list.set_text(synonyms if valid and synonyms else '')
        if valid and synonyms:
            self.synonyms.grid()
            self.synonym_title.grid()
        else:
            self.synonyms.grid_remove()
            self.synonym_title.grid_remove()


def style_practice(root, header, action, question, hint, choices, answer, type_two,
                   *, prompt, response, word, translation, continue_button,
                   skip_button, review):
    ui.card(action)
    root.grid_rowconfigure(0,weight=0)
    root.grid_rowconfigure(1,weight=1)
    action.configure(fg_color='transparent', border_width=0, corner_radius=0)
    from app.ui.module_style import primary_action
    header.grid_standard(columnspan=2)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)
    action.grid_configure(padx=(28, 12), pady=(8, 28))
    for row in range(5):
        action.grid_rowconfigure(row, weight=1 if row == 0 else 0)
    question.configure(fg_color=INK, bg_color=ui.SURFACE, corner_radius=24, border_width=0)
    question.configure(height=260)
    question.grid_propagate(False)
    question.grid_rowconfigure((0,1),weight=1)
    question.grid_configure(padx=0, pady=(12, 8), sticky='ew')
    type_two.configure(fg_color='transparent',bg_color=INK,corner_radius=0,border_width=0)
    for frame in (question, type_two):
        for widget in frame.winfo_children():
            if isinstance(widget, cst.CTkLabel):
                ui.label(widget, 23, ui.SURFACE)
            elif isinstance(widget, cst.CTkButton):
                ui.button(widget, '#73927a')
                widget.configure(bg_color=INK, height=90, width=150, border_width=0)
    ui.label(prompt, 42, ui.SURFACE, bold=True)
    prompt.configure(width=0,height=0,justify='center')
    from app.ui.fitted_text import fit_question_prompt
    question._fit_prompt=lambda:fit_question_prompt(prompt,question)
    question.bind('<Configure>',lambda event:question._fit_prompt(),add='+')
    question._mode_label = cst.CTkLabel(question, text='', font=(ui.FONT, 17),
                                       text_color='#bce0d6', anchor='w')
    question._mode_label.grid(row=0, column=0, columnspan=2, sticky='nw', padx=24, pady=18)
    ui.entry(response)
    response.configure(width=760, height=64, font=(ui.FONT, 29), border_color='#77b6a6',
                       placeholder_text=s.T('Your answer'), border_width=2)
    response.grid_configure(sticky='ew', padx=32, pady=(16, 8))
    ui.card(hint, '#cdb486')
    hint.configure(bg_color=ui.SURFACE, border_width=0)
    for widget in hint.winfo_children():
        ui.label(widget, 22, '#493c26', bold=True)
        widget.configure(wraplength=850)
        widget.grid_configure(padx=20, pady=10)
    ui.card(choices)
    choices.configure(border_width=0)
    for index, widget in enumerate(choices.winfo_children()):
        choice_button(widget)
        widget.grid_configure(sticky='ew', padx=8, pady=8)
    choices.configure(fg_color='transparent', corner_radius=0)
    choices.grid_columnconfigure((0, 1), weight=1, uniform='answers')
    ui.button(skip_button, secondary=True)
    action.grid_columnconfigure((0,1),weight=1,uniform='practice_actions')
    for widget in action.winfo_children():
        if isinstance(widget, cst.CTkButton):
            placement=widget.grid_info()
            primary_action(widget,placement['column'],placement['row'])
    ui.card(answer, ui.SUCCESS)
    answer.configure(border_width=2, border_color=SEA)
    for widget in answer.winfo_children():
        if isinstance(widget, cst.CTkLabel):
            ui.label(widget, 23)
        elif isinstance(widget, cst.CTkButton):
            ui.button(widget, SEA)
    answer._status_label = cst.CTkLabel(answer, text='', font=(ui.FONT, 18, 'bold'),
                                       text_color=INK)
    answer._status_label.grid(row=0, column=0, sticky='nw', padx=28, pady=24)
    continue_button.configure(text=s.T('OK'))
    ui.label(word, 44, INK, bold=True)
    ui.label(translation, 28)
    word.grid_configure(pady=(30, 8), sticky='s')
    continue_button.grid_configure(pady=28, sticky='s')
    sidebar = PracticeSidebar(root, review)
    sidebar.grid(row=1, column=1, sticky='nsew', padx=(0, 28), pady=(8, 28))
    header.attach_background(root._backdrop)
    action_surface = surface(action, root._backdrop)
    surface(question, action_surface)
    surface(hint, action_surface)
    choices_surface = surface(choices, action_surface)
    for button in choices.winfo_children():
        if isinstance(button, cst.CTkButton):
            surface(button, choices_surface)
    surface(response, action_surface)
    for widget in action.winfo_children():
        if isinstance(widget, cst.CTkButton):
            surface(widget, action_surface)
    surface(answer, root._backdrop)
    surface(sidebar, root._backdrop)
    from app.ui.components.shortcut_hint import ShortcutHint
    compact_shortcuts=ShortcutHint(root,'Repeat',s.T,get_context(root).preferences.show_synonyms,rounded=True)
    surface(compact_shortcuts,root._backdrop)
    root._compact_shortcuts=compact_shortcuts

    def resize(event):
        if event.widget not in (root,root._canvas):return
        width = event.width / root._get_widget_scaling()
        visible=width>=1100
        if getattr(root,'_sidebar_visible',None)!=visible:
            root._sidebar_visible=visible
            if visible:
                sidebar.grid()
                compact_shortcuts.grid_remove()
            else:
                sidebar.grid_remove()
                compact_shortcuts.grid(row=2,column=0,columnspan=2,sticky='ew',padx=28,pady=(0,12))
        usable = max(320, width - (350 if width >= 1100 else 100))
        for button in choices.winfo_children():
            if isinstance(button, cst.CTkButton) and button._text_label is not None:
                button._text_label.configure(wraplength=round(max(180, usable/2-40)*button._get_widget_scaling()))
        for widget in (word, translation):
            widget.configure(wraplength=usable-60)
        for widget in answer.winfo_children():
            if isinstance(widget, cst.CTkLabel):
                widget.configure(wraplength=usable-90)
        for widget in hint.winfo_children():
            if isinstance(widget, cst.CTkLabel):
                widget.configure(wraplength=max(200, usable-160))
        for widget in type_two.winfo_children():
            if isinstance(widget, cst.CTkLabel):
                widget.configure(wraplength=usable-100)
    root.bind('<Configure>', resize, add='+')
    return sidebar



"""Course cards over a dark, continuous branded background."""
import customtkinter as cst
from app.shared import settings as s
from app.ui.learning_layout import background
from app.ui.surfaces import surface
from app.ui.brand import logo_image
from app.ui.theme import TEXT, PAGE as QUIET, FONT as UI_FONT

NAVIGATION='#243f39'
TITLE_FONT="Segoe UI Variable Display"


def build_navigation(app,callbacks):
    app.configure(menu="")
    bar=cst.CTkFrame(app,fg_color=NAVIGATION,corner_radius=0)
    bar.pack(side="top",fill="x")
    bar.grid_columnconfigure(0,weight=1)
    cst.CTkLabel(bar,text='  '+s.app_name,image=logo_image(32),compound='left',
                 text_color='#fff0d3',font=(TITLE_FONT,25,"bold")).grid(
                     row=0,column=0,sticky="w",padx=28,pady=12)
    for column,(label,key) in enumerate((("About the app","about"),("Settings","settings"),
            ("Statistics","stats"),("Refresh","refresh"),("Exit app","exit")),1):
        cst.CTkButton(bar,text=s.T(label),command=callbacks[key],height=42,width=135,
            font=(UI_FONT,18),fg_color='#3e5d50',text_color='#fff0d3',
            hover_color="#56725d",corner_radius=12).grid(row=0,column=column,padx=4,pady=10)
    return bar


def _background(body):
    return background(body, 'home_background_v3.png')


def build_home(app, stats_by_lang, languages, callbacks, *, initial_language=None, on_select=None):
    body = cst.CTkFrame(app, fg_color=QUIET, corner_radius=0)
    body.pack(side='bottom', fill='both', expand=True)
    backdrop = _background(body)
    selected = initial_language if initial_language in languages else languages[0]
    cards = {}
    body.course_cards = cards
    if len(languages) > 2:
        chooser = cst.CTkFrame(body, fg_color='#dfd3b9', corner_radius=18)
        chooser.place(relx=.06, rely=.025, relwidth=.56)
        surface(chooser, backdrop)
        chooser.grid_columnconfigure(1, weight=1)
        cst.CTkLabel(chooser, text=s.T('Learning language'), text_color=TEXT,
            font=(UI_FONT, 19, 'bold')).grid(row=0, column=0, padx=18, pady=14)
        choices = {s.T(language): language for language in languages}
        def select_course(label):
            for card in cards.values():
                card.place_forget()
            cards[choices[label]].place(relx=.06, rely=.16, relwidth=.56)
            if on_select is not None:
                on_select(choices[label])
        body.course_selector = cst.CTkOptionMenu(chooser, values=list(choices), command=select_course,
            fg_color='#49736b', button_color='#355e59', button_hover_color='#426357',
            dropdown_fg_color='#eee5d2', dropdown_text_color=TEXT, font=(UI_FONT, 19), height=38)
        body.course_selector.grid(row=0, column=1, sticky='ew', padx=18, pady=14)
        body.course_selector.set(s.T(selected))
    for column, language in enumerate(languages):
        data = stats_by_lang[language]
        card = cst.CTkFrame(body, fg_color='#dfd3b9' if column == 0 else '#c8d0b6',
            corner_radius=24, border_width=1, border_color='#9b9872')
        surface(card, backdrop)
        cards[language] = card
        if len(languages) <= 2:
            card.place(relx=.06 if len(languages)==1 else .03+column*.30,
                       rely=.06,relwidth=.44 if len(languages)==1 else .28)
        card.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(card, text=s.T(language), font=(TITLE_FONT, 29, 'bold'), text_color=TEXT).grid(
            row=0, column=0, sticky='w', padx=22, pady=(20, 8))
        sections = [('Vocabulary', data['all_count'], 'Number of words',
            [('Repeat', 'practice', not data['rep_words'].empty, data['rep_count']),
             ('Learn', 'learn', not data['lrn_words'].empty, data['lrn_count']),
             ('Edit', 'edit', True, None)])]
        if callbacks['available'](language, 'grammar'):
            sections.append(('Grammar', data['gra_count'], 'Number of questions',
                [('Repeat', 'grammar', data['gra_count'] > 0, None), ('Edit', 'edit_grammar', True, None)]))
        if callbacks['available'](language, 'conjugation'):
            con_actions=[('Repeat','conjugation',data.get('con_practice_count',data['con_count'])>0,None)]
            if 'edit_conjugation' in callbacks:con_actions.append(('Edit','edit_conjugation',True,None))
            sections.append(('Conjugation', data['con_count'], 'Number of verbs',
                con_actions))
        for row, (title, count, count_label, actions) in enumerate(sections, 1):
            section = cst.CTkFrame(card, fg_color='#eee5d2', corner_radius=18)
            section.grid(row=row, sticky='ew', padx=14, pady=(6, 12))
            section.grid_columnconfigure(0, weight=1)
            cst.CTkLabel(section, text=s.T(title), font=(UI_FONT, 22, 'bold'), text_color=TEXT).grid(
                row=0, sticky='w', padx=14, pady=(12, 0))
            cst.CTkLabel(section, text=f'{s.T(count_label)}: {count}', font=(UI_FONT, 15),
                text_color='#615c45').grid(row=1, sticky='w', padx=14, pady=(0, 10))
            buttons = cst.CTkFrame(section, fg_color='transparent', corner_radius=0)
            buttons.grid(row=2, sticky='ew', padx=10, pady=(0, 12))
            for position, (caption, key, enabled, badge) in enumerate(actions):
                column=position
                buttons.grid_columnconfigure(column, weight=1, uniform='actions')
                label = s.T(caption)
                cst.CTkButton(buttons, text=label, command=lambda lang=language, action=key: callbacks[action](lang),
                    state='normal' if enabled else 'disabled', height=40, width=60,
                    font=(UI_FONT, 16), fg_color='#49736b' if caption!='Edit' else '#a16d48',
                    hover_color='#355e59' if caption!='Edit' else '#86573a', text_color='#fff4dc',
                    corner_radius=12).grid(row=0,column=column,sticky='ew',padx=3)
            if title == 'Vocabulary':
                counts = (s.T('Words to review: {count}').format(count=data['rep_count']) + '  ·  '
                          + s.T('New words to learn: {count}').format(count=data['lrn_count']))
                cst.CTkLabel(section, text=counts, font=(UI_FONT, 14), text_color='#615c45',
                    anchor='w', justify='left', wraplength=290).grid(
                        row=3, sticky='ew', padx=14, pady=(0, 12))
    if len(languages) > 2:
        select_course(s.T(selected))
    return body

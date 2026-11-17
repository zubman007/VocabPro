"""Question list and spacious grammar-specific editing form."""
from tkinter import ttk
import customtkinter as cst
from app.shared import settings as s
from app.ui import learning_layout as ui
from app.ui.training_layout import shell, action, text
from app.ui.surfaces import surface
from app.ui.components.editor_toolbar import EditorToolbar
from app.ui.components.search_filter_panel import SearchFilterPanel
from app.ui.sections import EditorTabs


def build(app, language, callbacks, theory=False):
    title_key = 'Edit grammar theory' if theory else 'Edit grammar questions'
    view = shell(app, title_key, 'grammar_background_v1.png',
        [('save', callbacks['save']), ('close', callbacks['back']),('exit',callbacks['exit'])])
    view.header.title_label.configure(text=s.T(title_key)+' · '+s.T(language))
    tab_labels = [s.T('Questions'), s.T('Grammar theory')]
    selected_tab = tab_labels[1 if theory else 0]
    def switch_tab(label):
        if label != selected_tab:
            view.tabs.set(selected_tab)
            callbacks['related']()
    view.tabs = EditorTabs(view.header, values=tab_labels, command=switch_tab)
    view.tabs.set(selected_tab)
    view.header.place_extension(view.tabs,sticky='w')
    view.tabs.attach_background(view.header._surface)
    view.body.grid_columnconfigure(0, weight=2)
    view.body.grid_columnconfigure(1, weight=3)
    view.body.grid_rowconfigure(0, weight=0)
    view.body.grid_rowconfigure(1, weight=1)
    view.tools=EditorToolbar(view.body,'Grammar editors',s.T)
    view.tools.grid(row=2,column=0,columnspan=2,sticky='ew',pady=(8,0))
    view.tools.attach_background(view.layer)
    view.shortcuts=view.tools.shortcuts
    listing = cst.CTkFrame(view.body, fg_color='#ded4bf', corner_radius=24)
    listing.grid(row=1, column=0, sticky='nsew', padx=(0, 12))
    listing.grid_columnconfigure(0, weight=1)
    listing.grid_rowconfigure(3, weight=1)
    surface(listing, view.layer)
    filters=SearchFilterPanel(view.header,s.T,placeholder='Search theory' if theory else 'Search questions',
        on_apply=callbacks['filter'],stacked=True)
    view.header.place_extension(filters)
    view.query=filters.query
    view.category_filter=filters.add_choice('category',[s.T('All categories')],kind='combo',
        command=lambda value:callbacks['filter'](),dropdown_font=(ui.FONT,14))
    holder = cst.CTkFrame(listing, corner_radius=0)
    holder.grid(row=3, sticky='nsew', padx=18,pady=16)
    holder.grid_rowconfigure(0, weight=1)
    holder.grid_columnconfigure(0, weight=1)
    style = ttk.Style(holder)
    style.configure('GrammarEditor.Treeview', background='#eee4d0', fieldbackground='#eee4d0',
        foreground=ui.TEXT, rowheight=38, font=(ui.FONT, 13))
    style.configure('GrammarEditor.Treeview.Heading', font=(ui.FONT, 13, 'bold'))
    view.tree = ttk.Treeview(holder, columns=('id', 'category', 'sentence'), show='headings',
        selectmode='browse', style='GrammarEditor.Treeview', height=10)
    for key, caption, width in (('id', 'ID', 55), ('category', 'Category', 140), ('sentence', 'Sentence', 230)):
        view.tree.heading(key, text=s.T('Title') if theory and key=='sentence' else s.T(caption))
        view.tree.column(key, width=width, minwidth=45, stretch=key=='sentence')
    if theory:
        view.tree.configure(displaycolumns=('category', 'sentence'))
    view.tree.grid(row=0, column=0, sticky='nsew')
    scroll = ttk.Scrollbar(holder, orient='vertical', command=view.tree.yview)
    scroll.grid(row=0, column=1, sticky='ns')
    view.tree.configure(yscrollcommand=scroll.set)
    horizontal = ttk.Scrollbar(holder, orient='horizontal', command=view.tree.xview)
    horizontal.grid(row=1, column=0, sticky='ew')
    view.tree.configure(xscrollcommand=horizontal.set)
    def fit_columns(event):
        width = max(420, event.width-4)
        if theory:
            view.tree.column('category', width=round(width*.45), stretch=False)
            view.tree.column('sentence', width=round(width*.55), stretch=False)
        else:
            view.tree.column('id', width=65, stretch=False)
            view.tree.column('category', width=round((width-65)*.4), stretch=False)
            view.tree.column('sentence', width=round((width-65)*.6), stretch=False)
    view.tree.bind('<Configure>', fit_columns, add='+')
    view.tree.bind('<<TreeviewSelect>>', callbacks['select'])
    buttons_spec = (('Add theory', 'add'), ('Delete theory', 'delete')) if theory else (('Add question', 'add'), ('Delete question', 'delete'))
    for column, (caption, key) in enumerate(buttons_spec):
        view.tools.add_action(key,caption,callbacks[key])
    view.count=view.tools.count
    form = cst.CTkScrollableFrame(view.body, fg_color='#e6dcc8', corner_radius=24)
    form.grid(row=1, column=1, sticky='nsew')
    form.grid_columnconfigure(0, weight=1)
    surface(form._parent_frame, view.layer)
    view.form_title = text(form, size=23, bold=True)
    view.form_title.grid(row=0, sticky='ew', padx=20, pady=(16, 8))
    view.fields = {}
    fields = (('category', 'Category', False), ('title', 'Title', False), ('level', 'Level', False),
        ('description', 'Description', True), ('rules', 'Rules', True), ('examples', 'Examples', True),
        ('common_mistakes', 'Common mistakes', True), ('subtopics', 'Subtopics', True)) if theory else (('category', 'Category', False),
        ('prompt', 'Question instruction', True), ('anchor', 'Sentence', True),
        ('explanation', 'Explanation', True))
    for row, (key, caption, multiline) in enumerate(fields, 1):
        text(form, s.T(caption), size=16, bold=True, color='#815632').grid(row=row*2-1, sticky='w', padx=20, pady=(10, 3))
        if multiline:
            widget = cst.CTkTextbox(form, height=150 if theory else 85 if key!='explanation' else 125, wrap='word',
                font=(ui.FONT, 17), fg_color='#f1e6d0', text_color=ui.TEXT, corner_radius=12)
        elif key == 'category':
            widget = cst.CTkComboBox(form, values=[''], font=(ui.FONT, 17), height=38,
                fg_color='#f1e6d0', text_color=ui.TEXT, button_color='#49736b',
                dropdown_fg_color='#e6dcc8', dropdown_text_color=ui.TEXT,
                dropdown_hover_color='#c5d4bc', dropdown_font=(ui.FONT, 17))
        else:
            widget = cst.CTkEntry(form, font=(ui.FONT, 17), height=38, fg_color='#f1e6d0',
                text_color=ui.TEXT, border_color='#b5a887', corner_radius=12)
        widget.grid(row=row*2, sticky='ew', padx=20)
        view.fields[key] = widget
    view.correct = cst.IntVar(value=0)
    if theory:
        action(form, 'Apply theory', callbacks['apply'], ui.TEAL).grid(row=18, sticky='ew', padx=20, pady=20)
        return view
    text(form, s.T('Select the correct answer.'), size=17, bold=True, color='#355e59').grid(
        row=9, sticky='w', padx=20, pady=(20, 8))
    for index in range(4):
        row = cst.CTkFrame(form, fg_color='transparent')
        row.grid(row=10+index, sticky='ew', padx=20, pady=4)
        row.grid_columnconfigure(1, weight=1)
        cst.CTkRadioButton(row, text=str(index+1), variable=view.correct, value=index,
            width=60, fg_color='#397d77', text_color=ui.TEXT).grid(row=0, column=0, padx=(0, 8))
        widget = cst.CTkEntry(row, height=42, fg_color='#d0dfd1', text_color=ui.TEXT,
            border_color='#7c9d8b', corner_radius=12, font=(ui.FONT, 17))
        widget.grid(row=0, column=1, sticky='ew')
        view.fields[f'option_{index+1}'] = widget
    action(form, 'Apply question', callbacks['apply'], ui.TEAL).grid(row=14, sticky='ew', padx=20, pady=20)
    return view

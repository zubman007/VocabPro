"""Grammar lesson with a question area and a scrollable session sidebar."""
from functools import partial
import customtkinter as cst
from app.ui import learning_layout as ui
from app.ui.training_layout import shell,text,action
from app.ui.surfaces import surface
from app.shared import settings as s
from app.ui.module_style import primary_action,choice_button,QUESTION,QUESTION_BORDER
from app.ui.module_style import SESSION_PAD,SESSION_TEXT_FONT,SESSION
from app.ui.components.session_panel import SessionPanel


def reset_option(button,value):
    choice_button(button)
    button.configure(text=value,state='normal')


def build(app,choose,reveal,next_question,back,exit_app,theory=None,category_filter=None,save=None):
    view=shell(app,'Grammar Trainer','grammar_background_v1.png',
        [('save',save),('close',back),('exit',exit_app)])
    body=view.body
    body.grid_columnconfigure(0,weight=1)
    body.grid_columnconfigure(1,weight=0,minsize=280)
    body.grid_rowconfigure(0,weight=1)
    view.session_frame=SessionPanel(body,s.T)
    view.session_frame.grid(row=0,column=1,rowspan=3,sticky='nsew',padx=(18,0))
    view.session_panel=view.session_frame.content
    sidebar=view.session_panel
    sidebar.grid_columnconfigure(0,weight=1)
    view.counter=view.session_frame.count
    view.mode=text(sidebar,size=16,color=ui.MUTED)
    view.mode.configure(font=SESSION_TEXT_FONT)
    view.mode.configure(wraplength=225)
    view.mode.grid(row=2,sticky='ew',padx=18,pady=8)
    view.score=text(sidebar,size=16,color=ui.MUTED)
    view.score.configure(wraplength=225)
    view.score.grid(row=3,sticky='ew',padx=18,pady=8)
    view.recent=cst.CTkFrame(sidebar,fg_color='transparent',corner_radius=0)
    view.recent.grid(row=4,sticky='ew',padx=SESSION_PAD,pady=(2,8))
    view.recent.grid_columnconfigure(tuple(range(10)),weight=1,uniform='recent')
    view.recent_caption=text(view.recent,size=13,color=ui.MUTED)
    view.recent_caption.grid(row=0,column=0,columnspan=10,sticky='ew',pady=(0,3))
    view.recent_markers=[]
    for column in range(10):
        marker=cst.CTkFrame(view.recent,height=7,width=1,corner_radius=3,
                            fg_color='#c6ceb8',bg_color=SESSION)
        marker.grid(row=1,column=column,sticky='ew',padx=(0,3) if column<9 else 0)
        view.recent_markers.append(marker)
    view.recent.grid_remove()
    view.theory=view.session_frame.add_action('Grammar theory',theory,row=5)
    view.category_filter=view.session_frame.add_action('Question categories',category_filter,row=6)
    view.filter_status=text(sidebar,size=14,color='#654c2d')
    view.filter_status.configure(wraplength=225)
    view.filter_status.grid(row=7,sticky='ew',padx=18,pady=(0,4))
    view.shortcuts=view.session_frame.add_shortcuts('Grammar',row=8)
    for widget in sidebar.winfo_children():
        if isinstance(widget,(cst.CTkLabel,cst.CTkButton)):
            widget.grid_configure(padx=SESSION_PAD)
    _fit_session(view)
    surface(view.session_frame,view.layer)
    view.question=cst.CTkScrollableFrame(body,fg_color=QUESTION,corner_radius=24,
        border_width=1,border_color=QUESTION_BORDER,height=220)
    question=view.question
    question.grid(row=0,column=0,sticky='nsew',pady=(0,12))
    question.grid_columnconfigure(0,weight=1)
    view.prompt=text(question,size=28,bold=True,color=ui.HONEY)
    view.prompt.grid(row=0,sticky='ew',padx=24,pady=(20,8))
    view.anchor=text(question,size=29,bold=True,color='#294e49')
    view.anchor.grid(row=1,sticky='ew',padx=24,pady=12)
    view.result=text(question,size=19)
    view.result.configure(fg_color='#ead9b9',text_color='#654c2d',corner_radius=18,padx=20,pady=14,bg_color='#e8dfcb')
    view.result.grid(row=2,sticky='ew',padx=12,pady=(8,16))
    surface(question._parent_frame,view.layer)
    options=cst.CTkFrame(body,fg_color='transparent',corner_radius=0)
    options.grid(row=1,column=0,sticky='ew')
    options.grid_columnconfigure((0,1),weight=1,uniform='options')
    option_layer=surface(options,view.layer)
    view.options=[]
    for index in range(4):
        button=action(options,'',partial(choose,index),ui.HONEY,True)
        reset_option(button,'')
        button.grid(row=index//2,column=index%2,sticky='ew',padx=8,pady=8)
        surface(button,option_layer);view.options.append(button)
    footer=cst.CTkFrame(body,fg_color='transparent',corner_radius=0)
    footer.grid(row=2,column=0,sticky='ew',pady=(10,0))
    footer.grid_columnconfigure((0,1),weight=1,uniform='actions')
    layer=surface(footer,view.layer)
    view.reveal=action(footer,'Reveal',reveal,ui.HONEY,True)
    view.next=action(footer,'Next',next_question,'#3c7f70')
    for column,button in enumerate((view.reveal,view.next)):
        primary_action(button,column)
        surface(button,layer)

    def resize_question(event):
        width=max(120,int(event.width/question._get_widget_scaling())-55)
        for label in (view.prompt,view.anchor,view.result):label.configure(wraplength=width)
    question._parent_canvas.bind('<Configure>',resize_question,add='+')
    def resize_options(event):
        wrap=max(100,int(event.width/options._get_widget_scaling()/2)-45)
        for button in view.options:button._text_label.configure(wraplength=round(wrap*button._get_widget_scaling()))
    options.bind('<Configure>',resize_options,add='+')
    return view


def _fit_session(view):
    """Tighten only vertical gaps when the normal sidebar would overflow."""
    content=view.session_panel
    canvas=content._parent_canvas
    normal={view.session_frame.heading:(14,4),view.mode:(8,8),view.score:(8,8),
            view.recent:(2,8),view.theory:(4,4),view.category_filter:(4,4),
            view.filter_status:(0,4),view.shortcuts:(6,12)}
    compact={view.session_frame.heading:(6,2),view.mode:(4,4),view.score:(4,4),
             view.recent:(2,6),view.theory:(3,3),view.category_filter:(3,3),
             view.filter_status:(0,2),view.shortcuts:(3,6)}
    pending=None
    view.session_compact=False
    caption_measure=cst.CTkFont(family=ui.FONT,size=13)

    def fit():
        nonlocal pending
        pending=None
        scale=content._get_widget_scaling()
        width=max(100,int(canvas.winfo_width()/scale)-2*SESSION_PAD)
        for label in (view.mode,view.score,view.recent_caption):
            if label.cget('wraplength')!=width:label.configure(wraplength=width)
        for size in (13,12):
            caption_measure.configure(size=round(size*scale))
            if caption_measure.measure(view.recent_caption.cget('text'))<=width*scale:break
        if view.recent_caption.cget('font')[1]!=size:
            view.recent_caption.configure(font=(ui.FONT,size))
        required=sum(widget.winfo_reqheight()/scale+sum(padding)
            for widget,padding in normal.items() if widget.winfo_manager()=='grid')
        # Compare with the normal outer inset, independent of compact geometry,
        # so shrinking the content cannot trigger alternating layout modes.
        tight=required>view.session_frame.winfo_height()/scale-32
        changed=tight!=view.session_compact
        view.session_compact=tight
        if changed:content.pack_configure(pady=12 if tight else 16)
        for widget,padding in (compact if tight else normal).items():
            if (widget.winfo_manager()=='grid' and
                    widget._last_geometry_manager_call['kwargs'].get('pady')!=padding):
                widget.grid_configure(pady=padding)

    def request(event=None):
        nonlocal pending
        # CTk drawing flushes idle callbacks itself; a timer keeps fitting out
        # of that nested draw and merges the resulting geometry notifications.
        if pending is None:pending=content.after(20,fit)

    def dispose(event):
        nonlocal pending
        if event.widget is content and pending is not None:
            content.after_cancel(pending)
            pending=None

    content.bind('<Configure>',request,add='+')
    canvas.bind('<Configure>',request,add='+')
    content.bind('<Destroy>',dispose,add='+')
    request()

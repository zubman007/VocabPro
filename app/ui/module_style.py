"""Shared editor/training chrome and image-backed auxiliary dialogs."""
from app.ui import learning_layout as ui
from app.ui.surfaces import surface
import customtkinter as cst

HEADER = '#355e59'
SESSION = '#d7dfca'
HEADER_FONT = (ui.FONT,32,'bold')
QUESTION = '#e8dfcb'
QUESTION_BORDER = '#c8b794'
SESSION_PAD = 24
SESSION_HEADING = '#8b603c'
SESSION_TITLE_FONT = (ui.FONT,20,'bold')
SESSION_COUNT_FONT = (ui.FONT,24,'bold')
SESSION_TEXT_FONT = (ui.FONT,16)
SESSION_SECTION_FONT = (ui.FONT,16,'bold')
SESSION_WORD_FONT = (ui.FONT,22,'bold')


def header_button(button):
    """Identical neutral actions in every module header, including Save."""
    ui.button(button,secondary=True)
    button.configure(font=(ui.FONT,18),height=44,corner_radius=14,border_width=0)
    font=cst.CTkFont(family=ui.FONT,size=18)
    button.configure(width=max(140,font.measure(button.cget('text'))+32))
    return button


def _fit_caption(button,minimum):
    button._caption_minimum=minimum
    button._caption_base_font=button.cget('font')[1]
    if getattr(button,'_caption_fit_bound',False):return
    button._caption_fit_bound=True
    def fit(event):
        if event.widget is not button._canvas:return
        label=button._text_label
        if label is None:return
        scale=button._get_widget_scaling()
        wrap=max(40,event.width-round(24*scale))
        size=button._caption_base_font
        for candidate in range(size,11,-1):
            font=cst.CTkFont(family=ui.FONT,size=round(candidate*scale))
            if font.measure(button.cget('text'))<=wrap:
                size=candidate
                break
        else:size=12
        if button.cget('font')[1]!=size:button.configure(font=(ui.FONT,size))
        if int(label.cget('wraplength'))!=wrap:
            label.configure(wraplength=wrap,justify='center')
        height=max(button._caption_minimum,round(label.winfo_reqheight()/scale)+14)
        if button.cget('height')!=height:button.configure(height=height)
    button.bind('<Configure>',fit,add='+')


def dialog_button(button):
    """Popup footer actions: consistent base size, wrapping for long captions."""
    ui.button(button,secondary=True)
    button.configure(font=(ui.FONT,16),height=44,width=160,corner_radius=14,border_width=0)
    button.grid_propagate(False)
    _fit_caption(button,44)
    return button


def dialog_actions(parent,buttons,row=0,pady=(4,4)):
    """Center equal-sized actions; use available width before wrapping captions."""
    parent.grid_columnconfigure(0,weight=1)
    font=cst.CTkFont(family=ui.FONT,size=16)
    def layout(event=None):
        if event is not None and event.widget not in (parent,getattr(parent,'_canvas',None)):return
        scale=buttons[0]._get_widget_scaling() if buttons else 1
        font.configure(size=round(16*scale))
        preferred=max((font.measure(button.cget('text'))/scale+32 for button in buttons),default=160)
        available=parent.winfo_width()/scale-24
        columns=min(3,len(buttons))
        if not columns:return
        width=max(80,min(max(160,preferred),(available-16*(columns-1))/columns)) if available>100 else 160
        width=round(width)
        for offset in range(0,len(buttons),3):
            group=buttons[offset:offset+3]
            for index,button in enumerate(group):
                if button.cget('width')!=width:button.configure(width=width)
                button.grid(row=row+offset//3,column=0,sticky='ns',
                    padx=(index*(width+16),(len(group)-1-index)*(width+16)),pady=pady)
    parent.bind('<Configure>',layout,add='+')
    layout()


def session_content(frame):
    """Same inset scroll area and rounded outer edge for learning sidebars."""
    frame.configure(fg_color=SESSION,corner_radius=24,width=300)
    content=cst.CTkScrollableFrame(frame,fg_color=SESSION,corner_radius=0,width=275)
    content.pack(fill='both',expand=True,padx=16,pady=16)
    content.grid_columnconfigure(0,weight=1)
    pending=None
    drawing=False
    def refresh_region():
        nonlocal pending
        pending=None
        canvas=content._parent_canvas
        region=(0,0,canvas.winfo_width(),content.winfo_reqheight())
        if tuple(map(float,str(canvas.cget('scrollregion')).split()))!=region:
            canvas.configure(scrollregion=region)
    def schedule_refresh(event=None):
        nonlocal pending
        if pending is None:pending=content.after_idle(refresh_region)
    def dispose(event):
        nonlocal pending
        if event.widget is content and pending is not None:
            content.after_cancel(pending)
            pending=None
    content.bind('<Configure>',schedule_refresh,add='+')
    content.bind('<Destroy>',dispose,add='+')
    def update_scrollbar(first,last):
        nonlocal drawing
        # Recheck after geometry settles, including a shrink while scrolled down.
        schedule_refresh()
        # CTkScrollbar redraws run idle tasks; do not re-enter a pending redraw.
        if drawing:return
        drawing=True
        try:content._scrollbar.set(first,last)
        finally:drawing=False
        first,last=content._parent_canvas.yview()
        overflow=last-first<.999999
        visible=content._scrollbar.winfo_manager()=='grid'
        if overflow and not visible:content._scrollbar.grid()
        elif not overflow and visible:content._scrollbar.grid_remove()
    content._parent_canvas.configure(yscrollcommand=update_scrollbar)
    return content


def choice_button(button):
    """Quiet answer buttons; feedback may still override their colours."""
    button.configure(fg_color='#cbd5bd',hover_color='#bac9ad',text_color=ui.TEXT,
        border_color='#99ad8e',border_width=1,corner_radius=18,
        font=(ui.FONT,21),anchor='w',border_spacing=10,height=72,width=180)


def tool_button(button):
    """Shared session/editor action, growing only when its caption needs it."""
    button.configure(fg_color='#58766b',hover_color='#426357',text_color='#fffcf5',
        text_color_disabled='#d2d7ca',border_width=0,corner_radius=12,
        font=(ui.FONT,14),height=36,width=140)
    _fit_caption(button,36)
    return button


def primary_action(button, column, row=0):
    ui.button(button,HEADER,secondary=column==0)
    button.configure(height=54, width=180)
    button.grid(row=row, column=column, sticky='ew', padx=16, pady=10)


def dialog_background(window, filename):
    backdrop = ui.background(window, filename)
    backdrop.lower()
    for child in window.winfo_children():
        if child is backdrop:
            continue
        target = getattr(child, '_parent_frame', child)
        if hasattr(target, 'configure'):
            surface(target, backdrop)
    return backdrop

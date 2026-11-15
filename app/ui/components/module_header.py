"""The single branded header used by editors, training and application dialogs."""
import customtkinter as cst
from app.ui.brand import logo_image
from app.ui.theme import FONT,PAGE,SURFACE
from app.ui.module_style import HEADER,HEADER_FONT,header_button
from app.ui.surfaces import surface


class ModuleHeader(cst.CTkFrame):
    """Supply content and actions; typography, logo and placement stay here."""
    ACTIONS={'save':'Save','close':'Close','exit':'Exit app','listen':'Listen'}
    LOGO_SIZE=64
    TITLE_COLOR=SURFACE

    def __init__(self,parent,title,subtitle='',*,translate=lambda value:value,actions=()):
        super().__init__(parent,fg_color=HEADER,bg_color=PAGE,corner_radius=24)
        self.translate=translate
        self.buttons={}
        self._layer=None
        self._extension_row=2
        self.grid_columnconfigure(1,weight=1)
        self.logo_label=cst.CTkLabel(self,image=logo_image(self.LOGO_SIZE),text='',fg_color='transparent')
        self.logo_label.grid(row=0,column=0,rowspan=2,padx=(20,0),pady=12)
        self.title_label=cst.CTkLabel(self,text=title,font=HEADER_FONT,text_color=self.TITLE_COLOR,
            anchor='w',justify='left',fg_color='transparent',width=0)
        self.title_label.grid(row=0,column=1,rowspan=2,sticky='ew',padx=20,pady=12)
        self.subtitle_label=None
        if subtitle:
            self.subtitle_label=cst.CTkLabel(self,text=subtitle,font=(FONT,18),text_color='#e5dec8',
                anchor='w',justify='left',fg_color='transparent',width=0)
            self.set_detail(self.subtitle_label)
        for key,callback in actions:self.add_action(key,callback)
        self.bind('<Configure>',self._resize,add='+')

    def add_action(self,key,callback,*,state='normal'):
        button=header_button(cst.CTkButton(self,text=self.translate(self.ACTIONS.get(key,key)),
            command=callback,state=state))
        self.buttons[key]=button
        for index,item in enumerate(self.buttons.values(),2):
            item.grid(row=0,column=index,rowspan=2,sticky='e',
                padx=(6,18 if index==len(self.buttons)+1 else 6),pady=12)
        if self._layer is not None:surface(button,self._layer)
        return button

    def set_detail(self,widget,*,sticky='ew'):
        self.title_label.grid_configure(rowspan=1,pady=(12,2))
        widget.grid(row=1,column=1,sticky=sticky,padx=20,pady=(0,12))
        return widget

    def place_extension(self,widget,*,sticky='ew'):
        widget.grid(row=self._extension_row,column=0,columnspan=len(self.buttons)+2,
            sticky=sticky,padx=20,pady=(0,16))
        self._extension_row+=1
        return widget


    def grid_standard(self,**kwargs):
        placement=dict(row=0,column=0,sticky='ew',padx=20,pady=(18,12))
        placement.update(kwargs)
        self.grid(**placement)

    def attach_background(self,provider):
        if self._layer is None:
            self._layer=surface(self,provider)
            surface(self.logo_label,self._layer)
            for button in self.buttons.values():surface(button,self._layer)
        return self._layer

    def refresh_action(self,key,*,text=None,command=None,state=None):
        button=self.buttons[key]
        changes={}
        if text is not None:changes['text']=text
        if command is not None:changes['command']=command
        if state is not None:changes['state']=state
        button.configure(**changes)
        header_button(button)
        self._resize()

    def _resize(self,event=None):
        if event is not None and event.widget not in (self,self._canvas):return
        if self.winfo_width()<=1:return
        scale=self._get_widget_scaling()
        reserved=sum(button.cget('width')+12 for button in self.buttons.values() if button.winfo_manager())
        wrap=max(100,int(self.winfo_width()/scale-reserved-self.LOGO_SIZE-100))
        for label in (self.title_label,self.subtitle_label):
            if label is not None and label.cget('wraplength')!=wrap:label.configure(wraplength=wrap)

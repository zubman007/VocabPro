"""Base popup lifecycle: tracked callbacks, centering, Escape and shared actions."""
import tkinter as tk
import customtkinter as cst
from app.ui.brand import set_window_icon
from app.ui.theme import PAGE
from app.ui.module_style import dialog_background,dialog_button,dialog_actions
from app.ui.learning_layout import background
from app.ui.module_style import SESSION
from app.ui.theme import FONT,TEXT,MUTED
from types import SimpleNamespace
from app.core.context import get_context


class AppDialog(cst.CTkToplevel):
    def __init__(self,owner,**kwargs):
        self._dialog_jobs=set()
        self.owner=owner
        self.app_context=get_context(owner)
        super().__init__(owner,**dict({'fg_color':PAGE},**kwargs))
        self.withdraw()
        self.transient(owner)
        set_window_icon(self)
        self.bind('<Escape>',lambda event:self.destroy())
        self.lifecycle_owner=None
        current=owner
        while current is not None:
            lifecycle=vars(current).get('_screen_controller')
            if lifecycle is not None and not lifecycle.closed:
                self.lifecycle_owner=lifecycle
                lifecycle.own_dialog(self)
                break
            current=vars(current).get('master')

    def after(self,delay,callback=None,*args):
        if callback is None:return super().after(delay)
        def invoke():
            self._dialog_jobs.discard(token)
            if self.winfo_exists():callback(*args)
        token=super().after(delay,invoke)
        self._dialog_jobs.add(token)
        return token

    def after_cancel(self,token):
        self._dialog_jobs.discard(token)
        return super().after_cancel(token)

    def present(self,*,modal=False):
        self.deiconify();self.update_idletasks()
        x=self.owner.winfo_rootx()+(self.owner.winfo_width()-self.winfo_width())//2
        y=self.owner.winfo_rooty()+(self.owner.winfo_height()-self.winfo_height())//2
        x=max(0,min(x,self.winfo_screenwidth()-self.winfo_width()))
        y=max(0,min(y,self.winfo_screenheight()-self.winfo_height()-40))
        dx=self.winfo_rootx()-self.winfo_x();dy=self.winfo_rooty()-self.winfo_y()
        self.geometry(f'+{max(0,x-dx)}+{max(0,y-dy)}')
        self.lift()
        if modal:self.grab_set()

    def focus_set(self):
        try:
            if self.winfo_exists():super().focus_set()
        except tk.TclError:pass

    focus=focus_set

    def apply_background(self,filename):
        self._backdrop=dialog_background(self,filename)
        return self._backdrop

    def make_background(self,filename):
        self._backdrop=background(self,filename)
        self._backdrop.lower()
        return self._backdrop

    def add_heading(self,title,subtitle='',*,row=0,rowspan=1):
        frame=cst.CTkFrame(self,fg_color=SESSION,corner_radius=18)
        frame.grid(row=row,rowspan=rowspan,sticky='ew',padx=20,pady=(20,8))
        frame.grid_columnconfigure(0,weight=1)
        heading=cst.CTkLabel(frame,text=title,font=(FONT,26,'bold'),text_color=TEXT,
            fg_color='transparent',anchor='w',justify='left',wraplength=600)
        heading.grid(row=0,sticky='ew',padx=16,pady=(12,4 if subtitle else 12))
        description=None
        if subtitle:
            description=cst.CTkLabel(frame,text=subtitle,font=(FONT,14),text_color=MUTED,
                fg_color='transparent',anchor='w',justify='left',wraplength=600)
            description.grid(row=1,sticky='ew',padx=16,pady=(0,12))
        def resize(event):
            if event.widget is not frame._canvas:return
            width=max(120,int(event.width/frame._get_widget_scaling())-32)
            for label in (heading,description):
                if label is not None and label.cget('wraplength')!=width:label.configure(wraplength=width)
        frame.bind('<Configure>',resize,add='+')
        return SimpleNamespace(frame=frame,title=heading,description=description)

    def add_actions(self,parent,actions,translate,*,row=0,pady=(4,4)):
        buttons=[dialog_button(cst.CTkButton(parent,text=translate(caption),command=callback))
            for caption,callback in actions]
        dialog_actions(parent,buttons,row=row,pady=pady)
        return buttons

    def destroy(self):
        for token in tuple(self._dialog_jobs):
            try:super().after_cancel(token)
            except tk.TclError:pass
        self._dialog_jobs.clear()
        super().destroy()

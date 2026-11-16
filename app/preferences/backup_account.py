"""Local-only sender configuration; saving never sends an email."""
from app.shared.messages import error_text
import customtkinter as cst
import tkinter as tk
from app.services.mail_credentials import load_credentials,save_credentials
from app.ui.components.app_dialog import AppDialog
from app.ui.theme import FONT,TEXT


class BackupAccountDialog(AppDialog):
    def __init__(self,owner,on_saved=None):
        super().__init__(owner)
        self._previous_grab=self.grab_current()
        self.translate=self.app_context.translate
        self.on_saved=on_saved
        self.title(self.translate('Backup sending account'))
        self.geometry('740x540');self.minsize(620,480)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.add_heading(self.translate('Backup sending account'),
            self.translate('Use the sending account for smtp.seznam.cz. The recipient stays in Backup mail.'))
        body=cst.CTkFrame(self,fg_color='#ded4bf',corner_radius=18)
        body.grid(row=1,sticky='nsew',padx=20,pady=8);body.grid_columnconfigure(0,weight=1)
        cst.CTkLabel(body,text=self.translate('Sender email'),font=(FONT,16),text_color=TEXT,
                     anchor='w').grid(row=0,sticky='ew',padx=16,pady=(14,4))
        self.username=cst.CTkEntry(body,font=(FONT,17),height=38,fg_color='#eee4d0',text_color=TEXT,border_color='#b7ac91')
        self.username.grid(row=1,sticky='ew',padx=16)
        cst.CTkLabel(body,text=self.translate('SMTP password'),font=(FONT,16),text_color=TEXT,
                     anchor='w').grid(row=2,sticky='ew',padx=16,pady=(12,4))
        self.password=cst.CTkEntry(body,font=(FONT,17),height=38,show='•',fg_color='#eee4d0',text_color=TEXT,border_color='#b7ac91')
        self.password.grid(row=3,sticky='ew',padx=16)
        self.message=cst.CTkLabel(body,text=self.translate('Leave the password blank to keep it for the same sender. Saved in Windows Credential Manager.'),
            font=(FONT,14),text_color='#657671',wraplength=620,justify='left',anchor='w')
        self.message.grid(row=4,sticky='ew',padx=16,pady=12)
        self.error=cst.CTkLabel(self,text='',text_color='#963f32',fg_color='#f2d9d0',
            corner_radius=12,font=(FONT,14),wraplength=620,justify='left',anchor='w')
        self.error.grid(row=2,sticky='ew',padx=20,pady=4);self.error.grid_remove()
        self.error.bind('<Configure>',self._resize_error,add='+')
        self.add_actions(self,[('Close',self.destroy),('Save',self.save)],self.translate,row=3,pady=(8,16))
        self.apply_background('sections_warm_v1.png')
        try:
            existing=load_credentials()
            if existing:
                self.username.insert(0,existing[0])
                self.password.insert(0,existing[1])
        except (OSError,ValueError,UnicodeError) as error:self.show_error(error)
        self.bind('<Control-s>',lambda event:self.save())
        self.bind('<Control-S>',lambda event:self.save())
        self.after(50,lambda:self.present(modal=True))
        body.bind('<Configure>',lambda event:self.message.configure(
            wraplength=max(100,int(event.width/body._get_widget_scaling())-32)),add='+')

    def show_error(self,error):
        self.error.configure(text=error_text(error, self.translate))
        self.error.grid()

    def _resize_error(self,event):
        if event.widget is self.error._canvas:
            width=max(100,int(event.width/self.error._get_widget_scaling())-16)
            if self.error.cget('wraplength')!=width:self.error.configure(wraplength=width)

    def destroy(self):
        previous=getattr(self,'_previous_grab',None)
        self._previous_grab=None
        super().destroy()
        try:
            if previous is not None and previous.winfo_exists():previous.grab_set()
        except tk.TclError:pass

    def save(self):
        try:
            username=self.username.get().strip()
            password=self.password.get()
            if not password:
                existing=load_credentials()
                if existing and existing[0]==username:password=existing[1]
            save_credentials(username,password)
        except (OSError,ValueError,UnicodeError) as error:
            self.show_error(error)
            return
        if self.on_saved:self.on_saved()
        self.destroy()

"""One sender account, automatic providers, and asynchronous test delivery."""
import tkinter as tk
import customtkinter as cst
import webbrowser
from app.shared.messages import error_text
from app.shared.background_task import BackgroundTask
from app.services.mail_credentials import load_credentials,save_credentials
from app.services.mail_providers import detect_provider,sender_address,SMTPConfig,APP_HELP
from app.services.mail_transport import account,decode_secret,encode_secret,send_test
from app.ui.components.app_dialog import AppDialog
from app.ui.theme import FONT,TEXT


class BackupAccountDialog(AppDialog):
    def __init__(self,owner,on_saved=None):
        super().__init__(owner)
        self._previous_grab=self.grab_current()
        self.translate=self.app_context.translate
        self.on_saved=on_saved
        self.task=None
        self._stored=None
        self._username_trace=None
        self.title(self.translate('Backup sending account'))
        self.geometry('800x700');self.minsize(620,480)
        self.grid_columnconfigure(0,weight=1);self.grid_rowconfigure(1,weight=1)
        self.add_heading(self.translate('Backup sending account'),
            self.translate('One sending account for all backups. Known email providers are configured automatically.'))
        body=self.body=cst.CTkScrollableFrame(self,fg_color='#ded4bf',corner_radius=18)
        body.grid(row=1,sticky='nsew',padx=20,pady=8);body.grid_columnconfigure(0,weight=1)
        def label(parent,key,row):
            result=cst.CTkLabel(parent,text=self.translate(key),font=(FONT,16),text_color=TEXT,anchor='w')
            result.grid(row=row,sticky='ew',padx=16,pady=(12,4))
            return result
        def entry(parent,row,**kwargs):
            result=cst.CTkEntry(parent,font=(FONT,17),height=38,fg_color='#eee4d0',text_color=TEXT,
                               border_color='#b7ac91',**kwargs)
            result.grid(row=row,sticky='ew',padx=16)
            return result
        label(body,'Sender email',0)
        self.username_var=cst.StringVar(master=self)
        self.username=entry(body,1,textvariable=self.username_var)
        self.provider_label=cst.CTkLabel(body,text='',font=(FONT,16,'bold'),text_color=TEXT,
                                       anchor='w',justify='left',wraplength=560)
        self.provider_label.grid(row=2,sticky='ew',padx=16,pady=(12,4))
        self.provider_help=cst.CTkLabel(body,text='',font=(FONT,14),text_color='#657671',
                                       anchor='w',justify='left',wraplength=560)
        self.provider_help.grid(row=3,sticky='ew',padx=16,pady=(0,6))
        self.manual=cst.CTkFrame(body,fg_color='#eee4d0',corner_radius=12)
        self.manual.grid(row=4,sticky='ew',padx=16,pady=8);self.manual.grid_columnconfigure(0,weight=1)
        label(self.manual,'SMTP server',0);self.host=entry(self.manual,1)
        label(self.manual,'SMTP port',2);self.port=entry(self.manual,3);self.port.insert(0,'465')
        label(self.manual,'Connection security',4)
        self.security=cst.CTkOptionMenu(self.manual,values=['TLS','STARTTLS'],font=(FONT,16))
        self.security.grid(row=5,sticky='ew',padx=16,pady=(0,12));self.security.set('TLS')
        self.manual.grid_remove()
        self.password_label=label(body,'SMTP password',5)
        self.password=entry(body,6,show='•')
        self.message=cst.CTkLabel(body,text=self.translate('Leave the password blank to keep it for the same sender. Saved in Windows Credential Manager.'),
            font=(FONT,14),text_color='#657671',wraplength=560,justify='left',anchor='w')
        self.message.grid(row=7,sticky='ew',padx=16,pady=12)
        self.help_button=cst.CTkButton(body,text=self.translate('Provider help'),command=self.open_provider_help)
        self.help_button.grid(row=8,sticky='w',padx=16,pady=6)
        self.test_status=cst.CTkLabel(body,text=self.translate('The test email is sent to the sender address.'),
                                     font=(FONT,14),text_color=TEXT,wraplength=560,justify='left',anchor='w')
        self.test_status.grid(row=9,sticky='ew',padx=16,pady=(4,12))
        self.error=cst.CTkLabel(self,text='',text_color='#963f32',fg_color='#f2d9d0',
            corner_radius=12,font=(FONT,14),wraplength=620,justify='left',anchor='w')
        self.error.grid(row=2,sticky='ew',padx=20,pady=4);self.error.grid_remove()
        self.error.bind('<Configure>',self._resize_error,add='+')
        _,self.test_button,self.save_button=self.add_actions(self,
            [('Close',self.destroy),('Send test email',self.start_test),('Save',self.save)],self.translate,row=3,pady=(8,16))
        self.apply_background('sections_warm_v1.png')
        try:
            self._stored=load_credentials()
            if self._stored:
                self.username.insert(0,self._stored[0])
                _,manual=decode_secret(self._stored[1])
                if detect_provider(self._stored[0]) is None:
                    manual=manual or SMTPConfig('smtp.seznam.cz')
                    self.host.insert(0,manual.host);self.port.delete(0,'end');self.port.insert(0,str(manual.port))
                    self.security.set(manual.security)
        except (OSError,ValueError,UnicodeError) as error:self.show_error(error)
        self._username_trace=self.username_var.trace_add('write',self._update_provider)
        self._update_provider()
        self.bind('<Control-s>',lambda event:self.save())
        self.bind('<Control-S>',lambda event:self.save())
        self.after(50,lambda:self.present(modal=True))
        body.bind('<Configure>',self._resize_body,add='+')

    def _resize_body(self,event):
        if event.widget is not self.body:return
        width=max(120,int(event.width/self.body._get_widget_scaling())-32)
        for widget in (self.provider_label,self.provider_help,self.message,self.test_status):
            if widget.cget('wraplength')!=width:widget.configure(wraplength=width)

    def _update_provider(self,*_):
        try:provider=detect_provider(self.username.get());valid=True
        except ValueError:provider=None;valid=False
        self.provider=provider
        app_password=provider is not None and provider.help_key==APP_HELP
        self.password_label.configure(text=self.translate('App password' if app_password else 'Mailbox password'))
        try:username=sender_address(self.username.get())
        except ValueError:username=''
        try:saved=bool(self._stored and self._stored[0]==username and decode_secret(self._stored[1])[0])
        except ValueError:saved=False
        self.message.configure(text=(self.translate('Password saved')+'\n' if saved else '')+self.translate(
            'The saved password is hidden. Leave this field blank to keep it, or enter a new password to replace it.'
            if saved else 'No password saved for this sender. Enter it and choose Save.'))
        if provider:
            self.provider_label.configure(text=self.translate('Email provider: {name}').format(name=provider.name))
            self.provider_help.configure(text=self.translate(provider.help_key))
        else:
            self.provider_label.configure(text=self.translate('Custom SMTP') if valid else self.translate('Sender email'))
            self.provider_help.configure(text=self.translate('Enter SMTP settings supplied by your email provider.') if valid else '')
        if valid and provider is None:self.manual.grid()
        else:self.manual.grid_remove()
        supported=provider is None or provider.supported
        busy=self.task is not None
        for widget in (self.username,self.host,self.port,self.security):
            widget.configure(state='disabled' if busy else 'normal')
        self.password.configure(state='normal' if supported and not busy else 'disabled')
        for button in (self.test_button,self.save_button):
            button.configure(state='normal' if supported and not busy else 'disabled')
        if provider:self.help_button.grid()
        else:self.help_button.grid_remove()

    def open_provider_help(self):
        if self.provider:webbrowser.open(self.provider.url)

    def _account(self):
        username=sender_address(self.username.get())
        password=self.password.get()
        if not password and self._stored and self._stored[0]==username:
            password,_=decode_secret(self._stored[1])
        manual=None
        if detect_provider(username) is None:
            port=self.port.get().strip()
            if not port.isascii() or not port.isdigit():raise ValueError('Enter a valid SMTP server, port and TLS security.')
            manual=SMTPConfig(self.host.get().strip(),int(port),self.security.get()).validated()
        return account(username,password,manual)

    def show_error(self,error):
        self.error.configure(text=error_text(error,self.translate));self.error.grid()

    def _resize_error(self,event):
        if event.widget is self.error._canvas:
            self.error.configure(wraplength=max(100,int(event.width/self.error._get_widget_scaling())-16))

    def save(self):
        if self.task is not None:return
        try:
            sender=self._account()
            secret=encode_secret(sender.password,sender.config if detect_provider(sender.username) is None else None)
            save_credentials(sender.username,secret)
        except (OSError,ValueError,UnicodeError) as error:
            self.show_error(error);return
        if self.on_saved:self.on_saved()
        self.destroy()

    def start_test(self):
        if self.task is not None:return
        try:sender=self._account()
        except (OSError,ValueError,UnicodeError) as error:
            self.show_error(error);return
        self.error.grid_remove()
        self.test_status.configure(text=self.translate('Sending test email…'))
        subject=self.translate('SMTP test message')
        body=self.translate('This test confirms that VocabPro can send email using your selected account.')
        self.task=BackgroundTask(self,lambda cancel,progress:send_test(sender,subject,body),
                                 self._test_complete,self._test_failed)
        self._update_provider();self.task.start()

    def _test_complete(self,_):
        self.task=None;self._update_provider()
        self.test_status.configure(text=self.translate('Test email sent. Check your inbox.'))

    def _test_failed(self,error):
        self.task=None;self._update_provider()
        self.test_status.configure(text=self.translate('The test email was not sent.'))
        self.show_error(error)

    def destroy(self):
        if getattr(self,'task',None) is not None:self.task.close();self.task=None
        if getattr(self,'_username_trace',None) is not None:
            self.username_var.trace_remove('write',self._username_trace);self._username_trace=None
        previous=getattr(self,'_previous_grab',None);self._previous_grab=None
        super().destroy()
        try:
            if previous is not None and previous.winfo_exists():previous.grab_set()
        except tk.TclError:pass

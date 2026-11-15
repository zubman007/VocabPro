"""Screen lifetime only: bindings, scheduled work, resources and leave decisions."""
import logging
import tkinter as tk
from tkinter import messagebox
from app.core.context import get_context
from app.ui.bindings import ScreenBindings

logger=logging.getLogger(__name__)


class ScreenController:
    def __init__(self,app,screen,commands=None,*,context=None,on_window_close=None):
        self.app,self.screen=app,screen
        self.context=get_context(app,context)
        self.closed=False
        self._jobs=set()
        self._cleanups=[]
        self._dialogs={}
        self._close_token=None
        self._previous_close=None
        self._previous_controller=None
        self.bindings=ScreenBindings(app,screen,commands or {})
        screen._canvas.bind('<Destroy>',self._destroyed,add='+')
        if on_window_close is not None:
            self._previous_close=app.protocol('WM_DELETE_WINDOW')
            previous=vars(app).get('_screen_controller')
            if previous is not None and previous._close_token==self._previous_close:
                self._previous_controller=previous
            app.protocol('WM_DELETE_WINDOW',on_window_close)
            self._close_token=app.protocol('WM_DELETE_WINDOW')
            app._screen_controller=self

    def _destroyed(self,event):
        if event.widget is self.screen._canvas:self.close()

    def add_cleanup(self,callback):
        if self.closed:raise RuntimeError('Cannot register resources on a closed screen.')
        self._cleanups.append(callback)

    def trace(self,variable,mode,callback):
        if self.closed:raise RuntimeError('Cannot register resources on a closed screen.')
        token=variable.trace_add(mode,callback)
        self.add_cleanup(lambda:variable.trace_remove(mode,token))
        return token

    def own_dialog(self,dialog,close=None):
        if self.closed:raise RuntimeError('Cannot register resources on a closed screen.')
        if dialog not in self._dialogs:
            def destroyed(event):
                if event.widget is dialog:self._dialogs.pop(dialog,None)
            dialog.bind('<Destroy>',destroyed,add='+')
        self._dialogs[dialog]=close or dialog.destroy
        return dialog

    def after(self,delay,callback,*args):
        if self.closed:return None
        def invoke():
            self._jobs.discard(token)
            if not self.closed:callback(*args)
        token=self.screen.after(delay,invoke)
        self._jobs.add(token)
        return token

    def after_idle(self,callback,*args):
        return self.after('idle',callback,*args)

    def cancel_after(self,token):
        if token not in self._jobs:return
        self._jobs.remove(token)
        self.screen.after_cancel(token)

    def can_leave(self,dirty,save,*,message='Save changes before leaving?',title='Close'):
        if self.closed:return False
        if not dirty:return True
        translate=self.context.translate
        answer=messagebox.askyesnocancel(parent=self.app,title=translate(title),message=translate(message))
        # An asynchronous save returns None; it completes navigation itself later.
        return save() is True if answer is True else answer is False

    def finish(self,action):
        if self.closed:return False
        self.close()
        action()
        return True

    def close(self):
        if self.closed:return
        self.closed=True
        self.bindings.close()
        for token in tuple(self._jobs):
            try:self.cancel_after(token)
            except tk.TclError:pass
        for close in tuple(self._dialogs.values()):
            try:close()
            except tk.TclError:pass
            except Exception:logger.exception('Screen dialog cleanup failed')
        self._dialogs.clear()
        for callback in reversed(self._cleanups):
            try:callback()
            except tk.TclError:pass
            except Exception:logger.exception('Screen resource cleanup failed')
        self._cleanups.clear()
        token,self._close_token=self._close_token,None
        if token is not None:
            try:
                previous=self._previous_controller
                restore=self._previous_close
                while previous is not None and previous.closed:
                    restore=previous._previous_close
                    previous=previous._previous_controller
                # Never overwrite a handler installed by a newer screen.
                if self.app.winfo_exists() and self.app.protocol('WM_DELETE_WINDOW')==token:
                    self.app.protocol('WM_DELETE_WINDOW',restore)
                if vars(self.app).get('_screen_controller') is self:self.app._screen_controller=previous
                self.app.deletecommand(token)
            except tk.TclError:pass

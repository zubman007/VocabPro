"""Application-language messages with Tk-compatible result contracts.

Callers supply already translated titles/messages. Only this module translates
the dialog's own controls; course content and technical details stay unchanged.
"""
import tkinter as tk
import customtkinter as cst
from app.core.context import get_context
from app.ui.components.app_dialog import AppDialog
from app.ui.module_style import dialog_button, dialog_actions
from app.ui.theme import FONT, TEXT, SECTION_SURFACE, SECTION_CONTROL

CAPTIONS = {'ok': 'OK', 'yes': 'Yes', 'no': 'No', 'cancel': 'Cancel'}


class MessageDialog(AppDialog):
    def __init__(self, owner, title, message, choices, *, translate, default=None, kind='info', detail=None):
        super().__init__(owner)
        self.configure(fg_color=SECTION_SURFACE)
        self.cancel_result = 'cancel' if 'cancel' in choices else 'no' if 'no' in choices else 'ok'
        self.result = self.cancel_result
        self.default = default if default in choices else self.cancel_result
        self.title(title)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        scale = self._get_widget_scaling()
        width = min(640, int(self.winfo_screenwidth() / scale) - 40)
        height = min(460 if len(message) > 250 or detail else 340,
                     int(self.winfo_screenheight() / scale) - 80)
        self.geometry(f'{width}x{height}')
        self.minsize(min(420, width), min(280, height))
        self.header = self.add_heading(title)
        self.header.title.configure(text_color='#963f32' if kind == 'error' else TEXT)
        body = cst.CTkScrollableFrame(self, fg_color='#eee4d0', corner_radius=16)
        body.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 12))
        body.grid_columnconfigure(0, weight=1)
        self.message_label = cst.CTkLabel(body, text=message + ('\n\n' + str(detail) if detail else ''),
            text_color=TEXT, font=(FONT, 18), anchor='nw', justify='left', wraplength=width - 90, height=0)
        self.message_label.grid(sticky='ew', padx=14, pady=14)
        def resize(event):
            wrap = max(80, int(event.width / self._get_widget_scaling()) - 32)
            if self.message_label.cget('wraplength') != wrap:
                self.message_label.configure(wraplength=wrap)
        body._parent_canvas.bind('<Configure>', resize, add='+')
        actions = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        actions.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 16))
        self.buttons = {}
        for choice in choices:
            button = dialog_button(cst.CTkButton(actions, text=translate(CAPTIONS[choice]),
                command=lambda choice=choice: self.choose(choice)))
            button.configure(fg_color=SECTION_CONTROL if choice == self.default else '#c8d0b6',
                             text_color='#fff4dc' if choice == self.default else TEXT)
            tk.Misc.configure(button, takefocus=1)
            self.buttons[choice] = button
        dialog_actions(actions, list(self.buttons.values()))
        self.bind('<Return>', self._return)
        self.bind('<space>', self._space)
        self.bind('<Escape>', lambda event: self.choose(self.cancel_result))
        self.protocol('WM_DELETE_WINDOW', lambda: self.choose(self.cancel_result))

    def _focused_choice(self):
        widget = self.focus_get()
        while widget is not None and widget is not self:
            for choice, button in self.buttons.items():
                if widget is button:
                    return choice
            widget = getattr(widget, 'master', None)
        return None

    def _return(self, event=None):
        self.choose(self._focused_choice() or self.default)
        return 'break'

    def _space(self, event=None):
        choice = self._focused_choice()
        if choice is not None:
            self.choose(choice)
            return 'break'

    def choose(self, choice):
        if choice not in self.buttons:
            raise ValueError('Choose a valid option.')
        self.result = choice
        self.destroy()


def _show(title, message, *, choices=('ok',), kind='info', parent=None, default=None, detail=None):
    parent = parent if parent is not None else tk._default_root
    if parent is None:
        raise RuntimeError('A message dialog requires an application window.')
    translate = get_context(parent).translate
    owner = parent.winfo_toplevel()
    fallback = {'info': 'Information', 'error': 'Error', 'warning': 'Warning', 'question': 'Confirm'}[kind]
    title = title if title else translate(fallback)
    previous_grab, previous_focus = owner.grab_current(), owner.focus_get()
    grab_status = previous_grab.grab_status() if previous_grab is not None else None
    dialog = MessageDialog(owner, title, '' if message is None else str(message), choices,
                           translate=translate, default=default, kind=kind, detail=detail)
    try:
        dialog.present(modal=True)
        dialog.buttons[dialog.default].focus_set()
        owner.wait_window(dialog)
        return dialog.result
    finally:
        try:
            if dialog.winfo_exists():
                dialog.destroy()
            if previous_grab is not None and previous_grab.winfo_exists():
                if grab_status == 'global': previous_grab.grab_set_global()
                else: previous_grab.grab_set()
            if previous_focus is not None and previous_focus.winfo_exists():
                previous_focus.focus_set()
        except tk.TclError:
            pass  # The owner may have closed while its dialog was open.


def showerror(title=None, message=None, **options):
    return _show(title, message, kind='error', **options)


def showwarning(title=None, message=None, **options):
    return _show(title, message, kind='warning', **options)


def showinfo(title=None, message=None, **options):
    return _show(title, message, **options)


def askyesno(title=None, message=None, **options):
    return _show(title, message, kind='question', choices=('yes', 'no'), **options) == 'yes'


def askyesnocancel(title=None, message=None, **options):
    result = _show(title, message, kind='question', choices=('yes', 'no', 'cancel'), **options)
    return None if result == 'cancel' else result == 'yes'

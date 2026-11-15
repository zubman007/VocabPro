"""Shared screen shell; lesson-specific widgets live in their own layouts."""
from types import SimpleNamespace
import customtkinter as cst
from app.ui import learning_layout as ui
from app.shared import settings as s
from app.ui.surfaces import surface
from app.ui.components.module_header import ModuleHeader


def shell(app, title, image, actions):
    root = cst.CTkFrame(app)
    root.pack(fill='both', expand=True)
    backdrop = ui.background(root, image)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    header=ModuleHeader(root,s.T(title),translate=s.T,actions=actions)
    header.grid_standard()
    body = cst.CTkFrame(root, fg_color='transparent', corner_radius=0)
    body.grid(row=1, sticky='nsew', padx=28, pady=(8, 24))
    body.grid_columnconfigure(0, weight=1)
    layer = surface(body, backdrop)
    header.attach_background(backdrop)
    return SimpleNamespace(root=root, header=header, body=body, layer=layer)


def text(parent, value='', size=20, bold=False, color=ui.TEXT):
    widget = cst.CTkLabel(parent, text=value, justify='left', anchor='w')
    ui.label(widget, size, color, bold)
    return widget


def action(parent, title, command, accent, secondary=False):
    widget = cst.CTkButton(parent, text=s.T(title), command=command)
    ui.button(widget, accent, secondary)
    return widget

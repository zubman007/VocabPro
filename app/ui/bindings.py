"""Keyboard bindings owned by one screen and released with that screen."""
import tkinter as tk


class ScreenBindings:
    def __init__(self, app, screen, commands):
        self.app = app
        self.tokens = {}
        self.closed = False
        for sequence, command in commands.items():
            self.bind(sequence, command)
        screen._canvas.bind('<Destroy>', lambda event: self.close(), add='+')

    def bind(self, sequence, command):
        if self.closed:
            return
        self.unbind(sequence)
        self.tokens[sequence] = self.app.bind(sequence, command, add='+')

    def unbind(self, sequence):
        token = self.tokens.pop(sequence, None)
        if token is not None:
            self.app.unbind(sequence, token)

    def close(self):
        if self.closed:
            return
        self.closed = True
        for sequence, token in self.tokens.items():
            try:
                self.app.unbind(sequence, token)
            except tk.TclError:
                pass
        self.tokens.clear()

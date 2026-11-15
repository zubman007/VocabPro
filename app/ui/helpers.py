"""Shared window, layout and background helpers."""
from tkinter import Grid
import customtkinter as cst

def Grid_ratio(frame, weight_row, weight_column):
    for i, weight in enumerate(weight_row): Grid.rowconfigure(frame, i, weight=weight)
    for i, weight in enumerate(weight_column): Grid.columnconfigure(frame, i, weight=weight)

def Clear_frames(app):
    for widget in app.winfo_children():
        if isinstance(widget, cst.CTkFrame): widget.destroy()

def Clear_tops(app):
    for widget in app.winfo_children():
        if isinstance(widget, cst.CTkToplevel): widget.destroy()


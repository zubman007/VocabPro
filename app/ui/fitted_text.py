"""Fit a learning prompt against its actual card, preserving the full text."""
from app.ui.theme import FONT
import tkinter as tk


def fit_question_prompt(label,card):
    scale=card._get_widget_scaling()
    width=max(80,int(card.winfo_width()/scale)-64)
    footer=getattr(card,'_prompt_footer',None)
    footer_height=0
    if footer is not None and footer.winfo_manager() and footer.cget('text'):
        if footer.cget('wraplength')!=width:footer.configure(wraplength=width)
        footer_height=max(footer.cget('height'),footer._label.winfo_reqheight()/scale)+12
    signature=(label.cget('text'),width,scale,footer_height)
    if getattr(card,'_prompt_fit_signature',None)==signature:return
    card._prompt_fit_signature=signature
    # Tk measures the rendered wrapping, including explicit newlines and words
    # without spaces; character counts alone cannot determine whether it fits.
    probe=tk.Label(card,text=label.cget('text'),wraplength=round(width*scale),padx=0,pady=0,bd=0)
    try:
        for size in range(42,21,-2):
            probe.configure(font=(FONT,-round(size*scale),'bold'))
            if probe.winfo_reqheight()<=176*scale:break
        height=max(260,int(probe.winfo_reqheight()/scale)+86+round(footer_height))
    finally:probe.destroy()
    label.configure(wraplength=width,font=(FONT,size,'bold'))
    if card.cget('height')!=height:card.configure(height=height)

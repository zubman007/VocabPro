"""Multiline review edits, committed to the practice session by the controller."""
import customtkinter as cst
from app.ui.learning_review import ReviewDialog
from app.ui import learning_layout as ui
from app.shared import settings as s


def edit_attribute(owner, title, word, value, on_save):
    dialog = None
    def save():
        text = editor.get('1.0','end-1c').strip()
        dialog.destroy()
        on_save(text if text else 'No found')
    dialog = ReviewDialog(owner,title,word,'',[],[('Save',save),('Close',lambda:dialog.destroy())])
    body=dialog.detail_body
    body.grid_columnconfigure(0,weight=1)
    editor=cst.CTkTextbox(body,height=280,wrap='word',font=(ui.FONT,19),
        fg_color='#f1e8d5',text_color=ui.TEXT,corner_radius=16)
    editor.grid(row=0,column=0,sticky='ew',padx=16,pady=16)
    if value not in ('','-','No found',None):editor.insert('1.0',value)
    cst.CTkLabel(body,text=s.T('Changes are saved with the practice session.'),font=(ui.FONT,14),
        text_color=ui.MUTED,wraplength=650).grid(row=1,column=0,sticky='w',padx=16,pady=(0,12))
    dialog.editor=editor
    dialog.save_edit=save
    return dialog

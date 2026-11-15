"""One muted shortcut style with whole-item wrapping for every learning screen."""
import customtkinter as cst
from app.ui.theme import FONT
from app.about.shortcuts import shortcut_sections


class ShortcutHint(cst.CTkLabel):
    def __init__(self,parent,section,translate,show_synonyms=True,vertical=False,rounded=False,*,tags_enabled=True):
        self.items=[f'{translate(key)} · {translate(label)}' for key,label in
                    dict(shortcut_sections(show_synonyms,tags_enabled))[section]]
        self.vertical=vertical
        self.hint_font=cst.CTkFont(family=FONT,size=12)
        super().__init__(parent,text='\n'.join(self.items),font=self.hint_font,text_color='#657671',
            fg_color='#d7dfca',corner_radius=12 if rounded else 0,padx=0,pady=6,justify='left',anchor='w',wraplength=180)
        self.bind('<Configure>',self._resize,add='+')

    def _resize(self,event):
        if event.widget is not self._canvas:return
        width=max(60,int(event.width/self._get_widget_scaling())-20)
        lines=[];line=''
        for item in self.items:
            candidate=(line+'    '+item) if line else item
            if line and (self.vertical or self.hint_font.measure(candidate)>width):
                lines.append(line);line=item
            else:line=candidate
        if line:lines.append(line)
        text='\n'.join(lines)
        if self.cget('text')!=text or self.cget('wraplength')!=width:
            self.configure(text=text,wraplength=width)

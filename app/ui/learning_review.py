"""Consistent, centered and scrollable review cards for learning screens."""
import customtkinter as cst
import pywinstyles
from app.shared import settings as s
from app.ui import learning_layout as ui
from app.ui.surfaces import surface
from app.ui.components.app_dialog import AppDialog


class ReviewDialog(AppDialog):
    def __init__(self, owner, title, heading, subtitle, details, actions=(),
                 subtitle_caption='Translation', background_file='practice_warm_v4.png'):
        super().__init__(owner, fg_color=ui.PAGE)
        self.withdraw()
        self.title(s.app_name + ' - ' + s.T(title))
        pywinstyles.apply_style(self, 'dark')
        self.minsize(650, 550)
        self.geometry('900x650')
        backdrop=self.make_background(background_file)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = cst.CTkFrame(self, fg_color='#48665a', corner_radius=24)
        header.grid(row=0, sticky='ew', padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)
        surface(header, backdrop)
        heading_labels = []
        for row, value, size in ((0, s.T(title), 17), (1, heading if len(heading) <= 90 else heading[:87] + '…', 30)):
            label = cst.CTkLabel(header, text=value, wraplength=720, justify='left')
            ui.label(label, size, color=ui.SURFACE, bold=row == 1)
            label.grid(row=row, padx=22, pady=(14, 2) if row == 0 else (2, 14), sticky='w')
            heading_labels.append(label)
        body = cst.CTkScrollableFrame(self, fg_color='#e6dcc8', corner_radius=24)
        body.grid(row=1, sticky='nsew', padx=20, pady=10)
        body.grid_columnconfigure(0, weight=1)
        self.detail_body = body
        surface(body._parent_frame, backdrop)
        fields = [(subtitle_caption, subtitle)] + list(details)
        if len(heading) > 90:
            fields.insert(0, ('Vocabulary', heading))
        detail_labels = []
        for item in fields:
            caption, value = item if isinstance(item, tuple) else ('Description', item)
            if value in ('', '-', '[]', 'No found', None):
                continue
            row = len(detail_labels) * 2
            label = cst.CTkLabel(body, text=s.T(caption), font=(ui.FONT, 16, 'bold'),
                                 text_color='#815632', anchor='w')
            label.grid(row=row, sticky='ew', padx=20, pady=(16, 2))
            label = cst.CTkLabel(body, text=value, justify='left', anchor='w', wraplength=700)
            ui.label(label, 23 if caption == 'Translation' else 21)
            label.grid(row=row+1, sticky='ew', padx=20, pady=(0, 12))
            detail_labels.append(label)
        body.bind('<Configure>', lambda event: [label.configure(wraplength=max(180, event.width/body._get_widget_scaling()-55))
                                               for label in detail_labels], add='+')
        footer = cst.CTkFrame(self, fg_color=ui.PAGE)
        footer.grid(row=2, sticky='ew', padx=20, pady=(8,16))
        footer_surface = surface(footer, backdrop)
        action_buttons = self.add_actions(footer,actions,s.T)
        for button in action_buttons:
            surface(button, footer_surface)
        footer.configure(fg_color='transparent')
        def resize(event):
            if event.widget is not self or not self.winfo_exists() or not header.winfo_exists():
                return
            width = event.width / header._get_widget_scaling()
            for label in heading_labels:
                label.configure(wraplength=max(200, width - 100))
        self.bind('<Configure>', resize, add='+')
        self.withdraw()
        self._present_id = self.after(250, lambda: self._present(owner))

    def _present(self, owner):
        self._present_id = None
        super().present()

    def destroy(self):
        if self._present_id is not None:
            self.after_cancel(self._present_id)
            self._present_id = None
        super().destroy()


def open_verb_review(owner, verb, persons):
    details = [verb.desc] + [f'{label}:  {getattr(verb, key)}'
                            for key, label in persons if getattr(verb, key, '')]
    return ReviewDialog(owner, 'Review of the previous verb', verb.targ_lng, verb.base_lng, details)

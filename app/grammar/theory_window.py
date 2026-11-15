"""Scrollable theory dialog; long explanations stay inside the window."""
import customtkinter as cst
from app.shared import settings as s
from app.ui import learning_layout as ui
from app.ui.surfaces import surface
from app.ui.components.app_dialog import AppDialog


class TheoryWindow(AppDialog):
    def __init__(self, owner, theory):
        super().__init__(owner, fg_color=ui.PAGE)
        self.withdraw()
        self.title(s.T('Grammar theory'))
        self.geometry('900x750')
        self.minsize(600, 450)
        self.transient(owner)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        backdrop=self.make_background('grammar_background_v1.png')
        header = cst.CTkFrame(self, fg_color='#8b683c', corner_radius=24)
        header.grid(row=0, sticky='ew', padx=22, pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)
        title = theory.get('title') or theory.get('category', '')
        heading = cst.CTkLabel(header, text=title, font=(ui.FONT, 28, 'bold'),
            text_color=ui.SURFACE, wraplength=760, justify='left', anchor='w')
        heading.grid(row=0, sticky='ew', padx=22, pady=(18, 6))
        cst.CTkLabel(header, text=' · '.join(filter(None, (theory.get('category'), theory.get('level')))),
            font=(ui.FONT, 17), text_color='#f0dfbd', wraplength=760, anchor='w').grid(
                row=1, sticky='ew', padx=22, pady=(0, 18))
        surface(header, backdrop)
        body = cst.CTkScrollableFrame(self, fg_color='#e6dcc8', corner_radius=24)
        body.grid(row=1, sticky='nsew', padx=22, pady=8)
        body.grid_columnconfigure(0, weight=1)
        surface(body._parent_frame, backdrop)
        self.body = body
        labels = []
        for field, caption in (('description', 'Description'), ('rules', 'Rules'),
                               ('examples', 'Examples'), ('common_mistakes', 'Common mistakes'),
                               ('subtopics', 'Subtopics')):
            value = theory.get(field, '').replace('\\n', '\n')
            if not value:
                continue
            if field in ('examples', 'subtopics'):
                value = '\n\n'.join('• ' + item.strip() for item in value.split('|') if item.strip())
            row = len(labels) * 2
            cst.CTkLabel(body, text=s.T(caption), font=(ui.FONT, 18, 'bold'),
                text_color='#815632', anchor='w').grid(row=row, sticky='ew', padx=22, pady=(18, 4))
            label = cst.CTkLabel(body, text=value, font=(ui.FONT, 20), text_color=ui.TEXT,
                wraplength=760, justify='left', anchor='w')
            label.grid(row=row+1, sticky='ew', padx=22, pady=(0, 12))
            labels.append(label)
        body.bind('<Configure>', lambda event: [label.configure(
            wraplength=max(150, event.width/body._get_widget_scaling()-55)) for label in labels], add='+')
        self.bind('<Configure>', lambda event: heading.configure(wraplength=max(200,
            self.winfo_width()/header._get_widget_scaling()-95)) if event.widget is self else None, add='+')
        close,=self.add_actions(self,[('Close',self.destroy)],s.T,row=2,pady=(12,20))
        surface(close, backdrop)
        self._present_job = self.after(250, self._present)

    def _present(self):
        self._present_job = None
        super().present(modal=True)

    def destroy(self):
        if self._present_job is not None:
            self.after_cancel(self._present_job)
            self._present_job = None
        super().destroy()

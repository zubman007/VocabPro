"""Read-only audit UI. Workers receive paths/events, never Tk objects."""
from collections import Counter
from pathlib import Path
from tkinter import filedialog
import customtkinter as cst
from app.shared.background_task import BackgroundTask
from app.shared.integrity import audit
from app.shared.atomic_bytes import save_bytes
from app.ui.theme import FONT, TEXT, MUTED, SECTION_SURFACE, SECTION_CONTROL, SURFACE, RADIUS
from app.ui import messagebox
from app.ui.components.app_dialog import AppDialog


class IntegrityPanel(cst.CTkFrame):
    PAGE_SIZE = 50

    def __init__(self, parent, folder, translate, *, report=None):
        super().__init__(parent, fg_color=SECTION_SURFACE, corner_radius=RADIUS)
        self.folder, self.tr = Path(folder), translate
        self.task = None
        self.report = None
        self.page = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        cst.CTkLabel(self, text=translate('Data integrity'), text_color=TEXT,
            font=(FONT, 24, 'bold'), anchor='w').grid(row=0, sticky='ew', padx=20, pady=(18, 6))
        self.help = cst.CTkLabel(self, text=translate('Integrity help'), text_color=MUTED,
            font=(FONT, 14), wraplength=850, justify='left', anchor='w')
        self.help.grid(row=1, sticky='ew', padx=20, pady=(0, 12))
        controls = cst.CTkFrame(self, fg_color='transparent')
        controls.grid(row=2, sticky='ew', padx=20)
        self.run = cst.CTkButton(controls, text=translate('Integrity run'), command=self.start,
            fg_color=SECTION_CONTROL, width=240)
        self.run.pack(side='left', padx=(0, 8))
        self.cancel = cst.CTkButton(controls, text=translate('Cancel'), command=self.stop,
            fg_color=SECTION_CONTROL, state='disabled')
        self.cancel.pack(side='left', padx=(0, 8))
        self.export = cst.CTkButton(controls, text=translate('Integrity export'), command=self.export_report,
            fg_color=SECTION_CONTROL, state='disabled', width=180)
        self.export.pack(side='left')
        self.progress = cst.CTkProgressBar(self, progress_color=SECTION_CONTROL)
        self.progress.grid(row=3, sticky='ew', padx=20, pady=12)
        self.progress.set(0)
        self.results = cst.CTkTextbox(self, fg_color=SURFACE, text_color=TEXT,
            font=(FONT, 14), wrap='word', corner_radius=14, state='disabled')
        self.results.grid(row=4, sticky='nsew', padx=20, pady=4)
        for severity,color in (('Critical','#963f32'),('Warning','#895d2f'),('Info',MUTED)):
            self.results.tag_config(severity,foreground=color)
        footer = cst.CTkFrame(self, fg_color='transparent')
        footer.grid(row=5, sticky='ew', padx=20, pady=10)
        self.area = cst.CTkOptionMenu(footer, values=[translate('Integrity all')],
            command=lambda _:self.show_page(0), fg_color=SECTION_CONTROL)
        self.area.pack(side='left')
        cst.CTkButton(footer, text='→', width=40, fg_color=SECTION_CONTROL,
            command=lambda:self.show_page(self.page+1)).pack(side='right')
        cst.CTkButton(footer, text='←', width=40, fg_color=SECTION_CONTROL,
            command=lambda:self.show_page(self.page-1)).pack(side='right', padx=6)
        self.pagination = cst.CTkLabel(footer, text='', text_color=TEXT, font=(FONT, 14))
        self.pagination.pack(side='right', padx=12)
        self.status = cst.CTkLabel(self, text='', text_color=TEXT, font=(FONT, 14),
            anchor='w', wraplength=850, justify='left')
        self.status.grid(row=6, sticky='ew', padx=20, pady=(0, 16))
        self.bind('<Configure>', self.resize_text, add='+')
        if report is not None:self.finished(report)

    def resize_text(self,event):
        width=max(160,int(event.width/self._get_widget_scaling())-40)
        for label in (self.help,self.status):label.configure(wraplength=width)

    def destroy(self):
        # CTkFrame.bind targets its canvas, so a frame-identity Destroy binding
        # would miss this cleanup and leave the Tk polling callback behind.
        if self.task is not None:self.task.close()
        super().destroy()

    def start(self):
        if self.task is not None and not self.task.closed:return
        folder = self.folder
        self.run.configure(state='disabled')
        self.cancel.configure(state='normal')
        self.export.configure(state='disabled')
        self.progress.set(0)
        self.status.configure(text=self.tr('Integrity running'))
        self.task = BackgroundTask(self,
            lambda cancelled, progress:audit(folder, cancelled=cancelled, progress=progress),
            self.finished, self.failed, self.update_progress).start()

    def stop(self):
        if self.task is not None:self.task.cancel()
        self.cancel.configure(state='disabled')

    def update_progress(self, state, total):
        offset, area, records = state
        self.progress.set(offset/max(1, total))
        self.status.configure(text=self.tr('Integrity progress {area} {count}').format(
            area=self.tr(area), count=records))

    def failed(self, error):
        # Exception messages can contain secrets or raw input; show a safe message.
        import logging
        logging.getLogger('vocabpro.integrity').warning('Audit failed (%s)', type(error).__name__)
        self.run.configure(state='normal')
        self.cancel.configure(state='disabled')
        self.status.configure(text=self.tr('Integrity unreadable'))

    def finished(self, report):
        self.report = report
        self.run.configure(state='normal')
        self.cancel.configure(state='disabled')
        self.export.configure(state='normal')
        if report.completed:
            self.progress.set(1)
        self.modules = {self.tr(area):area for area in sorted(set(report.modules)|{f.module for f in report.findings})}
        self._visible_area=object()
        self.area.configure(values=[self.tr('Integrity all'), *self.modules])
        self.area.set(self.tr('Integrity all'))
        counts = Counter(f.severity for f in report.findings)
        summary = self.tr('Integrity summary {files} {records} {critical} {warning} {info}').format(
            files=report.files, records=report.records, critical=counts['Critical'],
            warning=counts['Warning'], info=counts['Info'])
        mode=self.tr('Integrity quick') if report.mode=='quick' else self.tr('Integrity full')
        self.status.configure(text=mode+'\n'+summary+('' if report.completed else '\n'+self.tr('Integrity incomplete')))
        self.show_page(0)

    def show_page(self, page):
        if self.report is None:return
        area = self.modules.get(self.area.get())
        if area!=self._visible_area:
            # Audit results are already ordered by the worker. Pagination never
            # sorts or recreates the entire result list on the UI thread.
            self._visible_area=area
            self._visible=self.report.findings if area is None else [f for f in self.report.findings if f.module==area]
        findings=self._visible
        self.page = max(0, min(page, max(0, (len(findings)-1)//self.PAGE_SIZE)))
        rows = findings[self.page*self.PAGE_SIZE:(self.page+1)*self.PAGE_SIZE]
        start=self.page*self.PAGE_SIZE+1 if findings else 0
        self.pagination.configure(text=f'{start}–{min((self.page+1)*self.PAGE_SIZE,len(findings))} / {len(findings)}')
        self.results.configure(state='normal')
        self.results.delete('1.0', 'end')
        for finding in rows:
            heading=f'{self.tr(finding.module)} · {self.tr(finding.severity)} · {finding.file}'
            if finding.row:heading+=self.tr('Integrity row {row}').format(row=finding.row)
            self.results.insert('end',heading+'\n',finding.severity)
            self.results.insert('end',self.tr(finding.code)+'\n')
            if finding.severity!='Info':self.results.insert('end',self.tr('Integrity advice')+'\n')
            self.results.insert('end','\n')
        if not findings:
            self.results.insert('end',self.tr('Integrity no findings') if self.report.completed else self.tr('Integrity incomplete'))
        self.results.configure(state='disabled')

    def export_report(self):
        if self.report is None:return
        destination = filedialog.asksaveasfilename(parent=self, defaultextension='.json',
            filetypes=[(self.tr('Integrity report'), '*.json')], initialfile='vocabpro-integrity.json')
        if not destination:return
        try:
            path = Path(destination)
            if path.resolve().is_relative_to(self.folder.resolve()):raise ValueError
        except (OSError, ValueError):
            messagebox.showerror(parent=self, title=self.tr('Data integrity'), message=self.tr('Integrity export failed'))
            return
        report,translate=self.report,self.tr
        def write(cancelled,progress):
            payload=report.export(translate).encode('utf-8')
            if cancelled.is_set():return False
            save_bytes(path,payload)
            return True
        def finished(saved):
            self.run.configure(state='normal')
            self.export.configure(state='normal')
            self.cancel.configure(state='disabled')
            self.status.configure(text=self.tr('Integrity report') if saved else self.tr('Integrity incomplete'))
        def failed(error):
            finished(False)
            messagebox.showerror(parent=self,title=self.tr('Data integrity'),message=self.tr('Integrity export failed'))
        self.run.configure(state='disabled')
        self.export.configure(state='disabled')
        self.cancel.configure(state='normal')
        self.task=BackgroundTask(self,write,finished,failed).start()


def open_integrity(owner, folder, translate, report=None):
    dialog = AppDialog(owner)
    dialog.title(translate('Data integrity'))
    dialog.geometry('1060x720')
    dialog.minsize(820,560)
    panel = IntegrityPanel(dialog, folder, translate, report=report)
    panel.pack(fill='both', expand=True, padx=18, pady=18)
    dialog.present()
    return dialog

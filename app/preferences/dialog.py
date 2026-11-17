"""Preferences UI; validation is in preferences.data, persistence in repositories."""
from app.shared.messages import error_text
from app.ui.theme import FONT, PAGE, SECTION_SURFACE as CARD
from app.ui import messagebox
import customtkinter as cst
import pywinstyles
from app.preferences.data import (PREFERENCES_FILE, PreferenceError, options_for, section_for,
                                  with_defaults, group_for, TAG_DEPENDENT_FIELDS)
from app.repositories.preferences import load_preferences, save_preferences
from app.ui.theme import TEXT, SECTION_CONTROL as HEADER
from app.ui.sections import SectionTabs
from app.ui.components.module_header import ModuleHeader
from app.ui.components.app_dialog import AppDialog
from app.ui.surfaces import surface
from app.ui.theme import RADIUS
from app.preferences.courses import (COURSE_FIELD, decode_courses, legacy_courses, is_legacy_course_field)
from app.preferences.course_editor import CourseEditor

ACCENT = "#ad694e"


class PreferencesDialog(AppDialog):
    def __init__(self, parent, translate, path=PREFERENCES_FILE):
        super().__init__(parent)
        self.withdraw()
        self._show_after = None
        self.owner = parent
        from pathlib import Path
        self.translate, self.path, self.saved = translate, Path(path), False
        self.variables, self.fields, self.field_sections, self.secret_entries = {}, {}, {}, []
        self.field_labels, self.group_headers = {}, []
        self._tag_trace = None
        self._sound_trace = None
        self._records_trace = None
        self.choice_maps = {}
        try:
            self.frame = load_preferences(path)
            stored = dict(zip(self.frame.Name, self.frame.Value))
            courses = decode_courses(stored[COURSE_FIELD], stored['Learned by']) if COURSE_FIELD in stored else legacy_courses(stored)
            from app.repositories.course_files import resolve_conjugation_courses
            courses=resolve_conjugation_courses(self.path.parent,stored.get('Learned by',''),courses)
        except Exception:
            self.destroy()
            raise
        self.title(translate("Setting"))
        self.geometry("1120x760")
        self.minsize(min(950, self.winfo_screenwidth()), min(650, self.winfo_screenheight()-80))
        self.configure(fg_color=PAGE)
        backdrop=self.make_background('sections_warm_v1.png')
        pywinstyles.apply_style(self, "dark")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header=header=ModuleHeader(self,translate('Setting'),translate=translate,
            actions=[('save',self.save),('close',self.destroy)])
        header.grid_standard()
        header.attach_background(backdrop)
        self.tabs = SectionTabs(self)
        self.tabs.enable_transparent_panels()
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        tabs_surface = surface(self.tabs, backdrop)
        selector_surface = surface(self.tabs._segmented_button, tabs_surface)
        sections = {}
        for key in ("Languages", "Learning", "Backups", "API services"):
            title=translate(key)
            tab=self.tabs.add(title)
            tab_surface = surface(tab, tabs_surface)
            body=cst.CTkScrollableFrame(tab, fg_color=CARD, corner_radius=RADIUS)
            body.pack(fill="both", expand=True, padx=16, pady=12)
            surface(body._parent_frame, tab_surface)
            body.grid_columnconfigure(0, weight=1)
            body.grid_columnconfigure(1, weight=1)
            sections[key] = body
        for button in self.tabs._segmented_button.winfo_children():
            if isinstance(button, cst.CTkButton):
                surface(button, selector_surface)
        rows = dict.fromkeys(sections, 0)
        items = [item for item in with_defaults(self.frame).itertuples(index=False)
                 if item.Type != 'JSON' and not is_legacy_course_field(item.Name)
                 and (group_for(item.Name) != 'Grammar'
                      or any(course.enabled and course.grammar_enabled for course in courses))
                 and (group_for(item.Name) != 'Conjugation'
                      or any(course.enabled and course.conjugation_enabled for course in courses))]
        # Keep groups contiguous even when new defaults were appended to an older CSV.
        grouped = {}
        for item in items:
            grouped.setdefault((section_for(item.Name), group_for(item.Name)), []).append(item)
        group_order = ('Settings general', 'Vocabulary', 'Grammar', 'Conjugation', 'Practice records', 'Tags', 'Settings sounds')
        groups = sorted(grouped, key=lambda key:(tuple(sections).index(key[0]), group_order.index(key[1])))
        previous_group = None
        for item in (entry for group in groups for entry in grouped[group]):
            name, kind, value = item.Name, item.Type, item.Value
            section = section_for(name)
            body, row = sections[section], rows[section]
            group = (section, group_for(name))
            if group != previous_group:
                if rows[section]:
                    cst.CTkFrame(body, height=1, corner_radius=0, fg_color='#c9bea6').grid(
                        row=row, column=0, columnspan=2, sticky='ew', padx=12, pady=(14, 8))
                    row += 1
                title = cst.CTkLabel(body, text=translate(group[1]), fg_color='transparent',
                    text_color='#756348', font=(FONT, 16, 'bold'), anchor='w')
                title.grid(row=row, column=0, columnspan=2, sticky='ew', padx=12, pady=(6, 4))
                self.group_headers.append(title)
                row += 1
                previous_group = group
                if group[1]=='Practice records':
                    cst.CTkLabel(body,text=translate('Practice records help'),text_color='#657671',
                        font=(FONT,14),wraplength=650,justify='left',anchor='w').grid(
                            row=row,column=0,columnspan=2,sticky='ew',padx=12,pady=(0,8))
                    row+=1
            rows[section] = row + 1
            self.field_sections[name] = translate(section)
            label = cst.CTkLabel(body, text=translate(name), text_color=TEXT, fg_color='transparent',
                font=(FONT, 19), wraplength=430, justify="left", anchor="w")
            label.grid(row=row, column=0, sticky="w", padx=(12, 24), pady=10)
            self.field_labels[name] = label
            variable=cst.StringVar(value=value)
            self.variables[name] = variable
            choices=options_for(kind)
            if choices is not None:
                self.choice_maps[name]={translate(choice):choice for choice in choices}
                variable.set(translate(value))
                widget=cst.CTkOptionMenu(body, values=[translate(choice) for choice in choices], variable=variable,
                    fg_color=HEADER, button_color=HEADER, button_hover_color="#315347",
                    dropdown_fg_color=CARD, dropdown_text_color=TEXT,
                    font=(FONT, 19), height=38)
            elif kind == "Bool":
                widget=cst.CTkCheckBox(body, text="", variable=variable, onvalue="1", offvalue="0", fg_color=ACCENT)
            else:
                widget=cst.CTkEntry(body, textvariable=variable, fg_color="#eee4d0",
                    border_color="#b7ac91", text_color=TEXT, font=(FONT, 19), height=38)
                if section == "API services":
                    widget.configure(show="•")
                    self.secret_entries.append(widget)
                if kind not in ("Str", "Int"):
                    widget.configure(state="disabled")
            widget.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=10)
            self.fields[name]=widget
            if name == 'App sound volume':
                cst.CTkLabel(body, text=translate('App sounds do not affect pronunciation.'),
                    text_color='#657671', font=(FONT, 15), wraplength=750, justify='left').grid(
                        row=row+1, column=0, columnspan=2, sticky='w', padx=12, pady=(0, 12))
                rows[section] += 1
            if name == 'Autoplay pronunciation':
                cst.CTkLabel(body, text=translate('Autoplay pronunciation help'), text_color='#657671',
                    font=(FONT, 15), wraplength=750, justify='left').grid(
                        row=row+1, column=0, columnspan=2, sticky='w', padx=12, pady=(0, 12))
                rows[section] += 1
        self.course_editor = None
        if 'Learned by' in self.fields:
            source = lambda: self.choice_maps['Learned by'].get(self.variables['Learned by'].get(), self.variables['Learned by'].get())
            self.course_editor = CourseEditor(sections['Languages'], translate, source, courses)
            self.course_editor.grid(row=rows['Languages'], column=0, columnspan=2, sticky='ew', padx=12, pady=12)
            self.field_sections[COURSE_FIELD] = translate('Languages')
            self.fields[COURSE_FIELD] = self.course_editor
            self.fields['Learned by'].configure(command=lambda _: self.course_editor.refresh_add_button())
        self.show_secrets=cst.BooleanVar(value=False)
        from app.ui.module_style import tool_button
        self.sender_button=tool_button(cst.CTkButton(sections['Backups'],
            text=translate('Sending account'),command=self.open_sender_account))
        self.sender_button.grid(row=rows['Backups'],column=0,columnspan=2,sticky='w',padx=12,pady=12)
        cst.CTkCheckBox(sections["API services"], text=translate("Show API keys"),
            variable=self.show_secrets, command=self.toggle_secrets, text_color=TEXT,
            fg_color=ACCENT, font=(FONT, 18)).grid(row=rows["API services"], column=0,
                columnspan=2, sticky="w", padx=10, pady=18)
        self.error_panel=cst.CTkFrame(self, fg_color='#f2d9d0', border_color='#c88d7b',
            border_width=1, corner_radius=14)
        self.error_panel.grid(row=2, column=0, sticky='ew', padx=24, pady=(4, 12))
        self.error_panel.grid_columnconfigure(0, weight=1)
        self.error=cst.CTkLabel(self.error_panel, text='', fg_color='transparent',
            text_color='#963f32', wraplength=950, justify='left', font=(FONT, 17), anchor='w')
        self.error.grid(row=0, column=0, sticky='ew', padx=16, pady=12)
        self.error_panel.bind('<Configure>', lambda event:self.error.configure(
            wraplength=max(100,int(event.width/self.error_panel._get_widget_scaling())-32)), add='+')
        self.error_panel.grid_remove()
        from app.ui.components.shortcut_hint import ShortcutHint
        self.shortcuts=ShortcutHint(self,'Setting',translate,rounded=True)
        self.shortcuts.grid(row=3,column=0,sticky='ew',padx=24,pady=(0,10))
        surface(self.shortcuts,backdrop)
        surface(self.error_panel, backdrop)
        self._tag_trace = self.variables['Enable tags'].trace_add('write', self._update_tag_controls)
        self._update_tag_controls()
        self._sound_trace = self.variables['App sounds enabled'].trace_add('write', self._update_sound_controls)
        self._update_sound_controls()
        self._records_trace = self.variables['Track personal records'].trace_add('write', self._update_records_controls)
        self._update_records_controls()
        self.bind("<Control-s>", lambda event: self.save())
        self.bind("<Control-S>", lambda event: self.save())
        self.withdraw()
        self._show_after = self.after(250, self.present)

    def present(self):
        """Map after CustomTkinter's deferred titlebar setup, then make modal."""
        self._show_after = None
        if not self.winfo_exists():
            return
        super().present(modal=True)
        self.focus_set()

    def destroy(self):
        if getattr(self, '_records_trace', None) is not None:
            self.variables['Track personal records'].trace_remove('write', self._records_trace)
            self._records_trace = None
        if getattr(self, '_sound_trace', None) is not None:
            self.variables['App sounds enabled'].trace_remove('write', self._sound_trace)
            self._sound_trace = None
        if getattr(self, '_tag_trace', None) is not None:
            self.variables['Enable tags'].trace_remove('write', self._tag_trace)
            self._tag_trace = None
        if getattr(self, "_show_after", None) is not None:
            self.after_cancel(self._show_after)
            self._show_after = None
        super().destroy()

    def toggle_secrets(self):
        for entry in self.secret_entries:
            entry.configure(show="" if self.show_secrets.get() else "•")

    def open_sender_account(self):
        from app.preferences.backup_account import BackupAccountDialog
        dialog=getattr(self,'_sender_dialog',None)
        if dialog is not None and dialog.winfo_exists():
            dialog.lift()
            return
        def saved():
            coordinator=getattr(self.owner,'_backup_coordinator',None)
            if coordinator is not None:coordinator.reset_retry()
        self._sender_dialog=BackupAccountDialog(self,on_saved=saved)

    def _update_tag_controls(self, *_):
        enabled = self.variables['Enable tags'].get() == '1'
        for name in TAG_DEPENDENT_FIELDS:
            self.fields[name].configure(state='normal' if enabled else 'disabled')
            self.field_labels[name].configure(text_color=TEXT if enabled else '#858575')

    def _update_sound_controls(self, *_):
        enabled = self.variables['App sounds enabled'].get() == '1'
        self.fields['App sound volume'].configure(state='normal' if enabled else 'disabled')
        self.field_labels['App sound volume'].configure(text_color=TEXT if enabled else '#858575')

    def _update_records_controls(self, *_):
        enabled = self.variables['Track personal records'].get() == '1'
        self.fields['Show personal records'].configure(state='normal' if enabled else 'disabled')
        self.field_labels['Show personal records'].configure(text_color=TEXT if enabled else '#858575')

    def _show_error(self, text):
        self.error.configure(text=text)
        self.error_panel.grid()

    def save(self):
        try:
            values = {name: self.choice_maps.get(name,{}).get(var.get(),var.get())
                      for name,var in self.variables.items()}
            if self.course_editor is not None:
                values[COURSE_FIELD] = self.course_editor.configuration()
            updated = save_preferences(self.frame, values, self.path)
        except PreferenceError as error:
            self._show_error(self.translate(error.field) + ": " + self.translate(error.message))
            self.tabs.set(self.field_sections[error.field])
            self.fields[error.field].focus_set()
            return
        except (OSError, ValueError) as error:
            self._show_error(error_text(error, self.translate))
            return
        self.saved=True
        self.destroy()
        failures = updated.attrs.get('course_cleanup_warnings', [])
        if failures:
            messagebox.showwarning(parent=self.owner, title=self.translate('Setting'),
                message=self.translate('Settings saved. Some empty course files could not be removed: {files}').format(files=', '.join(failures)))


def open_preferences(app,*,context=None):
    from app.core.context import get_context
    context=get_context(app,context)
    from app.shared import settings
    settings.Clear_tops(app)
    try:
        dialog=PreferencesDialog(app,context.translate,context.files_dir/'settings.csv')
    except (OSError, ValueError) as error:
        messagebox.showerror(parent=app, title=settings.T("Error"), message=error_text(error, settings.T))
        return
    app.wait_window(dialog)
    if dialog.saved:
        context.go_home()

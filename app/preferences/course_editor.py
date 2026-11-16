"""A compact course list, independent of the persisted legacy language slots."""
import customtkinter as cst
from dataclasses import replace
from app.preferences.courses import StudyCourse, encode_courses, CourseConfigurationError, COURSE_FIELD
from app.preferences.data import PreferenceError
from app.shared.languages import LANGUAGE_CODES, language_id
from app.ui.theme import FONT, TEXT, SECTION_CONTROL


class CourseEditor(cst.CTkFrame):
    def __init__(self, parent, translate, source, courses):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.translate, self.source = translate, source
        self.rows = []
        self.archived = {course.target: course for course in courses if not course.enabled}
        self.known = {course.target: course for course in courses}
        self.names = {translate(name): code for name, code in LANGUAGE_CODES.items()}
        self.grid_columnconfigure(0, weight=1)
        cst.CTkLabel(self, text=translate('Study courses'), font=(FONT, 20, 'bold'),
            text_color=TEXT, anchor='w').grid(row=0, sticky='ew', pady=(12, 6))
        cst.CTkLabel(self, text=translate('Study courses help'), font=(FONT, 15), text_color='#657671',
            wraplength=750, justify='left', anchor='w').grid(row=1, sticky='ew', pady=(0, 12))
        self.list = cst.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.list.grid(row=2, sticky='ew'); self.list.grid_columnconfigure(0, weight=1)
        self.add_button = cst.CTkButton(self, text=translate('Add language'), command=self.add_course,
            fg_color=SECTION_CONTROL, hover_color='#315347', font=(FONT, 17), height=36)
        self.add_button.grid(row=3, sticky='w', pady=12)
        for course in courses:
            if course.enabled:
                self.add_course(course)

    def add_course(self, course=None):
        if course is None:
            available = self._available_languages()
            if not available:
                return
            course = replace(self.archived.get(available[0], StudyCourse(available[0])), enabled=True)
        card = cst.CTkFrame(self.list, fg_color='#eee4d0', corner_radius=16)
        card.grid(row=len(self.rows), sticky='ew', pady=5)
        card.grid_columnconfigure((0, 1), weight=1, uniform='course')
        target = cst.StringVar(value=self.translate(course.language))
        enabled = cst.StringVar(value='1' if course.enabled else '0')
        context = cst.StringVar(value=str(course.context_percent))
        audio = cst.StringVar(value=str(course.audio_percent))
        grammar = cst.StringVar(value='1' if course.grammar_enabled else '0')
        chooser = cst.CTkOptionMenu(card, variable=target, values=list(self.names), font=(FONT, 18),
            fg_color=SECTION_CONTROL, button_color=SECTION_CONTROL, button_hover_color='#315347',
            dropdown_fg_color='#eee4d0', dropdown_text_color=TEXT, height=36,
            command=lambda _: self._target_changed(row))
        chooser.grid(row=0, column=0, sticky='ew', padx=14, pady=12)
        toggle = cst.CTkCheckBox(card, text=self.translate('Enable course'), variable=enabled,
            onvalue='1', offvalue='0', text_color=TEXT, font=(FONT, 16), fg_color='#ad694e')
        toggle.grid(row=0, column=1, sticky='w', padx=14, pady=12)
        fields = [chooser]
        for column, (caption, variable) in enumerate((('Context questions (%)', context), ('Audio questions (%)', audio))):
            line = cst.CTkFrame(card, fg_color='transparent', corner_radius=0)
            line.grid(row=1, column=column, sticky='ew', padx=14, pady=(0, 12))
            line.grid_columnconfigure(0, weight=1)
            cst.CTkLabel(line, text=self.translate(caption), text_color=TEXT, font=(FONT, 15),
                wraplength=250, anchor='w', justify='left').grid(row=0, column=0, sticky='w', padx=(0, 8))
            entry = cst.CTkEntry(line, textvariable=variable, width=65, height=34, font=(FONT, 16),
                fg_color='#fffaef', border_color='#b7ac91', text_color=TEXT)
            entry.grid(row=0, column=1); fields.append(entry)
        grammar_toggle = cst.CTkCheckBox(card, text=self.translate('Enable grammar'), variable=grammar,
            onvalue='1', offvalue='0', text_color=TEXT, font=(FONT, 16), fg_color='#ad694e')
        grammar_toggle.grid(row=2, column=0, columnspan=2, sticky='w', padx=14, pady=(0, 12))
        fields.append(grammar_toggle)
        row = dict(target=target, enabled=enabled, context=context, audio=audio, grammar=grammar,
                   fields=fields, toggle=toggle, chooser=chooser, card=card)
        self.rows.append(row)
        def update():
            for field in fields:
                field.configure(state='normal' if enabled.get() == '1' else 'disabled')
        toggle.configure(command=update)
        update()
        self.refresh_add_button()

    def _available_languages(self):
        taken = {self.names[row['target'].get()] for row in self.rows}
        try:
            source = language_id(self.source())
        except KeyError:
            source = None
        return [code for code in LANGUAGE_CODES.values()
                if code not in taken and code != source]

    def refresh_add_button(self):
        self.add_button.configure(state='normal' if self._available_languages() else 'disabled')
        try: source = language_id(self.source())
        except KeyError: source = None
        for row in self.rows:
            others = {self.names[item['target'].get()] for item in self.rows if item is not row}
            row['chooser'].configure(values=[label for label, code in self.names.items()
                                            if code != source and code not in others])

    def _target_changed(self, row):
        target = self.names[row['target'].get()]
        saved = self.known.get(target, StudyCourse(target))
        row['context'].set(str(saved.context_percent))
        row['audio'].set(str(saved.audio_percent))
        row['grammar'].set('1' if saved.grammar_enabled else '0')
        self.refresh_add_button()

    def configuration(self):
        try:
            language_id(self.source())
        except KeyError:
            raise PreferenceError('Learned by', 'Choose a valid option.') from None
        courses = []
        for row in self.rows:
            percentages = []
            for kind in ('context', 'audio'):
                value = row[kind].get()
                if not value.isascii() or not value.isdigit() or not 0 <= int(value) <= 100:
                    raise PreferenceError(COURSE_FIELD, 'Enter a percentage between 0 and 100.')
                percentages.append(int(value))
            course = StudyCourse(self.names[row['target'].get()], row['enabled'].get() == '1',
                                 *percentages, row['grammar'].get() == '1')
            # An unchecked source-language row is being removed, not activated.
            if course.enabled or course.target != language_id(self.source()):
                courses.append(course)
        targets = {course.target for course in courses}
        courses.extend(course for target, course in self.archived.items()
                       if target not in targets and target != language_id(self.source()))
        try:
            return encode_courses(self.source(), courses)
        except CourseConfigurationError as error:
            raise PreferenceError(COURSE_FIELD, str(error)) from None

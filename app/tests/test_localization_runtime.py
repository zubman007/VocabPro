"""Real Tk localization smoke coverage; fixtures never touch user dictionaries."""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.shared.translations import LANGUAGES, get_catalog, translate
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.tests.test_grammar_editor import questions


class LocalizationRuntimeTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.root = cst.CTk(); self.root.geometry('1400x900')
        self.errors = []
        self.messages = []
        self.popup = patch('tkinter.messagebox.showerror', side_effect=lambda *args, **kwargs: self.messages.append(kwargs))
        self.popup.start()
        # These are text/interaction tests. Surface pixels have their own tests;
        # avoid compositing decorative backgrounds for every settings/About tab.
        self.surface_paint = patch('app.ui.surfaces.PanelSurface.paint')
        self.surface_paint.start()
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.files = Path(self.folder.name)
        settings = sample_preferences()
        settings = pd.concat([settings, pd.DataFrame([
            ('Random repeat batch - Conjugation', 'Int', '10'),
            ('Random repeat batch - Vocabulary', 'Int', '10')], columns=settings.columns)], ignore_index=True)
        settings.loc[settings.Name.eq('App language'), 'Type'] = 'Options[' + ','.join(LANGUAGES) + ']'
        settings.to_csv(self.files / 'settings.csv', sep=';', index=False)
        self.context = AppContext(files_dir=self.files, preferences=RuntimePreferences.from_frame(settings))
        self.context.bind(self.root)
        for language in ('English', 'Spanish'):
            course().rename(columns={'English': language}).to_csv(self.context.vocabulary_path(language), sep=';', index=False)
        questions().to_csv(self.context.grammar_path('Spanish'), sep=';', index=False)
        pd.DataFrame({'ID': [1], 'Spanish': ['hablar'], 'Czech': ['mluvit'], 'Description': ['presente'],
            'R': ['SF'], 'LR': [''], **{key: ['forma'] for key in ('s1', 's2', 's3', 'm1', 'm2', 'm3')}}).to_csv(
                self.context.conjugation_path('Spanish'), sep=';', index=False)

    def tearDown(self):
        for widget in tuple(self.root.winfo_children()): widget.destroy()
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy(); self.folder.cleanup()
        self.popup.stop()
        self.surface_paint.stop()
        self.assertEqual(self.errors, [])
        self.assertEqual(self.messages, [])

    def test_language_switch_rebuilds_home_and_dialogs_without_changing_learning_languages(self):
        from app.main import main_proc
        from app.preferences.dialog import open_preferences, PreferencesDialog
        from app.about.dialog import AboutDialog
        from app.repositories.preferences import load_preferences
        main_proc(self.root, self.context)
        for language in LANGUAGES:
            with self.subTest(language=language):
                old = tuple(self.root.winfo_children())
                def edit(dialog):
                    dialog.variables['App language'].set(dialog.translate(language))
                    dialog.save()
                with patch.object(self.root, 'wait_window', side_effect=edit):
                    open_preferences(self.root, context=self.context)
                self.root.update()
                self.assertEqual(self.context.preferences.app_language, language)
                self.assertEqual(self.context.preferences.learning_languages, ('Spanish', 'English'))
                self.assertFalse(any(widget.winfo_exists() for widget in old))
                navigation = next(w for w in self.root.winfo_children() if isinstance(w, cst.CTkFrame))
                labels = [w.cget('text') for w in navigation.winfo_children() if isinstance(w, cst.CTkButton)]
                self.assertIn(translate('Statistics', language), labels)
                stored = load_preferences(self.files / 'settings.csv').set_index('Name')
                self.assertEqual(stored.at['App language', 'Value'], language)
                about = AboutDialog(self.root, self.context.translate, 'VocabPro', 'Czech', ('Spanish', 'English'))
                about.present(); self.root.update()
                self.assertEqual(about.header.title_label.cget('text'), translate('About the application', language))
                about.destroy()
                preferences = PreferencesDialog(self.root, self.context.translate, self.files / 'settings.csv')
                preferences.variables['Learn batch'].set('-1'); preferences.save()
                self.assertIn(translate('Enter a whole non-negative number.', language), preferences.error.cget('text'))
                self.assertFalse(preferences.saved)
                preferences.destroy()

    def test_actual_training_editor_statistics_and_charts_request_known_ids_in_all_locales(self):
        from dataclasses import replace
        from app.conjugation.practise import Conjugation
        from app.vocabulary.editor import EditorController
        from app.statistics.viewer import Stats
        from app.statistics.window import StatisticsWindow
        from app.shared import settings as s
        from app.about.shortcuts import shortcut_sections
        keys = get_catalog('English')
        keyboard = {key for _, items in shortcut_sections(False) for key, _ in items}
        observed = set()
        original = self.context.translate
        def checked(message):
            # Course-defined columns are data, not catalog IDs.
            if any(char.isalpha() for char in message) and message not in keyboard and message != 'Custom':
                self.assertTrue(message in keys, f'Unknown UI message ID: {message!r}')
                observed.add(message)
            return original(message)
        before = {path: path.read_bytes() for path in self.files.glob('*_voc.csv')}
        before[self.context.conjugation_path('Spanish')] = self.context.conjugation_path('Spanish').read_bytes()
        # This test checks live message lookup and widget labels. Raster pixels
        # and visible statistics are covered by test_chart_rendering and
        # test_statistics_improvements. Give the content explicit geometry so
        # a withdrawn 1px toplevel does not collapse the layout; keep it hidden
        # to avoid repainting six desktop-sized windows in this lookup test.
        def begin(window, builder):
            window.content.place_configure(relwidth=0, relheight=0, width=1400, height=850)
            window.load(builder)
        with patch.object(self.context, 'translate', side_effect=checked), \
                patch.object(StatisticsWindow, 'begin', begin), \
                patch('app.statistics.charts.FigureCanvasTkAgg.draw_idle'):
            for language in LANGUAGES:
                with self.subTest(language=language):
                    print(f'PERF localization runtime: {language}', flush=True)
                    self.context.preferences = replace(self.context.preferences, app_language=language)
                    conjugation = Conjugation(self.root, 'Spanish', context=self.context)
                    self.root.update()
                    self.assertEqual(conjugation.view.header.title_label.cget('text'), translate('Verb Conjugation', language))
                    self.assertIn('hablar', conjugation.view.verb.cget('text'))
                    conjugation.lifecycle.close(); conjugation.view.root.destroy()
                    editor = EditorController(self.root, 'Spanish', context=self.context)
                    self.root.update()
                    self.assertEqual(editor.head_frm.title_label.cget('text'), translate('Edit course', language) + ' · ' + translate('Spanish', language))
                    self.assertEqual(editor.edit_tbl.ops.copy_label, translate('Copy', language))
                    self.assertEqual(editor.edit_tbl.ops.paste_label, translate('Paste', language))
                    for button in editor.head_frm.buttons.values():
                        if button._text_label:
                            self.assertLessEqual(button._text_label.winfo_reqwidth(), button.winfo_width() + 2)
                    editor.lifecycle.close(); editor.edit_frm.destroy()
                    window = Stats(self.root, context=self.context, section='Conjugation')
                    deadline = perf_counter() + 20
                    try:
                        while window.winfo_exists() and not window.ready and perf_counter() < deadline: self.root.update()
                        self.assertTrue(window.ready, repr(self.messages))
                        self.assertEqual(window.controller.conjugation_progress.labels['practised'].cget('text'),
                                         translate('Practised conjugation rounds', language))
                        canvas = window.controller.chart_con_frm._chart_canvas
                        self.assertEqual(canvas.figure.axes[0].get_ylabel(), translate('Number of verbs', language))
                        for section in ('Vocabulary', 'Grammar', 'Conjugation'):
                            window.statistics_tabs.select(section); self.root.update()
                        self.assertEqual(window.statistics_tabs.selected, 'Conjugation')
                        self.assertTrue(window.controller.conjugation_table.grid_info())
                    finally: window.destroy()
        for path, content in before.items(): self.assertEqual(path.read_bytes(), content)
        self.assertGreater(len(observed), 100)
        self.assertTrue({'Real', 'Ideal', 'Difficult conjugation rounds'} <= observed)
        print(f'PERF localization observed message IDs: {len(observed)} across six UI languages', flush=True)

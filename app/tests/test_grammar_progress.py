"""Stored grammar histories, retained bars, and placement below categories."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.shared.translations import translate
from app.statistics.data import training_statistics
from app.statistics.grammar_progress import GrammarQuestionProgress, grammar_question_progress
from app.statistics.grammar_progress_panel import GrammarProgressPanel, GrammarRecordPanel


class GrammarProgressTests(TestCase):
    def test_each_question_has_one_bucket_and_failure_resets_only_its_streak(self):
        frame = pd.DataFrame({'R': ['', None, 'F', 'SSSF', 'S', 'FFS',
                                    'SS', 'SSFSS', 'SSS', 'FSSSSSS']})
        before = frame.copy(deep=True)
        result = grammar_question_progress(frame)
        self.assertEqual(result, GrammarQuestionProgress(2, 2, 2, 2, 2))
        self.assertEqual(result.total, len(frame))
        pd.testing.assert_frame_equal(frame, before)

    def test_empty_legacy_and_invalid_characters_do_not_invent_answers(self):
        self.assertEqual(grammar_question_progress(pd.DataFrame()).counts, (0, 0, 0, 0, 0))
        self.assertEqual(grammar_question_progress(pd.DataFrame({'prompt': ['a', 'b']})).counts,
                         (2, 0, 0, 0, 0))
        result = grammar_question_progress(pd.DataFrame({'R': ['?', '  ', 'S?S', 'SS?F', 'F S ']}))
        self.assertEqual(result.counts, (2, 1, 1, 1, 0))

    def test_cached_legacy_csv_is_read_only_and_new_answer_invalidates_progress(self):
        from app.statistics.grammar_progress import grammar_question_progress as calculate
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'Spanish_gra.csv'
            frame = pd.DataFrame({'Category': ['A', 'A', 'B'], 'R': ['', 'SF', 'SS']})
            frame.to_csv(path, sep=';', index=False)
            before = path.read_bytes()
            with patch('app.statistics.data.grammar_question_progress', wraps=calculate) as compute:
                first = training_statistics(path, 'grammar')
                second = training_statistics(path, 'grammar')
                self.assertEqual(first['question_progress'], GrammarQuestionProgress(1, 1, 0, 1, 0))
                self.assertEqual(first['question_progress'], second['question_progress'])
                self.assertEqual(compute.call_count, 1)
                self.assertEqual(path.read_bytes(), before)
                frame.loc[0, 'R'] = 'S'
                frame.to_csv(path, sep=';', index=False)
                self.assertEqual(training_statistics(path, 'grammar')['question_progress'].counts,
                                 (0, 1, 1, 1, 0))
                self.assertEqual(compute.call_count, 2)


class GrammarProgressUITests(TestCase):
    def setUp(self):
        self.root = cst.CTk()
        self.context = AppContext()
        self.root.app_context = self.context
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after', 'info'):
            self.root.tk.call('after', 'cancel', job)
        self.root.destroy()
        self.assertEqual(self.errors, [])

    def test_bars_and_record_fit_all_locales_at_narrow_and_wide_widths(self):
        progress = GrammarQuestionProgress(12, 20, 3, 1, 4)
        for locale in ('en', 'cs', 'sk', 'de', 'es', 'fr'):
            self.context.preferences = replace(self.context.preferences, app_language=locale)
            for width in (560, 1200):
                with self.subTest(locale=locale, width=width):
                    self.root.geometry(f'{width}x850')
                    record = GrammarRecordPanel(self.root, self.context.translate)
                    record.pack(fill='x')
                    record.set_record(11)
                    panel = GrammarProgressPanel(self.root, self.context.translate)
                    panel.pack(fill='x')
                    panel.set_data(progress)
                    self.root.update()
                    self.assertEqual(record.record.cget('text'),
                                     translate('All-time best streak: {count}', locale).format(count=11))
                    from app.shared.localization_format import percent
                    self.assertTrue(panel.scale.cget('text').endswith('0–' + percent(1, locale)))
                    labels = [record.record, record.description, panel.title, panel.description, panel.scale]
                    for label, value, bar in panel.rows:
                        labels.extend((label, value))
                        self.assertGreater(bar.winfo_width(), width / 2)
                    for label in labels:
                        self.assertLessEqual(label._label.winfo_reqwidth(), label.winfo_width() + 2,
                                             label.cget('text'))
                        self.assertLessEqual(label._label.winfo_reqheight(), label.winfo_height() + 2,
                                             label.cget('text'))
                    panel.destroy()
                    record.destroy()

    def test_unchanged_snapshot_does_no_widget_work_and_empty_course_clears_values(self):
        self.root.geometry('1000x750')
        panel = GrammarProgressPanel(self.root, self.context.translate)
        panel.pack(fill='x')
        progress = GrammarQuestionProgress(1, 2, 3, 4, 10)
        panel.set_data(progress)
        self.root.update()
        widgets = tuple(str(child) for child in panel.body.winfo_children())
        self.assertEqual([bar.get() for _, _, bar in panel.rows], [.05, .1, .15, .2, .5])
        with patch.object(panel.rows[0][1], 'configure') as configure, \
                patch.object(panel.rows[0][2], 'set') as set_bar:
            start = perf_counter()
            for _ in range(1000):
                panel.set_data(progress)
            elapsed = perf_counter() - start
            configure.assert_not_called()
            set_bar.assert_not_called()
        print(f'PERF grammar progress: 1000 unchanged updates {elapsed*1000:.2f} ms; no widget updates')
        panel.set_data(None)
        self.root.update()
        self.assertEqual(tuple(str(child) for child in panel.body.winfo_children()), widgets)
        self.assertTrue(all(bar.get() == 0 for _, _, bar in panel.rows))
        self.assertTrue(all(value.cget('text') == '0 · 0.0%' for _, value, _ in panel.rows))

    def test_real_grammar_tab_places_graph_last_and_switches_data_without_stale_record(self):
        from threading import get_ident
        from app.statistics.viewer import Stats
        from app.tests.test_editor_save import course
        from app.repositories.grammar_records import record_path
        self.context.preferences = replace(self.context.preferences,
            learned_by='Czech', first_language='English', second_language='Spanish')
        with TemporaryDirectory() as folder:
            self.context.files_dir = Path(folder)
            frame = course().drop(columns='Enabled')
            frame.to_csv(self.context.vocabulary_path('English'), sep=';', index=False)
            frame.rename(columns={'English': 'Spanish'}).drop(columns='Phonetic').to_csv(
                self.context.vocabulary_path('Spanish'), sep=';', index=False)
            path = self.context.grammar_path('Spanish')
            pd.DataFrame({'category': ['A', 'B', 'B'], 'R': ['SSS', 'F', '']}).to_csv(
                path, sep=';', index=False)
            record_path(path).write_text('best_streak\n11\n', encoding='utf-8')
            pd.DataFrame(columns=['category', 'R']).to_csv(
                self.context.grammar_path('English'), sep=';', index=False)
            messages = []
            main_thread, calculation_threads = get_ident(), []
            def calculated(frame):
                calculation_threads.append(get_ident())
                return grammar_question_progress(frame)
            with patch('app.ui.messagebox.showerror', side_effect=lambda *args, **kwargs: messages.append(args)), \
                    patch('app.statistics.data.grammar_question_progress', side_effect=calculated):
                window = Stats(self.root, context=self.context, language='Spanish', section='Grammar')
                def ready():
                    deadline = perf_counter() + 30
                    while not window.ready and not messages and perf_counter() < deadline:
                        self.root.update()
                    self.assertEqual(messages, [])
                    self.assertTrue(window.ready)
                try:
                    ready()
                    controller = window.controller
                    categories = controller.grammar_categories_panel
                    graph = controller.grammar_progress_panel
                    record = controller.grammar_record_panel
                    self.assertIsNot(record.master, categories)
                    self.assertEqual(graph.master, categories.master)
                    self.assertGreater(graph.grid_info()['row'], categories.grid_info()['row'])
                    self.assertEqual(graph._snapshot[0].counts, (1, 1, 0, 0, 1))
                    self.assertEqual(categories.category_count.cget('text'), 'Total categories: 2')
                    self.assertEqual(record.record.cget('text'), 'All-time best streak: 11')
                    self.assertFalse(hasattr(categories, 'record'))
                    controller.lang_var.set('English')
                    window.load(controller.load)
                    ready()
                    self.assertEqual(graph._snapshot[0].total, 0)
                    self.assertEqual(record.record.cget('text'), 'All-time best streak: 0')
                    self.assertEqual(categories.category_count.cget('text'), 'Total categories: 0')
                    self.assertEqual(len(calculation_threads), 2)
                    self.assertTrue(all(thread != main_thread for thread in calculation_threads))
                finally:
                    window.destroy()

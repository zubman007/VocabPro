"""Coverage semantics, legacy language adapters and retained UI pixels."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.statistics.conjugation import conjugation_progress
from app.statistics.data import training_statistics
from app.shared.languages import LanguagePair, language_id, legacy_name
from app.core.context import AppContext


class ConjugationProgressTests(TestCase):
    def test_whole_round_coverage_and_weighted_difficulty_preserve_input(self):
        frame = pd.DataFrame({'ID': ['001', '002', '003', '004'],
            'Spanish': ['a', 'b', 'c', 'd'], 'Description': ['present'] * 4,
            'R': ['SFFF', 'SS', '', 'F'], 's1': ['a', 'b', 'c', 'd'],
            's2': [' ', 'b2', 'c2', None]})
        original = frame.copy(deep=True)
        result = conjugation_progress(frame, 'Spanish')
        self.assertEqual((result['practised'], result['unpractised'], result['covered_forms']), (3, 1, 4))
        self.assertEqual([item.identifier for item in result['difficult']], ['004', '001'])
        self.assertEqual(result['difficult'][1].accuracy, .25)
        pd.testing.assert_frame_equal(frame, original)

    def test_empty_courses_and_bounded_ranking(self):
        empty = pd.DataFrame(columns=['ID', 'R', 'Spanish', 's1'])
        result = conjugation_progress(empty, 'Spanish')
        self.assertEqual(result, dict(practised=0, unpractised=0, covered_forms=0, difficult=[]))
        result = conjugation_progress(pd.DataFrame({'R': ['F'] * 100, 'Spanish': ['a'] * 100}), 'Spanish')
        self.assertEqual(len(result['difficult']), 10)

    def test_existing_csv_is_read_only_and_cache_invalidates_after_result(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'verbs.csv'
            frame = pd.DataFrame({'ID': ['001'], 'Spanish': ['a'], 'R': ['SF'], 's1': ['a']})
            frame.to_csv(path, sep=';', index=False)
            before = path.read_bytes()
            result = training_statistics(path, 'conjugation', 'Spanish')
            self.assertEqual(result['summary'], (1, 1, 1))
            result['progress']['difficult'].clear()
            self.assertEqual(len(training_statistics(path, 'conjugation', 'Spanish')['progress']['difficult']), 1)
            self.assertEqual(path.read_bytes(), before)
            frame['R'] = 'SFF'
            frame.to_csv(path, sep=';', index=False)
            self.assertEqual(training_statistics(path, 'conjugation', 'Spanish')['summary'], (1, 1, 2))


class LanguageAdapterTests(TestCase):
    def test_codes_and_legacy_names_resolve_to_identical_existing_files(self):
        context = AppContext()
        context.preferences = replace(context.preferences, learned_by='Czech')
        self.assertEqual(LanguagePair('Czech', 'Spanish'), LanguagePair('cs', 'es'))
        for method in ('vocabulary_path', 'tags_path', 'conjugation_path', 'theory_path', 'audio_folder', 'grammar_path'):
            self.assertEqual(getattr(context, method)('es'), getattr(context, method)('Spanish'))
        for code in ('cs', 'en', 'es', 'de', 'fr', 'sk'):
            self.assertEqual(language_id(legacy_name(code)), code)
        with self.assertRaises(ValueError): LanguagePair('es', 'Spanish')
        with self.assertRaises(KeyError): language_id('unknown')

    def test_testing_preferences_resolve_by_language_not_selected_position(self):
        config = replace(AppContext().preferences, learned_by='Czech',
            context_probabilities=(10, 20), audio_probabilities=(30, 40))
        self.assertEqual(config.testing_probabilities('es'), (10, 30))
        self.assertEqual(config.testing_probabilities('English'), (20, 40))
        self.assertEqual([pair.target for pair in config.language_pairs], ['es', 'en'])
        disabled = replace(config, second_language_enabled=False)
        self.assertEqual(len(disabled.language_pairs), 1)
        with self.assertRaises(ValueError): disabled.testing_probabilities('English')


class RetainedStatisticsTests(TestCase):
    def setUp(self):
        import customtkinter as cst
        self.root = cst.CTk()
        self.root.geometry('900x600')

    def tearDown(self):
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy()

    def test_unchanged_surface_emits_no_canvas_mutations_but_redraw_invalidates(self):
        import customtkinter as cst
        from app.ui.surfaces import surface
        from app.tests.ui_helpers import solid_surface
        card = cst.CTkFrame(self.root, width=800, height=200)
        card.pack()
        panel = surface(card, solid_surface(self.root, '#eeeeee'))
        self.root.update()
        panel.paint()
        with patch.object(panel.canvas, 'itemconfigure') as configure, patch.object(panel.canvas, 'coords') as coords:
            for _ in range(20): panel.paint()
            configure.assert_not_called()
            coords.assert_not_called()
            card._draw()
            panel.paint()
            self.assertTrue(configure.called)

    def test_unchanged_chart_retains_figure_changed_data_releases_it(self):
        import customtkinter as cst
        from app.statistics.charts import Generate_chart
        host = cst.CTkFrame(self.root)
        data = pd.Series([1, 2], index=[0, 1])
        Generate_chart(data, host, 'Vocabulary trailing successes', 0)
        self.root.update()
        canvas = host._chart_canvas
        with patch.object(canvas, 'draw_idle') as draw:
            from time import perf_counter
            start = perf_counter()
            Generate_chart(data.copy(), host, 'Vocabulary trailing successes', 0)
            retained = perf_counter() - start
            self.assertIs(host._chart_canvas, canvas)
            draw.assert_not_called()
        start = perf_counter()
        Generate_chart(data * 2, host, 'Vocabulary trailing successes', 0)
        rebuilt = perf_counter() - start
        print(f'PERF chart update: retained {retained*1000:.2f} ms; rebuilt {rebuilt*1000:.2f} ms (construction only)')
        self.assertIsNot(host._chart_canvas, canvas)
        self.assertFalse(canvas.get_tk_widget().winfo_exists())

    def test_conjugation_section_loads_new_metrics_from_legacy_csv(self):
        from app.statistics.viewer import Stats
        from app.preferences.data import RuntimePreferences
        from app.tests.test_preferences_data import sample_preferences
        from app.tests.test_editor_save import course
        from time import perf_counter
        with TemporaryDirectory() as folder:
            config = RuntimePreferences.from_frame(sample_preferences())
            context = AppContext(files_dir=Path(folder), preferences=config)
            frame = course().rename(columns={'English': 'Spanish'})
            frame.to_csv(context.vocabulary_path('Spanish'), sep=';', index=False)
            pd.DataFrame({'ID': ['001'], 'Spanish': ['hablar'], 'Description': ['present'],
                'R': ['SF'], 'LR': [''], 's1': ['hablo']}).to_csv(context.conjugation_path('Spanish'), sep=';', index=False)
            window = Stats(self.root, context=context, section='Conjugation')
            deadline = perf_counter() + 20
            try:
                while not window.ready and window.winfo_exists() and perf_counter() < deadline:
                    self.root.update()
                self.assertTrue(window.ready)
                self.assertEqual(window.statistics_tabs.selected, 'Conjugation')
                controller = window.controller
                self.assertEqual(controller.conjugation_progress.values['practised'].cget('text'), '1')
                self.assertEqual(len(controller.conjugation_table.frame), 1)
                self.assertEqual(controller.conjugation_table.frame.iloc[0, -1], 50)
            finally:
                window.destroy()

"""Horizontal distribution, canonical filters, navigation and chart corners."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.repositories.part_of_speech_lessons import part_of_speech_lesson
from app.shared.translations import LANGUAGES, translate
from app.statistics.parts_of_speech import PartsOfSpeechPanel
from app.statistics.viewer import _practise_part_of_speech
from app.tests.test_editor_save import course


def distribution():
    counts = pd.DataFrame({'Real': [2, 0, 1], 'Ideal': [1, 1, 1]}, index=['Noun', 'Verb', 'Adverb'])
    percentages = counts / 3 * 100
    return [percentages, counts]


class PartOfSpeechLessonTests(TestCase):
    def test_read_only_exact_category_selection_keeps_ids_histories_and_schedule_order(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'Czech_English_voc.csv'
            frame = pd.concat([course().assign(ID=identifier, **{'Part of Speech': kind,
                'Repetition': history, 'Next repetition': day}) for identifier, kind, history, day in (
                    (1, 'Noun', '', '2026-11-20'), (2, 'Verb', 'SF', '2026-01-01'),
                    (3, 'Noun', 'SSSSSF', '2026-11-10'))], ignore_index=True)
            frame.to_csv(path, sep=';', index=False)
            before = path.read_bytes()
            result = part_of_speech_lesson(path, 'Noun')
            self.assertEqual(result.ID.astype(int).tolist(), [3, 1])
            self.assertEqual(result.Repetition.tolist(), ['SSSSSF', ''])
            self.assertEqual(result['Part of Speech'].tolist(), ['Noun', 'Noun'])
            self.assertEqual(result.Custom.tolist(), ['007;keep', '007;keep'])
            self.assertTrue(result.attrs['ordered_lesson'])
            self.assertTrue(part_of_speech_lesson(path, 'Adverb').empty)
            self.assertEqual(path.read_bytes(), before)


class PartOfSpeechUiTests(TestCase):
    def setUp(self):
        self.root = cst.CTk(); self.root.geometry('1200x650')
        self.context = AppContext(preferences=replace(AppContext().preferences, learned_by='Czech'))
        self.context.bind(self.root)
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)

    def tearDown(self):
        for child in tuple(self.root.winfo_children()): child.destroy()
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy()
        self.assertEqual(self.errors, [])

    def test_localized_horizontal_rows_buttons_and_equal_data_reuse(self):
        for language in LANGUAGES:
            self.context.preferences = replace(self.context.preferences, app_language=language)
            clicked = []
            panel = PartsOfSpeechPanel(self.root, self.context.translate, clicked.append)
            panel.pack(fill='x', padx=20, pady=20)
            panel.set_data(distribution()); self.root.update()
            noun, _, button = panel.rows['Noun']
            self.assertAlmostEqual(noun['Real'].get(), 2/3)
            self.assertAlmostEqual(noun['Ideal'].get(), 1/3)
            self.assertGreater(noun['Real'].winfo_width(), noun['Real'].winfo_height() * 5)
            self.assertEqual(panel.rows['Verb'][2].cget('state'), 'disabled')
            button.invoke(); panel.rows['Adverb'][2].invoke()
            self.assertEqual(clicked, ['Noun', 'Adverb'])
            for _, _, action in panel.rows.values():
                self.assertEqual(action.cget('text'), translate('Repeat', language))
                self.assertLessEqual(action._text_label.winfo_reqwidth(), action.winfo_width() + 2)
                self.assertLessEqual(action.winfo_rootx() + action.winfo_width(), panel.winfo_rootx() + panel.winfo_width() - 20)
            with patch.object(noun['Real'], 'set') as update:
                panel.set_data([frame.copy() for frame in distribution()])
                update.assert_not_called()
            panel.set_data([frame.iloc[:1] for frame in distribution()])
            self.assertEqual(list(panel.rows), ['Noun'])
            panel.destroy()

    def test_launch_uses_current_language_and_returns_to_vocabulary_statistics(self):
        window = cst.CTkToplevel(self.root)
        window.app_context = self.context
        window._statistics_language = cst.StringVar(value='English')
        self.context.on_home = Mock()
        selected = course()
        with patch('app.repositories.part_of_speech_lessons.part_of_speech_lesson', return_value=selected) as lesson, \
                patch('app.vocabulary.practise.Rep', return_value=object()) as practice:
            _practise_part_of_speech(window, 'Noun')
        lesson.assert_called_once_with(self.context.vocabulary_path('English'), 'Noun')
        self.assertIs(practice.call_args.args[1], selected)
        self.assertEqual(practice.call_args.args[2:4], ('English', 2))
        self.assertFalse(window.winfo_exists())
        with patch('app.statistics.viewer.Stats') as reopen:
            practice.call_args.kwargs['on_back']()
        self.context.on_home.assert_called_once()
        reopen.assert_called_once_with(self.root, context=self.context, language='English', section='Vocabulary')

    def test_no_lesson_or_busy_window_does_not_close_statistics(self):
        window = cst.CTkToplevel(self.root); window.app_context = self.context
        window._statistics_language = cst.StringVar(value='Spanish')
        with patch('app.repositories.part_of_speech_lessons.part_of_speech_lesson', return_value=course().iloc[:0]) as lesson, \
                patch('app.vocabulary.practise.Rep') as practice:
            window._building = True
            _practise_part_of_speech(window, 'Noun'); lesson.assert_not_called()
            window._building = False
            _practise_part_of_speech(window, 'Noun'); practice.assert_not_called()
        self.assertTrue(window.winfo_exists())
        self.assertFalse(window._opening_practice)

    def test_rectangular_charts_stay_inside_scaled_rounded_corners(self):
        from app.statistics.charts import Generate_chart
        host = cst.CTkFrame(self.root); host.pack(fill='both', expand=True)
        frame = cst.CTkFrame(host)
        Generate_chart(pd.Series([1, 2]), frame, 'Vocabulary trailing successes', 0)
        for scale in (1, 1.5):
            cst.set_widget_scaling(scale); self.root.update()
            inset = round(frame.cget('corner_radius') * frame._get_widget_scaling())
            canvas = frame._chart_canvas.get_tk_widget()
            self.assertGreaterEqual(canvas.winfo_x(), inset)
            self.assertGreaterEqual(canvas.winfo_y(), inset)
        cst.set_widget_scaling(1)

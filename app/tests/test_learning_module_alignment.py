"""Aligned learning controls, lossless category switching and header geometry."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest import TestCase
from unittest.mock import Mock, patch
import pandas as pd

from app.tests import test_conjugation_persons_ui as fixtures
from app.tests.test_conjugation_model import verbs
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_training_sessions import question
from app.preferences.data import RuntimePreferences, with_defaults, validate_preferences, PreferenceError
from app.repositories import conjugation_filters, grammar_filters
from app.repositories.preferences import load_preferences, save_preferences
from app.repositories.practice_records import update_records, record_path
from app.conjugation.categories import category_ids
from app.conjugation.practise import Conjugation
from app.grammar.session import GrammarSession


class LearningSettingsTests(TestCase):
    def test_effective_record_visibility_requires_both_options_without_losing_stored_choice(self):
        prefs = RuntimePreferences.from_frame(sample_preferences())
        for tracking in (False, True):
            for showing in (False, True):
                configured = replace(prefs, track_personal_records=tracking, show_personal_records=showing)
                self.assertEqual(configured.records_visible, tracking and showing)
                self.assertEqual(configured.show_personal_records, showing)

    def test_grammar_batch_defaults_validates_and_restarts_over_the_full_filtered_pool(self):
        frame = sample_preferences()
        self.assertEqual(RuntimePreferences.from_frame(frame).grammar_batch, 10)
        defaults = with_defaults(frame)
        for invalid in ('0', '-1', '1.5', ''):
            with self.subTest(value=invalid), self.assertRaises(PreferenceError):
                validate_preferences(defaults, {'Random repeat batch - Grammar': invalid})
        state = GrammarSession([question(str(i)) for i in range(40)], batch_size=7)
        self.assertEqual(state.round_size, 7)
        seen = set()
        while state.advance() is not None:
            seen.add(state.current['id'])
            state.answer(state.options.index('yes'))
        self.assertEqual(len(seen), 7)
        self.assertEqual(len(state.progress), 7)
        state.restart()
        self.assertEqual((state.round_size, len(state.remaining), len(state.questions)), (7, 7, 40))
        self.assertEqual(len(state.progress), 7)

    def test_filters_keep_case_sensitive_ids_modules_pairs_and_concurrent_settings_separate(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.csv'
            original = sample_preferences()
            original.to_csv(path, sep=';', index=False)
            grammar_filters.save_filter(path, 'Czech', 'English', {'verbs'}, {'verbs', 'articles'})
            conjugation_filters.save_filter(path, 'Czech', 'English', {'Stable-ID'}, {'Stable-ID', 'other', ''})
            save_preferences(original, {'Learn batch': '12'}, path)
            self.assertEqual(grammar_filters.load_filter(path, 'Czech', 'English', {'verbs', 'articles'}), {'verbs'})
            self.assertEqual(conjugation_filters.load_filter(path, 'Czech', 'English', {'Stable-ID', 'other', ''}), {'Stable-ID'})
            self.assertIsNone(conjugation_filters.load_filter(path, 'German', 'English', {'Stable-ID'}))
            self.assertIsNone(conjugation_filters.load_filter(path, 'Czech', 'Spanish', {'Stable-ID'}))
            self.assertIsNone(conjugation_filters.load_filter(path, 'Czech', 'English', {'removed'}))
            self.assertFalse(load_preferences(path).Name.duplicated().any())

    def test_all_categories_remove_saved_restriction_and_include_future_categories(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.csv'
            conjugation_filters.save_filter(path, 'Czech', 'English', {''}, {'', 'named'})
            self.assertEqual(conjugation_filters.load_filter(path, 'Czech', 'English', {'', 'named'}), {''})
            conjugation_filters.save_filter(path, 'Czech', 'English', {'', 'named'}, {'', 'named'})
            self.assertIsNone(conjugation_filters.load_filter(path, 'Czech', 'English', {'', 'named', 'new'}))


class LearningAlignmentUiTests(TestCase):
    def test_destroyed_spreadsheet_releases_redraw_and_tooltip_timers(self):
        from app.ui.components.spreadsheet import Spreadsheet
        sheet=Spreadsheet(self.root)
        callback=Mock()
        jobs=[]
        for owner,attribute in ((sheet,'after_redraw_id'),(sheet.MT,'tooltip_after_id'),
                                (sheet.CH,'tooltip_after_id'),(sheet.RI,'tooltip_after_id')):
            job=owner.after(1000,callback)
            setattr(owner,attribute,job);jobs.append(job)
        sheet.destroy();self.root.update()
        self.assertFalse(set(jobs)&set(self.root.tk.call('after','info')))
        callback.assert_not_called()

    def setUp(self):
        fixtures.ConjugationPersonsUiTests.setUp(self)
        errors = patch('app.ui.messagebox.showerror', side_effect=lambda *a, **k: self.fail(str(k)))
        errors.start(); self.addCleanup(errors.stop)

    tearDown = fixtures.ConjugationPersonsUiTests.tearDown

    def lesson(self):
        frame = pd.concat([verbs().assign(ID=str(i), R='', Description=('Alpha' if i < 2 else 'Beta')+', regular')
                           for i in range(4)], ignore_index=True)
        frame.to_csv(self.path, sep=';', index=False)
        controller = Conjugation(self.root, 'es', context=self.context)
        self.root.update()
        return controller

    def answer(self, controller):
        controller.view.variables['s1'].set('enseño')
        controller.view.variables['s2'].set('enseñas')
        controller.confirm()

    def test_persons_only_in_editor_and_settings_record_control_depends_on_tracking(self):
        from app import main
        from app.preferences.dialog import PreferencesDialog
        from app.conjugation.editor import Edit_conjugation
        import customtkinter as cst
        main.main_proc(self.root, self.context)
        def buttons(widget):
            for child in widget.winfo_children():
                if isinstance(child, cst.CTkButton):yield child.cget('text')
                yield from buttons(child)
        self.assertNotIn(self.context.translate('Grammatical persons'), list(buttons(self.root)))
        dialog = PreferencesDialog(self.root, self.context.translate, self.settings)
        self.assertNotIn(self.context.translate('Grammatical persons'), list(buttons(dialog)))
        self.assertIn('Random repeat batch - Grammar', dialog.fields)
        self.assertIn('Remember conjugation categories', dialog.fields)
        dialog.variables['Track personal records'].set('0')
        self.assertEqual(dialog.fields['Show personal records'].cget('state'), 'disabled')
        dialog.variables['Track personal records'].set('1')
        self.assertEqual(dialog.fields['Show personal records'].cget('state'), 'normal')
        dialog.destroy()
        editor = Edit_conjugation(self.root, 'es', context=self.context)
        self.assertIn('persons', editor.view.tools.buttons)
        self.assertNotIn('apply', editor.view.tools.buttons)
        self.assertIs(editor.view.filters.master, editor.view.header)
        self.assertIs(editor.view.tabs.master, editor.view.header)
        editor.view.tabs.set(self.context.translate('Categories')); self.root.update()
        self.assertTrue(editor.view.category_sheet.winfo_ismapped())
        self.assertFalse(editor.view.sheet.winfo_ismapped())

    def test_new_language_enables_conjugation_and_restored_language_keeps_previous_choice(self):
        from app.preferences.course_editor import CourseEditor
        from app.preferences.courses import StudyCourse
        panel = CourseEditor(self.root, self.context.translate, lambda: 'cs',
                             [StudyCourse('es', conjugation_enabled=False)])
        panel.add_course()
        self.assertEqual(panel.rows[-1]['conjugation'].get(), '1')
        row = panel.rows[-1]
        row['target'].set(self.context.translate('German')); panel._target_changed(row)
        self.assertEqual(row['conjugation'].get(), '1')
        self.assertEqual(panel.rows[0]['conjugation'].get(), '0')
        panel.destroy()

    def test_switching_categories_retains_unsaved_answers_and_saves_each_history_once(self):
        controller = self.lesson()
        before = self.path.read_bytes()
        mapping = dict(zip(controller.source.ID, category_ids(controller.source, controller.catalog)))
        first = str(controller.session.current.id)
        other = set(mapping.values()) - {mapping[first]}
        self.answer(controller)
        self.assertTrue(controller.apply_filter(other))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertIn(mapping[str(controller.session.current.id)], other)
        second = str(controller.session.current.id)
        self.answer(controller)
        self.assertTrue(controller.save(close=False))
        saved = pd.read_csv(self.path, sep=';', dtype=str, keep_default_na=False).set_index('ID')
        self.assertEqual(saved.R.to_dict(), {key: 'S' if key in (first, second) else '' for key in saved.index})
        once = self.path.read_bytes()
        self.assertTrue(controller.save(close=False))
        self.assertEqual(self.path.read_bytes(), once)
        self.assertEqual(saved.Custom.tolist(), controller.source.Custom.tolist())

    def test_remembered_verb_filter_restores_and_disabled_preference_ignores_it(self):
        controller = self.lesson()
        selected = {controller.categories[0][0]}
        self.assertTrue(controller.apply_filter(selected))
        controller.lifecycle.close()
        reopened = Conjugation(self.root, 'es', context=self.context)
        self.assertEqual(reopened.selected_categories, selected)
        reopened.lifecycle.close()
        self.context.preferences = replace(self.context.preferences, remember_conjugation_categories=False)
        unrestricted = Conjugation(self.root, 'es', context=self.context)
        self.assertEqual(len(unrestricted.selected_categories), 2)

    def test_filter_dialog_uses_verb_counts_and_enter_cannot_score_a_hidden_lesson(self):
        controller = self.lesson()
        controller.open_filter()
        dialog = controller._filter_window
        dialog.present(modal=True); self.root.update()
        self.assertEqual(dialog.title(), self.context.translate('Verb categories'))
        self.assertIn(self.context.translate('Number of verbs'), dialog.count.cget('text'))
        controller.confirm(Mock())
        self.assertEqual((controller.session.correct, controller.session.incorrect), (0, 0))
        dialog.destroy()

    def test_tracking_off_hides_repeat_and_both_statistics_records_without_deleting_saved_maxima(self):
        from app.statistics.viewer import Stats
        with update_records(self.path, 8, 12):pass
        before = record_path(self.path).read_bytes()
        self.context.preferences = replace(self.context.preferences, track_personal_records=False, show_personal_records=True)
        with patch('app.conjugation.practise.load_records', side_effect=AssertionError('tracking disabled')):
            controller = self.lesson()
        self.assertFalse(controller.view.records_panel.grid_info())
        self.answer(controller); self.assertTrue(controller.save(close=False))
        self.assertEqual(record_path(self.path).read_bytes(), before)
        window = Stats(self.root, context=self.context, language='Spanish', section='Conjugation')
        try:
            deadline = perf_counter()+30
            while not window.ready and perf_counter()<deadline:self.root.update()
            self.assertTrue(window.ready)
            self.assertFalse(window.controller.grammar_record_panel.grid_info())
            self.assertFalse(window.controller.conjugation_record_panel.grid_info())
        finally:window.destroy()

    def test_session_records_and_shortcuts_remain_separate_and_form_stays_scrollable(self):
        for locale in ('en', 'cs', 'de'):
            self.context.preferences = replace(self.context.preferences, app_language=locale)
            controller = self.lesson()
            self.root.geometry('1000x800'); self.root.update()
            view = controller.view
            self.assertIs(view.records_panel.master, view.session_panel)
            self.assertIs(view.shortcuts.master, view.session_panel)
            self.assertLessEqual(view.score.winfo_rooty()+view.score.winfo_height(), view.records_panel.winfo_rooty())
            self.assertLessEqual(view.records_panel.winfo_rooty()+view.records_panel.winfo_height(), view.shortcuts.winfo_rooty())
            self.assertNotIn(self.context.translate('Session: {correct} correct · streak {streak}').format(correct=0, streak=0), view.records.cget('text'))
            self.assertLessEqual(view.records._label.winfo_reqwidth(), view.records.winfo_width()+2)
            controller.lifecycle.close()

    def test_both_editor_tab_bars_composite_real_parent_pixels_at_rounded_corners(self):
        from app.conjugation.editor import Edit_conjugation
        from app.grammar.editor import Edit_grammar
        for open_editor in (Edit_conjugation, Edit_grammar):
            editor = open_editor(self.root, 'Spanish', context=self.context); self.root.update()
            tabs = editor.view.tabs
            layer = tabs._surface
            layer.paint()
            self.assertTrue(layer.rasterize_frame)
            expected = layer.parent.region(tabs).getpixel((0, 0))
            actual = tuple(map(int, self.root.tk.call(str(layer._photo), 'get', 0, 0)))
            self.assertEqual(actual, expected)
            self.assertEqual(tabs._canvas.itemcget('inner_parts', 'state'), 'hidden')
            editor.lifecycle.close()

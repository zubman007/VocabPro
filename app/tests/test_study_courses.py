"""N-course activation, explicit migration, independent progress and UI navigation."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.preferences.courses import (COURSE_FIELD, StudyCourse, encode_courses, decode_courses,
                                    CourseConfigurationError)
from app.preferences.data import RuntimePreferences, PreferenceError, validate_preferences, with_defaults
from app.repositories.preferences import load_preferences, save_preferences
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course


def configured(courses=None):
    return validate_preferences(sample_preferences(), {COURSE_FIELD: encode_courses('Czech', courses or (
        StudyCourse('es', True, 20, 20), StudyCourse('en', True, 20, 20), StudyCourse('fr', True, 15, 35)))})


class StudyCourseDataTests(TestCase):
    def test_legacy_adapter_is_read_only_and_retains_probabilities_and_disabled_values(self):
        frame = sample_preferences(); original = frame.copy(deep=True)
        config = RuntimePreferences.from_frame(frame)
        self.assertEqual(config.study_courses, (StudyCourse('es', True, 20, 20), StudyCourse('en', True, 20, 20)))
        self.assertEqual(replace(config, second_language_enabled=False).study_courses[1], StudyCourse('en', False, 20, 20))
        self.assertNotIn(COURSE_FIELD, frame.Name.values)
        pd.testing.assert_frame_equal(frame, original)

    def test_three_courses_resolve_paths_and_question_settings_by_identity(self):
        preferences = RuntimePreferences.from_frame(configured())
        context = AppContext(preferences=preferences)
        self.assertEqual(preferences.learning_languages, ('Spanish', 'English', 'French'))
        self.assertEqual(preferences.testing_probabilities('fr'), (15, 35))
        self.assertEqual(preferences.testing_probabilities('Spanish'), (20, 20))
        self.assertEqual(context.vocabulary_path('fr').name, 'Czech_French_voc.csv')
        self.assertEqual([pair.target for pair in preferences.language_pairs], ['es', 'en', 'fr'])
        self.assertEqual(preferences.app_language, 'English')

    def test_reorder_and_disable_preserve_per_language_settings(self):
        courses = (StudyCourse('fr', True, 15, 35), StudyCourse('es', False, 20, 20), StudyCourse('en', True, 40, 10))
        preferences = RuntimePreferences.from_frame(configured(courses))
        self.assertEqual(preferences.learning_languages, ('French', 'English'))
        self.assertEqual(preferences.testing_probabilities('en'), (40, 10))
        self.assertEqual(preferences.study_courses[1], courses[1])
        with self.assertRaises(ValueError): preferences.testing_probabilities('es')

    def test_versioned_list_is_authoritative_and_legacy_rows_are_preserved(self):
        frame = with_defaults(configured())
        changes = {'First learning language': 'English', 'Second learning language': 'Spanish',
                   'Enable second learning language': '0'}
        changed = validate_preferences(frame, changes)
        self.assertEqual(RuntimePreferences.from_frame(changed).learning_languages, ('Spanish', 'English', 'French'))
        for key, value in changes.items(): self.assertEqual(changed.set_index('Name').at[key, 'Value'], value)

    def test_bad_or_future_configuration_never_falls_back_to_two_courses(self):
        good = json.loads(encode_courses('cs', (StudyCourse('es'),)))
        bad = ['{', '', 'null', '{}', json.dumps(dict(good, version=2)),
               json.dumps(dict(good, source='en')), json.dumps(dict(good, courses=[])),
               '{"version":1,"version":1,"source":"cs","courses":[]}']
        for text in bad:
            with self.subTest(text=text), self.assertRaises(PreferenceError):
                validate_preferences(sample_preferences(), {COURSE_FIELD: text})
        wrong_type = configured()
        wrong_type.loc[wrong_type.Name.eq(COURSE_FIELD), 'Type'] = 'Str'
        with self.assertRaises(PreferenceError): validate_preferences(wrong_type, {})

    def test_invalid_targets_enabled_states_and_percentages_are_rejected(self):
        for courses in ((StudyCourse('es'), StudyCourse('es')), (StudyCourse('cs'),),
                        (StudyCourse('unknown'),), (StudyCourse('es', False),),
                        (StudyCourse('es', True, 80, 30),), (StudyCourse('es', True, -1, 20),),
                        (StudyCourse('es', True, True, 20),), (StudyCourse('es', 'yes'),)):
            with self.subTest(courses=courses), self.assertRaises((CourseConfigurationError, KeyError)):
                encode_courses('cs', courses)

    def test_disabled_legacy_excess_total_can_be_saved_but_not_enabled(self):
        courses = (StudyCourse('es'), StudyCourse('en', False, 80, 80))
        self.assertEqual(decode_courses(encode_courses('cs', courses), 'cs'), courses)
        with self.assertRaises(CourseConfigurationError):
            encode_courses('cs', (courses[0], replace(courses[1], enabled=True)))

    def test_all_registered_learning_languages_are_supported_without_slots(self):
        from app.shared.languages import LANGUAGE_CODES
        courses = tuple(StudyCourse(code) for code in LANGUAGE_CODES.values() if code != 'cs')
        preferences = RuntimePreferences.from_frame(configured(courses))
        self.assertEqual(len(preferences.learning_languages), len(LANGUAGE_CODES) - 1)
        for language in preferences.learning_languages:
            self.assertEqual(preferences.testing_probabilities(language), (0, 0))

    def test_save_reload_and_activation_leave_all_course_data_unchanged(self):
        from app.main import Load_setting
        with TemporaryDirectory() as folder:
            files = Path(folder); path = files / 'settings.csv'
            original = sample_preferences(); original['Notes'] = 'preserve metadata'
            original.to_csv(path, sep=';', index=False)
            for target in ('English', 'Spanish'):
                course().rename(columns={'English': target}).to_csv(files / f'Czech_{target}_voc.csv', sep=';', index=False)
            (files / 'Czech_English_con.csv').write_bytes(b'ID;R\n1;SSFS\n')
            audio = files / 'audio' / 'Czech_English'; audio.mkdir(parents=True)
            (audio / '1.wav').write_bytes(b'synthetic audio')
            before = {p: p.read_bytes() for p in files.rglob('*') if p.is_file() and p != path}
            context = AppContext(files_dir=files)
            legacy_bytes = path.read_bytes()
            Load_setting(context)
            self.assertEqual(path.read_bytes(), legacy_bytes)
            self.assertNotIn(COURSE_FIELD, load_preferences(path).Name.values)
            save_preferences(load_preferences(path), {COURSE_FIELD: encode_courses('cs', (
                *context.preferences.study_courses, StudyCourse('fr', True, 15, 35)))}, path)
            for enabled in (True, False, True):
                current = load_preferences(path); pref = RuntimePreferences.from_frame(current)
                courses = tuple(replace(item, enabled=enabled) if item.target == 'fr' else item for item in pref.study_courses)
                save_preferences(current, {COURSE_FIELD: encode_courses('cs', courses)}, path)
                Load_setting(context)
                self.assertEqual('French' in context.preferences.learning_languages, enabled)
                self.assertEqual(context.preferences.testing_probabilities('English'), (20, 20))
                for p, content in before.items(): self.assertEqual(p.read_bytes(), content)
            french = pd.read_csv(context.vocabulary_path('fr'), sep=';')
            self.assertTrue(french.empty)
            saved = load_preferences(path).set_index('Name')
            for row in original.itertuples(index=False):
                self.assertEqual(saved.at[row.Name, 'Value'], row.Value)
                self.assertEqual(saved.at[row.Name, 'Notes'], row.Notes)
            self.assertNotEqual(path.read_bytes(), legacy_bytes)

    def test_invalid_or_stale_save_is_atomic(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.csv'; configured().to_csv(path, sep=';', index=False)
            stale = load_preferences(path); original = path.read_bytes()
            with self.assertRaises(PreferenceError): save_preferences(stale, {COURSE_FIELD: '{}'}, path)
            self.assertEqual(path.read_bytes(), original)
            save_preferences(stale, {'Learn batch': '12'}, path)
            latest = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'Settings changed on disk'):
                save_preferences(stale, {COURSE_FIELD: encode_courses('cs', (StudyCourse('fr'),))}, path)
            self.assertEqual(path.read_bytes(), latest)

    def test_activating_preexisting_third_course_reuses_its_original_bytes(self):
        from app.main import Load_setting
        with TemporaryDirectory() as folder:
            files = Path(folder)
            configured().to_csv(files / 'settings.csv', sep=';', index=False)
            vocabulary = files / 'Czech_French_voc.csv'
            course().rename(columns={'English': 'French'}).assign(Repetition='SSFS').to_csv(vocabulary, sep=';', index=False)
            original = vocabulary.read_bytes()
            context = AppContext(files_dir=files)
            Load_setting(context)
            self.assertIn('French', context.preferences.learning_languages)
            self.assertEqual(vocabulary.read_bytes(), original)


class StudyCourseUiTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory(); self.files = Path(self.folder.name)
        self.root = cst.CTk(); self.root.geometry('1400x1000')
        self.context = AppContext(files_dir=self.files, preferences=RuntimePreferences.from_frame(configured()))
        self.context.bind(self.root); self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)

    def tearDown(self):
        for widget in tuple(self.root.winfo_children()): widget.destroy()
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy(); self.folder.cleanup()
        self.assertEqual(self.errors, [])

    def test_settings_add_third_language_and_save_canonical_ids_in_every_locale(self):
        from app.preferences.dialog import PreferencesDialog
        from app.shared.translations import LANGUAGES, translate
        path = self.files / 'settings.csv'
        for language in LANGUAGES:
            sample_preferences().to_csv(path, sep=';', index=False)
            dialog = PreferencesDialog(self.root, lambda key: translate(key, language), path)
            dialog.deiconify(); self.root.update()
            editor = dialog.course_editor
            self.assertEqual(len(editor.rows), 2)
            editor.add_button.invoke()
            row = editor.rows[2]; row['target'].set(translate('French', language))
            row['context'].set('15'); row['audio'].set('35')
            dialog.save()
            self.assertTrue(dialog.saved)
            pref = RuntimePreferences.from_frame(load_preferences(path))
            self.assertEqual(pref.learning_languages, ('Spanish', 'English', 'French'))
            self.assertEqual(pref.testing_probabilities('fr'), (15, 35))
            self.assertEqual(json.loads(load_preferences(path).set_index('Name').at[COURSE_FIELD, 'Value'])['source'], 'cs')

    def test_home_selector_invokes_third_course_and_keeps_only_selected_card_visible(self):
        from app.main import _build_main_window
        rows = pd.DataFrame({'ID': [1]})
        data = dict(rep_words=rows, lrn_words=rows, rep_count=1, lrn_count=1, all_count=1, gra_count=0, con_count=0)
        body = _build_main_window(self.root, dict.fromkeys(self.context.preferences.learning_languages, data), self.context)
        self.root.update()
        body.course_selector._dropdown_callback(self.context.translate('French')); self.root.update()
        self.assertEqual(body.course_selector.get(), self.context.translate('French'))
        self.assertEqual([name for name, card in body.course_cards.items() if card.winfo_ismapped()], ['French'])
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        repeat = next(widget for widget in descendants(body.course_cards['French'])
                      if isinstance(widget, cst.CTkButton) and widget.cget('text') == self.context.translate('Repeat'))
        with patch('app.vocabulary.practise.Rep') as practice:
            repeat.invoke()
            self.assertEqual(practice.call_args.args[2:], ('French', 3))
        self.assertLess(body.course_cards['French'].winfo_rootx() + body.course_cards['French'].winfo_width(),
                        body.winfo_rootx() + body.winfo_width())
        body.destroy()
        restored = _build_main_window(self.root, dict.fromkeys(self.context.preferences.learning_languages, data), self.context)
        self.assertEqual(restored.course_selector.get(), self.context.translate('French'))

    def test_statistics_selects_third_course_without_changing_its_history(self):
        from app.statistics.viewer import Stats
        for target in self.context.preferences.learning_languages:
            data = course().rename(columns={'English': target})
            data.to_csv(self.context.vocabulary_path(target), sep=';', index=False)
        before = {path: path.read_bytes() for path in self.files.glob('*.csv')}
        with patch('app.statistics.viewer.Generate_chart'):
            window = Stats(self.root, context=self.context, language='French')
            try:
                deadline = monotonic() + 25
                while not window.ready and monotonic() < deadline: self.root.update(); sleep(.005)
                self.assertTrue(window.ready)
                self.assertEqual(window.controller.lang_var.get(), 'French')
                self.assertEqual(window.controller.language_switch.cget('values'),
                                 [self.context.translate(name) for name in self.context.preferences.learning_languages])
                self.assertEqual(int(window.controller.tot_res_voc_lbl.cget('text')), len(course()))
            finally: window.destroy()
        for path, content in before.items(): self.assertEqual(path.read_bytes(), content)

    def test_real_third_course_practice_uses_its_settings_and_saves_only_its_history(self):
        from app.vocabulary.practise import PracticeController
        self.context.preferences = replace(self.context.preferences, autoplay_pronunciation=False)
        french = course().rename(columns={'English': 'French'})
        french.to_csv(self.context.vocabulary_path('fr'), sep=';', index=False)
        english = self.context.vocabulary_path('en')
        course().to_csv(english, sep=';', index=False)
        original = english.read_bytes()
        with patch('app.vocabulary.practise.messagebox.showerror', side_effect=AssertionError('Unexpected practice error')):
            controller = PracticeController(self.root, french, 'French', 3, context=self.context, on_back=lambda: None)
            try:
                self.root.update()
                self.assertEqual(controller.test_weights, (.5, .15, .35))
                self.assertEqual(controller.audio.folder, self.context.audio_folder('fr'))
                controller.session.fail(1)
                self.assertTrue(controller.Save_rep('', close=False))
                saved = pd.read_csv(self.context.vocabulary_path('fr'), sep=';', keep_default_na=False)
                self.assertEqual(saved.Repetition.tolist(), ['SFF'])
                self.assertEqual(saved.Custom.tolist(), ['007;keep'])
                self.assertEqual(english.read_bytes(), original)
            finally:
                controller.lifecycle.close(); controller.rep_frm.destroy()

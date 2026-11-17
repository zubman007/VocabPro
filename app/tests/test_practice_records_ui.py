"""Settings, controller persistence, hiding and record cards with real Tk widgets."""
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch
from app.tests import test_grammar_session_insight as fixtures
from app.repositories.practice_records import PracticeRecords, load_records, update_records, record_path
from app.conjugation.practise import ConjugationController
from app.conjugation.data import Verb
import pandas as pd
import customtkinter as cst


from unittest import TestCase
class PersonalRecordsUiTests(TestCase):
    setUp=fixtures.SessionInsightUiTests.setUp
    tearDown=fixtures.SessionInsightUiTests.tearDown
    lesson=fixtures.SessionInsightUiTests.lesson
    settle=fixtures.SessionInsightUiTests.settle

    def test_grammar_maxima_survive_round_reset_but_do_not_add_rounds(self):
        controller=self.lesson()
        for _ in range(3):
            controller.choose(controller.session.options.index('yes'));controller.next_question()
        controller.restart()
        for _ in range(2):
            controller.choose(controller.session.options.index('yes'));controller.next_question()
        with patch('app.grammar.practise.save_answers'):
            self.assertTrue(controller.save(close=False))
        self.assertEqual(load_records(controller.path),PracticeRecords(3,3))

    def test_tracking_off_preserves_existing_records_and_still_saves_answers(self):
        path=Path(self.directory.name)/'English_gra.csv'
        with update_records(path,2,4):pass
        before=record_path(path).read_bytes()
        self.context.preferences=replace(self.context.preferences,track_personal_records=False)
        controller=self.lesson();controller.choose(controller.session.options.index('yes'))
        with patch('app.grammar.practise.save_answers') as save:
            self.assertTrue(controller.save(close=False));save.assert_called_once()
        self.assertEqual(record_path(path).read_bytes(),before)
        self.assertIn('4',controller.view.score.cget('text'))

    def test_display_off_keeps_tracking_and_hides_record_text(self):
        self.context.preferences=replace(self.context.preferences,show_personal_records=False)
        controller=self.lesson();controller.choose(controller.session.options.index('yes'))
        self.assertNotIn(self.context.translate('All-time best streak: {count}').format(count=1),controller.view.score.cget('text'))
        with patch('app.grammar.practise.save_answers'):self.assertTrue(controller.save(close=False))
        self.assertEqual(load_records(controller.path),PracticeRecords(1,1))

    def conjugation(self):
        path=Path(self.directory.name)/'Czech_English_con.csv'
        frame=pd.DataFrame({'ID':['1','2'],'R':['',''],'LR':['',''],'s1':['form','form']})
        frame.to_csv(path,sep=';',index=False)
        verbs=[Verb(key,forms={'s1':'form'}) for key in frame.ID]
        return ConjugationController(self.root,frame,frame,verbs,(('s1','I'),),path,Mock(),context=self.context)

    def test_conjugation_failed_save_rolls_back_records_and_retry_counts_once(self):
        controller=self.conjugation();controller.view.variables['s1'].set('form');controller.confirm()
        self.assertEqual(controller.session.correct,1)
        with patch('app.conjugation.practise.save_results',side_effect=PermissionError()),patch('app.ui.messagebox.showerror'):
            self.assertFalse(controller.save(close=False))
        self.assertFalse(record_path(controller.path).exists())
        self.assertTrue(controller.save(close=False));self.assertTrue(controller.save(close=False))
        self.assertEqual(load_records(controller.path),PracticeRecords(1,1))
        controller.view.variables['s1'].set('wrong');controller.confirm()
        controller.confirm()  # Confirm revealed solution, automatically save/end.
        self.assertEqual(load_records(controller.path),PracticeRecords(1,1))

    def test_conjugation_both_switches_off_records_stay_absent(self):
        self.context.preferences=replace(self.context.preferences,show_personal_records=False,track_personal_records=False)
        controller=self.conjugation();self.settle()
        self.assertFalse(controller.view.records.winfo_ismapped())
        controller.view.variables['s1'].set('form');controller.confirm();controller.save(close=False)
        self.assertFalse(record_path(controller.path).exists())

    def test_cards_fit_long_translations_and_retain_unchanged_values(self):
        from app.statistics.grammar_progress_panel import GrammarRecordPanel
        for locale in ('en','cs','sk','de','es','fr'):
            self.context.preferences=replace(self.context.preferences,app_language=locale)
            self.root.geometry('600x850')
            panel=GrammarRecordPanel(self.root,self.context.translate,description='Conjugation records explanation')
            panel.pack(fill='x');panel.set_record(12,24);self.settle()
            for label in (panel.record,panel.correct,panel.description):
                self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2)
            with patch.object(panel.correct,'configure') as update:
                panel.set_record(12,24);update.assert_not_called()
            panel.set_record(12,None);self.assertIn('—',panel.correct.cget('text'));panel.destroy()

    def test_settings_switches_are_global_and_save_in_learning(self):
        from app.preferences.dialog import PreferencesDialog
        from app.tests.test_preferences_data import sample_preferences
        from app.repositories.preferences import load_preferences
        path=Path(self.directory.name)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
        dialog=PreferencesDialog(self.root,self.context.translate,path)
        for name in ('Track personal records','Show personal records'):
            self.assertEqual(dialog.field_sections[name],self.context.translate('Learning'))
            dialog.variables[name].set('0')
        dialog.save();self.assertTrue(dialog.saved)
        saved=load_preferences(path).set_index('Name').Value
        self.assertEqual((saved['Track personal records'],saved['Show personal records']),('0','0'))

    def test_real_statistics_load_both_records_and_hide_restore_without_stale_values(self):
        from time import perf_counter
        from app.preferences.courses import StudyCourse
        from app.repositories.course_files import ensure_course_files
        from app.statistics.viewer import Stats
        self.context.preferences=replace(self.context.preferences,learned_by='Czech',
            courses=(StudyCourse('en',conjugation_enabled=True),StudyCourse('es',conjugation_enabled=True)))
        ensure_course_files(self.context.files_dir,'cs',self.context.preferences.courses)
        with update_records(self.context.grammar_path('en'),7,9):pass
        with update_records(self.context.conjugation_path('en'),2,4):pass
        errors=[]
        with patch('app.ui.messagebox.showerror',side_effect=lambda *a,**k:errors.append(k)):
            window=Stats(self.root,context=self.context,language='English',section='Conjugation')
            def ready():
                deadline=perf_counter()+30
                while not window.ready and not errors and perf_counter()<deadline:self.root.update()
                self.assertEqual(errors,[]);self.assertTrue(window.ready)
            try:
                ready();controller=window.controller
                self.assertIn('9',controller.grammar_record_panel.correct.cget('text'))
                self.assertIn('4',controller.conjugation_record_panel.correct.cget('text'))
                self.context.preferences=replace(self.context.preferences,show_personal_records=False)
                window.load(controller.load);ready()
                self.assertFalse(controller.grammar_record_panel.grid_info())
                self.assertFalse(controller.conjugation_record_panel.grid_info())
                self.context.preferences=replace(self.context.preferences,show_personal_records=True)
                controller.lang_var.set('Spanish');window.load(controller.load);ready()
                self.assertTrue(controller.conjugation_record_panel.grid_info())
                self.assertIn('—',controller.conjugation_record_panel.correct.cget('text'))
                self.assertIn('—',controller.grammar_record_panel.correct.cget('text'))
            finally:window.destroy()

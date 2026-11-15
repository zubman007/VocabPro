"""Tag settings, direct filtering and statistics return paths on synthetic courses."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences, TAG_DEPENDENT_FIELDS, group_for, with_defaults
from app.preferences.dialog import PreferencesDialog
from app.shared.translations import LANGUAGES, get_catalog
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.tests.test_tag_catalog import catalog
from app.repositories.tags import save_catalog
from app.vocabulary.editor import EditorController
from app.statistics.viewer import _practise_category, _practise_tag


class TagUiFollowupTests(TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory()
        self.root=cst.CTk()
        self.root.geometry('1500x950')
        self.errors=[]
        self.root.report_callback_exception=lambda *error:self.errors.append(error)
        self.context=AppContext(files_dir=Path(self.directory.name),
            preferences=replace(RuntimePreferences.from_frame(sample_preferences()),
                autoplay_pronunciation=False, tag_display_language='Student language'),on_home=Mock())
        self.context.bind(self.root)
        save_catalog(self.context.tags_path('English'),catalog(),'Czech','English',None)
        self.course=pd.concat([course().assign(ID=1,English='alpha',Tags='1'),
                               course().assign(ID=2,English='beta',Tags='3')],ignore_index=True)
        self.path=self.context.vocabulary_path('English')
        self.course.to_csv(self.path,sep=';',index=False)
        self.before=self.path.read_bytes()

    def tearDown(self):
        for job in self.root.tk.call('after','info'):
            self.root.tk.call('after','cancel',job)
        self.root.destroy()
        self.directory.cleanup()
        self.assertEqual(self.errors,[])

    def settle_filter(self):
        self.root.after(320,self.root.quit)
        self.root.mainloop()

    def test_auto_search_operator_change_and_refresh_reset_without_data_writes(self):
        editor=EditorController(self.root,'English',context=self.context)
        self.root.update()
        self.assertEqual(editor.headers.index('Tag count'),editor.headers.index('Tags')+1)
        self.assertIsNone(editor.filt_frm.apply)
        for name in ('Phonetic','Repetition','Next repetition'):
            self.assertNotIn(editor.translate(name),editor.filt_frm.column.cget('values'))
        editor.filt_col_var.set(editor.translate('English'))
        editor.filt_entry_var.set('alp')
        self.settle_filter()
        self.assertEqual(editor.filt_df.ID.tolist(),[1])
        editor.sign_var.set(editor.translate('not like'))
        self.settle_filter()
        self.assertEqual(editor.filt_df.ID.tolist(),[2])
        editor.filt_col_var.set(editor.translate('Tags'))
        editor.filt_frm.set_tag_selection('Zvířata')
        editor.Filter()
        editor.filt_frm.reset.invoke()
        self.assertEqual(editor.filt_entry_var.get(),'')
        self.assertEqual(editor.filt_frm.tag_selection,'')
        self.assertEqual(editor.filt_frm.tag_button.cget('text'),editor.translate('Select tags'))
        self.assertFalse(editor.filt_flag)
        self.settle_filter()
        self.assertFalse(editor.filt_flag)  # A stale debounce must not reapply after Refresh.
        self.assertEqual(editor.edit_tbl.get_total_rows(),2)
        self.assertEqual(self.path.read_bytes(),self.before)

    def test_empty_numeric_filter_does_not_display_error_and_debounce_closes_cleanly(self):
        editor=EditorController(self.root,'English',context=self.context)
        editor.filt_col_var.set(editor.translate('Tag count'))
        with patch('app.vocabulary.editor.messagebox.showerror') as error:
            self.settle_filter()
            error.assert_not_called()
        editor.filt_entry_var.set('2')
        self.assertIsNotNone(editor._filter_job)
        editor.edit_frm.destroy()
        self.settle_filter()
        self.assertTrue(editor.lifecycle.closed)
        self.assertEqual(self.path.read_bytes(),self.before)

    def test_tag_dependencies_keep_values_and_error_banner_fits_every_language(self):
        path=Path(self.directory.name)/'settings.csv'
        with_defaults(sample_preferences()).to_csv(path,sep=';',index=False)
        before=path.read_bytes()
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            dialog=PreferencesDialog(self.root,self.context.translate,path)
            dialog.deiconify()
            dialog.tabs.set(self.context.translate('Learning'))
            dialog.variables['App sound volume'].set('37')
            dialog.variables['App sounds enabled'].set('0')
            self.assertEqual(dialog.fields['App sound volume'].cget('state'),'disabled')
            self.assertEqual(dialog.variables['App sound volume'].get(),'37')
            dialog.variables['App sounds enabled'].set('1')
            self.assertEqual(dialog.fields['App sound volume'].cget('state'),'normal')
            self.assertEqual(dialog.variables['App sound volume'].get(),'37')
            original={name:dialog.variables[name].get() for name in TAG_DEPENDENT_FIELDS}
            dialog.variables['Enable tags'].set('0')
            for name in TAG_DEPENDENT_FIELDS:
                self.assertEqual(dialog.fields[name].cget('state'),'disabled')
                self.assertEqual(dialog.variables[name].get(),original[name])
            dialog.variables['Enable tags'].set('1')
            for name in TAG_DEPENDENT_FIELDS:
                self.assertEqual(dialog.fields[name].cget('state'),'normal')
                self.assertEqual(dialog.variables[name].get(),original[name])
            dialog.variables['Maximum tags per word'].set('0')
            dialog.save()
            self.root.update()
            self.assertFalse(dialog.saved)
            self.assertEqual(dialog.error_panel.winfo_manager(),'grid')
            self.assertEqual(dialog.error_panel.cget('corner_radius'),14)
            self.assertEqual(dialog.error.cget('fg_color'),'transparent')
            self.assertLessEqual(dialog.error._label.winfo_reqwidth(),dialog.error.winfo_width()+2)
            self.assertEqual(path.read_bytes(),before)
            titles=[label.cget('text') for label in dialog.group_headers]
            self.assertIn(self.context.translate('Tags'),titles)
            self.assertEqual(titles.count(self.context.translate('Vocabulary')),1)
            dialog.destroy()

    def test_new_group_titles_exist_in_every_catalog(self):
        for language in LANGUAGES:
            for name in ('Settings general','Settings sounds'):
                self.assertTrue(get_catalog(language).get(name))
        self.assertEqual(group_for('Enable tags'),'Tags')
        self.assertEqual(group_for('Remember grammar categories'),'Grammar')
        self.assertEqual(group_for('Random repeat batch - Conjugation'),'Conjugation')

    def test_grammar_category_close_reopens_statistics_at_its_language_and_tab(self):
        window=cst.CTkToplevel(self.root)
        window._statistics_language=cst.StringVar(value='English')
        with patch('app.grammar.practise.Grammar_training') as launch:
            _practise_category(window,'Tenses')
        callback=launch.call_args.kwargs['on_back']
        self.assertFalse(window.winfo_exists())
        with patch('app.statistics.viewer.Stats') as stats:
            callback()
        self.context.on_home.assert_called_once()
        stats.assert_called_once_with(self.root,context=self.context,language='English',section='Grammar')

    def test_tag_close_reopens_statistics_and_failed_launch_preserves_window(self):
        window=cst.CTkToplevel(self.root)
        window._statistics_language=cst.StringVar(value='English')
        with patch('app.repositories.tag_lessons.tag_lesson',return_value=self.course), \
             patch('app.vocabulary.practise.Rep') as launch:
            _practise_tag(window,'1')
        callback=launch.call_args.kwargs['on_back']
        self.assertFalse(window.winfo_exists())
        with patch('app.statistics.viewer.Stats') as stats:
            callback()
        stats.assert_called_once_with(self.root,context=self.context,language='English',section='Vocabulary')
        window=cst.CTkToplevel(self.root)
        window._statistics_language=cst.StringVar(value='English')
        with patch('app.repositories.tag_lessons.tag_lesson',return_value=self.course.iloc[:0]), \
             patch('app.vocabulary.practise.Rep') as launch:
            _practise_tag(window,'1')
        self.assertTrue(window.winfo_exists())
        self.assertFalse(window._opening_practice)
        launch.assert_not_called()
        with patch('app.grammar.practise.Grammar_training',return_value=None):
            _practise_category(window,'Deleted topic')
        self.assertTrue(window.winfo_exists())
        window.destroy()

    def test_vocabulary_close_and_save_use_the_supplied_return_action(self):
        from app.vocabulary.practise import Rep
        for save in (False,True):
            callback=Mock()
            with patch('app.vocabulary.practise.PracticeAudio'), \
                 patch('app.vocabulary.practise.play_effect'), \
                 patch('app.vocabulary.practise.save_practice') as persist:
                controller=Rep(self.root,self.course,'English',2,context=self.context,on_back=callback)
                self.root.update()
                if save:controller.Save_rep('')
                else:controller.Back()
                callback.assert_called_once()
                self.assertEqual(persist.call_count,int(save))
                self.assertTrue(controller.lifecycle.closed)
            self.assertEqual(self.path.read_bytes(),self.before)

    def test_real_statistics_window_resumes_second_language_and_grammar_tab(self):
        from time import monotonic,sleep
        from app.statistics.viewer import Stats
        # StatisticsTable lists learned words only (more than four S records).
        self.course.assign(Repetition='SSSSSF').to_csv(self.path,sep=';',index=False)
        before=self.path.read_bytes()
        self.context.preferences=replace(self.context.preferences,first_language='Spanish',second_language='English')
        with patch('app.statistics.viewer.Generate_chart'):
            window=Stats(self.root,context=self.context,language='English',section='Grammar')
            deadline=monotonic()+15
            while not window.ready and monotonic()<deadline:
                self.root.update()
                sleep(.005)
            self.assertTrue(window.ready)
            self.assertEqual(window._statistics_language.get(),'English')
            self.assertEqual(window.statistics_tabs.selected,'Grammar')
            self.assertEqual(window.controller.df.shape[0],2)
            window.destroy()
        self.assertEqual(self.path.read_bytes(),before)

    def test_difficult_words_keep_all_information_in_compact_rows(self):
        from app.statistics.difficult_words import DifficultWordsPanel,DifficultWord
        panel=DifficultWordsPanel(self.root,self.context.translate)
        panel.pack(fill='x')
        panel.set_items([DifficultWord('example','translation','SFFSSSSSSS')]*6,63)
        self.root.update()
        self.assertEqual(len(panel.rows.winfo_children()),6)
        self.assertEqual(panel.count.cget('text'),'63')
        self.assertLess(panel.winfo_height()/panel._get_widget_scaling(),630)
        for row in panel.rows.winfo_children():
            captions=[w.cget('text') for w in row.winfo_children() if isinstance(w,cst.CTkLabel)]
            self.assertIn('example',captions)
            self.assertIn('translation',captions)
            self.assertTrue(any('2/10' in value and '20%' in value for value in captions))

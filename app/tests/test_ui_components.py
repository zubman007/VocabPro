"""Contracts and focused integration checks for shared UI components."""
import unittest
from unittest.mock import Mock
import customtkinter as cst
from app.ui.components.session_panel import SessionPanel
from app.ui.components.editor_toolbar import EditorToolbar
from app.ui.components.search_filter_panel import SearchFilterPanel
from app.ui.components.app_dialog import AppDialog


class ComponentTests(unittest.TestCase):
    def test_filter_arrow_is_one_continuous_line_and_tracks_state_and_resize(self):
        from tkinter import Canvas
        from app.ui.components.filter_option_menu import FilterOptionMenu
        panel=SearchFilterPanel(self.root,lambda key:key)
        panel.pack(fill='x')
        variable=cst.StringVar(master=self.root,value='Second')
        choice=panel.add_choice('column',['First','Second'],variable=variable)
        self.root.update()
        self.assertIsInstance(choice,FilterOptionMenu)
        self.assertEqual(choice.get(),'Second')
        for state,width in (('normal',200),('disabled',260),('normal',180)):
            choice.configure(state=state,width=width);self.root.update()
            canvas=choice._canvas
            self.assertEqual(canvas.itemcget('dropdown_arrow','state'),'hidden')
            arrow,=canvas.find_withtag('filter_arrow')
            self.assertEqual(canvas.type(arrow),'line')
            x1,y1,x2,y2,x3,y3=Canvas.coords(canvas,arrow)
            self.assertLess(x1,x2);self.assertLess(x2,x3)
            self.assertEqual(y1,y3);self.assertGreater(y2,y1)
            self.assertAlmostEqual(x2,(choice._current_width-choice._current_height/2)*choice._get_widget_scaling())
        choice.set('First');self.assertEqual(variable.get(),'First')

    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1600x900');self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):
            self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.assertFalse(self.errors)

    def test_session_progress_empty_round_and_actions(self):
        panel=SessionPanel(self.root,lambda key:key,progress=True)
        panel.pack(fill='both',expand=True)
        callback=Mock();button=panel.add_action('Review',callback,row=5)
        panel.set_progress(3,6)
        self.assertEqual(panel.count.cget('text'),'3 / 6')
        self.assertEqual(panel.progress.get(),.5)
        panel.set_progress(0,0);self.assertEqual(panel.progress.get(),0)
        button.invoke();callback.assert_called_once()

    def test_session_scrollbar_only_appears_for_overflow(self):
        panel=SessionPanel(self.root,lambda key:key)
        panel.pack(fill='both',expand=True)
        self.root.update()
        scrollbar=panel.content._scrollbar
        self.assertFalse(scrollbar.winfo_ismapped())
        labels=[]
        for row in range(3,70):
            label=cst.CTkLabel(panel.content,text=f'Row {row}')
            label.grid(row=row,pady=6);labels.append(label)
        self.root.update()
        self.assertTrue(scrollbar.winfo_ismapped())
        panel.content._parent_canvas.yview_moveto(1)
        for label in labels:label.destroy()
        self.root.update()
        canvas=panel.content._parent_canvas
        self.assertFalse(scrollbar.winfo_ismapped(),(canvas.yview(),canvas.cget('scrollregion'),panel.content.winfo_reqheight(),canvas.winfo_height()))
        self.assertEqual(canvas.yview()[0],0)

    def test_toolbar_preserves_action_state_help_and_shortcuts(self):
        panel=EditorToolbar(self.root,'Vocabulary',lambda key:key)
        panel.pack(fill='x')
        callback=Mock();button=panel.add_action('delete','Delete selected words',callback,state='disabled')
        panel.set_help('Add words');panel.count.configure(text='10 / 20')
        self.root.update()
        button.invoke();callback.assert_not_called()
        button.configure(state='normal');button.invoke();callback.assert_called_once()
        self.assertIs(panel.buttons['delete'],button)
        self.assertEqual(panel.help.cget('text'),'Add words')
        self.assertGreater(panel.shortcuts.winfo_height(),0)
        self.assertLess(button._text_label.winfo_reqheight(),30,(button.winfo_width(),button.cget('width'),button._text_label.cget('wraplength'),button._text_label.cget('font')))

    def test_filter_selection_placeholder_and_bidirectional_search(self):
        changed=Mock();apply=Mock();query=cst.StringVar(master=self.root)
        panel=SearchFilterPanel(self.root,lambda key:key,query_var=query,on_change=changed,on_apply=apply)
        panel.pack(fill='x')
        selection=cst.StringVar(master=self.root,value='Second')
        choice=panel.add_choice('category',['First','Second'],variable=selection)
        self.assertEqual(choice.get(),'Second')
        self.assertEqual(panel.query.cget('placeholder_text'),'Search')
        query.set('external');self.assertEqual(panel.query.get(),'external')
        panel.query.delete(0,'end');panel.query.insert(0,'typed');panel.query.read_value()
        self.assertEqual(query.get(),'typed');self.assertEqual(changed.call_count,2)
        self.assertEqual(panel._submit(),'break');apply.assert_called_once()
        panel.destroy();query.set('after destruction')

    def test_dialog_centers_and_cancels_pending_callbacks(self):
        dialog=AppDialog(self.root);dialog.geometry('600x400')
        dialog.add_heading('Title','Description')
        callback=Mock();dialog.after(1000,callback)
        dialog.present();self.root.update()
        center=dialog.winfo_rootx()+dialog.winfo_width()/2
        expected=self.root.winfo_rootx()+self.root.winfo_width()/2
        self.assertLess(abs(center-expected),40)
        dialog.destroy();self.root.update();callback.assert_not_called()
        self.assertFalse(dialog._dialog_jobs)

    def test_recording_dialog_opens_and_closes_without_recording(self):
        from tempfile import TemporaryDirectory
        from app.vocabulary.editor_audio import AudioRecorderPlayer
        table=Mock()
        with TemporaryDirectory() as directory:
            dialog=AppDialog(self.root)
            recorder=AudioRecorderPlayer(dialog,'word','translation','description',1,0,
                table,None,directory,'Spanish')
            recorder._present();self.root.update()
            self.assertEqual(recorder.stop_btn.cget('state'),'disabled')
            self.assertFalse(recorder.recording)
            recorder.Cancel_rec()
            self.assertFalse(dialog.winfo_exists())
            table.see.assert_called_once_with(0,0)

    def test_review_captions_use_wide_rows_before_wrapping(self):
        from app.ui.learning_review import ReviewDialog
        from app.shared.translations import translate
        from unittest.mock import patch
        for locale in ('cs','en','de','es','fr','sk'):
            with self.subTest(locale=locale),patch('app.shared.settings.T',side_effect=lambda key:translate(key,locale)):
                dialog=ReviewDialog(self.root,'Previous word','word','translation',[],
                    [(caption,Mock()) for caption in ('Delete audio','Delete word description','Delete example sentence',
                        'Edit synonyms','Edit description','Edit example')])
                dialog.deiconify();self.root.update()
                buttons=[child for frame in dialog.winfo_children() if isinstance(frame,cst.CTkFrame)
                    for child in frame.winfo_children() if isinstance(child,cst.CTkButton)]
                self.assertEqual(len(buttons),6)
                for button in buttons:
                    self.assertLess(button._text_label.winfo_reqheight(),30)
                dialog.destroy()


def component_regressions():
    names=[
        'app.tests.test_ui_components.ComponentTests',
        'app.tests.test_synonyms_ui',
        'app.tests.test_editor_async_ui',
        'app.tests.test_vocabulary_editor_dropdowns',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_grammar_editor_theory.TheoryEditorUiTests',
        'app.tests.test_grammar_category_filter.FilterTests.test_search_resets_scroll_without_changing_selected_categories',
        'app.tests.test_grammar_category_filter.FilterTests.test_filtered_round_restart_clear_and_dialog_cancel',
        'app.tests.test_grammar_theory.TheoryTests.test_current_previous_finish_restart_and_learning_language',
        'app.tests.test_grammar_theory.TheoryTests.test_long_theory_is_scrollable',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
        'app.tests.test_learning_ui.LearningUiTests.test_long_review_fields_scroll_without_expanding_the_dialog',
        'app.tests.test_learning_ui.LearningUiTests.test_review_buttons_invoke_callbacks_without_file_operations',
        'app.tests.test_learning_ui.LearningUiTests.test_preferences_dialog_stays_open_after_failed_write_then_saves',
        'app.tests.test_shared_controls.SharedControlsTests.test_about_and_preferences_header_actions_share_training_style_in_all_languages',
        'app.tests.test_module_panels.ModulePanelTests.test_grammar_session_is_on_right_and_answer_actions_are_separate',
        'app.tests.test_module_panels.ModulePanelTests.test_question_and_theory_actions_share_green_panel_and_have_exit',
    ]
    return unittest.defaultTestLoader.loadTestsFromNames(names)


def layout_refinements():
    return unittest.defaultTestLoader.loadTestsFromNames([
        'app.tests.test_ui_components.ComponentTests.test_session_scrollbar_only_appears_for_overflow',
        'app.tests.test_ui_components.ComponentTests.test_toolbar_preserves_action_state_help_and_shortcuts',
        'app.tests.test_ui_components.ComponentTests.test_review_captions_use_wide_rows_before_wrapping',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_synonym_candidates_use_numeric_ids_more_rows_and_available_width',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_select_save_reopen_remove_and_cancel',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_filter_searches_word_or_translation_and_scrolls_to_first_result',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
        'app.tests.test_shared_controls.SharedControlsTests.test_popup_action_groups_stay_equal_and_centered_when_resized',
        'app.tests.test_shared_controls.SharedControlsTests.test_dialog_action_sizes_and_long_translations_fit',
        'app.tests.test_shared_controls.SharedControlsTests.test_long_translated_tool_captions_fit_narrow_and_wide_panels',
        'app.tests.test_module_panels.ModulePanelTests.test_grammar_session_is_on_right_and_answer_actions_are_separate',
    ])

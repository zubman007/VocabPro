"""Shared lifecycle ownership, leave decisions and late-callback regressions."""
from unittest import TestCase,defaultTestLoader
from unittest.mock import Mock,patch
import customtkinter as cst
from app.core.context import AppContext
from app.core.screen_controller import ScreenController


class ScreenControllerTests(TestCase):
    def setUp(self):
        self.root=cst.CTk();self.root.geometry('900x650');self.root.update()
        self.context=AppContext(on_home=Mock())
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy();self.assertEqual(self.errors,[])

    def screen(self,**kwargs):
        frame=cst.CTkFrame(self.root);frame.pack(fill='both',expand=True)
        return ScreenController(self.root,frame,context=self.context,**kwargs)

    def test_clean_cancel_discard_save_failure_success_and_async_save(self):
        lifecycle=self.screen();save=Mock(return_value=True)
        with patch('app.core.screen_controller.messagebox.askyesnocancel') as ask:
            self.assertTrue(lifecycle.can_leave(False,save))
            ask.assert_not_called();save.assert_not_called()
            for answer,result,allowed in ((None,True,False),(False,True,True),
                    (True,False,False),(True,True,True),(True,None,False)):
                with self.subTest(answer=answer,result=result):
                    ask.return_value=answer;save.return_value=result
                    self.assertEqual(lifecycle.can_leave(True,save),allowed)

    def test_finish_and_cleanup_run_once_even_after_widget_destruction(self):
        lifecycle=self.screen();cleanup=Mock();home=Mock()
        lifecycle.add_cleanup(cleanup)
        child=cst.CTkButton(lifecycle.screen);child.destroy()
        self.assertFalse(lifecycle.closed)
        self.assertTrue(lifecycle.finish(home))
        self.assertFalse(lifecycle.finish(home))
        lifecycle.screen.destroy();lifecycle.close()
        cleanup.assert_called_once();home.assert_called_once()

    def test_destroy_cancels_owned_timers_and_traces_but_preserves_external_callbacks(self):
        external=self.root.bind('<Return>',lambda event:None,add='+')
        lifecycle=self.screen(commands={'<Return>':Mock()})
        callback=Mock();idle=lifecycle.after_idle(callback);later=lifecycle.after(1000,callback)
        variable=cst.StringVar(master=self.root)
        trace=lifecycle.trace(variable,'write',callback)
        lifecycle.screen.destroy();self.root.update()
        self.assertTrue(lifecycle.closed);callback.assert_not_called()
        self.assertIn(external,self.root.bind('<Return>'))
        self.assertNotIn(idle,self.root.tk.call('after','info'))
        self.assertNotIn(later,self.root.tk.call('after','info'))
        self.assertFalse(any(token==trace for modes,token in variable.trace_info()))
        variable.set('after close');callback.assert_not_called()

    def test_close_protocols_restore_correctly_in_both_disposal_orders(self):
        original=self.root.protocol('WM_DELETE_WINDOW')
        for order in ('old-first','new-first'):
            with self.subTest(order=order):
                one=self.screen(on_window_close=Mock());first=self.root.protocol('WM_DELETE_WINDOW')
                two=self.screen(on_window_close=Mock());second=self.root.protocol('WM_DELETE_WINDOW')
                if order=='old-first':
                    one.close();self.assertEqual(self.root.protocol('WM_DELETE_WINDOW'),second)
                    two.close()
                else:
                    two.close();self.assertEqual(self.root.protocol('WM_DELETE_WINDOW'),first)
                    one.close()
                self.assertEqual(self.root.protocol('WM_DELETE_WINDOW'),original)
                self.assertFalse(self.root.tk.call('info','commands',first))
                self.assertFalse(self.root.tk.call('info','commands',second))
                one.screen.destroy();two.screen.destroy()

    def test_cleanup_failure_does_not_prevent_remaining_resource_cleanup(self):
        lifecycle=self.screen();cleanup=Mock()
        lifecycle.add_cleanup(cleanup)
        lifecycle.add_cleanup(Mock(side_effect=ValueError('synthetic failure')))
        with self.assertLogs('app.core.screen_controller',level='ERROR'):lifecycle.close()
        cleanup.assert_called_once()

    def test_owned_dialogs_close_and_release_delayed_callbacks(self):
        from app.ui.components.app_dialog import AppDialog
        lifecycle=self.screen(on_window_close=Mock())
        first=AppDialog(self.root)
        self.assertIs(first.lifecycle_owner,lifecycle)
        first.destroy();self.assertNotIn(first,lifecycle._dialogs)
        second=AppDialog(self.root);callback=Mock();second.after(1000,callback)
        unrelated=cst.CTkToplevel(self.root)
        lifecycle.close();self.root.update()
        self.assertFalse(second.winfo_exists())
        self.assertTrue(unrelated.winfo_exists())
        self.assertEqual(lifecycle._dialogs,{})
        self.assertEqual(second._dialog_jobs,set())
        callback.assert_not_called();unrelated.destroy()

    def test_editor_shutdown_stops_recording_without_touching_the_old_table(self):
        from tempfile import TemporaryDirectory
        from app.ui.components.app_dialog import AppDialog
        from app.vocabulary.editor_audio import AudioRecorderPlayer
        lifecycle=self.screen(on_window_close=Mock())
        table=Mock()
        with TemporaryDirectory() as directory:
            dialog=AppDialog(self.root)
            recorder=AudioRecorderPlayer(dialog,'word','translation','',1,0,table,None,directory,'English')
            lifecycle.close()
            self.assertTrue(recorder.stop_event.is_set())
            self.assertTrue(recorder.closing)
            self.assertFalse(dialog.winfo_exists())
            self.assertIsNone(recorder._show_id)
            table.see.assert_not_called()

    def test_async_editor_exit_waits_for_success_and_keeps_data_on_failure(self):
        from dataclasses import replace
        from tempfile import TemporaryDirectory
        from threading import Event
        from time import monotonic,sleep
        from app.vocabulary.editor import EditorController
        from app.tests.test_editor_save import course
        for fail in (False,True):
            with self.subTest(fail=fail),TemporaryDirectory() as directory:
                context=AppContext(root_dir=directory,on_home=Mock())
                context.preferences=replace(context.preferences,learned_by='Czech')
                context.files_dir.mkdir()
                path=context.vocabulary_path('English')
                course().to_csv(path,sep=';',index=False);before=path.read_bytes()
                entered,release=Event(),Event()
                def worker(snapshot,*args,**kwargs):
                    entered.set();release.wait(2)
                    if fail:raise PermissionError('synthetic write failure')
                    return snapshot
                with patch('app.vocabulary.editor.save_course',side_effect=worker),\
                        patch('app.vocabulary.editor.messagebox.askyesnocancel',return_value=True) as ask,\
                        patch('app.vocabulary.editor.messagebox.showerror') as error,\
                        patch.object(self.root,'destroy') as destroy:
                    editor=EditorController(self.root,'English',context=context)
                    editor.edit_tbl.set_cell_data(0,editor.headers.index('Czech'),'changed')
                    try:
                        editor.Exit(self.root)
                        self.assertTrue(entered.wait(1))
                        self.assertTrue(editor._saving)
                        self.assertFalse(editor.lifecycle.closed)
                        destroy.assert_not_called()
                        release.set();deadline=monotonic()+3
                        while editor._saving and monotonic()<deadline:self.root.update();sleep(.005)
                        self.assertFalse(editor._saving)
                        ask.assert_called_once()
                        if fail:
                            error.assert_called_once();destroy.assert_not_called()
                            self.assertFalse(editor.lifecycle.closed)
                            self.assertEqual(editor.main_df.Czech.tolist(),['changed'])
                        else:
                            error.assert_not_called();destroy.assert_called_once()
                            self.assertTrue(editor.lifecycle.closed)
                        context.on_home.assert_not_called()
                        self.assertEqual(path.read_bytes(),before)
                    finally:
                        release.set()
                        if editor._task is not None:editor._task.thread.join(2)
                        editor.edit_frm.destroy()


def lifecycle_regressions():
    return defaultTestLoader.loadTestsFromNames([
        'app.tests.test_screen_controller.ScreenControllerTests',
        'app.tests.test_background_task',
        'app.tests.test_training_controllers',
        'app.tests.test_grammar_deferred_save',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_grammar_editor_theory.TheoryEditorUiTests',
        'app.tests.test_grammar_category_filter.FilterTests.test_filtered_round_restart_clear_and_dialog_cancel',
        'app.tests.test_grammar_theory.TheoryTests.test_current_previous_finish_restart_and_learning_language',
        'app.tests.test_editor_async_ui',
        'app.tests.test_synonyms_ui',
        'app.tests.test_app_context.ContextUiTests',
        'app.tests.test_module_consistency.ModuleConsistencyTests.test_both_grammar_editors_save_and_leave_once',
        'app.tests.test_module_consistency.ModuleConsistencyTests.test_failed_editor_save_preserves_screen_and_dirty_data',
        'app.tests.test_module_consistency.ModuleConsistencyTests.test_practice_empty_and_dirty_save_both_leave',
        'app.tests.test_learning_ui.LearningUiTests.test_practice_modes_and_answer_card_keep_their_shared_palette',
        'app.tests.test_learning_ui.LearningUiTests.test_conjugation_feedback_preserves_scoring_and_separates_header_rows',
    ])


def lifecycle_edge_regressions():
    return defaultTestLoader.loadTestsFromNames([
        'app.tests.test_screen_controller.ScreenControllerTests',
        'app.tests.test_background_task',
        'app.tests.test_training_controllers',
        'app.tests.test_editor_async_ui',
        'app.tests.test_grammar_editor.EditorUiTests',
        'app.tests.test_synonyms_ui.SynonymsUiTests.test_back_without_answers_or_vocabulary_edits_does_not_prompt',
        'app.tests.test_app_context.ContextUiTests',
        'app.tests.test_ui_components.ComponentTests.test_recording_dialog_opens_and_closes_without_recording',
    ])

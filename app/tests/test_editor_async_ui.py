"""Real Tk save transitions, using synthetic data and a fake worker only."""
from app.tests.context_helpers import patch_preferences
from threading import Event
from time import monotonic, sleep
import tkinter as tk
import unittest
from unittest.mock import patch
import customtkinter as cst
from app import main
from app.vocabulary import editor
from app.shared.background_task import check_cancelled
from app.tests.test_editor_save import course


class EditorAsyncUiTests(unittest.TestCase):
    def test_responsive_cancel_retry_and_completion(self):
        try:
            root=cst.CTk()
        except tk.TclError as error:
            self.skipTest(str(error))
        root.withdraw()
        callback_errors=[]
        root.report_callback_exception=lambda *args:callback_errors.append(args)
        entered=Event()
        release=Event()
        calls=[]

        def worker(snapshot, path, language, folder, revision, cancelled, progress, *, context):
            self.assertEqual(context.preferences.learned_by,'Czech')
            self.assertIsNone(context.on_home)
            calls.append(snapshot)
            entered.set()
            progress(1,2)
            release.wait(2)
            check_cancelled(cancelled)
            return snapshot

        def pump_until(predicate):
            deadline=monotonic()+3
            while not predicate() and monotonic()<deadline:
                root.update()
                sleep(.005)
            self.assertTrue(predicate())

        try:
            with patch_preferences(learned_by='Czech'), \
                 patch('app.shared.settings.T',side_effect=lambda text:text), \
                 patch('app.repositories.vocabulary.file_revision',return_value=b'revision'), \
                 patch('app.vocabulary.editor.next_word_id',return_value=2), \
                 patch('app.repositories.vocabulary.load_vocabulary',return_value=course().drop(columns=['Created','Custom']).assign(Tags='')), \
                 patch('app.vocabulary.editor.pygame.mixer.get_init',return_value=None), \
                 patch('app.vocabulary.editor.pygame.mixer.quit'), \
                 patch('app.vocabulary.editor.save_course',side_effect=worker) as save, \
                 patch('app.vocabulary.editor.messagebox.showerror') as errors:
                controller=editor.Edit(root,'English')
                previous_protocol=root.protocol('WM_DELETE_WINDOW')
                controller.Save(root,None)
                self.assertTrue(entered.wait(1))
                controller.Save(root,None)
                self.assertEqual(len(calls),1)
                heartbeat=[]
                root.after(0,lambda:heartbeat.append(True))
                pump_until(lambda:bool(heartbeat))
                self.assertTrue(controller._saving)
                pump_until(lambda:controller.save_progress.completed==1)
                self.assertEqual(controller.save_progress.total,2)
                self.assertEqual(controller.save_progress.bar.get(),.5)
                self.assertIn('1 / 2',controller.save_progress.processed.cget('text'))
                self.assertEqual(controller.save_progress.heading.cget('fg_color'),'transparent')
                self.assertEqual(controller.save_progress.cget('fg_color'),'#d7dfca')
                controller._cancel_save()
                release.set()
                pump_until(lambda:not controller._saving)
                errors.assert_not_called()
                self.assertEqual(root.protocol('WM_DELETE_WINDOW'),previous_protocol)
                self.assertEqual(controller.back_btn.cget('state'),'normal')
                self.assertFalse(controller.save_progress.winfo_manager())
                save.side_effect=PermissionError('read only')
                controller._close_after_save=True
                controller.Save(root,None)
                pump_until(lambda:not controller._saving)
                errors.assert_called_once()
                self.assertFalse(controller._close_after_save)
                self.assertTrue(root.winfo_exists())
                self.assertEqual(controller.main_df.English.tolist(),['NA'])
                save.side_effect=worker
                with patch.object(controller,'Cancel') as home:
                    controller.Save(root,None)
                    pump_until(lambda:not controller._saving)
                    home.assert_called_once_with(root)
                self.assertEqual(callback_errors,[])
        finally:
            release.set()
            for timer in root.tk.call('after','info'):
                root.tk.call('after','cancel',timer)
            root.destroy()

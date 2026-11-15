"""Background mail and main-thread scheduling, using fake SMTP and temporary preferences."""
from app.core.context import get_context
from app.tests.context_helpers import patch_context,patch_preferences
from datetime import datetime
from pathlib import Path
from threading import Event, get_ident
from types import SimpleNamespace
from unittest.mock import Mock, patch
import tempfile
import unittest
import tkinter as tk
import customtkinter as cst
import pandas as pd
from app.services.backup_background import BackupCoordinator
from app.repositories.preferences import record_success
from app.repositories.preferences import load_preferences, save_preferences
from app.tests.test_background_task import Scheduler
from app.tests.test_preferences_data import sample_preferences
from app import main


class Owner(Scheduler):
    def bind(self,*args,**kwargs):pass


class BackgroundBackupTests(unittest.TestCase):
    def test_real_window_remains_responsive_and_closes_during_send(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw();root.update()
        release=Event();entered=Event();completed=Mock();errors=[]
        root.report_callback_exception=lambda *error:errors.append(error)
        def send():entered.set();release.wait(2);return True
        manager=BackupCoordinator(root,completed,self.fail)
        try:
            manager.request('key',send);self.assertTrue(entered.wait(1))
            heartbeat=[];root.after(0,lambda:heartbeat.append(True));root.update()
            self.assertEqual(heartbeat,[True])
            frame=cst.CTkFrame(root);frame.destroy()
            self.assertFalse(manager.closed)
            root.destroy()
            self.assertTrue(manager.closed)
            release.set();manager.task.thread.join(2)
            completed.assert_not_called();self.assertEqual(errors,[])
        finally:
            release.set()
            if not manager.closed:root.destroy()

    def test_slow_send_does_not_block_callbacks_and_refresh_cannot_duplicate_it(self):
        owner=Owner();entered=Event();release=Event();threads=[];completed=[]
        def send():
            threads.append(get_ident());entered.set();release.wait(2);return True
        manager=BackupCoordinator(owner,lambda key:completed.append(get_ident()),self.fail)
        self.assertTrue(manager.request('first',send));self.assertTrue(entered.wait(1))
        self.assertFalse(manager.request('first',send))
        self.assertFalse(manager.request('changed settings',send))
        beat=[];owner.after(0,lambda:beat.append(True));owner.run()
        self.assertEqual(beat,[True]);self.assertFalse(completed)
        manager._destroyed(SimpleNamespace(widget=object()))
        self.assertFalse(manager.closed)
        release.set();manager.task.thread.join(2);owner.run()
        self.assertEqual(completed,[get_ident()]);self.assertNotEqual(threads,[get_ident()])

    def test_failure_and_no_attachments_do_not_mark_success_or_retry_on_each_refresh(self):
        for result in (False,OSError('SMTP unavailable')):
            with self.subTest(result=type(result).__name__):
                owner=Owner();success=Mock();error=Mock();send=Mock()
                if isinstance(result,Exception):send.side_effect=result
                else:send.return_value=result
                manager=BackupCoordinator(owner,success,error)
                manager.request('same',send);manager.task.thread.join(2);owner.run()
                success.assert_not_called()
                self.assertEqual(error.call_count,int(isinstance(result,Exception)))
                self.assertFalse(manager.request('same',send))
                send.assert_called_once()

    def test_destroyed_window_receives_no_callbacks(self):
        owner=Owner();release=Event();success=Mock();error=Mock()
        def send():release.wait(2);return True
        manager=BackupCoordinator(owner,success,error);manager.request('key',send)
        manager._destroyed(SimpleNamespace(widget=owner))
        release.set();manager.task.thread.join(2);owner.run()
        success.assert_not_called();error.assert_not_called()
        self.assertFalse(owner.jobs)
        self.assertFalse(manager.request('new',send))

    def settings(self,path):
        frame=sample_preferences()
        frame.loc[frame.Name.eq('Backup mail'),'Value']='to@example.com'
        frame.loc[frame.Name.eq('Backup period (days)'),'Value']='3'
        frame.loc[frame.Name.eq('Next backup'),'Value']='2026-11-01 00:00:00'
        frame.to_csv(path,sep=';',index=False)

    def test_success_uses_fresh_settings_and_changes_only_next_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';self.settings(path)
            frame=load_preferences(path)
            frame.loc[frame.Name.eq('Learn batch'),'Value']='27'
            frame.to_csv(path,sep=';',index=False)
            before=load_preferences(path)
            result=record_success(path,'to@example.com',3,'2026-11-01 00:00:00',datetime(2026,11,13,10))
            self.assertEqual(result,'2026-11-16 10:00:00')
            after=load_preferences(path)
            pd.testing.assert_frame_equal(before.loc[before.Name.ne('Next backup')].reset_index(drop=True),
                after.loc[after.Name.ne('Next backup')].reset_index(drop=True))

    def test_changed_recipient_or_schedule_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';self.settings(path)
            original=path.read_bytes()
            for recipient,period,previous in (('old@example.com',3,'2026-11-01 00:00:00'),
                    ('to@example.com',7,'2026-11-01 00:00:00'),('to@example.com',3,'')):
                self.assertIsNone(record_success(path,recipient,period,previous))
                self.assertEqual(path.read_bytes(),original)

    def test_open_preferences_can_save_after_automatic_date_update(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';self.settings(path)
            stale=load_preferences(path)
            date=record_success(path,'to@example.com',3,'2026-11-01 00:00:00')
            save_preferences(stale,{'Learn batch':'42','Next backup':'2026-11-01 00:00:00'},path)
            saved=load_preferences(path).set_index('Name').Value
            self.assertEqual(saved['Learn batch'],'42');self.assertEqual(saved['Next backup'],date)

    def test_main_schedules_once_and_updates_latest_preferences_after_send(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'settings.csv';self.settings(path)
            owner=Owner();entered=Event();release=Event()
            def send(*args):entered.set();release.wait(2);return True
            with patch_context(files_dir=folder), \
                 patch_preferences(backup_mail='to@example.com'),patch_preferences(backup_period=3), \
                 patch_preferences(next_backup='2026-11-01 00:00:00'),patch_preferences(app_language='English'), \
                 patch('app.main.send_backup',side_effect=send) as mail,patch('app.main.messagebox.showerror') as error:
                main.Back_up(owner);self.assertTrue(entered.wait(1));main.Back_up(owner)
                self.assertEqual(mail.call_count,1)
                frame=load_preferences(path);frame.loc[frame.Name.eq('Learn batch'),'Value']='31'
                frame.to_csv(path,sep=';',index=False)
                release.set();owner._backup_coordinator.task.thread.join(2);owner.run()
                saved=load_preferences(path).set_index('Name').Value
                self.assertEqual(saved['Learn batch'],'31')
                self.assertNotEqual(saved['Next backup'],'2026-11-01 00:00:00')
                self.assertEqual(get_context().preferences.next_backup,saved['Next backup'])
                error.assert_not_called()

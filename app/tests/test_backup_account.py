"""Sender configuration without accessing the user's vault or sending mail."""
import ctypes
import ssl
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock,patch
import customtkinter as cst
from app.services import mail_credentials as vault
from app.services.backup import send_backup
from app.services.backup_background import BackupCoordinator
from app.tests.test_backup_background import Owner
from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.tests.test_preferences_data import sample_preferences
from app.shared.translations import LANGUAGES


class VaultTests(TestCase):
    def test_native_layout_unicode_roundtrip_and_buffer_cleanup(self):
        api=Mock()
        saved={}
        def write(pointer,flags):
            item=ctypes.cast(pointer,ctypes.POINTER(vault._Credential)).contents
            saved.update(username=item.UserName,blob=ctypes.string_at(item.CredentialBlob,item.CredentialBlobSize),
                         pointer=item.CredentialBlob,size=item.CredentialBlobSize)
            self.assertEqual((item.TargetName,item.Type,item.Persist,flags),(vault.TARGET,1,2,0))
            return 1
        api.CredWriteW.side_effect=write
        vault._write_credentials(api,' sender@example.com ','Žluťoučký-test-🔑')
        self.assertEqual(saved['username'],'sender@example.com')
        self.assertEqual(ctypes.string_at(saved['pointer'],saved['size']),b'\0'*saved['size'])
        blob=(ctypes.c_ubyte*len(saved['blob'])).from_buffer_copy(saved['blob'])
        item=vault._Credential(UserName=saved['username'],CredentialBlob=blob,CredentialBlobSize=len(blob))
        def read(target,kind,flags,out):
            ctypes.cast(out,ctypes.POINTER(ctypes.POINTER(vault._Credential)))[0]=ctypes.pointer(item)
            return 1
        api.CredReadW.side_effect=read
        self.assertEqual(vault._read_credentials(api),('sender@example.com','Žluťoučký-test-🔑'))
        api.CredFree.assert_called_once()

    def test_missing_access_error_validation_and_failure_do_not_leak_password(self):
        api=Mock();api.CredReadW.return_value=0
        with patch.object(ctypes,'get_last_error',return_value=1168):self.assertIsNone(vault._read_credentials(api))
        with patch.object(ctypes,'get_last_error',return_value=5),self.assertRaises(OSError):vault._read_credentials(api)
        for user,password in [('bad','secret'),('a@b.cz',''),('a@b.cz','x'*2561)]:
            with self.assertRaises(ValueError):vault._write_credentials(api,user,password)
        api.CredWriteW.assert_not_called()
        api.CredWriteW.return_value=0
        with self.assertRaises(OSError) as error:vault._write_credentials(api,'a@b.cz','private-test-value')
        self.assertNotIn('private-test-value',str(error.exception))

    def test_saved_sender_supplies_missing_environment_credentials(self):
        with TemporaryDirectory() as folder:
            (Path(folder)/'English_gra.csv').write_text('ID;R\n1;S\n',encoding='utf-8')
            with patch('app.services.mail_credentials.load_credentials',return_value=('sender@example.com','synthetic')) as load,\
                 patch('app.services.backup.smtplib.SMTP_SSL') as smtp:
                smtp.return_value.__enter__.return_value.send_message.return_value={}
                self.assertTrue(send_backup(folder,'to@example.com','','',str,'VocabPro'))
                smtp.return_value.__enter__.return_value.login.assert_called_once_with('sender@example.com','synthetic')
                self.assertEqual(smtp.call_args.kwargs['context'].verify_mode,ssl.CERT_REQUIRED)
                self.assertTrue(smtp.call_args.kwargs['context'].check_hostname)
                load.assert_called_once()

    def test_account_change_releases_retry_delay_without_sending(self):
        manager=BackupCoordinator(Owner(),Mock(),Mock())
        manager.last_key='key';manager.retry_at=10**10
        manager.reset_retry()
        self.assertIsNone(manager.last_key)
        self.assertEqual(manager.retry_at,0)
        self.assertIsNone(manager.task)


class BackupAccountUiTests(TestCase):
    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1200x850')
        self.context=AppContext(preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.after_cancel(job)
        self.root.destroy();self.assertEqual(self.errors,[])

    def test_save_uses_vault_preserves_blank_password_and_rejects_other_sender(self):
        from app.preferences.backup_account import BackupAccountDialog
        with patch('app.preferences.backup_account.load_credentials',return_value=('from@example.com','secret-test')),\
             patch('app.preferences.backup_account.save_credentials') as save:
            callback=Mock();dialog=BackupAccountDialog(self.root,callback)
            self.assertEqual(dialog.password.get(),'')
            dialog.save();save.assert_called_once();callback.assert_called_once()
            from app.services.mail_transport import decode_secret
            self.assertEqual(save.call_args.args[0],'from@example.com')
            password,config=decode_secret(save.call_args.args[1])
            self.assertEqual((password,config.host),('secret-test','smtp.seznam.cz'))
            reopened=BackupAccountDialog(self.root)
            self.assertEqual(reopened.username.get(),'from@example.com')
            self.assertEqual(reopened.password.get(),'')
            reopened.destroy()
        with patch('app.preferences.backup_account.load_credentials',return_value=('from@example.com','secret-test')),\
             patch('app.preferences.backup_account.save_credentials',side_effect=ValueError('Enter the SMTP password.')) as save:
            dialog=BackupAccountDialog(self.root)
            dialog.password.delete(0,'end')
            dialog.username.delete(0,'end');dialog.username.insert(0,'other@example.com');dialog.save()
            save.assert_not_called()
            self.assertTrue(dialog.winfo_exists());dialog.destroy()

    def test_layout_translations_and_cancel_never_write_credentials(self):
        from app.preferences.backup_account import BackupAccountDialog
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            with patch('app.preferences.backup_account.load_credentials',return_value=None),\
                 patch('app.preferences.backup_account.save_credentials') as save:
                dialog=BackupAccountDialog(self.root);dialog.deiconify();dialog.geometry('620x480');self.root.update()
                self.assertEqual(dialog.password.cget('show'),'•')
                self.assertLessEqual(dialog.message._label.winfo_reqwidth(),dialog.message.winfo_width()+2)
                dialog.show_error(ValueError('Could not save the sending account in Windows Credential Manager.'))
                self.root.update()
                self.assertLessEqual(dialog.error._label.winfo_reqwidth(),dialog.error.winfo_width()+2)
                for button in dialog.winfo_children():
                    if isinstance(button,cst.CTkButton):
                        self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                dialog.destroy();save.assert_not_called()

    def test_settings_button_opens_once_and_restores_parent_modal_grab(self):
        from app.preferences.dialog import PreferencesDialog
        with TemporaryDirectory() as folder:
            path=Path(folder)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
            preferences=PreferencesDialog(self.root,self.context.translate,path)
            preferences.present();self.root.update()
            with patch('app.preferences.backup_account.load_credentials',return_value=None):
                preferences.sender_button.invoke();self.root.update()
                dialog=preferences._sender_dialog
                dialog.present(modal=True);self.root.update()
                preferences.open_sender_account()
                self.assertIs(preferences._sender_dialog,dialog)
                self.assertIs(self.root.grab_current(),dialog)
                dialog.destroy()
                self.assertIs(self.root.grab_current(),preferences)
            preferences.destroy()

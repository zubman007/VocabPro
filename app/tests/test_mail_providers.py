"""Provider routing, vault migration and delivery without real network or secrets."""
from email.message import EmailMessage
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event,get_ident
from time import perf_counter
from unittest import TestCase
from unittest.mock import Mock,patch,call
import smtplib
import ssl
import customtkinter as cst
from app.services.mail_providers import PROVIDERS,BY_DOMAIN,SMTPConfig,detect_provider
from app.services.mail_transport import (SendingAccount,MailError,account,credentials,saved_account,
                                        encode_secret,decode_secret,send_message,send_test)
from app.services.backup import send_backup


class ProviderTests(TestCase):
    def test_provider_instructions_are_translated_in_every_ui_language(self):
        from app.shared.translations import LANGUAGES,get_catalog
        for language in LANGUAGES:
            catalog=get_catalog(language)
            for provider in PROVIDERS:
                self.assertIn(provider.help_key,catalog)
                self.assertTrue(catalog[provider.help_key].strip())

    def message(self):
        message=EmailMessage();message['To']='recipient@example.net';message.set_content('synthetic')
        return message

    def test_every_known_domain_resolves_exactly_and_lookalikes_are_custom(self):
        domains=[domain for provider in PROVIDERS for domain in provider.domains]
        self.assertEqual(len(domains),len(set(domains)))
        for domain,provider in BY_DOMAIN.items():
            self.assertIs(detect_provider('person@'+domain.upper()),provider)
            self.assertIsNone(detect_provider('person@'+domain+'.example.net'))
        self.assertIsNone(detect_provider('person@company.example'))

    def test_shared_and_regional_infrastructure_are_not_confused(self):
        self.assertEqual(detect_provider('x@centrum.cz').smtp,detect_provider('x@atlas.cz').smtp)
        self.assertNotEqual(detect_provider('x@volny.cz').smtp,detect_provider('x@centrum.cz').smtp)
        self.assertNotEqual(detect_provider('x@yahoo.com').smtp,detect_provider('x@yahoo.co.jp').smtp)
        self.assertNotEqual(detect_provider('x@gmx.com').smtp,detect_provider('x@gmx.de').smtp)
        self.assertEqual(detect_provider('x@email.cz').smtp,detect_provider('x@seznam.cz').smtp)

    def test_all_supported_profiles_resolve_without_manual_configuration(self):
        for provider in PROVIDERS:
            if provider.supported:
                sender=account('x@'+provider.domains[0],'synthetic')
                self.assertEqual(sender.config,provider.smtp)
                self.assertIn(sender.config.security,('TLS','STARTTLS'))

    def test_unsupported_authentication_is_explicit_and_never_contacts_a_server(self):
        for domain in ('outlook.com','hotmail.com','live.com','proton.me','pm.me'):
            with patch('app.services.mail_transport.smtplib.SMTP_SSL') as tls,patch('app.services.mail_transport.smtplib.SMTP') as start:
                with self.assertRaises(MailError):account('x@'+domain,'not-a-working-oauth-token')
                tls.assert_not_called();start.assert_not_called()

    def test_unknown_provider_requires_settings_and_known_provider_cannot_be_overridden(self):
        with self.assertRaises(MailError):account('x@company.example','secret')
        custom=SMTPConfig('mail.company.example',2465,'TLS')
        self.assertEqual(account('x@company.example','secret',custom).config,custom)
        self.assertEqual(account('x@gmail.com','secret',custom).config.host,'smtp.gmail.com')

    def test_legacy_secret_and_custom_config_roundtrip_without_storing_a_second_account(self):
        self.assertEqual(decode_secret('legacy password'),('legacy password',None))
        config=SMTPConfig('smtp.example.net',587,'STARTTLS')
        encoded=encode_secret('žluťoučký-secret',config)
        self.assertEqual(decode_secret(encoded),('žluťoučký-secret',config))
        self.assertEqual(account('x@company.example',encoded).password,'žluťoučký-secret')
        self.assertNotIn('žluťoučký-secret',repr(account('x@company.example',encoded)))

    def test_legacy_saved_unknown_domain_preserves_the_original_seznam_route(self):
        with patch('app.services.mail_credentials.load_credentials',return_value=('old@company.example','legacy')) as load:
            sender=saved_account('','')
            self.assertEqual(sender.config,SMTPConfig('smtp.seznam.cz'))
            self.assertEqual(sender.password,'legacy');load.assert_called_once()

    def test_incomplete_other_sender_never_uses_the_stored_password(self):
        with patch('app.services.mail_credentials.load_credentials',return_value=('old@seznam.cz','private')):
            with self.assertRaises(MailError):credentials('different@gmail.com','')

    def test_explicit_account_failure_has_no_fallback_and_diagnostics_do_not_leak_secrets(self):
        with patch('app.services.mail_credentials.load_credentials',side_effect=AssertionError('must not switch account')):
            sender=saved_account('explicit@gmail.com','private-password')
        with patch('app.services.mail_transport.smtplib.SMTP_SSL') as smtp:
            client=smtp.return_value.__enter__.return_value
            client.login.side_effect=smtplib.SMTPAuthenticationError(535,b'private-password secret-server-text')
            with self.assertRaises(MailError) as error:send_message(sender,self.message())
            self.assertNotIn('private-password',str(error.exception))
            self.assertNotIn('secret-server-text',str(error.exception))
            smtp.assert_called_once();client.send_message.assert_not_called()

    def test_implicit_tls_checks_certificates_and_uses_the_selected_provider(self):
        with patch('app.services.mail_transport.smtplib.SMTP_SSL') as smtp:
            client=smtp.return_value.__enter__.return_value;client.send_message.return_value={}
            send_message(account('person@gmail.com','app-password'),self.message())
            self.assertEqual(smtp.call_args.args,('smtp.gmail.com',465))
            context=smtp.call_args.kwargs['context']
            self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED);self.assertTrue(context.check_hostname)
            client.login.assert_called_once_with('person@gmail.com','app-password')
            client.starttls.assert_not_called()
            message=client.send_message.call_args.args[0]
            self.assertTrue(message['Date'])
            self.assertTrue(str(message['Message-ID']).endswith('@gmail.com>'))

    def test_starttls_finishes_before_login_and_missing_tls_never_sends_credentials(self):
        with patch('app.services.mail_transport.smtplib.SMTP') as smtp:
            client=smtp.return_value.__enter__.return_value;client.send_message.return_value={}
            send_message(account('person@icloud.com','app-password'),self.message())
            self.assertEqual(smtp.call_args.args,('smtp.mail.me.com',587))
            self.assertEqual([method[0] for method in client.method_calls],['ehlo','starttls','ehlo','login','send_message'])
            self.assertTrue(client.starttls.call_args.kwargs['context'].check_hostname)
            client.reset_mock();client.starttls.side_effect=smtplib.SMTPNotSupportedError('no TLS')
            with self.assertRaises(MailError):send_message(account('person@icloud.com','app-password'),self.message())
            client.login.assert_not_called()

    def test_bad_server_security_port_and_injected_sender_are_rejected(self):
        for config in (SMTPConfig('smtp.example',0),SMTPConfig('smtp.example',True),SMTPConfig('smtp.example',25,'none'),
                       SMTPConfig('https://smtp.example'),SMTPConfig('smtp.example\r\nother')):
            with self.subTest(config=config),self.assertRaises(ValueError):config.validated()
        for sender in ('x@gmail.com\r\nBcc: other@example.com','two@example.com,three@example.com','Display <x@gmail.com>','@gmail.com'):
            with self.assertRaises(ValueError):account(sender,'password')

    def test_certificate_failures_and_refused_recipients_are_sanitized(self):
        with patch('app.services.mail_transport.smtplib.SMTP_SSL',side_effect=ssl.SSLCertVerificationError('untrusted secret')):
            with self.assertRaises(MailError) as error:send_message(account('x@seznam.cz','private'),self.message())
            self.assertNotIn('untrusted secret',str(error.exception))
        with patch('app.services.mail_transport.smtplib.SMTP_SSL') as smtp:
            smtp.return_value.__enter__.return_value.send_message.return_value={'x@example.net':(550,b'private diagnostics')}
            with self.assertRaises(MailError):send_message(account('x@seznam.cz','private'),self.message())

    def test_test_message_has_one_sender_recipient_and_no_backup_attachment(self):
        sender=account('x@seznam.cz','synthetic')
        with patch('app.services.mail_transport.send_message') as send:
            send_test(sender,'Test','Body')
            message=send.call_args.args[1]
            self.assertEqual(message['To'],sender.username)
            self.assertEqual(list(message.iter_attachments()),[])

    def test_custom_vault_config_is_used_for_backup_without_exporting_secrets(self):
        config=SMTPConfig('smtp.company.example',587,'STARTTLS')
        secret=encode_secret('vault-only-password',config)
        with TemporaryDirectory() as directory:
            root=Path(directory);(root/'English_gra.csv').write_text('ID;R\n1;S\n',encoding='utf-8')
            with patch('app.services.mail_credentials.load_credentials',return_value=('sender@company.example',secret)),\
                 patch('app.services.mail_transport.smtplib.SMTP') as smtp:
                client=smtp.return_value.__enter__.return_value;client.send_message.return_value={}
                self.assertTrue(send_backup(root,'recipient@example.net','','',str,'VocabPro'))
                client.login.assert_called_once_with('sender@company.example','vault-only-password')
                message=client.send_message.call_args.args[0]
                self.assertEqual(message['From'],'sender@company.example')
                self.assertNotIn('vault-only-password',message.as_string())
                self.assertEqual(list(root.iterdir()),[root/'English_gra.csv'])


class ProviderUiTests(TestCase):
    def test_password_guidance_and_saved_state_follow_the_selected_sender(self):
        from app.preferences.backup_account import BackupAccountDialog
        with patch('app.preferences.backup_account.load_credentials',return_value=('x@seznam.cz','synthetic-password')):
            dialog=BackupAccountDialog(self.root)
        tr=dialog.translate
        self.assertEqual(dialog.password.get(),'')
        self.assertIn(tr('Password saved'),dialog.message.cget('text'))
        self.assertEqual(dialog.password.cget('show'),'•')
        self.assertEqual(dialog.password_label.cget('text'),tr('Mailbox password'))
        self.assertEqual(dialog._account().password,'synthetic-password')
        self.assertEqual(dialog.provider_help.cget('text'),tr(detect_provider('x@seznam.cz').help_key))
        self.set_sender(dialog,'other@gmail.com')
        self.assertEqual(dialog.password_label.cget('text'),tr('App password'))
        self.assertEqual(dialog.password.cget('show'),'•')
        self.assertEqual(dialog.message.cget('text'),tr('No password saved for this sender. Enter it and choose Save.'))
        with self.assertRaises(ValueError):dialog._account()
        self.set_sender(dialog,'x@seznam.cz')
        self.assertEqual(dialog._account().password,'synthetic-password')
        dialog.password.insert(0,'replacement')
        self.assertEqual(dialog._account().password,'replacement')
        dialog.destroy()

    def setUp(self):
        from app.core.context import AppContext
        self.root=cst.CTk();self.root.geometry('1100x850');AppContext().bind(self.root)
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for child in tuple(self.root.winfo_children()):child.destroy()
        for token in self.root.tk.call('after','info'):self.root.after_cancel(token)
        self.root.destroy();self.assertEqual(self.errors,[])

    def dialog(self):
        from app.preferences.backup_account import BackupAccountDialog
        with patch('app.preferences.backup_account.load_credentials',return_value=None):
            return BackupAccountDialog(self.root)

    def set_sender(self,dialog,sender):
        dialog.username.delete(0,'end');dialog.username.insert(0,sender);self.root.update()

    def test_technical_fields_only_for_unknown_domain_and_unsupported_authentication_is_disabled(self):
        dialog=self.dialog()
        for address in ('x@gmail.com','x@centrum.cz','x@icloud.com','x@outlook.com','x@proton.me'):
            self.set_sender(dialog,address)
            self.assertFalse(dialog.manual.grid_info())
        self.assertEqual(dialog.save_button.cget('state'),'disabled')
        self.assertEqual(dialog.test_button.cget('state'),'disabled')
        self.set_sender(dialog,'x@company.example')
        self.assertTrue(dialog.manual.grid_info());self.assertEqual(dialog.save_button.cget('state'),'normal')

    def test_saved_password_is_never_inserted_and_unknown_config_roundtrips_in_one_vault_write(self):
        from app.preferences.backup_account import BackupAccountDialog
        config=SMTPConfig('smtp.company.example',587,'STARTTLS')
        with patch('app.preferences.backup_account.load_credentials',return_value=('x@company.example',encode_secret('private',config))),\
             patch('app.preferences.backup_account.save_credentials') as save:
            dialog=BackupAccountDialog(self.root)
            self.assertEqual(dialog.password.get(),'');self.assertEqual(dialog.host.get(),config.host)
            dialog.save();save.assert_called_once()
            self.assertEqual(decode_secret(save.call_args.args[1]),('private',config))

    def test_test_delivery_runs_off_ui_thread_and_does_not_save_credentials(self):
        dialog=self.dialog();self.set_sender(dialog,'x@gmail.com');dialog.password.insert(0,'app-password')
        workers=[];gate=Event();ui=get_ident()
        def deliver(*args):workers.append(get_ident());gate.wait(2)
        with patch('app.preferences.backup_account.send_test',side_effect=deliver),\
             patch('app.preferences.backup_account.save_credentials') as save:
            dialog.start_test()
            self.assertEqual(dialog.save_button.cget('state'),'disabled')
            gate.set();deadline=perf_counter()+5
            while dialog.task is not None and perf_counter()<deadline:self.root.update()
            self.assertIsNone(dialog.task);self.assertNotEqual(workers,[ui]);self.assertEqual(len(workers),1)
            save.assert_not_called()

    def test_closing_inflight_test_cancels_polling_and_late_callbacks(self):
        dialog=self.dialog();self.set_sender(dialog,'x@gmail.com');dialog.password.insert(0,'app-password')
        gate=Event()
        with patch('app.preferences.backup_account.send_test',side_effect=lambda *args:gate.wait(2)):
            dialog.start_test();task=dialog.task;dialog.destroy();gate.set();task.thread.join(3);self.root.update()
            self.assertTrue(task.closed);self.assertFalse(dialog.winfo_exists())

"""Backup transport with fake SMTP and temporary attachments only."""
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app.services.backup import backup_due, send_backup, backup_files


class BackupTests(unittest.TestCase):
    def test_disabled_and_due_dates(self):
        now=datetime(2026,11,13)
        self.assertFalse(backup_due('',1,'',now))
        self.assertFalse(backup_due('user@example.com',0,'',now))
        self.assertFalse(backup_due('user@example.com',1,'2026-11-14 00:00:00',now))
        self.assertTrue(backup_due('user@example.com',1,'2026-11-12 00:00:00',now))

    def test_attachment_names_contents_and_recipient(self):
        with tempfile.TemporaryDirectory() as directory:
            original=b'ID;word\n1;original content\n'
            path=Path(directory)/'Czech_Spanish_voc.csv';path.write_bytes(original)
            with patch('app.services.backup.smtplib.SMTP_SSL') as smtp:
                send_backup(directory,'to@example.com',
                            'from@example.com','fake-secret',lambda value:value,'VocabPro')
            client=smtp.return_value.__enter__.return_value
            client.login.assert_called_once_with('from@example.com','fake-secret')
            message=client.send_message.call_args.args[0]
            self.assertEqual(message['To'],'to@example.com')
            attachments=list(message.iter_attachments())
            self.assertEqual([item.get_filename() for item in attachments],['Czech_Spanish_voc.csv'])
            self.assertEqual(attachments[0].get_payload(decode=True),original)
            self.assertEqual(path.read_bytes(),original)

    def test_missing_credentials_never_contacts_smtp(self):
        with patch('app.services.backup.smtplib.SMTP_SSL') as smtp:
            with self.assertRaises(RuntimeError):
                send_backup('.', 'to@example.com', '', '', str, 'VocabPro')
            smtp.assert_not_called()

    def test_all_data_csvs_are_included_but_empty_and_sensitive_files_are_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            contents={
                'English_gra.csv':b'question_id;category\n1;Articles\n',
                'Czech_Spanish_gra_ex.csv':b'category;rules\nVerbs;A rule\n',
                'Other_course.CSV':b'ID;text\n1;"first line\nsecond;line"\n',
                'zero.csv':b'', 'header.csv':b'ID;word\n',
                'empty_rows.csv':b'\xef\xbb\xbf\nID;word\n;\n" ";" "\n\n',
                'settings.csv':b'Name;Value\nAPI key;fake-secret\n',
                'notes.txt':b'not CSV',
            }
            for name,data in contents.items():(root/name).write_bytes(data)
            result=dict(backup_files(root))
            self.assertEqual(set(result),{'English_gra.csv','Czech_Spanish_gra_ex.csv','Other_course.CSV'})
            for name,data in result.items():self.assertEqual(data,contents[name])

    def test_no_data_sends_no_empty_email(self):
        with tempfile.TemporaryDirectory() as directory,patch('app.services.backup.smtplib.SMTP_SSL') as smtp:
            (Path(directory)/'empty.csv').write_text('ID;word\n',encoding='utf-8')
            self.assertFalse(send_backup(directory,'to@example.com','user','secret',str,'VocabPro'))
            smtp.assert_not_called()

"""Email backup transport, independent of Tk and mutable app settings."""
from datetime import datetime
from email.message import EmailMessage
import smtplib
import ssl
from app.repositories.courses import backup_files


def backup_due(recipient, period, next_backup, now=None):
    if not recipient or period <= 0:
        return False
    return not next_backup or (now or datetime.now()) > datetime.strptime(next_backup, '%Y-%m-%d %H:%M:%S')


def send_backup(files_dir, recipient, username, password, translate, app_name):
    if not username or not password:
        from app.services.mail_credentials import load_credentials
        saved=load_credentials()
        if saved and (not username or username==saved[0]):username,password=saved
    if not username or not password:
        raise RuntimeError('Configure the sending account in Settings → Backups → Sending account.')
    message = EmailMessage()
    message['Subject'] = app_name + ' - ' + translate('Backups')
    message['From'], message['To'] = username, recipient
    message.set_content(translate('Hello user,') + '\n' +
        translate('here is the back up vocabulary from the day ') + str(datetime.now()) + ',\n' +
        translate('your ') + app_name)
    attachments = 0
    for filename, data in backup_files(files_dir):
        message.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
        attachments += 1
    if not attachments:
        return False
    with smtplib.SMTP_SSL('smtp.seznam.cz', 465, timeout=20,context=ssl.create_default_context()) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
    return True

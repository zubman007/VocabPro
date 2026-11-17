"""Email backup transport, independent of Tk and mutable app settings."""
from datetime import datetime
from email.message import EmailMessage
import smtplib
import ssl
from app.repositories.courses import backup_files
from app.services.mail_transport import credentials,saved_account,send_message


def backup_due(recipient, period, next_backup, now=None):
    if not recipient or period <= 0:
        return False
    return not next_backup or (now or datetime.now()) > datetime.strptime(next_backup, '%Y-%m-%d %H:%M:%S')


def send_backup(files_dir, recipient, username, password, translate, app_name):
    username,password=credentials(username,password)
    message = EmailMessage()
    message['Subject'] = app_name + ' - ' + translate('Backups')
    message['To'] = recipient
    message.set_content(translate('Hello user,') + '\n' +
        translate('here is the back up vocabulary from the day ') + str(datetime.now()) + ',\n' +
        translate('your ') + app_name)
    attachments = 0
    for filename, data in backup_files(files_dir):
        message.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
        attachments += 1
    if not attachments:
        return False
    send_message(saved_account(username,password),message)
    return True

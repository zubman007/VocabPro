"""One sender, verified TLS, sanitized errors, and versioned vault-only metadata."""
from dataclasses import dataclass,field
from email.message import EmailMessage
from email.utils import formatdate,make_msgid
import json
import smtplib
import ssl
from app.services.mail_providers import SMTPConfig,detect_provider,sender_address
from app.shared.messages import UserMessageError

PREFIX = 'VocabPro SMTP account v1:'


class MailError(UserMessageError, RuntimeError):
    pass


@dataclass(frozen=True)
class SendingAccount:
    username: str
    password: str = field(repr=False)
    config: SMTPConfig


def decode_secret(secret):
    if not secret.startswith(PREFIX):return secret,None
    try:
        data=json.loads(secret[len(PREFIX):])
        if set(data)!={'password','host','port','security'} or not isinstance(data['password'],str):raise ValueError
        return data['password'],SMTPConfig(data['host'],data['port'],data['security']).validated()
    except (ValueError,TypeError,KeyError):
        raise MailError('Invalid saved sending account. Configure it again.') from None


def encode_secret(password, config=None):
    if not password or '\0' in password:raise MailError('Enter the SMTP password.')
    if config is None and not password.startswith(PREFIX):return password
    # Known-provider passwords normally retain the original vault format.
    if config is None:raise MailError('Enter the SMTP password.')
    config.validated()
    return PREFIX+json.dumps(dict(password=password,host=config.host,port=config.port,security=config.security),ensure_ascii=False)


def credentials(username,password):
    if not username or not password:
        from app.services.mail_credentials import load_credentials
        saved=load_credentials()
        if saved and (not username or username==saved[0]):
            username,password=saved
            if detect_provider(username) is None and not password.startswith(PREFIX):
                password=encode_secret(password,SMTPConfig('smtp.seznam.cz'))
    if not username or not password:
        raise MailError('Configure the sending account in Settings → Backups → Sending account.')
    return username,password


def account(username,secret,manual=None):
    username=sender_address(username)
    password,stored=decode_secret(secret)
    provider=detect_provider(username)
    if provider is not None:
        if not provider.supported:raise MailError(provider.help_key)
        config=provider.smtp
    else:
        config=manual or stored
        if config is None:raise MailError('Configure SMTP for this unknown email provider.')
    if not password:raise MailError('Enter the SMTP password.')
    return SendingAccount(username,password,config.validated())


def saved_account(username,password):
    username,password=credentials(username,password)
    # Metadata is read only for the same selected sender, never as another account.
    if detect_provider(username) is None and not password.startswith(PREFIX):
        from app.services.mail_credentials import load_credentials
        saved=load_credentials()
        if saved and saved[0]==username:
            _,manual=decode_secret(saved[1])
            # Old vault entries always used Seznam. Preserve that existing route.
            return account(username,password,manual or SMTPConfig('smtp.seznam.cz'))
    return account(username,password)


def send_message(sender,message):
    config=sender.config.validated()
    message['From']=sender.username
    if 'Date' not in message:message['Date']=formatdate(localtime=True)
    if 'Message-ID' not in message:message['Message-ID']=make_msgid(domain=sender.username.rsplit('@',1)[-1])
    context=ssl.create_default_context()
    try:
        client=(smtplib.SMTP_SSL(config.host,config.port,timeout=20,context=context)
                if config.security=='TLS' else smtplib.SMTP(config.host,config.port,timeout=20))
        with client as smtp:
            if config.security=='STARTTLS':
                smtp.ehlo();smtp.starttls(context=context);smtp.ehlo()
            smtp.login(sender.username,sender.password)
            refused=smtp.send_message(message)
            if refused:raise MailError('The email server refused the recipient.')
    except MailError:raise
    except smtplib.SMTPAuthenticationError:
        raise MailError('Email authentication failed. Check the account and app password.') from None
    except ssl.SSLError:
        raise MailError('The email server TLS certificate could not be verified.') from None
    except (OSError,smtplib.SMTPException,UnicodeError):
        raise MailError('Email delivery failed. Check the connection and provider settings.') from None


def send_test(sender,subject,body):
    message=EmailMessage()
    message['To']=sender.username
    message['Subject']=subject
    message.set_content(body)
    send_message(sender,message)

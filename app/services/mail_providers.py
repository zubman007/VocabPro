"""Exact-domain SMTP profiles; account secrets and UI stay outside this registry."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int = 465
    security: str = 'TLS'

    def validated(self):
        if (not isinstance(self.host,str) or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?',self.host)
                or '..' in self.host or type(self.port) is not int or not 1 <= self.port <= 65535
                or self.security not in ('TLS','STARTTLS')):
            raise ValueError('Enter a valid SMTP server, port and TLS security.')
        return self


@dataclass(frozen=True)
class Provider:
    name: str
    domains: tuple[str,...]
    smtp: SMTPConfig | None
    help_key: str
    url: str
    supported: bool = True


PASSWORD_HELP = 'Use the mailbox password, or an app password if two-factor authentication requires it.'
APP_HELP = 'Use an app password generated in your email account security settings.'
PROVIDERS = (
    Provider('Seznam',('seznam.cz','email.cz','post.cz'),SMTPConfig('smtp.seznam.cz'),PASSWORD_HELP,
             'https://o-seznam.cz/napoveda/email/mohlo-by-se-hodit/postovni-programy-a-aplikace/'),
    Provider('Gmail',('gmail.com','googlemail.com'),SMTPConfig('smtp.gmail.com'),APP_HELP,
             'https://support.google.com/mail/answer/185833'),
    Provider('Outlook',('outlook.com','outlook.cz','outlook.sk','hotmail.com','hotmail.co.uk','hotmail.fr','hotmail.de',
                        'live.com','live.co.uk','live.fr','msn.com'),SMTPConfig('smtp-mail.outlook.com',587,'STARTTLS'),
             'Outlook requires OAuth2. OAuth sign-in is not configured in this application; password login is unavailable.',
             'https://support.microsoft.com/en-us/outlook/pop-imap-and-smtp-settings-for-outlook-com',False),
    Provider('Yahoo',('yahoo.com','ymail.com','rocketmail.com','yahoo.co.uk','yahoo.fr','yahoo.de','yahoo.es','yahoo.it',
                      'yahoo.com.au','yahoo.ca'),SMTPConfig('smtp.mail.yahoo.com'),APP_HELP,
             'https://help.yahoo.com/kb/SLN3217.html'),
    Provider('Yahoo! Japan',('yahoo.co.jp','ymail.ne.jp'),SMTPConfig('smtp.mail.yahoo.co.jp'),PASSWORD_HELP,
             'https://support.yahoo-net.jp/PccMail/s/article/H000007321'),
    Provider('iCloud',('icloud.com','me.com','mac.com'),SMTPConfig('smtp.mail.me.com',587,'STARTTLS'),APP_HELP,
             'https://support.apple.com/102525'),
    Provider('AOL',('aol.com','aim.com'),SMTPConfig('smtp.aol.com'),APP_HELP,
             'https://help.aol.com/articles/how-do-i-use-other-email-applications-to-send-and-receive-my-aol-mail'),
    Provider('Zoho',('zoho.com','zohomail.com'),SMTPConfig('smtp.zoho.com'),PASSWORD_HELP,
             'https://www.zoho.com/mail/help/zoho-smtp.html'),
    Provider('GMX',('gmx.com','gmx.fr','gmx.es'),SMTPConfig('mail.gmx.com'),PASSWORD_HELP,
             'https://support.gmx.com/pop-imap/imap/server.html'),
    Provider('GMX',('gmx.de','gmx.net','gmx.at','gmx.ch'),SMTPConfig('mail.gmx.net'),PASSWORD_HELP,
             'https://hilfe.gmx.net/pop-imap/einrichtung-mailprogramm-scheitert.html'),
    Provider('Mail.com',('mail.com','email.com','usa.com','myself.com','consultant.com'),SMTPConfig('smtp.mail.com'),
             'SMTP access may require a paid plan and must be enabled by your email provider.',
             'https://support.mail.com/pop-imap/imap/server.html'),
    Provider('Centrum / Atlas',('centrum.cz','atlas.cz','cbox.cz','mujmail.cz'),SMTPConfig('smtp.centrum.cz'),
             'Centrum and Atlas require an expanded mailbox with SMTP access enabled.',
             'https://freemail.help.economia.cz/articles/44668-adresy-postovnich-serveru'),
    Provider('Volny',('volny.cz',),SMTPConfig('smtp.volny.cz'),PASSWORD_HELP,
             'https://freemail.help.economia.cz/articles/44668-adresy-postovnich-serveru'),
    Provider('Fastmail',('fastmail.com','fastmail.fm'),SMTPConfig('smtp.fastmail.com'),APP_HELP,
             'https://www.fastmail.help/hc/en-us/articles/1500000278342-Server-names-and-ports'),
    Provider('WEB.DE',('web.de',),SMTPConfig('smtp.web.de'),PASSWORD_HELP,
             'https://hilfe.web.de/pop-imap/pop3/serverdaten.html'),
    Provider('Proton Mail',('proton.me','protonmail.com','protonmail.ch','pm.me'),None,
             'Proton requires Proton Mail Bridge or an eligible SMTP token. These authentication methods are not supported here.',
             'https://proton.me/support/imap-smtp-and-pop3-setup',False),
)
BY_DOMAIN = {domain:provider for provider in PROVIDERS for domain in provider.domains}


def sender_address(value):
    value=value.strip()
    if len(value)>254 or value.count('@')!=1:
        raise ValueError('Enter a valid email address.')
    local,domain=value.rsplit('@',1)
    try:domain=domain.encode('idna').decode('ascii').lower()
    except UnicodeError:raise ValueError('Enter a valid email address.') from None
    if (not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+",local) or local.startswith('.') or local.endswith('.')
            or '..' in local or '.' not in domain or not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?',domain)
            or '..' in domain):
        raise ValueError('Enter a valid email address.')
    return local+'@'+domain


def detect_provider(address):
    return BY_DOMAIN.get(sender_address(address).rsplit('@',1)[1])

# Zálohování a obnova

Odesílatel se nastavuje v Nastavení → Zálohy → Odesílací účet (pro
`smtp.seznam.cz:465`). Příjemce zůstává odděleně v Backup mail. Uložení účtu
samo neposílá žádný e-mail; po Save hlavního nastavení nebo Refresh se použije
standardní plán zálohy. Uložením účtu se zruší prodleva po minulém selhání.
Heslo je maskované; ponechání prázdného pole zachová uložené heslo pouze pro
stejné jméno účtu. Odesílání používá TLS s ověřením certifikátu a hostname.

`services/mail_credentials.py` používá nativní CredReadW/CredWriteW/CredFree,
Generic credential `VocabPro/SMTP`, lokální persistenci pro stejného uživatele.
Heslo se neukládá do projektu ani CSV a jeho hodnota se nepředvyplňuje do UI.
[Datové rozhraní Windows](https://learn.microsoft.com/en-us/windows/win32/api/wincred/ns-wincred-credentialw).
Při přenosu aplikace na jiný počítač je třeba účet nastavit znovu.

backup_due rozhoduje podle příjemce, kladného intervalu a Next backup.
BackupCoordinator dovolí nejvýše jednu odesílací úlohu; po stejném pokusu má
pětiminutovou prodlevu. Odesílání neblokuje Tk. Až úspěšný send aktualizuje
termín, a to pouze pokud příjemce/interval/původní termín stále souhlasí.

repositories/courses.backup_files vybírá všechna CSV přímo ve files kromě
settings.csv. Hlavička samotná nestačí, musí existovat neprázdný datový řádek.
Posílají se původní bajty v e-mailových přílohách včetně synonym, gramatiky a
teorie. Audio, obrázky, konfigurace s klíči a podadresáře se nezálohují.

Automatická obnova z e-mailu v aplikaci není implementovaná. Ruční postup:

1. Ukončit aplikaci a vytvořit vlastní kopii stávajících dat.
2. Z e-mailu vybrat konzistentní přílohy stejné zálohy, zkontrolovat názvy a CSV.
3. Obnovit potřebné soubory do files, bez změny ID slovíček; související
   synonymní tabulku obnovit společně se slovníkem.
4. Audio obnovit z vlastní souborové zálohy; e-mail jej neobsahuje.
5. Spustit aplikaci, ověřit počty a otevření editoru. Při chybě neukládat přes
   neplatné CSV; vrátit se ke své původní kopii.

Atomické nahrazení jednoho CSV chrání před běžným selháním zápisu. Audio
workflow při selhání obnovy ponechá `.recovery-*` u příslušné audio složky;
zachované rollback soubory nesmazat před ruční kontrolou. Celá vícesouborová
operace není garantovaná při pádu OS/výpadku napájení. [Diagram](diagrams/BACKUP_WORKFLOW.md).

Zdrojový návratový bod tohoto refaktoringu je oddělený od záloh uživatelských
dat; jeho source-only archiv v .refactoring-recovery neobsahuje files,
obrázky, katalogy ani proměnné prostředí a není součástí distribuce.

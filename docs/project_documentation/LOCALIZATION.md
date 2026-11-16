# Lokalizace

shared/translations.py načítá UTF-8 katalogy locales/en.json, cs.json, sk.json,
es.json, fr.json a de.json. Identifikátorem zprávy je stabilní anglický text.
translate(message_id, language) nejprve hledá zvolený jazyk, pak angličtinu,
nakonec vrátí identifikátor. Duplicitní JSON klíče a neřetězcové hodnoty odmítá.
Cache drží nanejvýš počet podporovaných jazyků; neuchovává Tk objekty.

Kontrolér používá context.translate. Historická s.T získává aktivní kontext
pomocí ContextVar; není vhodná pro novou sdílenou logiku ve workeru bez
explicitního kontextu. editor_localization mapuje kanonické Audio a PoS do
zobrazení a zpět; překlady se nesmí uložit jako nový datový enum.

Zkratky jsou definované v about/shortcuts.py a stejné seznamy používá
ShortcutHint. Automatické zobrazení synonym podmiňuje viditelnost Ctrl+H.
Pro nový text přidat stabilní klíč do všech šesti katalogů a otestovat dlouhý
německý/francouzský text v nejmenší podporované šířce. Pro nový jazyk UI
rozšířit UI_LANGUAGE_IDS a doplnit katalog; není to automaticky nový studijní kurz.

Lokalizační AST test kontroluje skutečné UI textové sinky a ověřuje pokrytí
zkratek. Interní parametr message v perzistenci není sám o sobě widget.
Technické kontexty chyb (cesta, CSV řádek, typ výjimky) nejsou jazykovým
obsahem kurzu a nemění se při překladu dat.

Chybové a potvrzovací dialogy všech modulů používají app/ui/messagebox.py.
Vrací stejné True/False/None a ok jako původní volání. Tlačítka a výchozí
titulky se překládají podle kontextu rodičovského okna; předaný obsah už
musí být přeložený. Vnořená zpráva obnoví předchozí grab a fokus. Ctrl+C
zkopíruje zprávu; dlouhý obsah má scroll. Návrat ke tkinter.messagebox
odmítá automatický audit, protože systémová tlačítka neřídí jazyk aplikace.

Redakční pravidla a aktuální výsledky jsou v [auditu](../localization-audit.md)
a [pokynech pro překlady](../../locales/README.md). Klíče a uložené hodnoty
slovníků se při úpravě stylu překladů nemění.

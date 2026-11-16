# Překlady rozhraní

Každý jazyk má jeden katalog UTF-8 JSON: `en`, `cs`, `sk`, `es`, `fr`, `de`.
Všechny mají stejné klíče, abecední pořadí, odsazení dvě mezery a jeden překlad na
řádek. Duplicitní klíče jsou chyba, nikoliv tiché přepsání předchozí hodnoty.
Při kopírování nebo balení aplikace přibal celou složku `locales/` vedle skriptů.

## Použití

```python
from app.shared.translations import translate

translate('Save', 'Czech')  # Uložit
translate('Save', 'cs')     # Uložit
```

Obrazovky mohou nadále používat `settings.T('Save')`, které vybírá jazyk aplikace.
Při chybějícím překladu se použije angličtina; neznámý klíč se zobrazí jako text.
Neznámý jazyk nebo chybějící jazykový soubor také použije angličtinu. Chybný JSON
se neignoruje. Kontroly v `app/tests/test_translations.py` ověřují úplnost katalogů.

Každý požadovaný katalog se načte jednou do omezené cache. Katalogy jsou pouze pro
čtení. Po ruční změně JSON restartuj aplikaci. Starší zápis
`translation['Save']['Czech']` zůstává podporovaný pomocí pohledu do katalogů,
bez sestavování druhé kopie všech jazyků.

## Proč textové klíče

Klíče jsou stabilní identifikátory, často původní anglický text. Jejich pravopis
nemusí odpovídat nynějšímu anglickému popisku: například klíč `Setting` zobrazuje
`Settings`. Opravuje se hodnota, nikoliv identifikátor. Některé klíče se zároveň
používají jako názvy nastavení nebo sloupců CSV; jejich přejmenování by vyžadovalo
migraci dat. Číselné odkazy by skryly význam volání a načítání by nezrychlily.

Při přidání nového textu zvol čitelný a jednoznačný klíč a přidej jej do všech
šesti souborů. U existujících skládaných popisků zachovej počáteční i koncové
mezery. Různé kontexty mohou mít různé klíče i pro stejný viditelný text.

Překládej pouze rozhraní. Do CSV patří původní interní hodnoty jako `No audio`,
`Own` nebo `True`, nikdy jejich lokalizované popisky. Jazyk rozhraní nesmí měnit
uložená data ani pravidla učení.

## Opakovatelný audit

```powershell
.venv/Scripts/python.exe -B -m app.shared.localization_audit
.venv/Scripts/python.exe -B -m app.tests.run_all
```

Audit kontroluje katalogy, pojmenované parametry, formátování, známá rozhraní
pro UI texty a nastavení načítaná z CSV. Testy doplňují reálné přepínání jazyka
a tvorbu obrazovek ve všech šesti jazycích. Neznámé texty vznikající z proměnných
nelze obecně dokázat statickou kontrolou. Katalogy se shodnými klíči proto samy
o sobě neznamenají úplný překlad.

Zprávy formátuj až po překladu: `translate('Words to review: {count}', language).format(count=count)`.
Pro nové parametrizované chyby používej `UserMessageError`; v UI `error_text`.
Neskládej překladové ID z uživatelských textů ani neposílej do překladače již
přeložené záhlaví. Číselná data a datumy lokalizuj až při zobrazení pomocí
`app.shared.localization_format`, nikdy před uložením CSV.

Nový jazyk rozhraní vyžaduje výslovné přidání do `UI_LANGUAGE_IDS`, kompletní
katalog, nabídku jazyka v nastavení a runtime/vizuální ověření. Přidání
studijního jazyka samo o sobě rozhraní aplikace nerozšiřuje.

Podrobný výsledek, omezení automatických kontrol a ruční checklist jsou v
[auditu lokalizace](../docs/localization-audit.md).

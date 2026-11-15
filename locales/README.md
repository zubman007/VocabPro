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

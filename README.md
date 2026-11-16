# VocabPro

V **Nastavení → Jazyky → Studované jazyky → Přidat jazyk** lze zapnout třetí
i další podporované jazyky. Každý kurz má vlastní slovník, výsledky a nastavení
otázek. Podrobnosti a kompatibilita: [Studované kurzy](docs/study-courses.md).

Aktualizovaná sestava knihoven je v projektové `.venv`. Spuštění:
`.\.venv\Scripts\python.exe start.py`. Úplné verze pro opakovatelnou instalaci
jsou v `requirements.lock.txt`; VS Code profil VocabPro používá tuto `.venv`.

Desktopová aplikace pro učení slovní zásoby, gramatiky a časování.
Spuštění ve Windows s Pythonem 3: `python start.py`.

## Funkce

- Editor kurzů s filtrováním, příklady, ručně zadávanými slovními druhy a vlastním audiem.
- Vybraná slovíčka lze smazat v editoru; změna se potvrdí uložením. Ostatní ID se nemění.
  Nové slovo dostane nejvyšší zbývající ID + 1; mezery uprostřed se nezaplňují.
- Procvičování překladu, kontextu a poslechu s plánováním dalšího opakování.
- Gramatické otázky s vysvětlením a procvičování slovesných tvarů.
- Odpovědi gramatiky se ukládají až tlačítkem Uložit / `Ctrl+S` nebo při potvrzeném
  odchodu. `Esc` slouží jako Zavřít; bez změn se aplikace na ukládání neptá.
- Gramatiku lze filtrovat podle více kategorií; výběr spustí nové kolo a zachová uloženou historii.
- Nastavení → Učení umožňuje zapamatovat filtr gramatiky pro každý kurz. Výběr je v `files/settings.csv`;
  volba všech kategorií zruší omezení a zahrne i budoucí témata.
- Gramatika: `1–4` odpovědi, `Enter` pokračování po výsledku, mezerník odhalení/pokračování,
  `Alt+→` další otázka, `Ctrl+Z` náhled předchozí otázky, `Ctrl+T` teorie a `Ctrl+F` kategorie.
- Editor gramatických otázek s filtrem kategorií, volbou správné odpovědi a zachováním historie.
- Editory otázek a teorie se přepínají záložkami. Chybějící kategorie dostanou prázdný záznam teorie.
- Smazání otázky přečísluje ID podle pořadí; historie zůstává u příslušné otázky.
- Statistiky pokroku a nastavení rozhraní v šesti jazycích.
- Ze statistik gramatických kategorií lze přímo spustit procvičování daného tématu.
- Statistiky připravují všechny grafy předem; výpočty se uchovávají v paměti a obnovují při změně dat, dne nebo souvisejícího nastavení.
- Podrobný průvodce a klávesové zkratky přímo v okně O aplikaci.

## Data a nastavení

Uložit / `Ctrl+S` v editorech a procvičování uloží změny a vrátí se do hlavního menu.
Při chybě zůstane obrazovka otevřená i s rozpracovanými změnami. Nastavení a editor
synonym po úspěšném uložení zavřou své vlastní okno.

Synonyma se spravují tlačítkem v editoru slovíček a ukládají samostatně do
`files/*_synonyms.csv` jako dvojice ID a datum. Zobrazují se při učení, chybě,
v přehledu slova a na vyžádání během opakování; nenahrazují správnou odpověď.
V Nastavení → Učení lze vypnout automatické zobrazení synonym aktuálního slova;
potom je odhalí tlačítko přímo u otázky. Synonyma předchozího slova se zobrazují
automaticky v panelu Session.
Při vypnuté automatice odhalí synonyma také `Ctrl+H`; zkratka se pak zobrazí
v nápovědě. Editor nabízí počítané sloupce s příznakem a počtem synonym;
příznak lze filtrovat hodnotami 1 (má) a 0 (nemá). Do CSV slovíček se neukládají.

Kurzy, historie a nastavení jsou v `files/*.csv`, audio v `files/audio`.
Po uložení nového jazyka se připraví slovník, štítky, synonyma a složka audia.
Přepínač **Zapnout gramatiku** navíc připraví otázky, teorii a soubor rekordů.
Vypnutá gramatika se pro daný jazyk skryje z nabídky i statistik. Vypnutý kurz
po uložení zmizí z formuláře; odstraní se pouze prázdné CSV a zcela prázdná
složka audia. Vyplněné soubory i nahrávky zůstávají pro opětovné přidání.
Synonyma a audio vznikají až při použití. Prázdné slovníkové a synonymní CSV
nepoužívaných kurzů se při načtení nastavení uklidí; soubory s daty zůstávají.
Kurzy již nepoužívají sloupec `Enabled`; všechna zbývající slovíčka patří do procvičování.
CSV se ukládají atomickým nahrazením; při chybě zápisu zůstává původní soubor.
Aplikace je určená pro jednu spuštěnou instanci, nikoli souběžné úpravy stejných dat.

API klíče se zadávají v nastavení a zůstávají uložené v CSV v čitelné podobě.
Automatické doplňování údajů a audia vyžaduje internet. Editor ukládá na pozadí
s průběhem a možností zrušení; právě běžící síťový požadavek musí nejprve doběhnout.
Při chybě nebo zrušení zůstávají úpravy v editoru pro další pokus. Editor odmítne
přepsat soubor změněný od jeho otevření. E-mailové zálohy se odesílají na pozadí.

Účet odesílatele nastavíte v Nastavení → Zálohy → Odesílací účet. Používá se
smtp.seznam.cz; heslo se ukládá do Správce pověření Windows. Po uložení účtu
uložte hlavní nastavení nebo obnovte hlavní stránku. Jako alternativu lze
nadále použít proměnné prostředí `VOC_SMTP_USER` a `VOC_SMTP_PASSWORD`.
Příjemce a interval se nastavují v aplikaci; interval 0 zálohy vypíná.
Záloha obsahuje všechna datová CSV přímo ve `files`, včetně gramatiky a teorie,
pokud mají alespoň jeden neprázdný datový řádek. Hlavička sama nestačí.
Audio a `settings.csv` s API klíči nejsou součástí e-mailových záloh.
Současně běží nejvýše jedno odesílání. Termín další zálohy se posune až po úspěchu;
po chybě se stejný pokus neopakuje při každém obnovení stránky (prodleva 5 minut).
Při zavření aplikace se na rozpracované odesílání nečeká; bez potvrzeného dokončení
se příští termín neposune.

Zvuky rozhraní jsou krátké původní syntetické signály ve `files/audio/Sounds/ui_*.wav`.
Původní zvuk editoru zůstává zachovaný. Efekty používají samostatný kanál a mají nižší
prioritu než výslovnost; opakované rychlé spuštění stejného efektu se potlačí.
V Nastavení → Učení lze zvuky aplikace vypnout a nastavit hlasitost 0–100 %,
nezávisle na výslovnosti slovíček. Volby se uloží po stisku Uložit.
Ve stejné záložce lze vypnout automatickou výslovnost; ruční poslech zůstává dostupný,
včetně poslechových otázek.

## Orientace v kódu

Kompletní technická mapa, katalog modulů, datové formáty a diagramy jsou v
[docs/project_documentation](docs/project_documentation/README.md).
Ověřené přímé závislosti jsou v `requirements.txt`.

- `start.py`: spuštění; `app/main.py`: navigace; `app/home/`: hlavní stránka.
- `app/vocabulary/`, `app/grammar/`, `app/conjugation/`: jednotlivé výukové moduly a jejich editory.
- `app/statistics/`, `app/preferences/`, `app/about/`: statistiky, nastavení a průvodce aplikací.
- `app/services/`: externí API a e-mailové zálohy.
- `app/repositories/`: načítání a ukládání CSV, kontrola verzí souborů a výběr dat pro zálohy.
  Výuková pravidla, validace editorů a výpočty statistik zůstávají v příslušných modulech;
  bezpečné atomické zápisy zajišťuje společný `app/shared/storage.py`.
- `app/ui/`: sdílený vzhled, podklady, rozložení výuky a klávesové vazby.
- `app/ui/components/`: opakovaně používané vizuální komponenty.
  `SessionPanel` sjednocuje výukové postranní panely, `EditorToolbar` spodní lišty editorů,
  `SearchFilterPanel` hledání a filtry a `AppDialog` vystředění, zavírání a akce dialogů.
  Kontroléry řídí obrazovky a předávají ukládání dat vrstvě `repositories`.
- `app/ui/components/module_header.py`: společné záhlaví modulů; logo, nadpis a standardní akce
  Save / Close / Exit app. Filtry a přepínače se přidávají přes jeho rozšiřující místa.
- `app/shared/`: zvuky, ukládání, práce na pozadí a překlady; katalogy zůstávají v `locales/`.
- `app/paths.py`: společné cesty k datům, obrázkům a překladům nezávislé na umístění skriptů.

Aplikaci spouštěj přes `start.py`; soubory uvnitř `app/` jsou importované moduly.

Editor a výukové obrazovky mají vlastní instance kontrolérů; jejich pracovní stav
se nesdílí v globálních proměnných. Vstupy z menu ani počet oken se tím nemění.

`app/core/context.py` obsahuje `AppContext`: aktuální nastavení, cesty k datům,
překlady a navigaci. Vytváří se při startu a předává kontrolérům; ty neimportují
`main.py`. Ukládání na pozadí dostává vlastní snímek kontextu. Formát CSV se nemění.

`app/core/screen_controller.py` sjednocuje životní cyklus editorů a procvičování:
zkratky, časovače, pomocná okna a rozhodnutí při odchodu. Výuková a ukládací
logika zůstává v jednotlivých modulech.

## Kontrola

Testy používají syntetická data a dočasné soubory:

```powershell
python -B -m app.tests.run_all --timeout 240
```

Pro menší změny stačí spustit testy dotčené části; u změn vzhledu vizuální kontrola.

Testy jsou v `app/tests/`. Spouštěč izoluje moduly do samostatných procesů,
blokuje skutečnou síť, mikrofon, přehrávání a zápisy do uživatelských dat.
Výběr části sady: `python -B -m app.tests.run_all --pattern test_grammar*.py`.
Každý modul má časový limit; na konci se zobrazí souhrn a při chybě vrátí nenulový kód.
Sada zahrnuje rozložení oken v šesti jazycích, delší scénáře ukládání a výkonové
kontroly nad syntetickými daty; naměřené časy se vypisují jako `PERF`.
GUI testy mohou krátce otevírat zkušební okna. Uživatelskou aplikaci lze nechat běžet;
po změně zdrojového kódu ji před ověřením nových úprav restartuj.

# Osobní rekordy Grammar a Conjugation

Settings → Learning → Osobní rekordy obsahuje dva společné přepínače pro
všechny studované jazyky:

- **Sledovat osobní rekordy**: ukládá nová maxima při uložení odpovědí.
  Vypnutí uchová dosavadní rekordy a běžné statistiky i historii odpovědí.
- **Zobrazovat osobní rekordy**: nezávisle řídí jejich zobrazení v lekci a
  samostatných kartách Stats. Skrytí může ponechat sledování zapnuté.

Při chybějících volbách jsou oba přepínače zapnuté, což zachová původní
sledování Grammar. Starý settings.csv se pouhým čtením nepřepisuje; nové
řádky vzniknou standardním Save nastavení. Parametry jsou součástí
RuntimePreferences, bez závislosti na pořadí jazyků.

## Význam rekordů

Každý modul sleduje nejvíce správných odpovědí v jednom kole a nejdelší sérii
správných odpovědí. Maximum kola není součet několika kol. Grammar restart
nebo změna kategorií zahájí nové kolo; nejlepší dosažená maxima předchozích
kol se ponechají jako kandidáti do explicitního Save. Chyba, odhalení řešení
a přeskočení přeruší sérii. Přeskočení se nadále nezapisuje jako chybná odpověď.

V Conjugation je jednotkou celé sloveso se všemi dostupnými vybranými tvary
správně na první pokus. Více osob nepřidává více bodů. Potvrzení odhalené
odpovědi dokončí sloveso, ale nezvýší správné odpovědi ani sérii. Výběr osob,
velikost dávky a kategorie ovlivňují obtížnost, rekordy nejsou standardizovaným
porovnáním výkonu mezi různými nastaveními.

Dosavadní Grammar best_streak se zachová. Nové maximum správných odpovědí
není možné bezpečně dopočítat ze staré R: chybí hranice jednotlivých lekcí.
Dokud není nový výsledek, zobrazuje se pomlčka. Přerušenou lekci lze uložit;
rekord vychází z jejích skutečně zodpovězených položek. Zahození neuložených
odpovědí zahodí i jejich kandidáty rekordů.

## Ukládání a konzistence

- Grammar používá původní `<Language>_gra_records.csv`, oddělený pro cílový
  jazyk stejně jako jeho otázky. Conjugation používá
  `<Source>_<Target>_con_records.csv`, oddělený podle jazykové dvojice.
- Čtečka přijímá původní sloupec `best_streak` i novou dvojici
  `best_streak;best_correct`. Chybějící soubor a prázdná původní hlavička
  jsou platné. Nová struktura se uloží až při novém rekordu.
- Sdílená repository aktualizuje nezávislá maxima, bez sčítání a snižování.
  Zámek, kontrola revize, dočasný soubor a atomická výměna chrání zápis.
  Při chybě uložení odpovědí se obnoví přesné původní byty včetně původní
  hlavičky, BOM a konců řádků. Souběžně změněný soubor se nepřepisuje.
- Opakované Save nezapočítá výsledek znovu. Existující mechanismy uchování
  R/LR a individuálních výsledků Conjugation zůstávají funkční.
- CSV rekordů jsou zahrnuté do stávajících datových záloh. Vypnutí modulu
  nebo sledování neodstraňuje jejich neprázdné soubory.

Rekord a odpovědi jsou dva soubory: běžné chyby zápisu jsou ošetřené rollbackem,
nejde o databázovou transakci odolnou vůči výpadku procesu mezi oběma zápisy.
Toto omezení existovalo už u původního Grammar rekordu.

## UI a výkon

Oba moduly používají stejnou zaoblenou kartu Stats s vlastním vysvětlením.
Karta Grammar zůstává samostatně nad kategoriemi; karta Conjugation je dole
pod individuálními výsledky. Texty jsou v šesti jazycích UI a zalamují se.
Nezměněné hodnoty zbytečně nekonfigurují widgety. Rekordy se ve statistickém
workeru čtou nezávisle na cache historie, takže se obnoví i bez změny CSV
otázek/sloves. Scrollování nedělá nové výpočty rekordů.

## Ověření

Nové moduly `test_practice_records` a `test_practice_records_ui` pokrývají
maxima, oddělení jazyků/modulů, původní formát, rollback, chyby a opakované
ukládání, přepínače, reset a přeskočení, odhalené odpovědi i rozložení karet.

```powershell
.venv\Scripts\python.exe -X utf8 -B -m app.tests.run_all --timeout 240
.venv\Scripts\python.exe -X utf8 -B -m app.tests.run_all --pattern 'test_practice_records*.py' --timeout 240
.venv\Scripts\python.exe -X utf8 -B -m app.shared.localization_audit --output docs/localization-audit-inventory.json
```

Kontrola na cílovém monitoru: v Learning přepnout každou kombinaci voleb,
uložit, otevřít novou lekci obou modulů a Stats, zkontrolovat skrytí i zachování
starých rekordů. V Grammar změnit kategorie a restartovat; v Conjugation
přeskočit sloveso a potvrdit odhalené řešení. Zkusit dlouhé popisky při vlastním DPI.

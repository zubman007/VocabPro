# Plán bezpečného refaktoringu

15. 11. 2026. Celý rozsah 0–8 a dokumentační fáze 9 byl uživatelem schválen.
Níže je původní pořadí; provedený stav a omezení jsou v závěrečné tabulce.

## Pořadí a podmínky dokončení

| Krok | Rozsah | Ověření / podmínka dokončení |
|---|---|---|
| 0. Stabilní základ | Reprodukovat nestabilní Ctrl+S scénář; opravit přesnost AST lokalizačního testu, nikoli jeho očekávání jen kvůli zelenému výsledku. Přidat regresní testy nálezů A01–A05, A08, A13. | Nové testy musí nejprve prokázat problém. Rozlišovat fokus/event a přímé save. Žádná reálná síť, audio ani uživatelské zápisy. |
| 1. Audio cesty a validace vstupů | Path místo konkatenace v editoru; validace ID gramatiky a zprávy s řádkem; konzistentní zacházení s nepovinnými poli. | Přehrát/smazat jen správný falešný soubor; původní data při chybě nezměněna. BOM, Unicode, prázdné, krátké a nadbytečné řádky. |
| 2. Zápisy bez tichých ztrát | Delta pro změněná pole ve vocabulary/conjugation; aktuální snímek před zápisem, ochrana revize, rozlišení chybějícího souboru. | Souběžně upravený cizí text a slovo mimo session zůstávají. Konflikt stejného pole neukládá nic; ID/historie/extra sloupce se zachovají. |
| 3. Bezpečné workflow ukládání editoru | Jediná orchestrace obohacení mimo repository; staging audia, potvrzení CSV a navazující úklid. | Cancellation, chyba API, chyba replace a selhání archivu v každém rozhodujícím bodě. Zachování uživatelského progressu a možnosti opakovat uložení. Nezaměňovat částečný úspěch s úplným selháním. |
| 4. Dávkové ukládání gramatiky | Index ID vytvořit jednou; změny aplikovat po skupinách se zachováním časového pořadí. | Identický výsledek pro opakované stejné ID, S/F a LR; celá dávka atomická při neexistujícím či změněném ID. Zopakovat stejný benchmark 10k/100 a 10k/1000. |
| 5. Cache a I/O editoru | Invalidovaný index vazeb synonym; omezená cache velikostí podkladu; debounce resize. | Test počtu čtení po textové úpravě vs. změně synonym. Po 20/100 resize omezený počet bitmap, stejné pixely a hladké rohy. Měření paměti před/po. |
| 6. Statistiky bez globálů | Instance StatisticsController; přesun opakovaných částí souhrnných karet; rozdělit renderování grafů jen podle skutečných rozdílů. | Přepínání jazyků, chybějící conjugation, zavření během načítání, opakované otevření a přechod na kategorii. Všechny grafy nadále připravit před prohlížením. |
| 7. Úklid a diagnostika | Odstranit potvrzené nepoužívané importy/konstantu; vyřešit editor/theory navigační cyklus; doplnit manifest přímých závislostí, type hints nových kontraktů a bezpečné logování. | Importy všech modulů, lokalizace a asset testy. Žádné hromadné přejmenování veřejných callbacků ani neověřené mazání facade modulů. |
| 8. Závěrečný audit | Přepočítat vazby/počty změn, doplnit CHANGES, PERFORMANCE a TEST_RESULTS. | Po každém celku cílené testy; na konci celé výchozí spektrum i nové regrese. Přiznat zbylá omezení a neúspěšné testy. |

Kroky 0–3 mají přednost před kosmetikou a drobnými optimalizacemi. Krok 6 je
větší strukturální zásah a musí mít schválený rozsah. Pokud měření neprokáže
přínos některé optimalizace, vynechat ji nebo ponechat pouze zjednodušení s
jasným přínosem pro správnost.

## Návrat a ochrana dat

Před implementací pořídit obnovitelný snímek měněných zdrojových souborů a
ověřit způsob jeho obnovy; neukládat do dokumentace ani snímku API tajemství.
Neměnit a nepřesouvat reálné CSV/audio. Všechny destruktivní scénáře výhradně
v dočasném adresáři. Každý krok musí jít vrátit samostatně bez migrace dat.

Uživatelské aplikaci běžící na původních modulech se během práce nemá
přepisovat konfigurace. Pro ověření nového kódu ji po změnách restartovat.
Automatické testy ověřují syntetické scénáře ve vlastních procesech.

## Kritéria zachování chování

- Stejné menu, obrazovky, vzhled, překlady a zkratky; Save úspěšně uloží a
  zavře příslušnou obrazovku, při chybě zůstanou rozpracované změny.
- ID slovíček zůstávají stabilní; smazané poslední ID lze znovu použít dle
  současného pravidla. Synonymní vazby nejsou alternativní správné odpovědi.
- Nezmění se plánování opakování, vyhodnocení, počítání statistik ani obsah záloh.
- CSV hlavičky, oddělovač, historie, extra sloupce a jazykové varianty zůstanou
  kompatibilní. Stávající zkrácené řádky s nepovinnými poli musí fungovat.
- Zachovat přednačtení všech statistických grafů a nízkonákladové scrollování.
- Srozumitelnější odmítnutí poškozených dat je oprava chyby; nesmí znamenat
  jejich automatické „opravení“ a uložení bez souhlasu uživatele.

## Co není součástí návrhu

Migrace na databázi, přepis UI frameworku, změna vzhledu, zavedení nového
formátu CSV, přečíslování slovíček, celoplošné přejmenování callbacků ani
automatické mazání údajně nepoužívaných souborů. Nezavádět univerzální ORM,
event bus nebo dependency-injection framework pro tuto velikost aplikace.

## Provedení schváleného rozsahu

| Krok | Stav | Doložení |
|---|---|---|
| 0 | Dokončeno | Sedm původně selhávajících regresí, přesnější AST test, ověřená queued klávesová událost. |
| 1 | Dokončeno | Path cesty a validace grammar ID; kompatibilní čtení stávajících formátů. |
| 2 | Dokončeno v rozsahu jedné instance | Delta + revize + zámky a atomická publikace nových souborů. Externí nespolupracující proces nelze plně uzamknout touto smlouvou. |
| 3 | Dokončeno pro běžné I/O chyby | Staging, snapshot audio revizí, rollback a recovery; zachovaný progress/cancellation před commitem. |
| 4 | Dokončeno | Indexovaný batch save, výsledek a benchmark porovnán s původním stavem. |
| 5 | Dokončeno | Invalidace synonym a omezené bitmapy; testy a měření Working Set v samostatných procesech. |
| 6 | Dokončeno | Instanční statistiky, worker dat, postupné předpřipravení figur, cleanup a poslední požadavek na jazyk. |
| 7 | Dokončeno pragmaticky | Odstraněné importy/konstanta, navigace bez přímého cyklu, requirements a bezpečné logy. Legacy facade zůstává pro kompatibilitu. |
| 8 | Dokončeno po závěrečné sadě | Konkrétní výsledky a počty v TEST_RESULTS a CHANGES. |
| 9 | Dokončeno | Samostatná projektová dokumentace, katalog všech modulů a diagramy; kontrola relativních odkazů. |

Návratový bod: původní Git HEAD 52bea41 a source-only baseline.zip s manifestem
SHA-256 v ignorované .refactoring-recovery. Archiv byl po implementaci znovu
ověřen. Nebyl proveden reset, cleanup Gitu ani commit uživatelských dat.

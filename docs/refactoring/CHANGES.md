# Skutečně provedené změny

## Nastavení odesílacího účtu záloh (15. 11. 2026)

Chyba chybějících SMTP proměnných byla potvrzena z prostředí i z dialogu.
Nastavení záloh nyní nabízí lokální konfiguraci účtu ve Windows Credential
Manager, bez zápisu hesla do CSV či projektu. Proměnné prostředí zůstávají
kompatibilní alternativou. Chybová zpráva odkazuje na konkrétní nastavení.
Uložení účtu umožní nový pokus bez pětiminutového čekání; žádný testovací mail
se při uložení neposílá. SMTP klient nyní výslovně ověřuje TLS certifikát.
Nové dialogy i chyby mají překlady v šesti jazycích a testovací runner blokuje
skutečné čtení/zápis SMTP údajů ve Windows, stejně jako síťové operace.

## Jeden nebo dva aktivní studované jazyky (15. 11. 2026)

Nový kompatibilní přepínač druhého jazyka ve výchozím stavu zachovává dva
jazyky. RuntimePreferences centralizuje aktivní seznam; main, Stats a About
používají stejnou vlastnost. Jednojazyčný main má širší kartu, Stats nenabízí
přepnutí na neaktivní jazyk. Nastavení zneaktivní výběr druhého jazyka a jeho
procenta, hodnoty i soubory zachová. Z běžného načítání byl odpojen úklid
prázdných neaktivních CSV, aby přepínání nic nemazalo. Doplněno šest překladů,
osm cílených regresních scénářů a dokumentace. Produkční data se nemigrují.

## Nové kombinované a zátěžové scénáře (15. 11. 2026)

Přidáno sedm scénářů `test_tag_scenarios`: množinový referenční model filtrů,
10 000 dvojjazyčných řádků, okrajové lokalizované layouty nastavení, dlouhé
seznamy štítků, opakované změny session a rozpočet resize konfigurací.
Výběr štítků již při nezměněné šířce nepřenastavuje wraplength každého labelu.
Opraven skutečný překryv deseti dlouhých štítků se zadáním v užším okně:
štítky mají vlastní grid řádek, který společný fitter započítá do výšky
karty. Zůstává minimální výška 260, texty ani dostupné režimy se nezkracují.
Starší test opakovaného ukládání nastavení nyní kontroluje i přesnou očekávanou
migraci nových výchozích voleb, současně stále porovnává celé uložené mapování.

## Historický rekord série v gramatice (15. 11. 2026)

Statistiky gramatiky a session zobrazují uložený per-jazykový rekord.
Překonání během session zvýrazní nový rekord, shoda nikoli. Kandidát přežije
restart i změnu filtru, uloží se s odpověďmi a při jejich neúspěšném zápisu
se změna rekordu vrátí. Lokality cs/sk/en/de/es/fr mají všechny nové popisky.
Nová repository nevytváří prázdné soubory a zachovává formát historie otázek.

## Jednotné cyklické řazení (15. 11. 2026)

Statistiky štítků, kategorie gramatiky, statistická tabulka a editor slovíček
používají společný `next_sort`: vzestupně, sestupně, původní pořadí.
Samostatné Asc/Desc a Unsort akce nahradila jedna cyklická akce se šipkou.
Editor ukazuje aktivní směr také v záhlaví sloupce. Filtry, editované hodnoty,
číselné/datové porovnávání a poslední umístění neznámé úspěšnosti zůstávají.


## Kontrola zkratek a ovládání štítků (15. 11. 2026)

- Doplněno `Ctrl+T` pro výběr štítků označeného slova, `Ctrl+Shift+T` pro
  katalog, `Ctrl+F` pro hledání ve výběru a `Ctrl+Enter` pro použití výběru.
  Bindingy editoru vlastní životní cyklus obrazovky a respektují ukládání,
  otevřený dialog a vypnutí štítků.
- About app, místní nápověda a katalog štítků používají společný seznam;
  vypnuté štítky skryjí související zkratky. Doplněna informace o skutečně
  podporovaném `Ctrl+Shift+Z` pro Redo v tabulkách.
- Přeloženo dosud chybějící Apply ve všech šesti katalozích. Nastavení
  a editor gramatiky nyní přijímají také variantu Ctrl+S s velkým písmenem.
- Rozšířena auditní kontrola zkratek o kombinace se Shift a Ctrl+Enter.

## Následné rozšíření: štítky slovíček

Rozšíření ID a lekcí: Tags v obou skutečných slovnících převedeny na stabilní
ID katalogu; ověřeno 5 523 řádků a shoda všech ostatních buněk. Při migraci
nebyly nalezeny neplatné vazby (odstraněno 0). Codec zůstává kompatibilní
s názvy. Paste/edit validace nyní odmítne neznámý či nejednoznačný název ihned.
Katalog nelze uložit bez používaného ID. Nastavení Učení nabízí vypnutí
zobrazení, jazyk názvů, zobrazení při otázce a maximální počet štítků (10).
Snížení pod již používané počty se odmítá. Virtuální Tag count podporuje
číselné filtry. Review umožňuje editovat přiřazení a uložit je se session.
Ve statistikách je 15 položek na stránku včetně nulových; Repeat vytváří
pořadovou lekci se všemi slovy štítku podle Next repetition včetně Learn.
Prázdné štítky mají neaktivní Repeat. Slabá slova jsou vertikálně úspornější.

Zkompaktněn zelený dolní panel editace slovíček: levé texty se skládají
nezávisle na dvou řadách pravých tlačítek. Volitelný kompaktní režim sdíleného
EditorToolbar zachovává původní vzhled ostatních modulů a má fallback pro
užší okna. Funkce tlačítek a obsah nápovědy se nemění.

Filtr Tags v editoru nyní používá katalogová zaškrtávátka a kvantifikátory
všechny/žádný/přesná sada. Sdílí WordTagsDialog v režimu pouhého výběru,
bez nové duplicitní implementace seznamu. Textový dotaz a operátor ostatních
sloupců se při přepnutí zachovají. Porovnání pracuje s celými množinami,
respektuje řazení a přesune výsledky nahoru. Popisky v šesti jazycích,
šířka kvantifikátoru podle nejdelšího lokalizovaného názvu.

Repeat nyní zobrazuje štítky přeložené do studovaného jazyka pod zadáním,
v learn/chybové odpovědi, Review word a předešlém slovíčku v Session.
Překlady katalogu i přiřazení slov se drží v instanci kontroléru, bez čtení
CSV při každé odpovědi. Chybějící překlad použije původní název, prázdná data
skryjí popisky. Předchozí pravidla pro skip a předešlé slovo zůstávají.

Statistiky slovíček rozšířeny o stránkovaný přehled štítků (5 řádků),
počet slov, počet odpovědí a váženou úspěšnost. Jednotná pravidla historie
se přebírají z hlavního souhrnu, bez dalšího načítání CSV. Agregace je součástí
workeru a stávající cache; UI podporuje hledání a řazení a nepřidává vnořený
svislý scrollbar. Nové popisky přeloženy do všech šesti jazyků.

Následně povoleno vkládání a editování buněk Tags v tabulce, aby fungovalo
Ctrl+V z Excelu i pro více řádků. Povinná validace příslušnosti všech štítků
do katalogu před uložením zůstává zachována; picker i dvojklik fungují dál.

Správa katalogu přesunuta do zeleného panelu dole. Přidán výběr více štítků
pro označené slovíčko pomocí `WordTagsDialog` (hledání v názvu/překladu,
více zaškrtávátek, Clear selection). Tags je v tabulce pouze pro čtení;
výběr otevře tlačítko nebo dvojklik. Přiřazení se potvrdí hlavním Save.
Datová validace v editoru i save_workflow odmítá neznámé štítky a změnu
revize použitého katalogu během ukládání. Produkční CSV nebyla tímto krokem
měněna. EditorToolbar má volitelný počet sloupců akcí; editor slovíček
používá čtyři a tlačítka rozděluje do dvou řad.

Přidán samostatný tabulkový katalog `Czech_English_tags.csv` a
`Czech_Spanish_tags.csv`, každý s 91 přeloženými položkami a sloupci ID,
výchozí jazyk, studovaný jazyk, Note. `AppContext.tags_path` sjednocuje cesty,
`repositories.tags` kontroluje data a revize, `TagsDialog` nabízí CRUD a
potvrzení neuložených změn. Tlačítko v horním filtru editoru otevře katalog
aktuálního jazyka. Původní slovníkové CSV tímto krokem nebyly přepsány.

Rozšířeno na více štítků v jedné buňce oddělených čárkami. Editor při synchronizaci
a uložení sjednotí mezery a odstraní duplicity, filtr `equals` rozpozná jednotlivý
štítek. Přidána lokalizovaná nápověda a širší sloupec. Tato následná úprava
nepřepisuje produkční CSV; nová schémata ani další tabulky nejsou potřeba.

Do editoru a nových kurzů přidán volitelný perzistentní sloupec `Tags`, včetně
překladů do všech šesti jazyků. Starší CSV fungují i bez tohoto sloupce.
Do existujících Czech_English_voc.csv (2 677 řádků) a Czech_Spanish_voc.csv
(2 846 řádků) doplněny výhradně prázdné štítky. Ověřena shoda všech původních
buněk a pořadí řádků před i po atomickém zápisu s kontrolou revize.

15. 11. 2026 — schválená implementace a projektová dokumentace.

## Rozsah

| Typ změny | Počet |
|---|---:|
| Upravené existující soubory projektu | 40 |
| Přidané soubory projektu | 37 |
| Odstraněné soubory projektu | 0 |
| Nové produkční moduly | 3 |
| Nové testovací moduly | 2 |
| Změněná uživatelská CSV, audio a obrázky | 0 |

Počty jsou vůči zdrojovému manifestu po auditu, před první implementační
změnou; zahrnují šest upravených auditních dokumentů. Nové soubory: tři
produkční moduly, dva testovací, requirements.txt a 31 souborů projektové
dokumentace. Ignorované pracovní zálohy, logy a generátory se do distribuce
ani těchto počtů nezahrnují. Původní Git HEAD byl 52bea41, necommitnuté docs
byly zachovány. Nebyl vytvořen commit nebo změněn index Gitu.

## Původní auditní etapa

- Analýza zdrojů, závislostí a kritických operací.
- Výchozí běh celé dostupné sady a dvě ověření nestabilního scénáře.
- Reprodukce datových kolizí, nesprávného audio path a změn audia před commitem
  na dočasných syntetických datech.
- Měření současného výkonu a cache bitmap; návrh oprav v prioritním pořadí.

## Skutečná implementace

- Třícestná delta a obsahové revize pro vocabulary/conjugation save;
  nezměněné externí hodnoty se zachovají a konflikt odmítá celou operaci.
- Atomické create-if-absent a koordinace zapisovačů per-path zámky.
- Path cesty přehrávání/mazání a validace gramatických ID před výukou.
- Indexovaný batch save gramatiky: stejné S/F pořadí a LR, zhruba 97% pokles
  času v benchmarku 10k otázek / 1k odpovědí.
- vocabulary/save_workflow oddělil síťové obohacení od repository; izolovaný
  audio staging, revize, rollback a recovery pro neúspěšnou obnovu. Prázdné
  staré vazby se prořežou i před recyklací ID, při chybě se obnoví.
- Opravené zpracování nezměněného NaT v časování, aby se nezapsal jako text.
- Editorová cache počtů synonym a omezená cache resize bitmap s debounce.
- StatisticsController odstranil globální mutable stav. Datové výpočty ve
  workeru, příprava všech figur po UI krocích, cleanup a poslední přepnutí jazyka.
- summary_metrics sjednotil tři opakované konstrukce souhrnných karet.
- editor_navigation odstranil přímou kruhovou vazbu editor/theory editor.
- Odstraněné nepoužívané csv/Path/pandas importy a historická COLUMNS konstanta.
- Bezpečná diagnostika bez textů provider výjimek, manifest závislostí a
  explicitní kontext/importy přestavěných statistik; legacy facade zůstala.
- Zpřesněná kontrola skutečných UI textových sinků a deterministicky zadaná
  queued klávesová událost s ověřením doručení místo prodlužování čekání.
- Úplná samostatná projektová dokumentace: 18 hlavních souborů, 13 souborů
  diagramů (14 Mermaid bloků včetně ER), 121 produkčních modulů v katalogu.

Za opravené produkční chybové scénáře se zde počítá osm: dva ztrátové zápisy,
předčasné audio přesuny, chybná cesta, duplicitní grammar ID, hromadění bitmap,
kolize nově vzniklého souboru a NaT delta. Opravy dvou testových problémů,
architektonické a výkonové úpravy se do tohoto čísla nepřičítají.

## Zachované limity

Externí proces může změnit existující CSV v úzkém okně hash-check/replace;
vícesouborový save není garantovaně atomický při výpadku OS. Jedna složitá
Matplotlib figura stále pracuje v hlavním vlákně. Legacy styly a context
fallback v nedotčených screenech zůstávají pro kompatibilitu. Nebyl důvod
odstranit celý modul, měnit CSV schéma, výukové algoritmy nebo vizuální design.

Ověření a otevřené ruční scénáře jsou v TEST_RESULTS, konkrétní časy v
PERFORMANCE a stav každého A01–A17 v AUDIT. Zdrojový archiv je znovu ověřený
SHA-256; obnova nepotřebuje změny uživatelských CSV.

## Následná optimalizace grafů

Hover grafů převeden na blitting s invalidací při resize/full draw, fallbackem
pro nepodporovaný backend a cleanupem callbacků. SciPy odstraněna z přímých
závislostí; prognóza používá numpy.interp. Hodnoty zůstávají, hladká kubická
spojnice je nyní lineární. Doplněn test_chart_rendering a aktualizována
projektová dokumentace. Výše uvedené počty souborů patří původnímu refaktoringu.

## Aktualizace knihoven

Vytvořena čistá projektová .venv, instalovány poslední stabilní kompatibilní
wheel balíčky z PyPI. Aktualizovány přímé i tranzitivní závislosti;
requirements.txt obsahuje přímé verze, requirements.lock.txt úplný freeze.
VS Code profil VocabPro používá výslovně .venv; systémový Python ostatních
projektů nebyl měněn. Původní requirements je zachovaný pro návrat.
Klávesový GUI test nově ověřuje skutečný Windows focus před KeyPress.

## Nastavení, filtrování štítků a návrat ze cvičení (15. 11. 2026)

- Validační zprávy v nastavení mají společný zaoblený červený panel
  s přizpůsobením délky textu. Položky jsou seskupené pod lokalizovanými
  nadpisy a oddělené jemnými čarami. Vypnutí štítků zneaktivní související
  nastavení, jejich hodnoty zůstávají zachované.
- Words needing attention má menší odsazení a výšku řádků; překlady,
  historie, počty i pravidla výběru zůstaly zachované.
- Procvičování štítku nebo kategorie spuštěné ze statistik používá návratovou
  akci: Close i úspěšné Save obnoví statistiky stejného jazyka a záložky.
  Veřejné vstupy mají pouze volitelné nové argumenty; běžná navigace zůstává.
- Tag count je v editoru hned za Tags. Filtr už nemá nadbytečné tlačítko
  Filter: text používá debounce 250 ms, Enter a Apply v dialogu štítků
  filtrují hned. Refresh ruší dotaz, výběr štítků i řazení. Nabídka neobsahuje
  Phonetic, Repetition a Next repetition. Časovače a dialog vlastní lifecycle.
- Doplněné regresní testy a dokumentace GUI, konfigurace a navigace.
  Tato změna neupravovala produkční CSV ani jejich formáty.

## Vážené míchání gramatiky (15. 11. 2026)

Pevné řazení podle koncových S nahrazuje vážené náhodné pořadí bez opakování.
Pět normalizovaných signálů: rovnoměrnost 30 %, nezodpovězené 20 %, nedávné
chyby a míra zvládnutí 30 %, stáří LR 10 % a nižší počet odpovědí 10 %.
Výběr používá výhradně filtrované otázky; větší témata si zachovávají váhu
odpovídající počtu otázek. Všechny otázky se v dokončeném kole stále ukážou
právě jednou. Možnosti odpovědí se míchají samostatně.

Loader nově předává již existující LR jako `last_review`. Pracovní mapa
`GrammarSession.progress` zohlední skutečné neuložené odpovědi při restartu
i změně filtru bez mutace zdrojových záznamů. Zápisové delty, Save/Close,
reveal, skórování a CSV formáty zůstávají zachované. Nebyly přidány závislosti.

Přidáno 16 čistých regresních testů a jeden integrační GUI scénář. Původní
dvě kontroly pevného řazení nyní ověřují prioritu při stejném náhodném klíči;
skutečnou pravděpodobnost a náhodnost ověřují nové seedované simulace.

## Kompaktní přehled posledních odpovědí v grammar session (15. 11. 2026)

Session panel nově ukazuje úspěšnost posledních až 10 odpovědí v kole a malou
zeleno-terakotovou řadu výsledků. Před první odpovědí je přehled skrytý;
restart jej resetuje. Základem je omezená deque v GrammarSession, nikoliv CSV.
Duplicitní odpovědi a přeskočení nevytváří další výsledek. Reveal odpovídá
stávajícímu chybnému skóre. Všech šest jazyků má nový popisek lokalizovaný.

Při nedostatku výšky se automaticky zmenšují mezery; texty, tlačítka i celé
zkratky zůstávají zachované. Při zvětšení se vrátí normální odsazení. Skutečný
overflow u dlouhého obsahu se stále řeší scrollováním. Přepočet se slučuje
časovačem mimo vnořené CTk idle vykreslování; cleanup jej ruší.

## Kompaktní a seřaditelné kategorie gramatiky (15. 11. 2026)

- GrammarCategoriesPanel má menší vertikální odsazení a ukazatele, zachovává
  souhrny, pokrytí, S/F, úspěšnost i tlačítko procvičování každého tématu.
- Tři lokalizovaná tlačítka řadí počet otázek, počet různých procvičených
  otázek a úspěšnost. Opakovaný klik obrací směr; šipka a barva označují stav.
  Neznámá úspěšnost je poslední v obou směrech. Shody mají deterministické
  pořadí; výchozí slabší výsledky a vazby tlačítek na kategorie zůstávají.
- Řazení znovu používá hotové řádky bez změn CSV a zachová volbu při načtení
  jiného jazyka. Prázdný přehled má ovládání neaktivní.
- Odstraněn duplicitní Questions by grammar topic včetně jeho frame, přípravy
  dat, specifické větve grafu a stylu. Z vieweru zmizel nepotřebný pandas import.
- Při stejném šestipoložkovém vzorku jsou řádky o 16,9 % a celý přehled
  i s novým ovládáním o 13,7 % nižší. Přepočet statistik ani datové formáty
  se nemění; nebyly přidány závislosti.

# 2026-11-15 – Explicitní směr řazení statistiky štítků

- Panel `VocabularyTagsPanel` má vedle hledání samostatná lokalizovaná tlačítka
  pro vzestupné a sestupné řazení; aktivní směr je barevně odlišen.
- Směr se uplatní na právě vybranou metriku (počet slov, odpovědi nebo
  úspěšnost), při změně směru se stránkování vrátí na první stránku a neznámá
  úspěšnost zůstává vždy na konci.
- Načtení nové jazykové datové sady obnoví bezpečný výchozí stav: počet slov
  sestupně.

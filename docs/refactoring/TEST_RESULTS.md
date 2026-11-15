# Výsledky ověření výchozího stavu

## Lokální konfigurace SMTP odesílatele (15. 11. 2026)

Potvrzeno, že aktuální proces, uživatelské i systémové prostředí neměly ani
VOC_SMTP_USER, ani VOC_SMTP_PASSWORD. Jejich hodnoty ani příjemce nebyly vypsány.
Tím je vysvětlená konkrétní hláška před připojením SMTP, nikoli chyba doručení.

Prošlo 36 různých souvisejících testů: backup_account 7, app_backup 5,
backup_background 8, translations 8, localization_audit 5 a package_assets 3. Nové testy ověřují
Win32 datové rozhraní přes falešné API, Unicode hesla, vyprázdnění zapisovacího
bufferu, CredFree, neexistující záznam a odmítnutý přístup. Dále ověřují
použití uloženého účtu při chybějícím prostředí, TLS CERT_REQUIRED/hostname,
samostatnou konfiguraci bez odeslání, zachování prázdného hesla pouze stejnému
uživateli, chybové zprávy v šesti jazycích při 620×480, otevření jediného dialogu
a obnovení grabu nadřazeného nastavení. Uživatelský Windows trezor ani SMTP
server nebyly měněny/kontaktovány. Skutečné uložení do Windows a přihlášení
k serveru vyžadují lokálně zadané údaje uživatele; živé doručení není ověřeno.

## Jeden aktivní studovaný jazyk (15. 11. 2026)

Nových osm scénářů `test_single_language` ověřuje kompatibilní výchozí stav
dvou jazyků, povinný první jazyk, zákaz duplicit mezi aktivními jazyky,
opakované Save/Load přepínání, byte-for-byte zachování neaktivních CSV,
prázdných hlaviček i syntetického audia a nevytváření neaktivního kurzu.
GUI kontroluje zneaktivnění příslušných parametrů beze změny hodnot v šesti
jazycích, jednu širší kartu mainu, správnou sadu parametrů procvičování,
skrytý přepínač ve Stats a obnovení údajů po zapnutí druhého jazyka.

Prošly také preferences_data 12, home_data 7, app_context 10,
extended_scenarios 6, translations 8, statistics_practice_link 5 a skutečné
znovuotevření/přepnutí statistik z refactoring_integration 1. Související
produkční data nebyla přepisována; zápisové scénáře používaly dočasné adresáře.
Design matrix 3 rovněž prošla: celkem 60 různých souvisejících testů, bez
selhání a přeskočení. Poslední kontrola zachování dat navíc výslovně zahrnuje
CSV časování a rekordů gramatiky. Celá nesouvisející sada nebyla opakována.

## Rozšířené scénáře a celá sada (15. 11. 2026)

Celý runner `app.tests.run_all --timeout 180` dokončil 76 modulů a 471 testů,
bez přeskočení. První průchod měl 470 úspěšných testů a jedno selhání:
`test_extended_scenarios.test_repeated_preference_updates_never_reset_unrelated_values`.
Test nepočítal s migrací pěti přidaných výchozích voleb. Jeho očekávání nyní
výslovně zahrnuje tyto volby a stále porovnává celé mapování původních hodnot;
následný běh všech šesti testů modulu prošel. Nešlo o reset uživatelských dat.
Původní log je `.refactoring-recovery/scenarios_20261115/full-suite.log`.

Šest nových scénářů bylo již součástí celé sady. Sedmý byl dokončen později
a samostatně nejprve odhalil skutečný překryv dlouhých štítků se slovem
(spodní hrana zadání s mezerou 525 px, horní hrana štítků 513 px).
Po opravě prošel pro překlad, kontext i audio při 1150×800 a kontroluje
také dostupnost tlačítka Next. Dále prošly související practice_tags 3
a learning_ui 18. Jde tedy o 472 různých ověřovaných testů; po opravách
nebyla podruhé spuštěna celá nesouvisející sada.

Závěrečný společný běh všech sedmi nových scénářů prošel za 80,3 s,
bez selhání a přeskočení. Dodatečné ověření přechodu na otázku bez štítků
také prošlo: karta se vrátí na výšku 260. Po této poslední úpravě znovu
prošly dotčený scénář, practice_tags 3 a learning_ui 18. Nezůstává známý
selhávající test. Výkonová část posledního běhu naměřila 288,4 ms;
rozptyl lokálních měření není vydáván za garantovaný výkon.

Kontroly nastavení zahrnují šest jazyků, všechny čtyři záložky a geometrie
950×650 / 1400×900. Výběr ze 120 dlouhých štítků kontroluje celý text,
deset přiřazení, filtrování a návrat scrollu nahoru. Session scénář střídá
dlouhé a prázdné štítky dvacetkrát v každém jazyce. Seedovaný množinový
model prověřuje 90 kombinací filtrů nad 400 slovy. Hromadný převod 10 000
řádků kontroluje oba jazyky, ID, duplicity, neměnnost vstupu a neplatný
poslední řádek. Živé služby, mikrofon a zápisy do produkčních dat blokoval
izolovaný runner. Jiná DPI a skutečné doručení e-mailu vyžadují ruční kontrolu.

Naměřeno: tagový převod/filtr/validace 180,9 ms v celé sadě; statistiky
10 000 otázek 51,1 ms za studena / 1,29 ms medián z cache; agregace
50 000 otázek 32,9 ms. End-to-end GUI měření velkého katalogu není stabilní
důkaz zrychlení (53,0 → 65,4 s); zůstává kandidátem pro cílené profilování.

## Rekord série v gramatice (15. 11. 2026)

28 různých souvisejících testů prošlo: nové grammar_records 4, čtyři
stávající GUI scénáře grammar_session_insight, stats_grammar_categories 8,
translations 8 a grammar_deferred_save 4. První běh zděděné GUI scénáře
opakoval; nový modul nyní sdílí pouze fixture a spouští své čtyři testy.

Ověřeno chybějící/neplatné metadata, maximum bez snížení, oddělení jazyků,
rollback při neúspěšném zápisu odpovědí, opakování Save bez zdvojení odpovědí,
shoda versus překonání rekordu a restart session. Statistiky načtou změněný
rekord i při nezměněném CSV otázek v cache. Šest jazyků zachovává čitelný
sidebar a kategorie. Zápisové scénáře používaly pouze dočasná syntetická data.
Produkční CSV nebyla přepisována ani migrována. Historický rekord před
zavedením funkce nelze zjistit z per-otázkových R a není odhadován.

## Jednotné cyklické řazení (15. 11. 2026)

30 různých souvisejících testů prošlo: sorting_cycle 1, statistics_tags 8,
stats_grammar_categories 8, statistics_table_layout 3, dva cílené GUI scénáře
synonyms_ui pro řazení editoru a translations 8. Ověřeny tři kroky cyklu,
změna metriky, obě orientace, návrat původního pořadí, zachování filtru a
editovaných buněk, stránkování, callbacky kategorií a šest lokalizací.
Test původního automatického řazení byl aktualizován na nově požadovaný
neutrální stav a následně prošel. Zápisy používaly syntetická data, produkční
CSV nebyla touto změnou měněna.


## Kontrola zkratek a štítků (15. 11. 2026)

25 souvisejících testů prošlo bez selhání nebo přeskočení: test_translations 8,
test_localization_audit 5, test_shortcut_hint_layout 2, test_practice_shortcuts 7,
dva nové testy WordTagUiTests a lokalizovaný layout katalogu štítků 1.

Ověřeny skutečné události Ctrl+T, Ctrl+Shift+T, Ctrl+F a Ctrl+Enter (i z entry),
výběr bez označeného slova, změna přiřazení pouze v pracovní kopii, vypnuté
štítky, ukládání, modální okno a odstranění bindingů při zavření obrazovky.
Nápovědy byly vykreslené v šesti jazycích při šířkách 240, 650 a 1100.
Kontrola AST porovnává vlastní zkratky s About app včetně Shift a Ctrl+Enter;
všechny popisky existují ve všech katalozích. Produkční CSV nebyla měněna.
Celá nesouvisející sada se znovu nespouštěla.

## Směr řazení statistiky štítků (15. 11. 2026)

- `app.tests.test_statistics_tags`: 8/8 testů prošlo.
- Ověřeno vzestupné i sestupné řazení, přepínání metrik, návrat na první
  stránku, nulové odpovědi, neznámá úspěšnost vždy na konci a reset při načtení
  jiné datové sady.
- Obě směrová tlačítka byla vykreslena a jejich text se vešel ve všech šesti
  podporovaných lokalizacích. Produkční CSV nebyla měněna.

## Následné ověření štítků slovíček

ID, konfigurace a lekce: 92 různých souvisejících testů prošlo:
test_tag_id_upgrade 7, test_word_tag_selection 12, test_tag_catalog 11,
test_statistics_tags 6, test_practice_tags 3, test_translations 8,
test_preferences_data 12, test_editor_save 7, test_localization_audit 5,
test_vocabulary_tag_filter 6, test_stats_cache 5, test_stats_difficult_words 2,
test_vocabulary_tags 7 a importní kontrola všech produkčních modulů 1.
Pokryty codec obou jazyků, neznámé ID/názvy, cleanup, limit, zablokování
smazání používaného ID, lekce s prázdnou historií a termínem, stabilní pořadí
po dokončení slova, nulový/neexistující štítek, disabled tlačítko, nastavení,
immediate paste validace, zobrazení/skrytí a číselné filtry počtu.

Starší test nesprávně předpokládal neměnný počet 91 položek v uživatelském
katalogu (uživatel jej mezitím upravil na 65). Nyní kontroluje skutečný
kontrakt unikátních ID a neprázdných názvů. Očekávání textových Tags při
zápisu byla změněna na výslovně požadovaná ID; fixture starého UI určuje
Student language. Test neplatného paste nyní očekává okamžité odmítnutí,
nikoliv dřívější čekání na Save. Původní běh se zasekl na nové chybové hlášce
a byl ukončen; po opravě interakce testy prošly. Nebyly vypnuty žádné testy.

Migrace produkčních CSV zvlášť porovnala buňky i pořadí: 2 677 anglických
a 2 846 španělských slov, změněn pouze Tags; neplatných vazeb 0.
Kompletní nesouvisející sada aplikace nebyla opakována. Živý poslech a
ruční vizuální kontrola na uživatelově DPI nejsou tímto během pokryty.

Kompaktní zelený panel: prošel cílený GUI test
`WordTagUiTests.test_editor_footer_and_picker_fit_all_languages` (šest jazyků).
Jednorázová kontrola při šířce okna 1500 logických pixelů naměřila výšku
159,2 → 96,0 logických pixelů a ověřila neprolínání textů s tlačítky.
Při šířce 1100 se obnovilo skládané rozložení. CSV se nekontrolovala zápisem
ani neměnila; další nesouvisející testy nebyly spouštěny.

Kvantifikovaný filtr štítků: 28 různých souvisejících testů prošlo:
test_vocabulary_tag_filter 6, test_vocabulary_editor_data 6,
test_translations 8, test_localization_audit 5,
test_vocabulary_editor_dropdowns 1 a dva cílené GUI testy původního přiřazení
štítků (výběr během hledání / přiřazení při filtru). Nové testy ověřují
všechny tři množinové operace, prázdný výběr, stará data, pořadí a duplicity,
přepínání text/štítky, zrušení dialogu a zachování skrytých editací i CSV.
Kontrola rozložení v šesti jazycích byla zopakována samostatně po doplnění
adaptivní šířky operátoru a měření jeho popisků.

Zobrazení štítků v Repeat: 15 souvisejících testů prošlo. Nová sada
test_practice_tags 3/3 ověřuje překlady a fallback, skutečné GUI pro španělštinu
a angličtinu při anglickém UI, aktuální slovo, chybnou odpověď, Session,
Review word, skrytí prázdných štítků a neměnnost zdrojového CSV. Dále prošly
test_translations 8/8 a čtyři cílené regresní GUI testy: rozložení a režimy
Repeat, Session se synonymy, zachování předešlého slova při skip/chybě a
callbacky tlačítek Review. Testy používají dočasná data bez skutečného audia.

Statistiky štítků: 24 souvisejících testů prošlo (test_statistics_tags 6,
test_stats_cache 5, test_translations 8, test_localization_audit 5).
Prvních pět nových testů proběhlo v modulu, následný šestý integrační test
StatisticsController/worker byl spuštěn samostatně. Pokryty překrývající se
štítky, duplicity, vážení úspěšnosti, prázdné/stará CSV, pravidla úvodního
učení, cache hit bez opakovaného čtení, invalidace při změně Tags, stránkování,
hledání, řazení a reset dat. V šesti jazycích s dlouhými názvy a 91 položkami
ověřeno nejvýše pět viditelných řádků a výška panelu pod 430 logických pixelů.
Testy pracují pouze s dočasnými CSV; produkční soubory se neměnily.

Vkládání štítků z Excelu: dva nové cílené GUI testy prošly. Používají skutečnou
Tk schránku a `tksheet.paste`, nikoliv programové nastavení buněk. Ověřují
vložení více řádků i více štítků v buňce, správné přiřazení při aktivním filtru,
zachování ID/historie a odmítnutí neznámého štítku před spuštěním save workeru.
Při odmítnutí se původní dočasné CSV nezměnilo. Produkční data se neměnila.

Výběr štítků pouze z katalogu a přesun tlačítka: 57 různých souvisejících
testů úspěšných (bez přeskočení): test_word_tag_selection 10, test_tag_catalog
11, test_translations 8, test_editor_save 7, test_editor_async_ui 1,
test_vocabulary_editor_data 6, test_vocabulary_tags 7,
test_localization_audit 5, test_vocabulary_editor_dropdowns 1 a importní
test všech produkčních balíčků 1. Desátý test výběru (dvojklik do buňky Tags)
byl doplněn a spuštěn samostatně po úspěchu předchozích devíti.
Nové scénáře ověřují více štítků, udržení výběru během hledání, zrušení,
přiřazení podle ID při aktivním filtru, neměnnost CSV před hlavním Save,
odmítnutí neznámého štítku z importu před API operacemi a konflikt změny
katalogu během ukládání. Rozložení dolních tlačítek ověřeno v šesti jazycích.
První běh nových GUI testů zachytil nesprávné volání testovacího checkboxu
(`invoke` místo podporovaného `toggle`); po opravě testovací interakce prošly.
Produkční CSV nebyla v tomto kroku upravována.

Katalog štítků: 35 souvisejících testů úspěšných, bez přeskočení:
test_tag_catalog 11/11, test_vocabulary_tags 7/7, test_translations 8/8,
test_localization_audit 5/5, test_course_files 3/3,
test_vocabulary_editor_dropdowns 1/1. Nové testy pokrývají CSV/BOM,
neplatné ID/názvy, souběžné změny, selhání zápisu a opakovaný Save, zálohy,
tabulkové přidání/mazání bez přečíslování a bez přepsání slovníku,
zavření bez uložení, UI v šesti jazycích a otevření správného katalogu z editoru.
Čtením ověřeno 91 položek a překlady v obou skutečných nových katalozích.

Po rozšíření na více štítků prošlo 27 souvisejících testů: test_vocabulary_tags
7/7, test_translations 8/8, test_vocabulary_editor_data 6/6, test_module_panels
6/6. Ověřeny duplicity, prázdné položky, přesné hledání jednotlivých štítků,
neměnnost ostatních polí, CSV roundtrip a GUI. Nový test byl zpřesněn na porovnání
s původním `prepare_save`, které již z historických důvodů odstraňuje `Enabled`.

Cílené testy: test_vocabulary_tags 4/4, test_editor_save 7/7,
test_course_files 3/3, test_vocabulary_editor_data 6/6, test_translations 8/8,
test_vocabulary_editor_dropdowns 1/1, test_synonyms_ui 23/23 a
test_editor_async_ui 1/1. Celkem 53 různých testů ověřeno jako úspěšných;
u synonymního GUI byl po rozšíření očekávané hlavičky opakován jen dotčený test,
ostatních 22 již prošlo. Mock asynchronního editoru doplněn o nový datový kontrakt.
Nové testy používají dočasné CSV; migrace skutečných CSV zvlášť ověřila všechny
původní buňky i prázdné štítky. Kompletní nesouvisející sada nebyla opakována.

15. 11. 2026. První část zachovává výchozí stav auditu; závěr obsahuje
ověření implementace. Požadované výsledky testů nebyly oslabeny.

## Celá sada

```text
python -B -u -m app.tests.run_all --timeout 180
335 tests; 0 skipped; 2 failed modules / 58.
```

333 testů prošlo, 2 testy selhaly; 56 modulů prošlo, 2 moduly měly selhání.
Nebyl hlášen timeout ani test přeskočený kvůli chybějícímu GUI. Spouštěč vrací
exit code 1, takže výchozí stav není zelený. Testy běžely v izolovaných
procesech s blokací skutečné sítě, SMTP, mikrofonu, přehrávání a zápisů do
files/images/locales. Existující kontrola funkčnosti těchto blokací prošla.

Prošly mimo jiné storage (3), repositories (5), editor_save (7), synonyms (10),
synonyms_ui (23), training_data (17), training_sessions (8), preferences_data
(12), stats_cache (5), performance_regressions (4), package_assets (3),
learning_ui (18), app_context (10) a screen_controller (8).
Počty jednotlivých modulů je nutné číst jako součást celkových 335, nikoli
jako další testy navíc. Podrobné počty jsou v původním logu; výše uvedený
výběr nenahrazuje tvrzení o všech modulech.

## Dvě selhání a jejich ověření

1. `test_grammar_deferred_save.GrammarNavigationTests.test_clean_back_and_deferred_save_cancel_discard_and_keyboard_save`
   v hromadném běhu: po event_generate('<Control-s>') zůstala pending_answers
   neprázdná. Stejný test spuštěný samostatně prošel (1/1); opakování celého
   modulu také prošlo (4/4). Evidováno jako nestabilita událostí/fokusu nebo
   jiný timing problém, nikoli prokázaná trvalá chyba save. Příčina dosud
   není uzavřena. Nedělat změnu očekávání nebo slepě prodlužovat sleep.
2. `test_localization_audit.LocalizationAuditTests.test_no_raw_english_widget_text_and_shared_ui_titles_are_in_catalog`
   vykazuje šest výskytů tří různých zpráv. AST pravidlo posuzuje i interní
   keyword message u repository a lifecycle metod jako přímý text UI.
   Všechny tři zprávy existují ve všech šesti JSON katalozích; cesty prezentace
   je překládají. Jde o prokázanou nepřesnost testu, nikoli šest chybějících
   překladů. Opravit cílení pravidla a zachovat kontrolu skutečných UI sinků.

Samostatná opakování zvyšují počet testových spuštění o 5, nikoli počet
unikátních testů. Neznamenají, že celá původní sada dodatečně prošla.

## Diagnostické experimenty mimo regresní sadu

Vše pouze v TemporaryDirectory, se syntetickými tabulkami a falešnými audio
bajty; nevznikl nový trvalý testovací script:

| Scénář | Výsledek |
|---|---|
| Externě upravený text mimo výběr časování, poté save_results ze starého snímku | Novější text byl přepsán; A01 potvrzeno. |
| Externě upravený popis slovíčka, poté save_practice s nezměněným starým popisem | Novější popis byl přepsán; A02 potvrzeno. |
| Nové/recyklované ID s existujícím falešným MP3, CancelledError při obohacení | CSV necommitnuto, MP3 již archivováno; A03 potvrzeno. |
| Výpočet editorové audio cesty bez koncového oddělovače | Liší se od správné Path cesty; A04 doloženo. Callback s reálným audiem nebyl spuštěn. |
| Grammar CSV se dvěma stejnými question_id | Loader přijme obě otázky; A05 potvrzeno. |
| Dvacet resize variant CTkImage | Cache uchová všech 20; A08 potvrzený mechanismus. |

Tyto experimenty dokazují uvedené problémy. **Nejsou úspěšnými regresními
testy opraveného kódu**. Před implementací se z nich mají stát trvalé testy
se správným požadovaným chováním a ověřeným počátečním selháním.

## Zbývající rizika a neověřené oblasti

- Živé SMTP/API, výpadky skutečného mikrofonu, hardwarové audio a omezení
  poskytovatelů nebyly testovány. Používají se mocky a testy parsování/transportu.
- Strukturální kontrola skutečných CSV není úplný obsahový audit každé otázky.
- Plošné pokrytí všech větví nebylo měřeno; 335 testů není důkaz bezchybnosti.
- Neběžel dlouhodobý soak test nebo měření celkové RSS při několikahodinové práci.
- Více souběžných instancí a atomické potvrzení více souborů nejsou garantovány.
- Neproběhla pixelová kontrola všech kombinací rozlišení, DPI a překladů;
  existující testy layoutu a překladů pokrývají jen své definované scénáře.

Následné testování: kritické regrese ukládání/rušení/konfliktů, po každém
implementačním kroku pouze dotčené části, na konci celá sada a původní
výkonové scénáře. Toto byl výchozí plán; skutečný výsledek je níže.

## Konečný výsledek implementace

```text
python -B -u -m app.tests.run_all --timeout 180
355 tests; 0 skipped; 0 failed modules / 60.
Exit code: 0
```

Všech 335 původních testů a 20 nových regresních/integračních testů prošlo.
Nebyl vypnut žádný test ani oslabeno očekávání jen kvůli zelenému výsledku.
Nový testovací soubor safety má 7 testů, integration má 13 testů.

Před opravou nový safety modul vykázal 4 selhání a 3 chyby; po opravě 7/7.
Mezilehlé běhy zachytily chybějící mock po odstranění pd importu, chybějící
dočasný CSV fixture po zpřísnění source read, uvolnění kontroléru a kolizi
Created u testovacího editačního frame. Mocky byly přesunuty na skutečné
hranice, doplněny fixture/byte kontroly a opraveny implementační problémy.
Neúspěšné mezilehlé výsledky nebyly vydávány za úspěch.

Po významných celcích proběhly cílené kontroly ukládání, nových regresí,
slovníkových modulů, záhlaví, cache a statistik. Před konečným během prošla
i úplná sada 348 a následně 354 testů; poslední výše uvedená sada už obsahuje
celý aktuální rozsah 355, včetně skutečných Matplotlib oken.

Nové integrační scénáře ověřují:

- Atomický create-if-absent při kolizi přímo v okamžiku publikování.
- Zachování cizích polí a atomické odmítnutí stejného změněného pole.
- Zrušení před commitem bez přesunutého původního audia.
- Obnovu audia i synonym po selhání finálního CSV, recyklaci ID bez zděděných
  starých vazeb, selhání provideru/archivu a možnost opakovaného save.
- NaT/datumové ekvivalence, aby nezměněné LR nevytvořilo neplatný text.
- Jedno čtení relací pro opakované aktualizace a invalidaci při změně CSV.
- Bezpečné logování bez citlivé zprávy výjimky.
- Hlavní vlákno pro grafy, worker pro data, UI heartbeat a přípravu všech grafů.
- Zavření během workeru, uvolnění controlleru, poslední požadavek na jazyk,
  dvě skutečná otevření statistik, přepnutí dostupnosti conjugation a resize.
- Omezený počet bitmap na skutečném background helperu.

Klávesový scénář explicitně kontroluje i doručení queued Ctrl+S události.
AST lokalizační kontrola dále chrání skutečné UI sinky a katalogy, místo aby
mylně odmítala interní parametr message.

## Kontrola zdrojů a dokumentace

- Všechny Python soubory prošly AST parsováním; package/import a asset testy
  prošly v úplné sadě. git diff --check bez whitespace chyb.
- Zdrojový návratový archiv byl znovu porovnán s SHA-256 manifestem.
- Git neukazuje změny ve files, images, locales ani sandbox.py. Nebyla použita
  destruktivní operace Gitu nebo produkční data k destruktivním scénářům.
- Katalog přesně pokrývá 121 produkčních modulů včetně start a značek balíčků.
- Projektová dokumentace má 31 souborů, z toho 13 diagramových; 14 Mermaid
  bloků včetně ER. Všech 977 relativních odkazů v této dokumentaci má cíl.
- Mermaid byl kontrolován strukturálně (fences, deklarace, tokeny hran,
  párování popisků a ER struktura). Plný Mermaid renderer/CLI není v prostředí
  dostupný; vizuální render ve VS Code/GitHubu zůstává ruční kontrolou.

## Co stále ověřit ručně

Skutečný mikrofon a přehrávání s ovladači, živé SMTP/API a jejich kvóty,
vzhled všech obrazovek na uživatelově DPI a vykreslení Mermaid v cílovém
editoru. Čistá online instalace do nového venv nebyla provedena; manifest
odpovídá verzím skutečně otestovaného lokálního prostředí. Několikahodinový
soak test a výpadek OS uprostřed vícesouborového commitu nejsou simulovány.

Zbylý technický dluh: legacy facade v nedotčených modulech, čas jedné velké
Matplotlib figury v UI vlákně, neúplná víceprocesová izolace existujících CSV
a absence plné crash-recovery transakce přes CSV/audio/vazby. Tato omezení
jsou zdokumentována; nejsou skrytě vydávána za opravená.

## Následná změna: hover blitting a odstranění SciPy

Spuštěny související sady přes izolovaný runner: test_chart_rendering 7/7,
test_learning_ui 18/18 a test_refactoring_integration 13/13.
Celkem 38 testů prošlo, žádné selhání nebo přeskočení. Celá dřívější sada
355 se kvůli lokální změně neopakovala. Nové testy kontrolují přesné obnovení
pixelů, skutečný Tk hover, resize, fallback backendu, cleanup a interpolaci.
Integrační sada ověřila i skutečné statistiky při změně jazyka a zavírání.
Benchmark při opakování: 364,62 ms plný draw / 23,27 ms blit pro 20 aktualizací
rastrové části. git diff --check bez whitespace chyb.

## Aktualizovaná sestava knihoven v projektové .venv

Čistá instalace binárních wheelů: CustomTkinter 6.0.0, tksheet 7.6.0,
pandas 3.1.1, NumPy 2.5.4, Matplotlib 3.11.2, Pillow 13.0.0, requests 2.34.2;
pygame 2.6.1, PyAudio 0.2.14 a pywinstyles 1.8 beze změny. Úplná sestava je
v requirements.lock.txt. pip check: No broken requirements found.
Import start.py prošel; SciPy není v novém prostředí nainstalovaná.

Úplná sada v nové .venv: 362 testů, 0 přeskočených, 1 neúspěšný test v jednom
ze 61 modulů. Příčinou byla odlišná konverze zlomkového DPI pixelu (7 vs 8)
v test_module_panels. Test nyní ověřuje přesné logické pady (6,12) a fyzické
pixely s tolerancí nejvýše jednoho pixelu; aplikační rozložení nebylo měněno.
Následné opakování celého dotčeného modulu: všech 6 testů prošlo. Ostatních
60 modulů prošlo v úplném běhu; celý běh se po čistě testové opravě neopakoval.

První průzkumný běh zachytil také dříve známé nedoručení syntetického Ctrl+S.
Samostatná opakování prošla; test doplnil čekání na skutečný nativní focus
Windows před KeyPress. Následný úplný běh tuto kontrolu prošel.
Jeden starší rozpracovaný běh byl ukončen, aby GUI sady neběžely souběžně.

Spouštět `.\.venv\Scripts\python.exe start.py` nebo profil VocabPro ve VS Code.
Systémové balíčky ostatních projektů nebyly aktualizovány. Živý mikrofon,
API/SMTP a všechna uživatelská DPI stále vyžadují uvedenou ruční kontrolu.

## Nápověda z písmen na vyžádání

Cílené sady: test_letter_hints 3/3, test_preferences_data 12/12,
test_learning_ui 18/18, test_localization_audit 5/5, test_translations 8/8.
Celkem 46 různých souvisejících testů prošlo. Katalogový test nejprve zachytil
řazení nových klíčů; katalogy byly seřazeny a opakování prošlo. Ověřeno
uložení všech tří režimů, kompatibilní výchozí hodnota bez zápisu starého CSV,
reset odhalení, vypnutí a potlačení hintu u audio otázek. Produkční settings
nebyl přepsán; nové nastavení se uloží běžným Save v dialogu.

## Nastavení a navigace štítků (15. 11. 2026)

Ověřeno 113 různých souvisejících testů ve 13 modulech; po níže popsaných
opravách všechny prošly, žádný nebyl přeskočen. Použita projektová `.venv`
a izolovaný runner `app.tests.run_all --worker`; GUI sady běžely postupně.

| Modul | Počet |
| --- | ---: |
| test_tag_ui_followup (nový) | 9 |
| test_vocabulary_tag_filter | 6 |
| test_statistics_practice_link | 5 |
| test_training_controllers | 8 |
| test_learning_ui | 18 |
| test_shared_controls | 9 |
| test_vocabulary_editor_dropdowns | 1 |
| test_tag_id_upgrade | 7 |
| test_synonyms_ui | 23 |
| test_preferences_data | 12 |
| test_translations | 8 |
| test_localization_audit | 5 |
| test_stats_difficult_words | 2 |

Nové scénáře ověřují automatický filtr a jeho zrušení při zavření, reset
štítků/řazení, pořadí sloupců, deaktivaci nastavení bez ztráty hodnot,
validační banner a nadpisy skupin ve všech šesti jazycích, návratové callbacky
Close/Save, zachování statistik při neúspěšném spuštění a skutečné znovuotevření
statistik na druhém jazyce a záložce Grammar. Grafy jsou v posledním scénáři
nahrazené mockem; načítání dat a navigace používají skutečné implementace.
Kompaktní statistika zachovává všech šest řádků, texty i historii.

Průběžné kontroly zachytily staré očekávání pořadí sloupců v test_synonyms_ui,
nesprávnou jednotku při DPI kontrole výšky a syntetický vzorek, který nesplňoval
pravidlo tabulky pro naučená slova (> 4 záznamy S). Očekávání pořadí bylo
aktualizováno podle zadání, výška se kontroluje v logických pixelech a vzorek
nyní splňuje existující pravidlo. Příslušné testy následně prošly; celá dlouhá
sada synonym se po opravě jediného pořadového očekávání znovu neopakovala.

Zápisové testy používaly syntetická CSV v dočasných adresářích a kontrolovaly
jejich obsah. Produkční CSV nebyla touto úpravou přepsána. `git diff --check`
prošel. Celá projektová sada se kvůli této lokální úpravě neopakovala.
Vzhled na všech možných uživatelských DPI zůstává ruční kontrolou.

## Vážené míchání gramatiky (15. 11. 2026)

69 různých souvisejících testů v 9 modulech prošlo, bez selhání a přeskočení:
test_grammar_selection 16, test_training_data 17, test_training_sessions 8,
test_grammar_category_filter 4, test_grammar_deferred_save 4,
test_grammar_theory 3, test_training_controllers 8,
test_statistics_practice_link 5 a test_workflows 4.
Spuštění přes projektovou `.venv` a bezpečnostní wrapper `run_all --worker`;
GUI sady běžely postupně, produkční CSV nebyla testovacími zápisy dotčena.

Nové kontroly pokrývají všechny váhové signály, součet pravděpodobností,
nehladovění zvládnutých otázek, zastoupení velkých/malých kategorií,
statistické rozložení 12 000 kol s pevným seedem, opakovatelnost generátoru,
jedinečnost ID v kole a prázdnou/jednoprvkovou množinu. Ověřeno chybějící,
neplatné, budoucí i časovou zónou opatřené LR, zachování BOM/Unicode/001,
zkrácené řádky CSV a uložení dvou kol bez zdvojení historie.

Reálný kontrolér prošel změnou filtru Articles → Tenses → Articles po chybné
odpovědi; stará odpověď zůstává pending, nová fronta zohlední její pracovní
historii a jiné kategorie do kola neproniknou. Ověřeny restart, odhalení,
přeskočení, teorie, chyby ukládání a návrat do statistik. Celá projektová
sada se při této cílené změně znovu nespouštěla. Měření přípravy 10 000 otázek
a rozložení výběru jsou v projektové dokumentaci PERFORMANCE.md.

## Kompaktní grammar session a poslední odpovědi (15. 11. 2026)

34 různých souvisejících testů prošlo bez selhání a přeskočení:
test_grammar_session_insight 6 (nový modul), test_training_sessions 8,
test_translations 8, test_module_panels 6, test_localization_audit 5
a jeden cílený test gramatického skórování z test_learning_ui.
GUI sady běžely postupně přes izolovaný runner; zápisy do produkčních dat
jsou v něm blokované. Celá projektová sada se kvůli této lokální změně neopakovala.

Nové testy ověřují chronologické okno nejvýše 10 odpovědí, správné procento,
barvy, odhalení, přeskočení, duplicitní odpověď, restart a absenci nového
zápisu historie. Všech šest jazyků při geometrii 1400×850 zachovalo celý
sidebar bez scrollbaru a nový přehled do 42 logických pixelů výšky. Testované
zmenšení na 1400×650 aktivovalo kompaktní mezery; zvětšení na 1400×1000
obnovilo normální odsazení. Písmo zkratek zůstalo 12. Dlouhý název kategorie
je stále scrollovatelný a zničení během resize nevyvolalo callback výjimky.

Průběžné testy odhalily vnořený idle přepočet při CTk vykreslování a neplatný
předpoklad o interním geometrickém atributu CTkScrollableFrame. Obojí bylo
opraveno: přepočet používá slučovaný 20ms timer a změnu vnějšího odsazení
sleduje vlastní stav. Původní zaseknutý test byl ukončen, následný úplný běh
nového modulu prošel. Náhled s 7 syntetickými výsledky byl vizuálně zkontrolován.

Kontrola whitespace dotčených zdrojů, překladů a dokumentace prošla.
Celoprojektový git diff --check byl blokován přístupem k souboru audia mimo
rozsah úpravy. Kontrolní hashe tří produkčních CSV se během práce změnily;
tato změna do nich nezapisuje a žádná taková data nebyla obnovována ze zálohy.
Nový přehled zůstává výhradně v paměti, produkční obsah není součástí testovacích
fixtures. Vzhled na jiných DPI stále vyžaduje běžnou ruční kontrolu.

## Seřaditelné kompaktní kategorie gramatiky (15. 11. 2026)

29 souvisejících testů prošlo, žádný nebyl přeskočen: test_stats_grammar_categories
8, test_translations 8, test_chart_rendering 7, test_statistics_practice_link
5 a test_real_statistics_reopen_and_language_switch_prepare_all_figures
z test_refactoring_integration 1. GUI testy běžely postupně v projektové `.venv`
přes bezpečnostní wrapper, zápisové scénáře používaly pouze dočasné soubory.

Kontrolováno číselné řazení 10/20/100, obě orientace, rozdíl mezi počtem
různých procvičených otázek a opakovanými odpověďmi, 0 % oproti neznámé
úspěšnosti, deterministické shody, prázdná data, zachování všech souhrnů,
identity hotových widgetů a callbacků kategorií po přerovnání. Nová data
z jiného jazyka zachovají zvolené řazení a odstraní staré řádky.

Geometrie byla ověřena v šesti jazycích při šířce 600 i 1200: popisky jsou
celé, tlačítka se vejdou. Kompaktní rozpočet 110 logických pixelů na běžný
řádek se kontroluje při šířce 1200. První pokus vztahoval tento rozpočet
i na úzké zalomené texty; kontrola nyní odděluje kompaktní běžnou šířku od
úplné čitelnosti v úzkém okně. Povolené zalamování nebylo potlačeno.

Skutečné otevření/zavření statistik a přepnutí mezi dvěma jazyky prošlo
dvakrát; ostatní figury jsou připravené, odstraněný grammar_topics_chart
nevzniká a nový sort funguje. Souhrnné testy hoveru a uvolnění zbývajících
grafů prošly. Výchozí a nová výška byly změřeny na stejných šesti syntetických
kategoriích; výsledky jsou v projektovém PERFORMANCE.md. Tato úprava do
produkčních CSV nezapisuje. Celá projektová sada se znovu neopakovala.

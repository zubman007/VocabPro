# Technický audit VocabPro

Datum: 15. 11. 2026. Původní nálezy níže jsou historický výchozí stav.
Schválená implementace byla provedena; aktuální stav je v závěrečné tabulce.

## Rozsah a metoda

- Statická analýza všech 180 Python souborů v `app/`: 117 produkčních modulů
  (8 488 řádků) a 63 souborů testů a jejich infrastruktury. Navíc `start.py` a
  `sandbox.py`; sandbox nebyl spuštěn ani změněn.
- AST kontrola definic, importů, velikostí funkcí a závislostí, následovaná
  ručním průchodem kritických cest: start, navigace, editory, procvičování,
  repositories, zápisy, audio, zálohy, statistiky, společné UI a lokalizace.
- Výchozí sada: 335 testů v 58 modulech. Samostatné reprodukce na syntetických
  souborech; měření importů, agregací, ukládání a cache obrázků.
- Čistě čtecí kontrola struktury deseti skutečných CSV: počet polí, chybějící
  pole, prázdná a duplicitní ID. Nebyly vypisovány hodnoty nastavení ani klíče.
- Ověření obrazových zdrojů a jejich odkazů existujícími testy.

Statická reference není důkaz vykonání každé větve. Callbacky, zděděné metody,
reexporty a dynamické importy nebyly automaticky označovány za mrtvý kód.
Neproběhlo živé volání API, e-mailu, mikrofonu ani destruktivní testování dat.

## Co je již dobře

Projekt má členění podle modulů, `AppContext`, samostatné stavy výukových kol,
`ScreenController`, společné vizuální komponenty a vrstvu `repositories`.
`storage.save_csv` zapisuje do dočasného souboru, provádí flush/fsync a teprve
potom nahrazuje cíl. Testy potvrzují zachování původního CSV při selhání zápisu
i nahrazení. HTTP a WAV zápisy používají obdobný postup. Editor slovíček a
e-mailové zálohy pracují na pozadí. Statistiky mají omezenou cache výsledků a
podklad, který se při samotném scrollování znovu nerasterizuje.

To jsou části k zachování, nikoli důvody k celkovému přepisu.

## Nálezy podle priority

P1 = riziko ztráty změn nebo zásahu do souborů; P2 = významná funkční,
výkonová či architektonická slabina; P3 = údržba a menší nedostatky.
„Reprodukováno“ znamená syntetický scénář, nikoli zásah do uživatelských dat.

| ID | Priorita / jistota | Důkaz | Dopad a navržená náprava |
|---|---|---|---|
| A01 | P1, reprodukováno | `repositories/conjugation.py:16`, `save_results` vychází z původního `all_df`. Novější text u jiného ID v cílovém CSV byl v experimentu přepsán. | Číst aktuální dokument při ukládání, zapisovat pouze změny vlastněné relací; ověřit identitu a očekávané hodnoty. Odmítnout konflikt místo tichého přepsání. |
| A02 | P1, reprodukováno | `repositories/vocabulary.py:34`, `save_practice` kopíruje ze session vedle historie i Audio/Description/Example. Novější externí Description byl přepsán starší hodnotou, i když jej session neupravovala. | Rozlišit změněné atributy a nezměněný snímek; zachovat cizí úpravy, při kolizi stejného pole oznámit konflikt. |
| A03 | P1, reprodukováno | `repositories/vocabulary.py:69–74`: pro nové ID se prořezávají vazby a archivuje existující audio ještě před obohacením a CSV commitem. Vynucené zrušení obohacení ponechalo původní CSV, ale audio již přesunulo. | Oddělit přípravu a commit; před úspěšným potvrzením neprovádět nevratné změny. Pro související soubory použít staging a obnovu při chybě. Nejde o důkaz smazání audia: v reprodukci zůstalo v archivu. |
| A04 | P2, přímo doloženo kódem | `vocabulary/editor.py:131–132,449` skládá `audio_folder + ID + přípona`; konstruktor ukládá `str(context.audio_folder(...))` bez koncového oddělovače. | Editor hledá např. `audio/Czech_English1.mp3` místo `audio/Czech_English/1.mp3`. Nahrávání a PracticeAudio už používají Path správně. Sjednotit výpočet cest a otestovat skutečné callbacky s falešnými soubory. |
| A05 | P2, reprodukováno | `repositories/grammar.py:10`: načtení přijalo dva řádky se stejným question_id. `save_answers` vyžaduje právě jeden odpovídající řádek. | Kolo lze otevřít nad daty, která následně nelze uložit. Validovat ID při načtení; doplnit číslo řádku/sloupec. Zachovat podporu zkrácených řádků s prázdnými nepovinnými poli. |
| A06 | P2, měřeno | `repositories/grammar.py:48–59` opakovaně prohledává celý DataFrame pro každou odpověď. 10 000 otázek / 1 000 odpovědí: medián 3 009 ms. | Ukládání běží v UI vlákně a může způsobit viditelné zatuhnutí. Připravit index ID jednou, dávkovat změny a zachovat pořadí opakovaných odpovědí i kontrolu obsahu otázky. |
| A07 | P2, strukturálně ověřeno | `statistics/viewer.py:25,37–41,218`: modulové globální widgety, top, lang_var a df. `_build_statistics` má 180 řádků. | Přetrvávají reference na poslední okno; callbacky závisejí na posledním globálním stavu. Převést stav na instanci StatisticsController a pohled. Neprohlašuji to za změřený neomezený memory leak. |
| A08 | P2, mechanismus a syntetický růst ověřeny | `ui/learning_layout.py:28` mění velikost CTkImage. Instalovaná CTkImage 5.2.2 při změně size nemaže cache variant. 20 velikostí syntetického obrázku zůstalo v cache. | Dlouhé resize může držet více bitmap. Doplnit omezenou cache/debounce s veřejným rozhraním pro podklady. Odhad 22,51 MiB pixelů není měření RSS aplikace. |
| A09 | P2, strukturálně ověřeno | `statistics/window.py:61–64` volá builder synchronně z Tk callbacku. `viewer.Change_lang` znovu vytváří grafy; `charts.Generate_chart` má 160 řádků. | Loading cover zakryje sestavování, ale nezajišťuje odezvu během něj. Nejprve změřit výpočty a vykreslení zvlášť. Zachovat předpřipravení všech grafů; přesunout případné čisté výpočty do workeru, Tk/Matplotlib objekty ponechat v UI vlákně. |
| A10 | P2, strukturálně ověřeno | `repositories/vocabulary.py:11,73` importuje a spouští editor_attributes / API. Import app.main tak načítá i HTTP providery. | Repository kombinuje perzistenci se síťovým workflow a audiem. Přesunout orchestrace do vocabulary/save_workflow; repository ponechat čtení a bezpečný commit. |
| A11 | P2, skutečné testové selhání, příčina neuzavřena | `test_grammar_deferred_save` selhal v hromadném běhu na Ctrl+S; samostatný scénář i opakování celého modulu prošly. | Nestabilní GUI test nebo timing/focus chyba. Nezakrývat změnou assertu. Rozlišit doručení události, fokus, aktivní binding a samotnou perzistenci. |
| A12 | P3, falešný poplach testu ověřen | `test_localization_audit.py:61–77` zaměňuje libovolný keyword message za text widgetu. Označené tři různé zprávy existují ve všech šesti katalozích a při prezentaci se překládají. | Test nyní neprojde i pro korektní interní rozhraní. Omezit AST pravidlo na známé UI sinky; současně testovat překlady doménových chyb a skutečné widgety. |
| A13 | P2, konstrukční omezení | `shared/storage.py:35–37`, `repositories/csv_store.py:25–28`: kontrola revize/existence a os.replace nejsou jeden zamčený krok. U několika nových souborů se expected_revision=None používá jako žádná kontrola. | Optimistická ochrana není plná víceprocesová transakce. Zpřesnit smlouvu „soubor dosud neexistoval“, sjednotit zápisy a zdokumentovat zbylé časové okno. Nezavádět bez potřeby databázi nebo obecný transakční framework. |
| A14 | P3, strukturálně ověřeno | `vocabulary/editor.py:263–269` při synchronizaci tabulky znovu volá add_columns; ten znovu načítá a validuje synonyma. | I běžné textové úpravy vyvolávají souborové čtení nesouvisejících vazeb. Uchovávat odvozený index počtů a obnovit ho při změně vazeb nebo jejich revize. Zrychlení ještě nebylo měřeno. |
| A15 | P3, logická kruhová vazba | `grammar/editor_theory.py:3` dědí z GrammarEditor; `grammar/editor.py:214` zpětně lokálně importuje editor_theory kvůli navigaci. | Nejde o aktuálně selhávající import: lokální import cyklus při startu obchází. Předat navigační callback z composition root nebo oddělit společný základ až bude potřebný. |
| A16 | P2/P3, ověřeno | Chybí requirements/pyproject a deklarace podporovaných verzí. Široké except v kontrolérech často jen ukážou messagebox; grammar_filters.load_filter při chybě vrátí None bez diagnostiky. | Reprodukce instalace a diagnostika jsou obtížnější. Doplnit minimální manifest ze skutečně používaných přímých závislostí; centralizovat pouze logování a prezentaci chyb, s redakcí API klíčů. Zachovat užitečné fallbacky. |
| A17 | P3, historické provázání | `shared/settings.py` reexportuje config, legacy_styles a UI; `T` používá aktivní ContextVar. Barvy se místy nastavují nejprve legacy a poté přepisují společným stylem. | Závislosti nejsou vždy explicitní a mohou vytvářet zbytečné překreslení. Migrovat dotčené moduly postupně, nemazat facade ani přejmenovávat všechno naráz. |

## Mrtvý kód a duplicity

Spolehliví kandidáti pro pozdější malý úklid:

- `grammar/theory_data.py`: importy csv a Path po přesunu I/O.
- `services/backup.py`: import Path.
- `vocabulary/practise.py`: import pandas jako pd.
- `repositories/grammar_filters.py:8`: historická konstanta COLUMNS pro starou
  samostatnou tabulku; aktuální filtr je JSON v settings.csv. Nebyl nalezen odběratel.

Záměrně neoznačeno k odstranění: DataFrame pod TYPE_CHECKING, reexporty
linked_ids/describe, barvy přístupné přes learning_layout a shared.settings,
callbacky, entry pointy, `__init__.py`, testovací infrastruktura ani sandbox.
Žádný celý produkční skript nebo veřejnou funkci jsem tímto průchodem
neprokázal jako bezpečně odstranitelnou. Nepřítomnost takového nálezu není
formální důkaz dosažitelnosti všech větví.

Slučovat dává smysl zejména sestavování audio cest, kontroly CSV kontraktů a
revizí, opakované načítání synonym a tři různá schémata ukládání výukových
výsledků. Zvláštnosti formátů a pravidel každého modulu musí zůstat explicitní.

## Kompatibilita a hranice závěrů

Deset skutečných CSV nemělo při strukturální kontrole přebytečná ani chybějící
pole; kontrolované ID sloupce neměly prázdná ani duplicitní ID. Nejde o úplnou
obsahovou validaci všech otázek nebo správnosti synonym. Asset test potvrdil,
že všechny aktuální soubory v images mají odkaz a lze je dekódovat.

Nebyl zjištěn důvod měnit CSV schéma, databázový engine, UI knihovnu ani
identifikátory. ID slovíček se nesmějí přečíslovat; stávající přečíslování
gramatických otázek po smazání je naopak součástí současného chování.

Heslo e-mailu je v proměnných prostředí; API klíče zůstávají v settings.csv,
jak uvádí README. Jejich ukládání není šifrované. Audit neověřoval historii
verzovacího systému ani nezveřejňoval žádné tajné hodnoty. Přechod na úložiště
pověření by byl samostatné schvalované rozšíření, nikoli skrytá součást úklidu.

## Stav po implementaci

| Nález | Stav | Skutečné řešení / zbylé omezení |
|---|---|---|
| A01 | Vyřešeno | Conjugation save čte aktuální CSV a provede deltu pouze R/LR proti původnímu zdroji. |
| A02 | Vyřešeno pro aplikaci | Vocabulary controller předává original snapshot; nezměněný externí popis se nepřepíše. Kompatibilní přímé volání bez original nemůže znát výchozí stav. |
| A03 | Vyřešeno v rozsahu běžných chyb | Izolované audio_output, rollback kopie, obnovení vazeb i audia, zachování recovery při chybě obnovy. Výpadek OS není ACID transakce. |
| A04 | Vyřešeno | Path pro přehrávání i mazání v editoru; skutečný callback testován s falešným MP3. |
| A05 | Vyřešeno | Loader odmítá prázdná/duplicitní ID s CSV řádkem, podporuje BOM a nepovinné krátké řádky. |
| A06 | Vyřešeno | Jednorázový index a dávkové R/LR; 1 000 odpovědí na 10k otázkách přibližně 90 ms. |
| A07 | Vyřešeno | StatisticsController místo globálních widgetů/df; test uvolnění instance po close. |
| A08 | Vyřešeno | Reset obsolete image variant přes veřejné API a debounce resize; měření bitmap i Windows Working Set. |
| A09 | Významně vyřešeno, omezení zůstává | Čisté výpočty ve workeru, render po figurách a předpřipravení všech grafů. Jedna složitá figura stále běží v UI vlákně. |
| A10 | Vyřešeno | Skutečná orchestrace v vocabulary/save_workflow.py; repository jen zachovává odložený kompatibilní vstup. |
| A11 | Stabilizován test | Explicitní queued KeyPress a Ctrl stav, kontrola doručení události; bez přidávání sleep. Trvalá produkční save chyba nebyla prokázána. |
| A12 | Vyřešeno | AST kontroluje skutečné UI sinky; katalogové a geometrické testy zůstaly aktivní. |
| A13 | Částečně vyřešeno | Per-path zámky a atomické create-if-absent. Zbylé okno mezi hash check a replace existujícího souboru u cizího procesu je zdokumentované. |
| A14 | Vyřešeno | Editor-owned SynonymCounts; test deset změn → jedno čtení, změna vazeb → invalidace. |
| A15 | Vyřešeno | Otázkový editor přímo neimportuje theory editor; směrování v editor_navigation. |
| A16 | Vyřešeno v bezpečném rozsahu | Manifest ověřených přímých závislostí, redigovaná diagnostika ukládání a vadných filtrů, type hints revizního rozhraní. |
| A17 | Částečně, záměrně | Přestavěné statistiky mají explicitní kontext a přímé UI závislosti; legacy facade pro ostatní funkční screeny zůstala kompatibilní. |

Navíc byl zachycen a opraven scénář, kdy by nová delta časování ukládala
nezměněný NaT jako text. Je pokrytý novým testem; nejde o záměrnou změnu
výukového pravidla. Nebyl odstraněn žádný celý produkční modul nebo funkce
jen podle počtu statických referencí.

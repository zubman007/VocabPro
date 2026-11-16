# Audit lokalizace VocabPro — 16. 11. 2026

## Následné opravy — aktuální stav

Po zavedení N studijních kurzů měly katalogy 496 klíčů. Navazující opravy
lokalizace upravily **120 existujících hodnot** (cs 41, sk 55, de 8, es 10,
fr 3, en 3) a přidaly **5 klíčů / 30 hodnot** pro vlastní dialogy. Po této fázi
měl každý katalog **501 klíčů**. Následná správa souborů kurzů
a příznak gramatiky doplnily dva klíče. Graf aktuálních sérií otázek,
samostatná karta rekordu a počet kategorií přidaly deset dalších;
aktualizovaný inventář má **513 klíčů v každém ze šesti jazyků**.
Audit nehlásí chybějící překlady,
prázdné či duplicitní klíče, chyby parametrů ani kontrolované pevné UI texty.

- Čeština a slovenština používají vykání ve zprávách, nápovědě i průvodci.
  Němčina používá převládající „du“; nové texty kurzů a SMTP už nepřepínají
  do „Sie“. Španělština ponechává „tú“ také v novém nastavení kurzů.
- Pro opakování učiva je španělské `repasar`/`repaso`. Výrazy o opakovaných
  chybách (`errores repetidos`) zůstávají významově odlišené.
- Angličtina používá britské `practise` jako sloveso a `practice` jako
  podstatné jméno, včetně `practised`. Stabilní ID se nepřejmenovávala.
- Slovenské mazání položek používá `Odstrániť`, vyprázdnění buněk
  `Vyprázdniť obsah`; popis je jednotně `Opis`.
- Francouzské ukládání změn používá `Enregistrer` i v průvodci. Zálohy
  nadále používají odpovídající výraz `sauvegarde`.
- Popisky posledních výsledků gramatiky mají nezlomitelnou mezeru před
  procentem v cs/sk/de/es/fr; angličtina zachovává zápis bez mezery.

Všechny chybové a potvrzovací messageboxy aplikace nyní používají společný
`app/ui/messagebox.py` místo systémových dialogů. Přepojeno je 14 modulů.
Tlačítka Ano/Ne/Zrušit/OK i výchozí titulky se určují podle kontextu aplikace,
nikoli jazyka Windows. Zachované jsou návratové hodnoty `True`/`False`/`None`
a `ok`, výchozí kladná volba původních dotazů, Escape/zavření jako odmítnutí
nebo zrušení, Enter a možnost zkopírovat zprávu pomocí Ctrl+C. Dlouhé zprávy
se zalamují a posouvají. Po zavření vnořené zprávy se obnovuje modalita
původního dialogu. Titulky a obsah se znovu nepřekládají, proto se nemění
uživatelská data ani technické podrobnosti. Výběr Yes/No/Cancel má stále
stejný význam pro uložení, zahození změn a pokračování v práci.

Kontrolní nástroj nově odmítá návrat importů nativního messageboxu a odhalí
také pevné poziční titulky/zprávy. Validátor formátů nyní ověřuje skutečný
výsledek vnořených specifikací, jejich hloubku i nepovolený přístup k atributům;
neplatná šablona už neprojde jen kvůli přítomnosti `{width}`.

Aktualizovaný inventář obsahuje **83 kandidátů bez literálového odkazu** a
76 skupin shodných hodnot. Jde o podněty ke kontrole, ne prokázané chyby.
Historické titulky a přípony zůstávají dostupné starším voláním; automatické
smazání by odporovalo požadavku na kompatibilitu. Německé `Phrase` zůstává
obecnou kategorií: kód ani editor ji neomezují na ustálené výrazy, takže
nahrazení užším významem `Wendung` by nebylo podloženou opravou.
Osm technických invariantů/diagnostik je uvedeno odděleně od UI textů.

Nový regresní modul `test_localization_followup` prošel **10/10**. Ověřuje
redakční pravidla, formátování, zákaz nativních dialogů, skutečné modální
návratové hodnoty, zavření vlastníka, obnovu grabu, výchozí kontext, klávesy
a dlouhé zprávy ve všech jazycích při třech simulovaných měřítkách UI.
Český potvrzovací dialog byl také vizuálně zkontrolován v reálném okně Windows.
Tato kontrola nenahrazuje nezávislou jazykovou korekturu ani fyzické ověření
všech původních obrazovek na třech různých nastaveních DPI.

Závěrečný úplný běh s limitem 240 sekund na modul prošel **542/542 testy
v 85 modulech**, bez chyb a bez přeskočení. Zahrnuje původní funkce,
lokalizaci, N kurzy, editory, ukládání, potvrzení odchodu i statistiky.
Po posledním doplnění redakčního pravidla a kontroly konstruktoru dialogu
byly navíc znovu spuštěny cílené kontroly politik a validace katalogů.
Uživatelské slovníky, historie a nastavení se nepřepisovaly.

Následující části zachycují původní audit a jeho tehdejší měření.

## Závěr a rozsah jistoty

Aplikace má šest jazyků rozhraní: angličtinu (`en`), češtinu (`cs`), slovenštinu
(`sk`), španělštinu (`es`), francouzštinu (`fr`) a němčinu (`de`). Na začátku
auditu měl každý katalog 476 klíčů; po doplnění sedmi šablon a dvou dynamických
legend má každý **485**. Právě legendy `Real`/`Ideal` ukázaly, proč nestačí
porovnat soubory: chyběly ve všech katalozích včetně angličtiny, ale za běhu se
používaly při přejmenování sloupců grafu slovních druhů.

Katalogy byly prověřeny proti zdrojovému kódu, nastavení načítanému z CSV,
výchozím nabídkám tabulkové knihovny, grafům, dynamickým popiskům a chybovým
cestám. Shoda katalogů není důkaz úplné lokalizace. Statická kontrola neumí
dokázat všechny možné hodnoty předávané přes proměnné a nevztahuje se na obsah
uživatelských kurzů. Jazyková revize není nezávislá korektura rodilými mluvčími.

Automatický sken zahrnuje `app/**/*.py`, `start.py`, katalogy a názvy/nabídky
nastavení z `files/settings.csv`. Testy a diagnostický auditovací CLI nejsou
desktopové UI. Pracovní `sandbox.py`, staré záložní kopie a celé zdroje
závislostí nejsou cílové rozhraní; z tksheet byly prověřeny aktivní nabídky.

## Katalogy a inventář

| Jazyk | Klíče před / po | Chybějící dynamické klíče před / po | Prázdné / neplatné | Duplicitní klíče | Chyby parametrů |
| --- | ---: | ---: | ---: | ---: | ---: |
| Angličtina | 476 / 485 | 2 / 0 | 0 | 0 | 0 |
| Čeština | 476 / 485 | 2 / 0 | 0 | 0 | 0 |
| Slovenština | 476 / 485 | 2 / 0 | 0 | 0 | 0 |
| Španělština | 476 / 485 | 2 / 0 | 0 | 0 | 0 |
| Francouzština | 476 / 485 | 2 / 0 | 0 | 0 | 0 |
| Němčina | 476 / 485 | 2 / 0 | 0 | 0 | 0 |

Rozdíly klíčů mezi samotnými katalogy byly nulové už před opravou. Dva chybějící
klíče jsou počet konkrétně nalezených dynamických mezer, nikoli tvrzení o úplném
pokrytí všech možných hodnot ze zdrojových proměnných.

Kompletní strojový výstup je v [localization-audit-inventory.json](localization-audit-inventory.json).
Obsahuje i shodné hodnoty, skupiny stejných překladů, technické výjimky a
kandidáty na nepoužívané klíče. Neobsahuje hesla ani obsah slovníků.

Statický inventář označil **84 kandidátů bez přímého literálového odkazu**.
To nejsou potvrzené nepoužívané položky: například `True`/`False` mohou vzniknout
převodem hodnot, jiné položky slouží starším obrazovkám, CSV nebo integracím.
Staré složené titulky kurzů a původní přípony počtů jsou vhodní kandidáti k
pozdějšímu úklidu. Nic nebylo smazáno ani přejmenováno.

Shoda hodnot s angličtinou není automaticky chybou: `Audio`, `ID`, `OK`,
španělské `General` či francouzské `Description` jsou legitimní. Interní klíč
`Saved grammar category filters` je nastavení typu JSON, které se v dialogu
nezobrazuje. Různé identifikátory se stejným viditelným textem jsou často
úmyslné, například `Setting` a `Settings`; jejich automatické slučování by
mohlo poškodit kompatibilitu. Jednoznačnost lokalizovaných enumů ověřují testy.

Inventář obsahuje 74 skupin stejných hodnot: en 11, cs 8, sk 9, es 13, fr 15,
de 18. Byly posouzeny podle kontextu. Například německé `Redo` a `Repeat`
mohou oba zobrazit `Wiederholen`, protože první je akce editoru a druhé vstup
do procvičování; nejde o dva různé datové enumy v jedné nabídce.

## Potvrzené problémy a opravy

Bylo změněno **27 existujících překladových hodnot**: 25 oprav významu,
pravopisu či slovotvorby a dvě sjednocení francouzského označení ukládání.
Nejde o tvrzení, že zbývající překlady nemohou mít stylistické nedostatky.

| Problém | Rozsah | Oprava |
| --- | --- | --- |
| Průvodce tvrdil, že odpovědi gramatiky se průběžně zapisují do souboru | Všech 6 jazyků | Popis nyní odpovídá odloženému uložení a nabídce uložit při odchodu |
| Hlášení o jazycích předpokládalo vždy dva aktivní studované jazyky | Všech 6 jazyků | Mluví o všech aktivních jazycích, funguje i při vypnutém druhém jazyku |
| „v repeat“ | Čeština a slovenština | „při opakování“ / „pri opakovaní“ |
| „slůpec“, „němčiny“, „španělštiny“ | Slovenština, 3 hodnoty | `stĺpec`, `nemčiny`, `španielčiny` |
| „Englisch Kurs bearbeiten“ a podobné historické popisky | Němčina, 5 hodnot | Složeniny jako `Englischkurs bearbeiten` |
| Malá počáteční písmena podstatných jmen `konjugation`, `grammatik`, `verben zum konjugieren` | Němčina, 3 hodnoty | `Konjugation`, `Grammatik`, `Verben zum Konjugieren` |
| `Save` a ručně psaná zkratka používaly jiné sloveso než ostatní akce | Francouzština, 2 hodnoty | Jednotné `Enregistrer` pro akci ukládání |

Devět nových klíčů znamená **54 doplněných hodnot**: dvě úplné šablony počtů,
tři chyby poskytovatelů, chybějící sloupce CSV a lokalizovaný obal technické
chyby a dvě legendy skutečného/cílového zastoupení. Parametry jazyků se lokalizují až při zobrazení. Anglický text výjimky
zůstává dostupný pro logy a existující integrace.

### Pevné a dynamické texty mimo katalogy

| Místo / původní text | Zjištění a stav |
| --- | --- |
| `app/services/backup.py`: `- backup` v předmětu e-mailu | Skutečný pevný text notifikace; předmět nyní používá přeložené `Backups` |
| `app/statistics/window.py`: holé `str(error)` při sestavení okna | Opraveno použitím společného překladače chyb |
| `app/vocabulary/editor.py`: holá výjimka při mazání audia a připojené technické detaily při přehrávání | Opraveno; známá hlášení se přeloží, neznámá dostanou lokalizovaný kontext |
| `app/vocabulary/editor_audio.py`: holá chyba nahrávání a přehrávání | Opraveno stejným mechanismem |
| `app/vocabulary/practise.py`: připojený nezpracovaný text výjimky | Opraveno stejným mechanismem |
| Slovníkové API a Conjugation: jazyk/názvy sloupců vložené do anglické výjimky před překladem | Strukturované šablony `UserMessageError`, formátování až v UI |
| Editor: klíč složený jako `Edit ` + jazyk + ` course` | Dvě samostatně přeložené části titulku; nevyžaduje nový klíč pro každou dvojici |
| Conjugation tabulka: již přeložené názvy sloupců znovu předávané do překladače | Data mají stabilní názvy; překládá se až viditelné záhlaví |
| Domovská stránka: číslo + přípona „slov…“ | Celé neutrální šablony s `{count}`, bez chybného skloňování pro 0/1/2/5/21 |
| Graf slovních druhů: dynamické názvy `Real` a `Ideal` | Chyběly ve všech šesti katalozích; nyní mají překlad, v angličtině `Actual`/`Target` |

Úvodní sken navíc označil sedm podezřelých literálů, které po kontrole nebyly
nezlokalizovaným UI: tři předané klíče `can_leave`, tři revizní zprávy předané
datové vrstvě a technický identifikátor `ID`. Kontrola nyní rozumí těmto
konkrétním rozhraním; nejde o plošné ignorování podobných zpráv.

Zůstává sedm výskytů technických výjimek bez katalogového ID (navigace,
registrace prostředků na zavřené obrazovce, neplatná dvojice jazyků, profilovací
CLI a neplatný interní filtr). Jde o vývojářské invarianty/diagnostiku. Při
zobrazení neočekávané chyby přes opravená UI rozhraní dostanou lokalizovaný obal.

## Automatická kontrola

Původní `test_translations.py` a `test_localization_audit.py` již kontrolovaly
shodu klíčů, duplicity v JSON, prázdné hodnoty, NFC, základní literály,
enumy, fallback a některá skutečná okna. Chyběla kontrola formátovacích
kontraktů, část složených textů, holé výjimky a e-mailový předmět.

Nový příkaz je read-only vůči nastavení a slovníkům:

```powershell
.venv/Scripts/python.exe -B -m app.shared.localization_audit
.venv/Scripts/python.exe -B -m app.shared.localization_audit --output docs/localization-audit-inventory.json
```

Vrací nenulový kód pro chyby katalogů, chybějící zjištěné klíče a kandidáty
na pevné UI texty. Ověřuje také nastavení a jejich nabídky z CSV. Kandidáti na
nepoužívané klíče, stejné překlady a interní výjimky jsou informace k posouzení,
nikoli důvod k automatickému mazání nebo překládání dat.

Nové testy záměrně vkládají duplicitní JSON klíče, chybějící soubory, prázdné
překlady, neplatné hodnoty, ztracené/přidané parametry, neplatné konverze a
formáty, text ve f-stringu, nepřeložený nadpis grafu či předmět e-mailu.
Přeskupení pojmenovaných parametrů je povolené; změna jejich významu/formátu
se hlásí. Neznámá struktura formátování se nemá potichu přijmout.

Kontroly jsou součástí běžného `python -B -m app.tests.run_all`, není třeba
nový testovací framework. Audit používá standardní knihovnu a nepotřebuje GUI.

## Runtime, formáty a kompatibilita

- Změna jazyka se aplikuje uložením nastavení: hlavní obrazovka se znovu
  sestaví, další otevřená okna mají nový jazyk. Dialog nastavení samotný se
  během rozpracovaného výběru nepřekládá. Není zaveden reaktivní překlad
  libovolného starého okna po přímé změně kontextu v paměti.
- Seznam jazyků UI je nyní výslovný (`UI_LANGUAGE_IDS`), nezávislý na tom,
  kolik jazyků může mít registr studijních jazyků. Identita jazyka se sdílí;
  dostupnost překladu rozhraní se od dostupnosti výuky neodvozuje.
- Procenta, desetinné hodnoty statistik a datumy v grafech používají lokální
  formát. Například `12,50 %` a `16.11.2026` pro češtinu, `16/11/2026` pro
  francouzštinu; angličtina používá desetinnou tečku a jednoznačné ISO datum.
  Nejde o plný systém regionů, např. samostatné en-US/en-GB.
- V editovatelných datech CSV a nastavení termínu záloh zůstává stávající
  ISO formát. Nemění se chronologické řazení, časové pásmo ani uložené hodnoty.
- Číselné hodnoty tabulek zůstávají čísly pro řazení; lokalizuje se až jejich
  zobrazení. Procentní sloupec Conjugation má výslovnou jednotku.
- Slovíčka, vlastní názvy kategorií, osoby časování, popisy, příklady, názvy
  vlastních sloupců a texty od slovníkových služeb jsou obsah kurzu. Nemají se
  překládat při změně UI jazyka. Enumy se při uložení vracejí na interní hodnoty.
- Známé chyby mají překlad. Neznámé zprávy OS, zařízení a poskytovatelů se
  zachovají jako **technické podrobnosti s lokalizovaným kontextem**, nikoli
  jako údajně přeložený text. Nativní tlačítka Windows messageboxů se řídí OS.

## Redakční rozhodnutí a zbývající omezení

Původní stylistické návrhy byly při navazující opravě rozhodnuty a provedeny:

1. Čeština/slovenština: vykání; krátké názvy akcí zůstávají v infinitivu.
2. Němčina: „du“; neosobní názvy akcí zůstávají v infinitivu.
3. Španělština: „tú“ a `repasar` pro opakování učiva.
4. Francouzština: `Enregistrer` pro změny, `sauvegarde` pro zálohy.
5. Angličtina: britský pravopis při zachování všech stabilních ID.
6. Německé `Phrase`: zachovat obecný význam stávající slovní kategorie.
7. Slovenština: `Odstrániť` pro položky, `Vyprázdniť obsah` pro obsah buněk.

Vizuální checklist pro každý z šesti jazyků:

- [ ] Windows 100 %, 125 % a 150 % DPI; minimální okna a maximalizace.
- [ ] Domovská stránka s počty 0, 1, 2, 5, 21 a dlouhými hodnotami.
- [ ] Nastavení: všechny záložky, zapnuté/vypnuté funkce, validace,
      odesílací účet, skrytá hesla a nabídky jazyků.
- [ ] Editor slovíček: pravé tlačítko v buňce/záhlaví/indexu, dropdowny,
      filtrování, třídění, záznam audia a chybějící API klíč.
- [ ] Gramatika, teorie a Conjugation: správná/chybná odpověď, odhalení,
      dokončení kola, předchozí položka, prázdná data a potvrzení odchodu.
- [ ] Statistiky: všechny sekce, jazyky kurzů, osy, legendy a hover,
      desetinné čárky, datumy, dlouhé kategorie a názvy štítků.
- [ ] Dialogy synonym/štítků, About a průvodce: všechny záložky a scroll.
- [ ] Zamčený/chybějící CSV, chyba zařízení a služby: lokalizovaný kontext
      a užitečné technické podrobnosti; žádný nezformátovaný `{placeholder}`.
- [x] Nahradit systémové messageboxy vlastními dialogy v jazyce aplikace;
      otestovat výsledky dotazů, obnovu modality, dlouhé texty a klávesy.

Automatické testy geometrie nenahrazují vizuální korekturu na všech displejích.
Není zde označena za hotovou nezávislá jazyková korektura, kontrola všech DPI
ani plná lokalizace textů třetích stran.

## Výsledky testování

Nové validační testy prošly **10/10**. Runtime smoke testy prošly **2/2** a
pro všech šest jazyků ověřily **132 různých požadovaných ID**, včetně obou
legend. Skutečná změna jazyka přes nastavení obnovila domovskou obrazovku,
nové dialogy a ponechala studijní jazyky beze změny. Kontrolují se také aktivní
Copy/Paste nabídky tksheet, titulky, validace, data kurzů a sekce statistik.

Kompletní mapovaný průchod obrazovkami v šesti jazycích byl také spuštěn; byl
nákladný (175 s) a odhalil pozdní Tk chyby při uvolňování grafů. Oprava odkládá
odstranění Tcl příkazu až po skončení aktuální události Destroy. Regresní test
ověřuje, že po zavření hostitele nezůstává příkaz a nevzniká Tcl `bgerror`.
Modul vykreslování po opravě prošel **8/8** testů.

Trvalý rychlejší smoke test sestavuje statistiky ve skrytém okně a bez
opakovaného rasterizování 30 grafů. Ověřuje skutečné lookupy, widgety a obsah
grafů, nikoli jejich pixely. Pixely a skutečně zobrazené okno ověřují samostatné
testy `test_chart_rendering` a `test_statistics_improvements`; další geometrii
všech jazyků ověřují stávající UI scénáře. Tento rozdíl nelze zaměňovat za
úplnou vizuální kontrolu všech šesti jazyků na všech DPI.

Úplný závěrečný běh provedl **508 testů v 81 modulech, bez přeskočení**.
V 80 modulech nebyla chyba. Jediná chyba byla v `tearDown` jednoho testu v
`test_tag_scenarios`: `root.after_cancel` odstranil Tcl příkaz časovače
potomka, ale ponechal jeho záznam ve vlastníkovi; následné zničení widgetu ho
zkusilo odstranit znovu. Úklid byl opraven na zrušení Tcl časovače bez smazání
příkazu jiného vlastníka. **Dotčený modul po opravě prošel 7/7**.
Celý běh po této čistě testovací opravě znovu spouštěn nebyl; nejde o tvrzení
o jednom úplném zeleném průchodu. Rozšířený validátor byl po posledních
úpravách navíc znovu ověřen **10/10** testy. CLI audit vrací kód **0**:
žádné chyby katalogů, parametrů, zjištěných klíčů ani kontrolovaných UI sinků.

Všechny testy běží
s existujícími pojistkami proti síti, mikrofonu, přehrávání a zápisům do
uživatelských dat. Existující změny v `sandbox.py`, `files/Spanish_gra.csv`
a předchozí úpravy statistik/jazykového modelu zůstaly zachované.

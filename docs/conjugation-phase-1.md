# Conjugation — implementace 1. fáze

Implementováno podle [schváleného návrhu](conjugation-phase-1-proposal.md).
Rozsah této fáze tvoří gramatické osoby. Description zůstává volným textem;
nevzniklo nové členění na časy, způsoby, rody ani univerzální gramatický systém.

## Ovládání

1. V Nastavení → Jazyky má každý kurz nezávislé **Zapnout časování**.
   Po Save se připraví chybějící soubory. Nové kurzy mají modul vypnutý;
   u starých nastavení se zachová dostupnost podle původního CSV.
2. Home nabízí u zapnutého modulu **Repeat**, **Edit** a **Gramatické osoby**.
   Repeat je aktivní jen při neprázdném výběru osob a alespoň jednom slovesu
   s připraveným vybraným tvarem. Prázdný modul je možné editovat.
3. **Gramatické osoby** jsou dostupné i v nastavení kurzu. Dialog umožňuje
   přidat osobu, změnit označení, posunout pořadí, deaktivovat a opět aktivovat.
   Bezpečné odebrání je deaktivace; tvary a výsledky zůstanou zachované.
   Zvláštní volba **Procvičovat** vybírá podmnožinu aktivních definic.
   Dialog má vlastní Save a ochranu neuložených změn; jeho uložení není
   podmíněno následným uložením přepínačů kurzu. Nápověda to výslovně uvádí.
4. Editor má vlevo seznam s hledáním, vpravo posuvný formulář. Nabízí
   Add verb, Delete verb, Apply a Save. Formulář obsahuje sloveso, překlad,
   původní popis a pole všech aktivních osob. Překlad a tvary mohou zůstat
   prázdné, cílové sloveso je povinné. Smazání slovesa potvrzuje i odstranění
   jeho historie; ostatní ID se nikdy nepřečíslují. Odchod podporuje
   Save/Discard/Cancel; chyba ukládání ponechá formulář a rozpracované změny.

Vypnutý modul zmizí z Home, statistik, nápovědy i přímých vstupů do editoru
a procvičování. Pokud je vypnutý všude, skryje se i jeho globální velikost
dávky. Zachová se CSV včetně prázdného souboru i konfigurace osob. Odebrání
celého kurzu může dál odklidit pouze prokazatelně prázdné CSV; konfigurace osob
se automaticky nemaže.

## Model a soubory

- `files/<vlastní jazyk>_<cílový jazyk>_con.csv` zachovává původní řádky,
  ID, jazykové sloupce, Description, R/LR a neznámé sloupce. Původní šestice
  `s1/s2/s3/m1/m2/m3` má dál stejnou identitu. Nová osoba dostává stabilní
  `p_<uuidhex>` a nový sloupec se stejným ID. Slovesa mají dynamický slovník
  `forms`; dosavadní konstruktor a přístupy k původním atributům zůstávají
  kompatibilní. Nová slovesa dostávají UUID, stará ID včetně `001` se zachovají.
- `files/<cílový jazyk>_con_persons.json` verze 1 obsahuje `language`,
  uspořádané definice `persons` (`id`, `label`, `enabled`) a samostatná
  `practice_person_ids`. Změna názvu, pořadí ani jazyka UI nemění vazby tvarů.
  Konfigurace je společná cílovému jazyku, nikoli jazykové dvojici.
- Výchozí definice existují pro všech šest registrovaných jazyků. Nová
  angličtina má pět osob; původní soubor se šesti sloupci zachová šest
  identit, včetně dvou historických `you`. Regionální `vos` lze běžně přidat.
  Počet osob není omezen na šest; delší cvičení používá posuvný formulář.
- Chybějící konfigurace se při čtení adaptuje pouze v paměti. Neznámé platné
  sloupce osob z obnoveného CSV se zpřístupní jako neaktivní definice; jejich
  výběr se automaticky nezapíná. Chybějící tvar znamená prázdný text, nikoliv
  chybnou odpověď. Explicitní Save editoru doplní chybějící sloupce.
- `Study courses` verze 3 přidává boolean `conjugation`. Verze 1/2 i původní
  dvouslotové nastavení zůstávají čitelné. Rozhodnutí podle existence CSV
  probíhá v repository/contextu, bez I/O v parseru; při uložení se stane
  explicitním booleanem. Původní řádky nastavení se neodstraňují.

## Procvičování a nové statistiky

Způsobilá slovesa se vyberou před plánováním dávky, aby prázdné vybrané tvary
neobsadily celou lekci a nevytvořily falešný úspěch. Dosavadní priority R/LR
a velikost dávky zůstávají. Matching a barevné odhalení nyní používají stejnou
normalizaci: velikost písmen, španělské ñ/n a klávesnicové ň v odpovědi,
včetně velkých Ñ/Ň. Alternativní tvary se nezavádějí, protože je původní
Conjugation nepodporovalo; jedna buňka dál znamená jeden správný text.

Volitelný `Person history` v CSV ukládá například
`{"version":1,"results":{"s1":"SF","s2":"S"}}`. První odeslání zaznamená S/F
každé skutečně procvičované osobě s vyplněným tvarem. Správná osoba dostane S
i při F celého kola. Opakované potvrzení odhaleného řešení a přeskočení nic
nepřidávají. Staré R se na výsledky osob nepřepočítává.

Dole v Conjugation statistikách je nový přehled osob s počty správných a
chybných odpovědí, procentem a vodorovným pruhem. Bez nových pozorování se
zobrazuje pomlčka, nikoliv fiktivní nula úspěšnosti. Zachované výsledky
neaktivních osob jsou označené. Původní souhrny celých kol, obtížná slovesa
a graf koncových úspěchů zůstávají; popis rozlišuje výsledky osob a kol.

Agregace běží ve stávajícím statistickém workeru. Cache zahrnuje konfiguraci
osob, takže změna označení nebo aktivace nezanechá staré popisky a počty
aktuálních tvarů. Nezměněný snapshot nepřestavuje widgety. Scroll nepřepočítává
historii a nový panel nepotřebuje Matplotlib rendering.

## Ochrana dat

CSV i JSON se ukládají přes dočasný soubor, flush/fsync a atomické nahrazení,
s kontrolou očekávané revize a bezpečným create-if-absent. Chyba zápisu
nepoškodí původní soubor. Při neúspěšném Save hlavního nastavení se odklidí
jen vlastní nezměněné nově vytvořené soubory; souběžně upravená data zůstanou.

Editor odmítne přepsat souběžnou změnu. Výsledky lekce se slučují podle ID
a měněných polí, zachovají nesouvisející úpravy a odmítnou konflikt výsledků
i změnu právě procvičovaného tvaru. R/LR a výsledky osob se zapisují jedním
CSV uložením. Opakované uložení nepřidává stejné výsledky znovu; samotné
přeskočení lekce a nezměněný již uložený snapshot nemění soubor.

Před prvním rozšířením schématu při zápisu vznikne
`<soubor>.csv.pre-persons.bak` s původními byty. Existující kopie se nikdy
nepřepíše. Původní nestandardní znaky v R, neznámé sloupce a neupravené tvary
se nečistí. Poškozená konfigurace nebo individuální historie vyvolá chybu,
nikoliv tiché nahrazení výchozími hodnotami. Zálohy výslovně přidávají validní
rozpoznané `*_con_persons.json`; settings a jiné JSON se neposílají.

## Ověření

Reprodukovatelné příkazy z kořene projektu:

```powershell
.venv\Scripts\python.exe -X utf8 -B -m app.tests.run_all --timeout 240
.venv\Scripts\python.exe -X utf8 -B -m app.tests.run_all --pattern 'test_conjugation*.py' --timeout 240
.venv\Scripts\python.exe -X utf8 -B -m app.shared.localization_audit --output docs/localization-audit-inventory.json
```

Nové testy pokrývají datový model, lifecycle souborů a skutečné UI:
`test_conjugation_model`, `test_conjugation_lifecycle`, `test_conjugation_persons_ui`.
Služby používají izolované náhrady a data dočasné složky; testy neposílají
e-mail a nemění produkční slovníky. Samostatné čtení původního španělského CSV
ověřilo 365 záznamů a šest osob při stejné kontrolní sumě souboru.

## Další fáze a meze

Časy, způsoby, rody a další strukturované kategorie zůstávají pro samostatné
rozšíření; stávající volný Description nadále funguje. Historickou úspěšnost
osob ani rychlost odpovědí nelze domýšlet. Podpora alternativních správných
tvarů je také budoucí obsahová změna. Osoby se bezpečně deaktivují; fyzické
mazání sloupců a hromadné čištění historie se nenabízí.

Automatické kontroly rozložení nepokrývají všechny možné uživatelské texty
a DPI. Na cílovém monitoru lze ručně ověřit dlouhé vlastní označení, posun
desáté osoby, klávesnici a návrat přes Save/Cancel. Změny konfigurace osob
se načtou pro novou lekci; již otevřená lekce používá svůj konzistentní snapshot.

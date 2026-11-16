# Conjugation: analýza a návrh 1. fáze

Stav: návrh schválen uživatelem; implementace a ověření jsou popsané
v [reportu 1. fáze](conjugation-phase-1.md). Následující analýza zachycuje
výchozí stav a schválená rozhodnutí před implementací.
Předmětem jsou výhradně gramatické osoby. Dosavadní volný text `Description`
zůstává zachován; nevzniká katalog časů, způsobů ani dalších kategorií.

## Zjištěný stav

- `app/conjugation/data.py` má model `Verb` s přesně šesti atributy
  `s1/s2/s3/m1/m2/m3`. `build_verbs()` i validační loader vyžadují všech šest
  sloupců. `PERSONS_MAP` obsahuje šest osob pro každý ze šesti registrovaných
  jazyků. Angličtina má dvě samostatná `You`.
- Layout, controller, session a dialog předchozího slovesa již přijímají
  seznam osob, ale hodnoty čtou přes pevné atributy slovesa. Formulář
  procvičování nemá posuvnou oblast pro větší počet osob.
- `R` a `LR` patří celému slovesnému záznamu/koli, nikoliv konkrétní osobě.
  Jedna chyba znamená `F` celého kola. Potvrzení odhalených správných tvarů
  nepřidává `S`; vynechání slovesa nepřidává žádný výsledek.
- Matching ignoruje velikost písmen a zachovává dosavadní pravidla pro
  `ñ/n/ň`. Alternativní tvary Conjugation nyní nepodporuje: očekává jeden
  text v buňce. Podpora alternativ ve Vocabulary je samostatný mechanismus.
- Chybí editor Conjugation a přepínač modulu podle jazyka. Domovská stránka
  nabízí pouze Repeat, dostupnost určuje existence CSV. Statistiky také
  čtou Conjugation podle existence souboru a pokrytí mají pevně šest sloupců.
- Grammar má potřebné stavební prvky: přepínač v `StudyCourse`, přípravu
  souborů, oddělený editorový dokument, explicitní ukládání, kontrolu revizí,
  hlášení konfliktů, ochranu neuložených změn a navigaci přes ScreenController.
  Z editoru Grammar se nepřevezme přečíslování ID při mazání: zde musí
  identita ostatních sloves zůstat beze změny.
- `course_files.py` už používá správný název Conjugation CSV, ale automaticky
  ho nevytváří. Při odebrání celého kurzu může odstranit prokazatelně prázdný
  soubor. Samotný modul zatím samostatně vypnout nelze.
- Zálohy zahrnují neprázdné datové CSV; JSON nyní nepřenášejí a `settings.csv`
  záměrně vynechávají kvůli citlivým nastavením. Konfiguraci osob je proto
  nutné přidat do zálohování výslovně.

Kontrola existujících dat byla pouze pro čtení. V `Czech_Spanish_con.csv`
je 365 záznamů, bez duplicitních ID a bez záznamu se všemi šesti tvary prázdnými.
Historie obsahuje 2 799 značek S/F. Ve třech historiích jsou také jiné znaky;
jejich původní obsah se zachová, bez automatického čištění. Žádný současný
tvar v tomto souboru neobsahuje lomítko.

## Doporučený model

### 1. Zachovat CSV a jeho identitu

Slovesa zůstanou v `files/<vlastní jazyk>_<cílový jazyk>_con.csv`, například
`Czech_Spanish_con.csv`. Jeden řádek nadále představuje jeden slovesný
záznam. Stejné sloveso se může vyskytovat vícekrát s různým popisem.

Stávající ID, překlady, `Description`, šest původních sloupců, `R`, `LR`
i případné další sloupce se zachovají. Nový model slovesa bude mít slovník
`forms: {person_id: text}` namísto pevného konstruktoru se šesti tvary.
Adaptér přečte původní šestici beze změny jejích identifikátorů.

Nová osoba dostane jednou vygenerované ID, například `p_<uuid>`, které bude
zároveň názvem jejího CSV sloupce. Zobrazovaný název se ukládá odděleně.
Přejmenování a přesun osoby proto nemění vazbu na uložené tvary.
Chybějící sloupec nově přidané osoby znamená prázdný tvar; přidá se při
explicitním uložení editoru. Otevření souboru jej nepřepisuje.

Nová slovesa dostanou unikátní stabilní ID. Mazání jednoho záznamu
nepřečísluje ostatní a potvrdí odstranění jeho vlastní historie.

### 2. Samostatná konfigurace osob cílového jazyka

`files/Spanish_con_persons.json` bude verzovaný dokument s identitou
`language: "es"`, uspořádaným seznamem definic a zvláštním výběrem pro
procvičování. Název souboru používá současný jazykový adaptér; obsah používá
kanonický jazykový identifikátor. Konfigurace je společná cílovému jazyku,
takže změna vlastního jazyka nemění osobní zájmena.

Příklad struktury:

```json
{
  "version": 1,
  "language": "es",
  "persons": [
    {"id": "s1", "label": "yo", "enabled": true},
    {"id": "s2", "label": "tú", "enabled": true},
    {"id": "s3", "label": "él / ella / usted", "enabled": true},
    {"id": "m1", "label": "nosotros / nosotras", "enabled": true},
    {"id": "m2", "label": "vosotros / vosotras", "enabled": true},
    {"id": "m3", "label": "ellos / ellas / ustedes", "enabled": true},
    {"id": "p_<uuid>", "label": "vos", "enabled": false}
  ],
  "practice_person_ids": ["s1", "s2", "s3", "m1", "m2", "m3"]
}
```

Regionální variantu lze přidat běžným přidáním osoby. Nevzniká další systém
regionálních profilů. Uživatelské názvy osob jsou obsah v cílovém jazyce,
nezávislý na jazyku UI.

Výchozí seznamy vycházejí ze současných jazyků. U nového anglického souboru
lze začít pěti osobami podle zadání. U existujícího šestisloupcového souboru
zůstane šest původních identit: dvě historická `you` se nesloučí. Uživatel
může jednu osobu deaktivovat, zatímco její tvary zůstanou v CSV.
Pokud obnovený starší soubor obsahuje další původní osobu, kterou společná
konfigurace dosud nezná, adaptér ji zpřístupní jako neaktivní obnovitelnou
definici s původním ID. Uživatelský výběr se tím nezmění a starý sloupec
nezůstane bez možnosti opětovného použití. Definice se uloží až explicitně.

Dialog nabídne přidání, změnu označení, přesun nahoru/dolů, deaktivaci
a opětovnou aktivaci. Bezpečné odebrání znamená deaktivaci, nikoliv smazání
sloupce nebo historie. Neaktivní definice zůstanou dohledatelné a jejich ID
se znovu nepřidělí jiné osobě. Výběr k procvičování je samostatný; prázdný
výběr je přípustný, ale Repeat bude neaktivní.

Validace kontroluje verzi, jazyk, jedinečnost a bezpečný tvar ID, neprázdné
názvy a platné odkazy výběru. Poškozená konfigurace vyvolá chybu místo
nahrazení výchozími hodnotami. Úpravy se projeví po explicitním uložení
dialogu nastavení osob; zavření bez uložení zachová původní dokument.

### 3. Aktivace modulu a soubory

`StudyCourse` získá `conjugation_enabled`; verzované nastavení kurzů se
rozšíří na verzi 3. Verze 1 a 2 zůstanou čitelné.

Při převzetí starého nastavení se zachová dosavadní viditelnost: existující
Conjugation CSV znamená zapnutý modul, chybějící CSV vypnutý. Tuto adaptaci
vyřeší repository/context s přístupem k datové složce, bez diskových čtení
uvnitř čistého parseru. Nový kurz bude mít Conjugation vypnuté, dokud ho
uživatel nezapne. Při prvním explicitním uložení se výsledek uloží jako bool.

Po zapnutí a uložení nastavení se připraví chybějící validní prázdné CSV
a konfigurace osob. Existující obsah se nepřepíše. Prázdný modul nabídne
Edit a nastavení osob; Repeat zůstane neaktivní, dokud existuje alespoň
jeden záznam s vyplněným tvarem pro vybranou aktivní osobu.

Vypnutí samotného Conjugation zachová CSV i konfiguraci, včetně prázdného
CSV, a skryje nabídku modulu, statistiky i přímé vstupy do editoru/procvičování.
Vypnuté soubory se při načítání přehledů vůbec nečtou. Opětovné zapnutí
obnoví původní obsah. Odebrání celého studijního kurzu ponechá dosavadní
úklid pouze prokazatelně prázdných CSV; konfigurace osob obsahuje uživatelská
data, a proto se automaticky nemaže.

Nové JSON ukládání použije stejný princip jako CSV: validace, zámek cíle,
kontrola očekávané revize a atomické nahrazení souboru. Při neúspěšném
uložení nastavení se odklidí jen vlastní nezměněné nově vytvořené soubory.
Změny existující konfigurace osob mají vlastní explicitní uložení a kontrolu
konfliktů. Nelze předstírat atomickou transakci několika souborů současně.

Záloha přidá pouze rozpoznané konfigurace `*_con_persons.json`, nikoliv
obecně všechny JSON nebo citlivé `settings.csv`. Před prvním rozšířením
existujícího CSV při zápisu vznikne jednorázová kopie původních bytů `.bak`;
existující záložní kopie se nepřepíše.

### 4. Editor a procvičování

Editor dostane samostatný dokument a controller s využitím společných
UI komponent Grammar: seznam s hledáním vlevo, formulář vpravo, Add/Delete,
Apply/Save, hlídání neuložených změn a návrat přes ScreenController.
Podoba Editoru Grammar se tím nemění.

Formulář nabídne cílové sloveso, překlad, stávající volný popis a dynamická
pole podle aktivních definic osob. Překlad může zůstat prázdný. Prázdný tvar
znamená, že pro tuto osobu není připravená otázka. Záznam bez dostupných
tvarů lze zachovat/editovat, ale nedostane se do procvičování. Neaktivní
tvary a neznámé sloupce se při uložení zachovají. Delší seznam osob bude
posuvný, s pevně dostupnými akcemi.

Stejná konfigurace řídí cvičení i review. Výběr vhodných sloves proběhne před
plánováním dávky, takže nedostupná osoba nebo prázdné tvary nezaberou celou
dávku a nevytvoří falešný úspěch. Dosavadní plánování podle R/LR, velikost
dávky, normalizace odpovědí a způsob počítání celých kol zůstanou zachovány.
Vyhodnocení a barevné odhalení použijí společný matching; nynější porovnání
barev je totiž citlivé na velikost písmen, zatímco vlastní scoring není.

Alternativní tvary se v této fázi nezavedou, protože je současné Conjugation
nepodporuje a zadání je podmiňuje existující podporou. Buňka zůstane jedním
správným textem; případné budoucí alternativy mohou rozšířit hodnotu ve
slovníku `forms` bez změny identity osob.

### 5. Statistiky podle osob od nových odpovědí

Vedle nezměněných R/LR doporučuji zavést volitelný CSV sloupec `Person history`.
Jeho obsah bude verzovaný JSON, například:

```json
{"version":1,"results":{"s1":"SF","m3":"S"}}
```

Chybějící sloupec nebo prázdná buňka znamená, že individuální výsledky ještě
nebyly zaznamenávány. Staré R se do něj nepřepočítává. Sloupec se doplní při
novém uložení, původní historie zůstane zachována.

První vyhodnocení kola přidá S/F každé skutečně zodpovídané osobě podle její
vlastní odpovědi. Osoba se správnou odpovědí získá S i při chybě jiné osoby.
Prázdné tvary a nevybrané osoby nemají výsledek. Potvrzení odhaleného řešení
a vynechání nic nepřidávají. Zápis individuální a souhrnné historie proběhne
jedním atomickým uložením stejného CSV, se stávající ochranou konfliktů.

Statistiky zachovají současné souhrny celých kol a přidají přehled osob:
počet skutečně zaznamenaných odpovědí, správné/chybné a jejich poměr.
U starých dat bude individuální úspěšnost neznámá, nikoliv nula.
Popis upozorní, že tyto výsledky začínají novým sběrem; R celých kol může
nově vycházet z různých uživatelských výběrů osob a není měřítkem konkrétní
osoby. Historie neaktivních osob zůstane zachována.

Výpočty poběží v existujícím statistickém workeru. Cache zohlední také revizi
konfigurace osob, aby přejmenování nebo změna aktivních osob nezanechaly staré
popisky a počty aktuálních tvarů. Už připravené přehledy se při scrollování
nepřepočítávají. Poškozená individuální historie se nepřepíše nulami.

## Samostatně ověřitelné kroky po schválení

1. Definice osob, legacy adaptér, verzovaný dokument a bezpečné JSON ukládání.
2. Příznak kurzu, čtení starších nastavení, příprava souborů a dostupnost
   v Home/Statistics/About i přímo volaných entry pointech.
3. Dynamický model slovesa, volba osob, výběr způsobilých záznamů a skórování.
4. Editor s ochranou historie, stabilních ID a konfliktů; nastavení osob.
5. Sběr individuálních výsledků a odpovídající přehled v cached statistikách.
6. Zálohy konfigurace, překlady ve všech šesti UI jazycích, dokumentace,
   vizuální kontrola a kompletní regresní sada.

Nové testy musí pokrýt zejména legacy šest osob versus nové anglické pětice,
libovolný počet osob, vos, změnu názvu/pořadí, deaktivaci a obnovení s původními
tvary, chybějící/prázdné soubory, opakovanou aktivaci, chybu zápisu,
souběžnou editaci, zachování neznámých sloupců i nestandardního původního R,
unikátní ID po mazání, nulový výběr osob a záznam bez vyplněných vybraných tvarů.
U individuálních výsledků také potvrzení po odhalení, skip, oddělení jazyků
a zamezení dvojímu zápisu při opakovaném uložení. UI testy ověří mnoho osob,
dlouhé popisky, malé okno, všechny lokalizace a skrytí vypnutého modulu.

## Dosavadní ověření a hranice schválení

V analytické fázi prošlo 32 cílených regresních testů: `test_training_data`
(17), `test_training_sessions` (8) a `test_refactoring_safety` (7).
Použily izolované služby a dočasné soubory. Bezprostředně před tímto zadáním
prošla také celá stávající sada: 569 testů v 87 modulech.

V této fázi vznikl pouze tento návrh. Produkční implementace Conjugation,
nastavení a uživatelské soubory zatím nebyly změněny. Ke schválení jsou
zejména samostatná konfigurace osob, dynamické sloupce se stabilními ID
a nový volitelný sběr individuálních výsledků. Po schválení následuje
implementace, nové testy a závěrečný report podle zadání.

# GUI a životní cyklus

Při vypnutí druhého studovaného jazyka zobrazuje hlavní stránka jednu širší
kartu. Statistiky nabízejí jen aktivní jazyk, bez přepínače na neaktivní kurz.
About app vypisuje jen aktivní jazyky. Sdíleným zdrojem seznamu je vlastnost
`RuntimePreferences.learning_languages`; uložený `second_language` se nemění.
Při opětovné aktivaci se obnoví přístup k existujícím souborům a pokroku.
Load_setting již nevolá automatické odstraňování neaktivních prázdných CSV.

Seznam N kurzů po uložení skrývá vypnuté řádky; přidání stejného jazyka obnoví
dřívější volby i vyplněná data. Jen ukládání nastavení smí odstranit prázdné
soubory. Inicializace doplňuje chybějící soubory aktivních kurzů. Příznak
gramatiky je samostatný pro každý jazyk: řídí jeho domovskou sekci, kartu/tab
statistik a vstupní funkce. Při přepnutí jazyka ve statistikách se nabídka
aktualizuje; skrytí právě zvolené gramatiky přepne na slovní zásobu.

Štítky právě zkoušeného slova jsou v samostatném spodním grid řádku karty
zadání. `fit_question_prompt` rezervuje jejich skutečnou zalomenou výšku,
aby deset dlouhých štítků nepřekrývalo slovo, kontext ani audio tlačítko.
Bez štítků zůstává původní rozložení a minimální výška karty.

Grammar session ukazuje kromě série v kole také rekord všech uložených
session daného jazyka. Po jeho překonání se popisek změní na zvýrazněné
„Nový rekord“. Shoda nestačí, chybné odpovědi ani změna filtru již dosažený
rekord nezruší. Uložení session uloží také rekord, odchod bez uložení nikoli.

Řazení používá společný tříklikový cyklus ↑, ↓, ↕ (původní pořadí).
Ve statistikách se kliká na metriku nebo záhlaví tabulky, v editoru slovíček
na jediné tlačítko Řadit nebo stejnojmennou položku kontextové nabídky.
Sloupec určuje označená buňka či záhlaví; směr je vidět také v jeho nadpisu.
Zrušení řazení ponechá filtr a rozpracované hodnoty. Neznámá úspěšnost
zůstává při řazení statistik poslední v obou směrech.

Editor slovíček nabízí volitelný sloupec „Štítky“ (`Tags`), podle kterého lze
filtrovat a řadit. Do sloupce lze vložit jednu či více buněk z Excelu přes
Ctrl+V, případně text upravit. Více štítků v jedné buňce oddělují čárky.
Při editaci a vložení se názvy ihned ověřují proti katalogu; neznámý štítek zablokuje
uložení a hláška uvede jeho název a ID slovíčka. Pro označené
slovíčko otevře tlačítko „Štítky slovíčka“ nebo dvojklik do buňky štítků
`WordTagsDialog`: více zaškrtávátek, hledání v obou jazykových názvech a možnost
vymazat výběr. Nabízí výhradně názvy z uloženého katalogu. Výběr přežije změnu
hledání. Apply nahradí štítky právě jednoho slovíčka v rozpracovaném editoru;
Close nic nepřiřadí. Teprve Save hlavního editoru zapíše slovníkové CSV.
V editoru otevře `Ctrl+T` štítky vybraného slova a `Ctrl+Shift+T` katalog.
Ve výběru štítků `Ctrl+F` přesune kurzor do hledání a `Ctrl+Enter` použije
výběr, včetně režimu filtrování. Zkratky jsou uvedené v místní nápovědě
i About app; při vypnutých štítcích se příslušné položky skryjí. Nové zkratky
editoru jsou blokované při ukládání nebo otevřeném dialogu.
Štítky se zobrazují podle nastavení v jazyce studenta nebo studovaném jazyce;
v CSV se ukládají jako stabilní ID. Vkládání přijímá názvy z obou jazyků.
Odvozený sloupec Tag count se neukládá do CSV a má číselné filtry `<`, `=`, `>`.
Seznam ve výběru řadí přiřazené štítky před ostatní a podporuje vymazání výběru.

Při výběru sloupce Tags v horním filtru se textové hledání nahradí tlačítkem
výběru štítků. Otevře stejný dialog se zaškrtávátky v režimu `selection_only`,
který pouze připraví podmínku filtru, nepřiřazuje štítky slovu. Apply potvrdí
výběr, poté se v editoru zvolí kvantifikátor a stiskne Filter:

- **Obsahuje všechny:** má všechny označené štítky, může mít i další.
- **Neobsahuje žádný:** nemá ani jeden z označených štítků.
- **Právě tyto štítky:** má přesně vybranou sadu, bez dalších štítků.

Porovnávají se celé názvy bez ohledu na pořadí, opakování či velikost písmen.
Pro prázdný výběr první dva režimy zahrnou všechna slova; třetí pouze slova
bez štítků. Při návratu k jinému sloupci se obnoví původní textový dotaz i
operátor; volba štítků zůstává dostupná po přepnutí zpět. Filtr respektuje
řazení a po aplikaci zobrazí začátek výsledků. Hledání, filtrování ani výběr
nemění CSV.

Tlačítko „Správa štítků“ v dolním zeleném rámečku otevře modální `TagsDialog` z
[editor_tags](../../app/vocabulary/editor_tags.py). Tabulka obsahuje ID, název
ve výchozím jazyce, překlad a poznámku. ID je pouze pro čtení; „Přidat štítek“
zvolí max ID + 1, „Smazat štítek“ odstraní označené řádky/buňky po následném Save.
Save/Ctrl+S uloží a zavře, Close/Esc nabízí uložení neuložených změn. Chyba
ponechá okno i rozpracované hodnoty otevřené. Katalog se ukládá samostatně od
slovníku; přidání položky automaticky nepřiřazuje štítek žádnému slovíčku.
Dolní akce editoru slovíček jsou rozdělené do dvou řad, aby se nová tlačítka
vešla vedle ostatních akcí. „Štítky slovíčka“ je bez označeného slova neaktivní.
`EditorToolbar(compact=True)` skládá počet, zkratky a nápovědu těsně nad sebe
vlevo, tlačítka vpravo přes všechny tři řádky. Při méně než 520 logických
pixelech dostupných pro text přejde na původní rozložení přes celou šířku,
aby popisky zůstaly čitelné. Ostatní moduly mají výchozí `compact=False`.

Repeat zobrazuje přiřazené štítky ve zvoleném jazyce dole uvnitř tmavého rámu zadání,
v přehledu nového/chybně zodpovězeného slova, v Review word a u předešlého
slovíčka v Session. Například český štítek `Zvířata` se při španělštině zobrazí
jako `Animales` i při anglickém jazyce UI. Více názvů odděluje `·` a text se
zalamuje. Prázdné štítky skryjí celý příslušný popisek. Session respektuje
dosavadní pravidla předešlého slova, včetně přeskakování a právě zkoušeného ID.
Katalog i přiřazení se načtou jednou při otevření procvičování. Chybějící
překlad použije původní název; neplatný katalog ohlásí chybu a procvičování
může pokračovat s původními názvy. Zobrazení žádné štítky ani CSV nemění.

main sestavuje nabídky a karty Vocabulary, Grammar a Conjugation pro každý
studovaný jazyk. Otevření výuky/editoru nahrazuje obsah hlavního rootu;
About, Settings, Statistics a pomocné dialogy jsou samostatná okna.
Conjugation má samostatné Repeat, Edit a Gramatické osoby. Repeat vyžaduje
alespoň jeden vyplněný tvar mezi vybranými aktivními osobami; prázdný modul
umožňuje editaci. Editor má vyhledávaný seznam vlevo a posuvný formulář
vpravo, dynamická pole osob, Add/Delete/Apply a Save/Discard/Cancel při
odchodu. Více než šest osob má posuvnou oblast také v procvičování.
Vypnuté časování se do nabídky ani statistik daného kurzu nezařazuje.
[Navigace](diagrams/GUI_NAVIGATION.md) a [životní cyklus](diagrams/APPLICATION_LIFECYCLE.md).

ModuleHeader sjednocuje logo, nadpis a Save/Close/Exit app. SessionPanel,
EditorToolbar, SearchFilterPanel a ShortcutHint sdílejí pravidla barev,
odsazení a přizpůsobení textu. Lokální layouty určují obsah každého modulu.
Katalog štítků používá stejný `ShortcutHint` jako ostatní moduly. Seznamy
zkratek pro nápovědu i About app pocházejí z `app/about/shortcuts.py`.
SynonymSummary používá menší překlad a zvýrazněné cizí slovo. ReviewDialog
vynechává prázdné detaily včetně synonym.

ScreenController vlastní bindingy, after jobs, traces, dialogy a cleanup.
can_leave rozlišuje čistý screen a potvrzení Save/Discard/Cancel. Asynchronní
uložení samo dokončí navigaci až po úspěchu. ScreenBindings uvolňuje jen své
callbacky. Nevolat unbind_all nebo odstraňovat cizí události.

AppDialog zajišťuje centering, vlastnictví rootu, Escape a zrušení časovačů.
StatisticsWindow má vlastní loading lifecycle: zruší worker delivery a jobs,
drží cover do přípravy všech grafů a při rychlé změně jazyka zpracuje poslední
požadavek. Po zavření se uvolní controller reference.

Podklady skládá Pillow s PanelSurface. Opakované resize podkladu jsou sloučené
krátkým after a původní CTk cache velikostí se při změně rozměru resetuje přes
veřejné image configure. Všechny bitmapy patří svému Tk interpreteru.

GUI testy kontrolují rozložení v šesti jazycích a některá malá rozlišení.
Ruční ověření na cílovém DPI, reálném monitoru a s hardwarem audia zůstává
nutné; automatická kontrola není pixelová garance všech možných obsahů.

Filtr editoru slovíček používá text po 250 ms bez dalšího psaní, Enter okamžitě.
Použije také změnu operátoru nebo potvrzení výběru štítků. Refresh vymaže text,
výběr štítků i řazení; samostatné tlačítko Filter zde není. Ve výběru sloupců
filtru nejsou Phonetic, Repetition ani Next repetition. Odvozený Tag count je
v tabulce hned za Tags a nadále se nezapisuje do CSV.

Procvičování spuštěné ze statistik dostane vlastní návratovou akci `on_back`.
Close i úspěšné Save znovu otevřou statistiky původního jazyka a příslušné záložky
(Vocabulary nebo Grammar) s aktuálními daty. Běžné spuštění z hlavní nabídky se
nadále vrací na hlavní obrazovku; Exit app zůstává ukončením aplikace.

Session panel gramatiky po první odpovědi zobrazí kompaktní úspěšnost
posledních nejvýše 10 výsledků v aktuálním kole. Pod popiskem je deset
zaoblených značek: zelené jsou správné, terakotové chybné a neobsazené tlumené.
Pořadí je zleva od starších k novějším odpovědím. Samotné odhalení se počítá
jako chyba stejně jako ve skóre kola; přeskočení výsledek nevytváří.

`grammar.layout._fit_session` přizpůsobuje šířku textu a při nedostatku výšky
zmenšuje vertikální mezery a vnější odsazení. Velikost písma zkratek zůstává
12; krátký nový popisek může zmenšit písmo ze 13 na 12. Změny geometrie se
slučují 20ms časovačem, který se při zničení panelu ruší. Běžná geometrie se
vejde bez scrollbaru, velmi nízké okno nebo dlouhý obsah zůstávají scrollovatelné.

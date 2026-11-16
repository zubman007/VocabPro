# Výuková pravidla

## Slovíčka

Písmenková nápověda má nastavitelný režim: automatická, na vyžádání tlačítkem,
nebo vypnutá. Odhalení se resetuje při každé další otázce včetně přeskočení.
Nemění vyhodnocení odpovědi, historii ani plán dalšího opakování.

course_overview vybere slova s Next repetition před aktuálním lokálním časem.
Více než čtyři S v historii patří do opakování, nejvýše čtyři do učení.
Učení se omezí náhodným learn_batch. Pokud není nic k opakování, použije se
nejbližší plán z položek s alespoň čtyřmi S. Běžný neprázdný seznam due se
tímto fallbackovým repeat_batch neomezuje.

PracticeSession vybírá náhodně ze zbývajících ID. Prázdná historie při prvním
představení dostane S. Správná odpověď připojí S; dokončení slova nastane až
má před odpovědí alespoň čtyři S. Chyba připojí F a ukáže opravu. Next odstraní
slovo ze zbývajících bez nové správné/chybné odpovědi. Přesun mezi seznamy
používá index pozic a výměnu posledního prvku místo opakovaného hledání.

next_repetition ignoruje počáteční úsek po čtvrté S včetně. Z následného
úseku spočítá koncové S a vybere počet dní z days_gap_map; výchozí default_wait
je 200 dní. Mapa v shared/config.py: 0→0, 1→1, 2→2, 3→4, 4→7, 5→15,
6→25, 7→50, 8→100, 9→150. Po F je streak 0 a termín je aktuální čas.

answers_match normalizuje Unicode NFD, odstraňuje diakritiku a interpunkci,
ponechává lomítka jako oddělovače variant. Stačí neprázdný průnik variant
očekávané a zadané odpovědi. Synonymní vazby se do této množiny nepřidávají.
ChoicePool pro poslech drží omezenou cache kandidátů, vyloučí správný text,
vybere tři jiné řádky a zamíchá čtyři možnosti. Stejný překlad na různých
řádcích zachovává svou váhu; algoritmus nezaručuje tři různé texty distraktorů.

## Gramatika

Kategorie se nejprve filtrují normalizovaným category_key; mimo vybraná témata
se nepočítají váhy ani nevytváří fronta. `grammar.data.question_weights` poté
pro každou dostupnou otázku smíchá následující normalizované signály:

| Podíl váhy | Signál |
| --- | --- |
| 30 % | Rovnoměrné zastoupení všech dostupných otázek. |
| 20 % | Dosud nezodpovězené otázky (prázdná historie S/F). Pokud žádné nejsou, podíl se rozdělí rovnoměrně. |
| 30 % | Chybovost posledních 10 odpovědí, zvýhodnění poslední chybné odpovědi a potlačení dlouhé série správných odpovědí. |
| 10 % | Stáří poslední odpovědi podle LR; růst je odmocninový a omezený na 180 dní. |
| 10 % | Menší dosavadní počet odpovědí, aby už procvičené otázky nevytlačily málo známé. |

Signál obtížnosti je `(1 + 2 × podíl F v posledních 10 + 1,5 × poslední je F)
/ sqrt(1 + koncové S)`. Signál stáří je `1 + sqrt(dny)`; chybějící či neplatné
LR a budoucí datum mají neutrální hodnotu 1. Pokrytí má hodnotu
`1 / sqrt(1 + počet odpovědí)`. Každý sloupec se zvlášť vydělí svým součtem
a následně se násobí uvedeným podílem; výsledné pravděpodobnosti mají součet 1.
Podíly určují počáteční pravděpodobnosti, nikoli pevné kvóty otázek za kolo.

Kategorie nemají stejné kvóty. Při stejné historii a stáří má téma se 100
otázkami dvojnásobnou počáteční pravděpodobnost oproti tématu s 50 otázkami.
Oba počty se vztahují pouze k aktuálně vybraným kategoriím.

`Shuffle_copy` vytvoří vážené náhodné pořadí bez opakování pomocí klíčů
`-log(1 - U) / váha`, kde U je rovnoměrně náhodné číslo. Klíče se seřadí
vzestupně a session používá deque. Každá vybraná otázka se tedy v celém kole
objeví právě jednou; vyšší váha zvyšuje šanci na časné zařazení. Náklady
přípravy jsou O(n log n); další otázka už nevypočítává váhy celé množiny.
Možnosti odpovědí se stále míchají rovnoměrně a nezávisle.

`GrammarSession.progress` uchovává pracovní historii a čas poslední skutečné
odpovědi podle ID. Kontrolér ji sdílí mezi filtrovanými koly. Restart a změna
filtru proto zohlední i dosud neuložené odpovědi; zdrojové otázky se nemění.
Přeskočení ani samotné odhalení řešení do této historie nepřidává S/F.

Správná hodnota pochází z option_1. choose
zapíše S/F do pending_answers, zvýší počitadla a ukáže zpětnou vazbu. Reveal
zvýší chybné počitadlo session a odhalí řešení, ale sám nepřidává pending
odpověď do historie. Toto je zachované stávající chování.

save_answers jednou vytvoří index ID, ověří všechny odpovědi a případně obsah
otázky, seskupí přírůstky historie v pořadí dávky a LR nastaví podle poslední
odpovědi pro ID. Při neplatném ID se neuloží ani platná část dávky.

Pro kompaktní přehled aktuální formy drží `GrammarSession.recent_results`
nejvýše 10 booleovských výsledků v pořadí odpovědí. Úspěšnost je počet True
dělený délkou této fronty, zaokrouhlený na celé procento. Duplicitní odpověď
se nepřidá, reveal přidá jediné False a skip nic. Restart nebo změna kategorií
zahajují nové kolo s prázdným přehledem; pracovní historie pro vážení zůstává
zachovaná. Tento přehled se nezapisuje do CSV a nemění výukové algoritmy.

## Časování

Nejdřív se vyřadí záznamy bez vyplněných tvarů pro vybrané aktivní osoby.
Prázdný výběr nepovolí lekci. select_verbs zamíchá priority, pak řadí koncové S vzestupně a LR od nejstaršího,
neznámé LR první; vrací conjugation_batch položek. Prázdný očekávaný tvar
osoby se nezkouší. Odpověď ignoruje case a nahrazuje ñ (u odpovědi též ň) za n.
Chybný pokus zapisuje F, ukáže očekávané tvary. Následná správná odpověď po
odhalení nepřidává S, pouze dokončí sloveso. Neodhalený správný pokus zapisuje S.
První vyhodnocení navíc zaznamená vlastní S/F každé vybrané osobě s neprázdným
tvarem; správná osoba dostane S i při F celého kola. Opakované potvrzení
odhaleného řešení a přeskočení další výsledky nevytvářejí. Původní R/LR se
nepřevádějí na domnělé výsledky osob. Osoby mají stabilní ID; změna popisku,
pořadí a deaktivace nemažou tvary ani historii. Časy a způsoby zůstávají mimo
strukturovaný model této fáze; Description je dál volný text.

Algoritmy jsou v [practise_session](../../app/vocabulary/practise_session.py),
[practise_data](../../app/vocabulary/practise_data.py),
[grammar/session](../../app/grammar/session.py),
[conjugation/data](../../app/conjugation/data.py) a
[conjugation/session](../../app/conjugation/session.py).

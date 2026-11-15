# Výkon a optimalizační zásady

## Zátěžové scénáře štítků (15. 11. 2026)

Nový scénář zpracuje 10 000 syntetických řádků, smíšené názvy ve dvou
jazycích, ID, převod zpět, přesný množinový filtr a neplatný poslední řádek.
První běh celé této kombinace naměřil 183,2 ms. Jde o lokální kontrolu
škálování, nikoli garantovanou odezvu aplikace na všech počítačích.

U výběru štítků se zalamování popisků nyní nastavuje pouze při skutečné
změně šířky. Test 200 opakovaných resize při stejné šířce ověřuje, že se
popisek znovu nekonfiguruje. Celý šestijazykový GUI scénář se 120 dlouhými
štítky trval před úpravou 53,0 s a po ní 65,4 s; rychlejší odezva tímto
měřením doložená není. Test zahrnuje vytváření oken, hledání a opakované
vykreslení, běžel na sdílené pracovní stanici. Velké seznamy stále vytvářejí
widget pro každou viditelnou položku; případná virtualizace vyžaduje samostatné
profilování a ověření zachování výběru.

save_answers má jeden index ID místo nového boolean masku pro každou
odpověď. Náklady přípravy a zápisu jsou přibližně úměrné počtu otázek a
odpovědí, místo jejich součinu. Zachovává pořadí S/F i poslední LR.

Statistická cache je omezená, invaliduje podle dat a voleb a kopíruje vracené
hodnoty. Čisté výpočty běží mimo UI, grafy se vytvářejí postupně, přesto jsou
všechny hotové před prohlížením. Scroll podkladu používá hotové pixely.

SynonymCounts je vlastněný editorem, ne globální neomezenou cache. Při běžné
editaci znovu nečte CSV; kontroluje pouze souborovou signaturu. Background
resize slučuje události a uvolňuje obsolete varianty CTkImage přes veřejné API.
Životní cyklus screenů/dialogů ruší časovače a callbacky.

Výchozí a konečná měření s metodikou jsou v
[PERFORMANCE refaktoringu](../refactoring/PERFORMANCE.md). Naměřený import
není čas celého startu GUI. Odhad počtu RGBA bajtů není RSS procesu. Síťová
latence a fsync se nemají zaměňovat za náklady algoritmu.

Při další optimalizaci nejprve měřit konkrétní scénář. Neměnit deepcopy cache
na sdílený mutable objekt, nevynechávat fsync kvůli lepším číslům a nepřesouvat
Tk/Matplotlib canvas operace do pracovního vlákna.

Hover používá blitting statického podkladu místo opakovaného vykreslení os,
dat a textů. Cache se obnoví po full draw a zruší při resize; nepodporovaný
backend bezpečně přejde na draw_idle. V izolovaném Agg testu 20 aktualizací
vyšlo na 388,08 ms plným vykreslením a 18,59 ms blittingem (pokles 95,2 %).
Toto měření nezahrnuje přenos pixelů přes Tk/OS a není časem načtení statistik.
SciPy již není přímá závislost: jedinou interpolaci nahrazuje numpy.interp.

## Vážené gramatické kolo (15. 11. 2026)

Syntetický soubor 10 000 otázek, čtyři druhy historie, 3 zahřívací běhy a
25 měřených opakování přípravy pořadí v projektové `.venv`:

| Příprava pořadí | Medián | Maximum |
| --- | ---: | ---: |
| Původní shuffle + pevné řazení koncových S | 3,34 ms | 5,21 ms |
| Nová kombinace pěti signálů + vážené pořadí | 30,58 ms | 41,32 ms |

Nová logika provádí více práce; nejde o zrychlení původního algoritmu.
Nárůst mediánu o 27,24 ms nastává jednou při přípravě kola. Následující
průchod všemi 10 000 otázkami s mícháním čtyř možností trval 17,63 ms celkem
(bez GUI, sítí a zápisu CSV). Výběr další otázky zůstává O(1) díky deque.
Příprava má O(n log n), nevzniká opakovaný přepočet celého zbytku po každé otázce.

Kontrola 12 000 nezávislých dvouotázkových kol se seedem 261115 prokázala,
že se nové signály skutečně projevují. Při stejných ostatních podmínkách:

| Scénář: podíl, kdy zvýhodněná otázka přijde první | Původně | Nově |
| --- | ---: | ---: |
| Stejná historie, ale starší LR | 49,43 % | 54,48 % |
| Stejný počet odpovědí a koncových S, více F v posledních 10 | 49,43 % | 55,04 % |

Jde o kontrolovaná syntetická měření, nikoli garanci odezvy každého počítače.
Vyšší váha neznamená pevné pořadí ani opakované vložení stejné otázky do kola.

## Kompaktní kategorie gramatiky (15. 11. 2026)

Stejných šest syntetických kategorií při šířce 1400 logických pixelů:
výška běžného řádku klesla ze 128 na 106,4 px (−16,9 %). Celý panel včetně
nových tří tlačítek řazení klesl z 1016,8 na 877,6 px (−13,7 %).
Úzká okna nadále dovolují zalomení překladů; nemají pevný limit výšky řádku.
Řazení používá číselné hodnoty, přemístí existující widgety bez jejich nové
konstrukce a nečte CSV. Samostatný duplicitní graf počtů kategorií se již
nevytváří, včetně jeho FigureCanvas a specifické renderovací větve.

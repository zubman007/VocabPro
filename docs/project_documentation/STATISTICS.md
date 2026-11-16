# Statistiky

Přehledy štítků a kategorií gramatiky sdílejí barvy a zaoblení řádků,
stejně vysoké tři ovladače řazení a styl kompaktních akcí procvičování
z `statistics/components.py`. Mají sladěné odsazení nadpisu i popisu.
Štítky si zachovávají tabulkové řádky, hledání a stránkování; gramatika
podrobné karty s odpověďmi a pokrytím. V tabulce štítků jsou názvy číselných
sloupců zarovnané nad příslušnými hodnotami nezávisle na ovladačích řazení.

Gramatika zobrazuje v samostatné kartě nejlepší sérii správných odpovědí
dosaženou během session daného jazyka. Evidence začíná zavedením této funkce; starší historii R nelze
globálně seřadit napříč otázkami a historický rekord z ní není dopočítáván.
Rekord načítá `app/repositories/grammar_records.py` také při použití cache,
aby po uložení session nebyla hodnota zastaralá.

Nahoře v přehledu kategorií je drobný údaj o jejich celkovém počtu. Zahrnuje
i skupinu „Bez kategorie“, pokud existují nezařazené otázky. Řádky mají mírně
menší písmo a svislé mezery; delší texty se nadále zalamují. Při nezměněných
výsledcích se jejich widgety zachovají, stejně jako při řazení.
V kontrolním rozložení při šířce okna 1200 logických pixelů se výška běžného
řádku snížila ze 106,4 na 85,6 logického pixelu (o 19,5 %).

Úplně dole v záložce Grammar je graf „Aktuální série u gramatických otázek“.
Každou otázku zahrne právě jednou podle konce její historie `R`: neprocvičená,
poslední odpověď chybná, jedna správná v řadě, dvě nebo alespoň tři. Neplatné
znaky historie nejsou odpovědi, stejně jako v souhrnech kategorií. Pět
vodorovných pruhů má společnou stupnici 0–100 % všech otázek a uvádí také
absolutní počty. Nejde o časový vývoj ani o globální rekord session; nepoužívá
ani nevyžaduje nová historická data.

Výpočet `grammar_question_progress` probíhá v existujícím workeru a výsledek
je součástí cache podle revize CSV. `GrammarProgressPanel` vytváří pět řádků
jen jednou, při změně výsledků upraví pouze hodnoty a délky pruhů. Stejný
snímek nevyvolá žádné aktualizace widgetů. Scrollování graf nepřepočítává ani
nevytváří další Matplotlib figuru. Chybějící nebo prázdná gramatika vynuluje
graf i rekord při přepnutí kurzu; vypnutá gramatika celou záložku nadále skryje.

V záložce Vocabulary je kompaktní přehled „Slovíčka podle štítků“
(`VocabularyTagsPanel` z [vocabulary_tags.py](../../app/statistics/vocabulary_tags.py)).
Zobrazuje nejvýše 15 řádků na stránku, hledání a řazení kliknutím na záhlaví
počtu slov, odpovědí a úspěšnosti. Opakované kliknutí cyklí vzestupně →
sestupně → původní pořadí, směr ukazuje šipka u metriky. Stejná funkce
`app/ui/sorting.py:next_sort` řídí kategorie gramatiky, statistickou tabulku
a editor slovíček. Nemá vlastní svislý scrollbar.
U každého použitého štítku uvádí počet přiřazených slov, počet zaznamenaných
opakování a úspěšnost s malým zeleným ukazatelem. Bez odpovědí je úspěšnost
neznámá (`—`), nikoliv nulová. Dlouhé názvy se zkracují výpustkou, hledání
pracuje s celým názvem. Po změně jazyka se hledání a stránka obnoví.
Přehled zahrnuje i nepoužité katalogové štítky s nulovými počty; jejich Repeat
je neaktivní. Repeat u použitého štítku otevře lekci jen jeho slovíček, stabilně
seřazených podle Next repetition, bez časového omezení na dnešní termín.
Prázdné/neplatné termíny jsou první. Prázdná historie zůstává prázdná a běžný
PracticeController tak otevře Learn. Výběr dalších slov používá původní pořadí
i po odebrání dokončených slov. Neprázdná přiřazení se párují přes ID katalogu.
Slabá slova mají menší mezery a písmo, ale zachovávají všechna původní data.

`tag_statistics(frame, outcomes)` projde přiřazení v jediném průchodu.
Duplicitní štítek na slově nezapočítá dvakrát, názvy slučuje bez ohledu na
velikost písmen. Slovo s více štítky je v každém z nich, takže součet počtů
nemusí odpovídat velikosti slovníku. Počet slov zahrnuje i dosud nenaučená.
Úspěšnost je vážená podle odpovědí: součet S / (součet S + součet F), ne
průměr procent jednotlivých slov. Používá stejné již spočítané výsledky po
úvodním učení jako hlavní souhrn slovníku. Výpočty běží ve stávajícím workeru
a patří do stejné cache závislé na revizi slovníkového CSV. Nečtou znovu
katalog štítků ani historii při stránkování.

Statistic table zobrazuje celou aktuální stránku (nejvýše 25 řádků) bez
vlastního svislého scrollbaru. Výška se přizpůsobí i filtru a poslední stránce;
kolečko nad tabulkou posouvá vnější stránku statistik. Vodorovný scrollbar
se ukáže pouze tehdy, když se sloupce při úzkém okně nevejdou.

Stats vytvoří StatisticsWindow a jeho StatisticsController. Controller vlastní
widgety, výběr jazyka, poslední tabulku a worker; modul nedrží globální okno.
prepare_statistics připraví slovíčka a případně gramatiku a časování.
BackgroundTask vrátí hodnoty do UI pollingem. _render_charts vytváří po jednom
grafu a mezi nimi uvolní event loop; cover zůstane až do konce všech grafů.

Výpočty v statistics/data.py:

- Slovníkový souhrn počítá položky a S/F u slov s více než čtyřmi S; z jejich
  historie odstraňuje počáteční prefix jednoho až pěti S stejně jako původní
  implementace. Není to totéž jako počet všech stisků v Session.
- Forecast simuluje ideální další úspěchy po výchozím učení, s plánovací mapou
  a horizontem; není predikcí skutečné budoucí úspěšnosti.
- Growth je kumulativní počet podle Created, s historickým sentinelovým datem
  1900-01-01 zahrnutým do základu. PoS porovnává reálné a ideální podíly.
- Tréninkové souhrny počítají S/F z R. Kategorie gramatiky počítají otázky,
  otázky s historií, všechny správné/chybné odpovědi a jejich podíl. Nejprve
  se zobrazují horší výsledky; bez historie nemá kategorie accuracy.
  Přehled má tlačítka řazení podle počtu otázek, počtu různých vyzkoušených
  otázek a úspěšnosti. První klik řadí vzestupně, druhý sestupně a třetí
  obnoví výchozí pořadí. Aktivní metriku a směr ukazuje
  barva a šipka. Bez odpovědí zůstávají kategorie při řazení úspěšnosti poslední
  v obou směrech. Řazení se při přepnutí jazyka v témže okně zachová.
  Zkrácená odsazení a výška ukazatelů ponechávají všechny údaje a procvičování.
  Samostatný graf Questions by grammar topic byl odstraněn; jeho počty jsou
  dostupné v tomto seřaditelném přehledu a nevzniká pro něj další figura.
- Difficult words používá posledních deset platných S/F; kandidát musí mít
  alespoň pět odpovědí a dvě F, řadí se podle chyb, podílu a názvu, nejvýše šest.

StatisticsCache má nejvýše 12 položek. Klíč obsahuje cestu, namespace a volby
výpočtu, u slovíček i dnešní datum. Signatura souboru zahrnuje mtime/ctime,
velikost a inode. Výsledek se kopíruje, aby jej UI nemohlo změnit v cache.
Při změně během čtení se výpočet nejvýše jednou zopakuje; další změna je chyba.

Generate_chart spravuje FigureCanvas, hover anotace a uvolnění callbacků.
Soukromý _HoverBlit uchovává statické pixely celé figury; při hoveru obnoví
podklad, vykreslí jen anotaci a provede blit. Full draw obnovuje cache,
resize ji zneplatní. Backend bez podpory blittingu používá původní draw_idle.
Při odstranění grafu se odpojí také draw/resize callbacky a uvolní podklad.
Prognóza používá numpy.interp: lineární spojení bodů bez překmitů, včetně
jediného bodu. Dřívější hladká kubická interpolace SciPy byla odstraněna;
změnil se pouze tvar spojnice, nikoli vstupní hodnoty nebo výpočet prognózy.
SuccessRing rasterizuje ve vyšším rozlišení a zmenšuje LANCZOS pro hladké
okraje. StatisticsBackdrop posouvá již připravené pixely; při scrollu
nespouští Pillow rendering. Chybějící conjugation skryje kartu i záložku.

[Tok statistik](diagrams/STATISTICS_FLOW.md). Známé omezení: samotné vytvoření
jedné složité Matplotlib figury stále zabere část UI vlákna; nedělí se do
podprocesů ani se nepřesouvá Tk rendering do workeru.

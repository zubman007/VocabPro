"""




cjvv xzih pfrc dqmw
hovnival007!
hovnival007!

sjednotit stats conjugation a grammar designově troškinku.. I obsahově... Uvaž sám.



Když dělám poslední slovo v voc repeat, udělá to pouze úspěšný zvuk.. Mělo by to taktéž přehrát dané slovo jako u všech pokusů.



synonyma při opakování by měla respektovat způsob konkrétního opakování.. V review word je zobraz celá. Ale třeba když mám pouze audio, nemělo by tam být zobrazen čeký překlad u synonym.. Pak to "prozradí" správnou odpověď.. U kontextového opakování taktéž-- U opakování typu české slovo a já mám napsat cizí název, to tam můžeš napsat všechno.


Email se pořád neposílá pro seznam.cz.. Dávám tam dobré heslo na mail i adresu, ale pořád nic.. Taky když tam to heslo dám a uložím, nic se tam nezobrzauje..Pokud pošlu zkušební mail a ten nedojde, má se zkušební mail odeslat na mail, kde chci posílat maily. Pokud ale tam je chyba.. Proč mi to nehodí chybovou hlašku?


Ty fily na conjugation person dej všechny do jednoho filu.. Všechny jazyky.

U data integrity u chyby vypiš konkrétní řádek... Trošku jiným písmem aby to bylo oddělitelné.
Ten cancel tlačítko z data integrity zruš..

 
Jak funguje ten release? Který script musím spustit, aby se stpustila aplikace? Když spustím ten release, zapne se pouze start. A co je to vocabpro_data? Udělej to tak, že fily budou v tom novém exe.. Ale při vytvoření exe bude exe prázdné.. Když to tedy spustím, fily budou chybět.. Dále to udělej tak, že když aplikaci spustím a nějaký file chybí, prostě ho vytvořím nový, prázdný. Dej tam tedy nějaké defaultní nastavení při prvním spuštění exe.. Jinak je to fajn.. Prostě to chci tak, že spustím script a vygeneruje se mi funkční nová verze exe.. Dále do exe verze nepůjdou věci jako je dokumentace a tools.. Ty tam jsou samozřejmě zbytečné.. Ani testy.. Pouze věci, které jsou nezbytné k běhu aplikace.


Jaký script musím spustit na ten quiality check?

Udělej to intuitivněji.. Nějaký jeden script, co spustí vše, další pomocné scripty budou ve spšl složce.. To samé u exe release.. Tyto dvě věci budou v tools.. quelity test a release budou mít spešl složky..





Udělej pořádek.. Staré nefunčkní testy smaž.. 




# VocabPro – Kompletní aktualizace dokumentace
Proveď důkladnou analýzu celého projektu VocabPro a **aktualizuj veškerou existující dokumentaci** tak, aby přesně odpovídala aktuálnímu stavu zdrojového kódu, včetně EXE distribuce pomocí Nuitky.
Cílem je profesionální, přehledná a srozumitelná dokumentace, díky které lze rychle pochopit architekturu, fungování i strukturu celého projektu.
### 1. Architektura a logika aplikace
- Popiš celkovou architekturu, jednotlivé moduly a jejich odpovědnosti.
- Vysvětli, jak spolu moduly komunikují a jak na sebe navazují.
- Zdokumentuj spouštění aplikace, načítání dat, ukládání, nastavení, lokalizaci, statistiky, zálohování a EXE distribuci.
- Vysvětli hlavní datové toky a důležitá návrhová rozhodnutí.
### 2. Kompletní přehled zdrojového kódu
- Vytvoř seznam všech relevantních skriptů a zdrojových souborů.
- U každého uveď jeho účel, hlavní třídy/funkce, závislosti a návaznosti na ostatní soubory.
- Přidej přehled struktury adresářů.
- Rozlišuj aktivní kód, testy, konfigurační soubory a build skripty.
- Vysvětli, kde hledat konkrétní funkcionalitu a jak ji bezpečně rozšiřovat.
### 3. Diagramy
Vytvoř přehledné diagramy, ideálně pomocí Mermaid:
- Architektura aplikace a propojení modulů.
- Závislosti mezi hlavními skripty.
- Tok dat od načtení po uložení.
- Spouštění aplikace a inicializace modulů.
- Proces vytváření a obnovy záloh.
- Proces sestavení a aktualizace EXE.
Diagramy musí vycházet ze skutečného kódu, nikoliv z předpokladů.
### 4. Statistiky projektu
Automaticky spočítej a zdokumentuj:
- Celkový počet zdrojových souborů.
- Počet řádků kódu celkem a podle jazyků.
- Počet řádků jednotlivých skriptů.
- Počet tříd, funkcí a metod, pokud je lze spolehlivě zjistit.
- Přehled největších modulů.
Odděl zdrojový kód od komentářů, prázdných řádků, testů, generovaných souborů a externích závislostí. Uveď metodiku výpočtu a datum vytvoření statistik.
### 5. Výstup a údržba
- Aktualizuj existující README a veškerou relevantní dokumentaci.
- Odstraň zastaralé informace a zbytečné duplicity.
- Zachovej přehlednou strukturu dokumentace v Markdownu.
- Vytvoř také **kompletní PDF dokumentaci** s obsahem, kapitolami, tabulkami, diagramy a statistikami.
- Zajisti správné vykreslení české diakritiky, diagramů a odkazů.
- Přidej jednoduchý skript pro opakovanou aktualizaci statistik a generování PDF z dokumentace.
- Dokumentaci uspořádej tak, aby bylo snadné ji průběžně aktualizovat při dalším vývoji.
### Důležitá pravidla
- **Neměň aplikační kód ani uživatelská data.** Pracuj pouze s dokumentací a pomocnými skripty pro její generování.
- Nevymýšlej neexistující funkce, soubory ani závislosti.
- Nevkládej do dokumentace hesla, tokeny ani jiné citlivé údaje.
- Zachovej necommitnuté změny.
- Pokud některé diagramy nebo statistiky nelze automaticky vytvořit, použij vhodnou alternativu a vysvětli omezení.
**Výsledek:** Aktuální, profesionální dokumentace celého VocabPro, včetně přehledného PDF, skutečných architektonických diagramů, kompletního seznamu skriptů, jejich návazností a přesných statistik zdrojového kódu.
Nezůstávej u návrhu – proveď analýzu, aktualizaci dokumentace, vytvoření PDF i potřebných generačních skriptů. Na závěr stručně vypiš vytvořené soubory a způsob jejich aktualizace.











24.1. Štěpa
27.1. Barča
11.2. Adélka
15.3. Verča
30.3. Jura
22.4. Krb
27.4. Pavla
5.5. Pavlík
20.5. Kubík
27.5. Mamka
26.6. Cuba Tarija
7.8. Heďa
13.8. Eliška
21.8. Matěj
14.9. Manu
15.9. Maruška
15.9. Luz
26.9. KOLÓN
4.10. Taťka
10.10. Dáša
1.11. Simonka
2.11. Adam


23.12. Kuba



verter
moverse
distraer
tender
emprender
regir
aducir
pertenecer
perseguir

"""


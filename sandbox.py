"""



V setting u learning u grammar a conjugation přehod u jednoho z nich to nastavení, ať je to jednotně.. Nejdříve batch a pak remember filter.




# VocabPro – Kompletní systém kontroly integrity dat
Analyzuj celý projekt VocabPro a implementuj profesionální, centralizovaný systém kontroly integrity uživatelských dat.
**Hlavní cíl:** Zajistit, aby aplikace dokázala automaticky odhalovat poškozená, neplatná, neúplná nebo vzájemně nekonzistentní data, předcházet vzniku nových chyb a umožňovala uživateli provést kompletní audit.
Systém musí být bezpečný, výkonný, rozšiřitelný a plně kompatibilní se současnou aplikací.
## 1. Analýza datové architektury
Nejprve důkladně analyzuj:
- Všechny datové soubory, databáze a používané formáty.
- Struktury slovníků, překladů, jazyků, tematických kategorií a synonym.
- Data modulů Grammar a Conjugation.
- Statistiky učení, rekordy a historii odpovědí.
- Uživatelská nastavení a konfigurace.
- Mechanismy načítání, ukládání, importu, exportu a zálohování.
- Vazby mezi jednotlivými datovými strukturami.
- Současné validační mechanismy a jejich případné duplicity.
Na základě skutečného kódu definuj pravidla integrity. **Nevymýšlej povinná pole, omezení ani vztahy, které neodpovídají existující architektuře.**
Rozlišuj skutečné chyby od legitimních volitelných, historických nebo prázdných hodnot.
## 2. Rychlá kontrola při spuštění aplikace
Implementuj automatickou kontrolu integrity při každém spuštění VocabPro.
Kontroluj zejména:
- Existenci a čitelnost nezbytných datových souborů.
- Základní správnost jejich struktury.
- Podporované verze datových formátů.
- Přítomnost skutečně povinných údajů.
- Zjevné poškození nebo neplatné hodnoty.
- Základní konzistenci důležitých datových vazeb.
**Požadavky:**
- Kontrola musí být maximálně rychlá a nesmí výrazně prodlužovat start aplikace.
- Neprováděj při každém spuštění zbytečný kompletní průchod všemi daty.
- Využij existující načítací mechanismy a pokud možno nekontroluj stejná data opakovaně.
- Pokud to architektura umožňuje, odděl rychlé kritické kontroly od méně důležitých kontrol prováděných na pozadí.
- Nepřistupuj ke GUI z pracovního vlákna způsobem, který není bezpečný pro použitý framework.
- Při nalezení nekritického problému umožni pokračovat v používání aplikace.
- Pokud jsou data nebezpečná pro další zápis, zabraň jejich přepsání nebo dalšímu poškození a nabídni bezpečný postup.
Nikdy automaticky nepřepisuj poškozená data výchozími hodnotami pouze proto, že se nepodařilo načtení.
## 3. Validace při ukládání dat
Zaveď jednotný validační mechanismus pro vytváření a úpravy dat.
Před uložením ověřuj podle konkrétního typu záznamu:
- Povinná pole a jejich datové typy.
- Platnost hodnot a povolených rozsahů.
- Unikátnost identifikátorů tam, kde je vyžadována.
- Existenci referencovaných záznamů.
- Konzistenci vztahů mezi daty.
- Správnost relevantních statistických hodnot.
- Kompatibilitu se současným datovým formátem.
Validace musí být implementována **v datové vrstvě**, nikoliv pouze v grafickém rozhraní, aby platila také pro importy, obnovu záloh a další způsoby zápisu.
Využívej společné validační komponenty a nepřidávej duplicitní logiku do jednotlivých modulů.
Při chybě:
1. Zabraň uložení neplatné změny.
2. Zachovej původní data.
3. Zobraz uživateli srozumitelnou informaci.
4. Zaznamenej technické podrobnosti pro diagnostiku.
Zápisy prováděj bezpečně a atomicky, pokud to použitá technologie umožňuje.
## 4. Kompletní audit integrity dat
Do **Nastavení VocabPro** přidej samostatnou funkci pro kompletní kontrolu integrity.
Například sekci:
**Nastavení → Integrita dat**
Uživatel zde musí mít možnost spustit důkladný audit všech relevantních uživatelských dat.
Audit má kontrolovat:
- Slovníky, slovíčka, překlady a jejich vazby.
- Jazyky, kategorie a přiřazené štítky.
- Synonyma a jejich reference.
- Grammar a Conjugation.
- Statistiky, rekordy a historii učení.
- Uživatelská nastavení.
- Konzistenci identifikátorů a vzájemných odkazů.
- Duplicitní nebo osiřelé záznamy, pokud jsou podle datového modelu neplatné.
- Strukturální poškození a nepodporované formáty.
Rozlišuj tři závažnosti nálezů:
- **Critical:** Poškození nebo nekonzistence ohrožující bezpečné načítání či ukládání.
- **Warning:** Podezřelé nebo neúplné údaje, které nemusí znamenat skutečnou chybu.
- **Info:** Informativní upozornění a doporučení.
Kontrola nesmí automaticky měnit žádná uživatelská data.
## 5. Grafické rozhraní auditu
Vytvoř přehledné rozhraní respektující současný design VocabPro.
Mělo by obsahovat:
- Tlačítko pro spuštění kompletní kontroly.
- Průběh kontroly a aktuálně kontrolovanou oblast.
- Počet zkontrolovaných záznamů.
- Počet nalezených kritických chyb, varování a informací.
- Výsledky rozdělené podle modulů.
- Konkrétní popis nalezených problémů.
- Identifikaci dotčeného souboru nebo záznamu, pokud je bezpečné ji zobrazit.
- Doporučený postup řešení.
- Možnost exportovat diagnostický report.
Při větším objemu dat nesmí kontrola blokovat nebo zamrazovat GUI.
Zajisti bezpečné ukončení nebo zrušení auditu a správné uvolnění prostředků.
Pokud to odpovídá existující architektuře, zobraz také datum posledního úspěšně dokončeného auditu.
## 6. Bezpečnost uživatelských dat
**Toto je absolutní priorita implementace.**
Dodrž následující pravidla:
- Nikdy automaticky nemaž slovíčka, statistiky ani jiné uživatelské záznamy.
- Nikdy neopravuj data bez výslovného souhlasu uživatele.
- Samotný audit musí být pouze pro čtení.
- Při chybě načítání nepřepisuj existující soubor prázdným nebo výchozím obsahem.
- Neprováděj neověřené migrace dat.
- Zachovej všechny existující zálohy.
- Nezasahuj do uživatelských souborů během automatických testů.
- Diagnostické reporty nesmí obsahovat hesla, tokeny ani jiné citlivé údaje.
- Zachovej kompatibilitu se staršími platnými daty.
Pokud implementuješ možnost opravy některých problémů, musí být oddělená od auditu, předem vytvořit bezpečnou zálohu, přesně vysvětlit plánované změny a vyžadovat potvrzení uživatele.
**Nepřidávej automatické opravy, pokud nejsou skutečně bezpečné a potřebné.**
## 7. Architektura a výkon
Navrhni centralizovaný, modulární systém integrity.
- Jednotlivé datové oblasti mohou mít vlastní validační pravidla.
- Společná infrastruktura musí sjednocovat výsledky, závažnosti a diagnostiku.
- Využívej existující datové modely a validační funkce.
- Nevytvářej paralelní datovou vrstvu ani zbytečně složitou architekturu.
- Zachovej možnost přidávat nové moduly a pravidla.
- Minimalizuj dopad na rychlost spouštění a ukládání.
- Neprováděj opakované kompletní skenování bez důvodu.
- Ošetři souběžné operace, aby audit nevyhodnocoval nekonzistentní stav během zápisu.
## 8. Automatické testy
Vytvoř nové automatické testy pokrývající zejména:
- Správná a úplná data.
- Chybějící povinné hodnoty.
- Neplatné datové typy.
- Poškozené soubory.
- Neexistující reference.
- Neplatné duplicity.
- Nekonzistentní statistiky.
- Starší, ale stále podporované datové formáty.
- Selhání ukládání.
- Přerušení auditu.
- Ochranu původních dat při chybě.
- Výkon rychlé kontroly při spuštění.
Testuj také integraci s grafickým rozhraním a ověř, že uživateli správně zobrazuje výsledky.
**Všechny testy musí používat izolovaná testovací data.**
## 9. Integrace s existujícím systémem kvality
Pokud už v projektu existuje `check_quality.ps1`, integruj do něj testy integrity dat.
Pokud zatím neexistuje, připrav testy tak, aby je bylo možné později snadno začlenit.
Kontrola kvality by měla zahrnovat:
- Výsledky automatických testů integrity.
- Pokrytí validačních pravidel testy.
- Zjištěné chyby na testovacích datech.
- Výkon rychlé a kompletní kontroly.
Nespouštěj kompletní audit skutečných uživatelských dat automaticky při každém vývojovém testování.
## 10. Realizace a omezení
Nezůstávej pouze u návrhu. Proveď analýzu, implementaci a testování.
Dodrž:
- Zachování všech současných funkcí VocabPro.
- Zachování současného vzhledu a lokalizačního systému.
- Doplnění všech potřebných překladů do podporovaných jazyků.
- Kompatibilitu Python i Nuitka EXE verze.
- Žádné zbytečné změny nesouvisejících modulů.
- Žádné mazání nebo úpravy skutečných uživatelských dat.
- Zachování necommitnutých změn.
- Žádné zásahy do sandboxu nebo existující dokumentace.
Na závěr uveď:
1. Které datové oblasti a pravidla integrity byly implementovány.
2. Jak funguje rychlá kontrola při spuštění.
3. Jak funguje validace při ukládání.
4. Jak spustit kompletní audit v nastavení.
5. Výsledky automatických testů.
6. Naměřený dopad na výkon.
7. Případná omezení a oblasti, které zatím nelze spolehlivě kontrolovat.
**Výsledný stav:** VocabPro automaticky chrání konzistenci dat při spuštění a ukládání, umožňuje kompletní audit v nastavení a dokáže bezpečně upozornit na problémy, aniž by riskoval ztrátu uživatelských dat.







# VocabPro – Automatický audit kvality, testování, GUI a výkonu
Analyzuj celý projekt VocabPro a vytvoř **kompletní automatizovaný systém kontroly kvality**, který bude možné opakovaně spouštět jediným skriptem `check_quality.ps1`.
Systém musí analyzovat zdrojový kód, spouštět existující automatické testy, testovat grafické rozhraní, měřit výkon a generovat přehledné reporty.
## 1. Automatické kontroly
Zahrň následující oblasti:
- **Statistiky kódu:** počet souborů, řádků kódu, tříd, funkcí a metod, rozdělení podle jazyků a modulů.
- **Kvalita kódu:** chyby, nepoužité prvky, duplicity, složitost funkcí, problematické závislosti a potenciálně neudržovatelný kód.
- **Automatické testy:** spusť všechny existující testy a zaznamenej úspěšné, neúspěšné a přeskočené.
- **Test coverage:** změř pokrytí kódu, identifikuj nepokryté části a doporuč, které testy doplnit.
- **Audit testů:** identifikuj zastaralé, duplicitní nebo nedostatečné testy. Existující testy nemaž ani neupravuj.
- **Bezpečnost:** potenciální zranitelnosti, rizikové konstrukce, zastaralé závislosti a možné úniky citlivých údajů.
- **Výkon:** rychlost spuštění, načítání dat, vyhledávání, statistických výpočtů a spotřeba RAM.
- **Historie:** porovnávej výsledky s předchozími měřeními a upozorňuj na zhoršení.
Použij vhodné nástroje podle skutečné architektury projektu (např. Ruff, pytest-cov, Radon, Bandit, pip-audit, psutil, jscpd).
## 2. Automatické GUI testování
**Integruj testování grafického rozhraní přímo do společného auditu.**
Zjisti používaný GUI framework a zvol odpovídající testovací nástroje.
GUI testy musí podle možností aplikace automaticky:
- Spustit a bezpečně ukončit VocabPro.
- Procházet hlavní obrazovky a moduly.
- Simulovat klikání, zadávání textu a práci s formuláři.
- Testovat přepínání jazyků a nastavení.
- Ověřovat práci se slovníky, Grammar, Conjugation a statistikami.
- Testovat editory, dialogy, validace a chybové stavy.
- Ověřovat ukládání, načítání, zálohování a obnovu dat.
- Kontrolovat základní správnost vykreslování a reakce UI.
Testy musí ověřovat skutečné výsledky akcí, nikoliv pouze to, že aplikace nespadla.
Při selhání zaznamenej konkrétní krok, příčinu, traceback a pokud možno screenshot. GUI testy prováděj výhradně s izolovanými testovacími daty.
**Nevytvářej falešné výsledky ani nepředstírej otestování funkcí, které nebylo možné automatizovat.**
## 3. Režimy kontroly
Vytvoř dva režimy:
**Quick**
- Statická analýza.
- Základní automatické testy.
- Základní GUI smoke testy.
- Rychlá kontrola regresí.
**Full**
- Kompletní statická analýza.
- Všechny existující automatické testy.
- Kompletní dostupné GUI testy.
- Test coverage.
- Bezpečnostní audit.
- Analýza duplicit a složitosti.
- Výkonnostní benchmarky.
- Porovnání s historickými výsledky.
Výchozí režim nastav na Full. Umožni snadné spuštění Quick režimu parametrem skriptu.
## 4. Spouštěcí skript
Vedle současného startovacího skriptu vytvoř `check_quality.ps1`, který:
1. Automaticky spustí požadované kontroly a testy.
2. Změří dostupné metriky.
3. Porovná výsledky s předchozími měřeními.
4. Vygeneruje HTML a PDF report.
5. Automaticky otevře aktuální HTML report v prohlížeči.
6. Při selhání jednotlivé kontroly zaznamená chybu a bezpečně pokračuje v ostatních.
Skript musí fungovat opakovaně bez ruční konfigurace.
## 5. Ukládání výsledků
Použij strukturu:
```text
VocabPro/
├── check_quality.ps1
└── reports/
    └── quality/
        ├── latest.html
        ├── latest.pdf
        ├── history.json
        └── archive/
            ├── YYYY-MM-DD_HH-MM-SS.html
            └── YYYY-MM-DD_HH-MM-SS.pdf
```
- `latest.html` – hlavní interaktivní dashboard.
- `latest.pdf` – přehledná tisknutelná verze.
- `history.json` – historie naměřených hodnot.
- `archive/` – předchozí reporty.
Ukládej také diagnostické výstupy a screenshoty neúspěšných GUI testů do odpovídajících podadresářů.
Generované reporty přidej do `.gitignore`. Kontrolní skripty a jejich konfiguraci zachovej v Gitu.
## 6. Obsah reportů
Vytvoř profesionální HTML a PDF reporty obsahující:
- Souhrnný dashboard s hlavními metrikami.
- Grafy vývoje kvality, coverage a výkonu.
- Výsledky všech automatických testů.
- **Samostatnou sekci GUI Testing** s počty úspěšných a neúspěšných testů, testovanými moduly, chybami a screenshoty.
- Seznam nepokrytých funkcí a doporučených testů.
- Přehled největších, nejsložitějších a nejproblematičtějších souborů.
- Bezpečnostní upozornění a doporučení.
- Porovnání s předchozím auditem a identifikaci regresí.
Všechny hodnoty musí vycházet ze skutečných měření. Rozlišuj úspěšné, neúspěšné, přeskočené a neproveditelné kontroly. Pokud metrika není dostupná, jasně to uveď.
## 7. Bezpečnost a kompatibilita
- Automaticky nainstaluj potřebné analytické a testovací nástroje do izolovaného prostředí.
- **Neměň aplikační kód, existující testy, slovníky, nastavení ani uživatelská data.**
- Nové GUI testy a pomocné testovací soubory vytvářet můžeš.
- Všechny testy pracující s daty musí používat izolované dočasné prostředí.
- Neposílej skutečné e-maily, nemaž reálná data ani neprováděj nevratné operace.
- Neprováděj automatické opravy aplikace, pouze analyzuj a doporučuj.
- Nezasahuj do sandboxu ani existující dokumentace.
- Zachovej necommitnuté změny.
- Připrav možnost budoucí integrace s `update_exe.ps1`, aby před sestavením EXE mohly proběhnout důležité kontroly.
## 8. Realizace
**Nezůstávej pouze u návrhu.**
Analyzuj projekt, implementuj celý kontrolní systém, vytvoř potřebné GUI testy, nainstaluj nástroje a skutečně spusť první kompletní audit.
Ověř také opakované spuštění, ukládání historie, správnost reportů a bezpečnou izolaci testovacích dat.
Na závěr stručně uveď:
- Jak spouštět Quick a Full kontrolu.
- Počet úspěšných a neúspěšných automatických i GUI testů.
- Naměřené coverage a základní výkonnostní metriky.
- Nejvýznamnější nalezené problémy.
- Co nebylo možné automaticky otestovat.
**Hlavní cíl:** Jediným spuštěním `check_quality.ps1` získat komplexní přehled o kvalitě kódu, bezpečnosti, funkčnosti aplikace, grafickém rozhraní, výkonu a vývoji projektu v čase – bez rizika poškození VocabPro nebo uživatelských dat.





# VocabPro – Nuitka EXE a automatický release systém
Připrav kompletní Windows EXE distribuci aplikace VocabPro pomocí **Nuitky** a automatizuj její sestavování a aktualizace.
Jde zatím o testovací distribuci. Zdrojový projekt `VocabPro` budu nadále vyvíjet v Pythonu a EXE verzi chci pravidelně aktualizovat.
## 1. Instalace a sestavení EXE
- Analyzuj projekt, závislosti a současný způsob spouštění.
- Automaticky nainstaluj Nuitku a potřebné nástroje do vhodného vývojového prostředí. Pokud bude potřeba oprávnění, požádej o schválení.
- Použij **standalone režim**, nikoliv one-file, kvůli rychlosti spouštění.
- Vedle složky `VocabPro` vytvoř složku `VocabPro_exe` obsahující kompletní distribuční verzi včetně `VocabPro.exe`.
- Zajisti funkčnost na Windows bez instalovaného Pythonu.
- Zachovej všechny moduly, lokalizace, datové soubory, vzhled a funkcionalitu aplikace.
- Nevkládej do EXE hesla, tokeny ani jiné citlivé údaje.
## 2. Univerzální aktualizační skript
Vedle existujícího startovacího skriptu vytvoř nebo uprav `update_exe.ps1`.
Skript musí:
1. Automaticky sestavit aktuální zdrojový kód pomocí Nuitky.
2. Používat relativní cesty, nezávislé na umístění projektu.
3. Sestavovat novou verzi nejprve v dočasné složce.
4. Ověřit úspěšnost buildu a základní funkčnost EXE.
5. Teprve poté bezpečně aktualizovat `VocabPro_exe`.
6. Při selhání zachovat předchozí funkční verzi.
7. Odstranit zastaralé distribuční soubory, ale nikdy uživatelská data.
8. Zobrazit průběh a výsledek aktualizace.
## 3. Automatický release proces
Rozšiř aktualizační systém o následující funkce:
- **Integrace s `check_quality.ps1`:** před vydáním nové verze automaticky spusť důležité testy včetně dostupných GUI testů.
- Pokud kontrolní skript ještě neexistuje, připrav integraci tak, aby jej bylo možné později jednoduše připojit.
- **Kontrola před vydáním:** při selhání kritických testů nebo buildu aktualizaci zastav.
- **Verzování:** zaveď jednotné číslo verze aplikace, které bude dostupné v Python i EXE verzi. Nevytvářej duplicitní zdroje pravdy.
- **Changelog:** při aktualizaci vytvoř stručný přehled změn na základě dostupných Git informací. Nevymýšlej změny, které nelze doložit.
- **Validace EXE:** ověř spuštění, dostupnost závislostí a základních funkcí.
- **Rollback:** při neúspěšném nasazení umožni návrat k předchozí funkční verzi.
- **Opakovatelnost:** celý proces musí být možné kdykoliv znovu spustit bez ruční konfigurace.
Pokud to dává smysl, vytvoř `release.ps1`, který propojí kontroly a sestavení. **Nevytvářej však zbytečně více skriptů, pokud lze vše přehledně integrovat do `update_exe.ps1`.**
## 4. Uživatelská data a kompatibilita
- Uživatelská data, slovníky, statistiky, nastavení a zálohy musí být oddělené od distribučních souborů.
- Aktualizace nesmí tato data přepisovat ani mazat.
- Zachovej kompatibilitu původní Python a nové EXE verze.
- Pokud jsou nutné změny práce s cestami, proveď je pro obě varianty.
- Nepřepisuj otevřenou aplikaci; bezpečně detekuj její běh a vyžádej ukončení.
- Při změnách datového formátu neprováděj neověřené migrace.
## 5. Výkon a testování
- Optimalizuj build pro rychlé spuštění a plynulý běh.
- Pokud možno porovnej Python a EXE verzi z hlediska rychlosti spuštění, RAM a velikosti distribuce.
- Otestuj opakované sestavení a aktualizaci.
- Ověř bezpečné chování při selhání buildu i nasazení.
- Otestuj funkčnost bez systémově nainstalovaného Pythonu, pokud je dostupné vhodné izolované prostředí. Jinak toto omezení výslovně uveď.
- Nevydávej neotestovanou verzi za ověřenou.
## 6. Pravidla realizace
- **Nezůstávej u návrhu – implementuj, sestav a otestuj.**
- Zachovej veškerou existující funkcionalitu, výkon a vzhled.
- Neměň obsah slovníků ani uživatelská data.
- Nezasahuj do sandboxu ani dokumentace.
- Zachovej necommitnuté změny v Gitu.
- Neměň zbytečně architekturu aplikace.
- U rizikových nebo destruktivních operací požádej o schválení.
Na závěr stručně uveď umístění EXE, způsob spuštění aktualizace, výsledky testů, velikost distribuce, naměřený výkon a případná omezení.
**Cíl:** Zachovat `VocabPro` jako vývojový projekt a vedle něj udržovat plně funkční `VocabPro_exe`. Jediným skriptem bezpečně provádět testování, sestavení, kontrolu, verzování a aktualizaci EXE bez ztráty dat. 







sjednotit design track record conjugation a grammar v session
sjednotit setting remember category pořadí.. Je to u learning.. U modulů je to opčaně.



Moc nerozumím nastavení tomu mailu.. Mám tam dávat heslo od toho emailu (v případě seznamu)? Když ho tam dám a uložím to a znovu zobrazím, nic se nezobrazuje.




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






sjednotit stats conjugation a grammar





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


# Testování

`test_tag_scenarios` doplňuje seedované porovnání filtrů s množinovým modelem,
obousměrný převod 10 000 řádků mezi názvy a ID, odmítnutí neplatného konce
dávky a kontrolu neměnnosti vstupů. GUI scénáře zkouší všech šest lokalizací:
všechny labely nastavení při 950×650 i 1400×900, výběr ze 120 dlouhých štítků
v minimálním okně, deset přiřazení, reset scrollu po hledání a opakované
zobrazení/skrytí dlouhých štítků v session. Výkonový test tiskne skutečný čas;
30sekundová mez slouží jen jako hrubá ochrana před výraznou regresí.
Sedmý scénář ověřuje deset dlouhých štítků u právě zkoušeného slovíčka
v okně 1150×800: žádný překryv se zadáním ve třech režimech procvičování
a dostupné spodní tlačítko. Tento scénář nejprve prokázal skutečný překryv.

```powershell
python -B -u -m app.tests.run_all --timeout 240
python -B -m app.tests.run_all --pattern 'test_grammar*.py'
python -B -m app.tests.run_all --worker app.tests.test_refactoring_integration
```

V aktualizovaném projektu tyto příkazy spouštět po aktivaci `.venv`, případně
pomocí `.\.venv\Scripts\python.exe` místo samotného `python`.

Limit 240 sekund je určený i pro moduly se všemi šesti lokalizacemi a mnoha
velikostmi oken. Není to časový limit jedné uživatelské operace. Výchozí limit
runneru zůstává 120 sekund; rozsáhlý `test_tag_scenarios` jej může překročit.
Podporu N kurzů a kompatibilitu nastavení ověřuje `test_study_courses`.

Spouštěč izoluje moduly do samostatných procesů. safety blokuje skutečné
HTTP/SMTP/socket spojení, mikrofon, přehrávání a zápisy do files/images/locales.
Dočasné syntetické adresáře jsou povolené. Používat oficiální runner, protože
přímé unittest spuštění celého projektu by tyto globální ochrany nezapnulo.
Runner rovněž nahrazuje načítání SMTP účtu prázdným výsledkem a blokuje jeho
uložení do Windows. `test_backup_account` používá falešné CredRead/CredWrite
i SMTP a ověřuje Unicode, uvolnění bufferu, validaci, obnovu modality dialogu,
uložení/prázdné heslo a čitelnost všech šesti překladů bez přístupu k reálnému
trezoru nebo odesílání e-mailu.

Testy pokrývají modely session, ID, historii, repository kontrakty, neúspěšné
zápisy, konflikty, synonyma, zálohy, API parsování, lokalizaci, rozložení oken,
životní cyklus a výkonové rozpočty. test_refactoring_safety obsahuje původně
selhávající regrese auditu. test_refactoring_integration ověřuje rollback,
create-if-absent kolizi, cache, bezpečné logy, vlákna statistik a cleanup.
test_chart_rendering navíc ověřuje hover blitting na Agg i skutečném Tk
canvasu, obnovení pixelů, invalidaci resize, fallback a odstranění SciPy.

GUI test potřebuje funkční Windows desktop/Tk a může otevřít krátká zkušební
okna. Test klávesové události řadí explicitní KeyPress s Ctrl do fronty až po
focus/map událostech; neřeší nejistotu prodlužováním sleep. Stav samotného
save se ověřuje i přímo, nezávisle na doručení klávesy.
Před syntetickým KeyPress test výslovně ověří udělení nativního Windows
fokusu; čeká na podmínku nejvýše dvě sekundy. Nečeká pevnou prodlevu.

Nový test má používat TemporaryDirectory a malé tabulky s jednoznačnými
hodnotami. Při ověřování atomického selhání kontrolovat původní bytes, nejen
vyvolání výjimky. U změny rozhraní přesunout mock na skutečnou hranici,
nezměnit požadovaný výsledek. U výkonu uvádět data, počet běhů a prostředí.

Aktuální konkrétní výsledek a známé neověřené scénáře jsou v
[výsledcích refaktoringu](../refactoring/TEST_RESULTS.md). Živý mikrofon, SMTP,
API kvóty a všechna monitorová DPI nemají automatickou plnou garanci.

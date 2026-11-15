# Výkon: výchozí měření

15. 11. 2026. Původní hodnoty níže jsou zachované pro porovnání.
Výsledky po implementaci a jejich interpretace jsou v závěrečné části.

## Prostředí a metodika

Windows 11 (build 26200), Python 3.13.14; lokální pracovní stanice. Některá
měření běžela při regresní sadě, takže nejsou izolovaným laboratorním
benchmarkem. Importy: nový interpreter při každém pokusu, zahřátá OS cache,
měřeno včetně vytvoření procesu. Nejde o čas od kliknutí do hotového UI.
Syntetická data a dočasné adresáře; žádná reálná síť, mikrofon nebo přehrávání.

Instalované relevantní verze: pandas 2.3.3, numpy 2.4.0, CustomTkinter 5.2.2,
tksheet 7.5.19, Matplotlib 3.10.8, SciPy 1.17.0, Pillow 11.3.0, pygame 2.6.1,
PyAudio 0.2.14, pywinstyles 1.8, requests 2.32.5. Jde o zjištěné prostředí,
nikoli doporučení nebo deklaraci otestovaných rozsahů verzí.

## Naměřené hodnoty

| Scénář | Opakování | Před: medián / údaj | Po |
|---|---:|---:|---|
| Samotný import app.main | 3 nové procesy | 1,278 s | Neprovedeno |
| Samotný import app.statistics.viewer | 3 nové procesy | 2,351 s | Neprovedeno |
| course_overview, 1 500 syntetických slovíček | 5 | 18,75 ms | Neprovedeno |
| save_answers, 10 000 otázek / 100 odpovědí | 3 | 398,0 ms | Neprovedeno |
| save_answers, 10 000 otázek / 1 000 odpovědí | 3 | 3 008,7 ms | Neprovedeno |
| Statistiky gramatiky, 10 000 řádků, první výpočet | Existující výkonový test | 57,4 ms | Neprovedeno |
| Stejná statistika, medián 20 cache hitů | Existující výkonový test | 1,11 ms; CSV čteno celkem jednou | Neprovedeno |
| Agregace kategorií, 50 000 otázek | Existující výkonový test | 23,6 ms | Neprovedeno |
| 10 000 nezměněných aktualizací souhrnu synonym | Existující výkonový test | 1,55 ms | Neprovedeno |
| Rozložení přeložené gramatiky, 12 scénářů | Existující UI test | 21,93 s celkem včetně tvorby oken | Neprovedeno |

Jednotlivé pokusy, sekundy:

```text
import app.main:              1.3430, 1.0766, 1.2780
import app.statistics.viewer: 2.4445, 2.3514, 1.9190
home 1500:                   .0206804, .0184987, .0189117, .0181553, .0187475
grammar 100:                 .3980326, .3774287, .4497488
grammar 1000:                3.2771167, 3.0086602, 2.7830037
```

Importtime navíc potvrdil cestu app.main → home.data → repositories.vocabulary
→ editor_attributes → services.api → requests. V jednom instrumentovaném
průchodu měla větev editor_attributes kumulativně přibližně 136,5 ms, requests
124,9 ms. Časy jsou vnořené, nesčítat je. To opodstatňuje odložit závislost na
obohacení; výsledné zrychlení se musí teprve přeměřit.

## Paměť obrázků

Syntetický CTkImage: 20 různých velikostí od 640×400, přírůstky 5×3 pixelů,
vždy configure(size=...) a create_scaled_photo_image v testovacím interpreteru.
Po dokončení cache držela všech 20 variant, celkem 5 901 850 pixelů. Hrubý
přepočet na RGBA je 22,51 MiB, **nikoli naměřená RSS spotřeba procesu**.
Zdroj CTkImage.configure potvrzuje, že změna size cache nevyprázdní; změna
zdrojového light_image ji vyprázdní. Aplikace mění size při resize podkladu.

Závěr: pro dlouhé resize existuje konkrétní mechanismus hromadění variant.
Ještě není změřeno, kolik paměti při běžné práci drží celá aplikace. Neprovádět
úpravy privátní cache knihovny bez testů; preferovat kontrolované veřejné
rozhraní pro background a omezené vlastnictví bitmap.

## Navazující srovnání po schválení

Zopakovat stejná data, počty běhů a prostředí; oddělit výpočet, CSV serializaci,
fsync a renderování. Pro statistiky doplnit time-to-ready a odezvu event loopu
při zachovaném předpřipravení všech grafů. Pro editor měřit počet CSV čtení
za změnu buňky. Pro paměť sledovat RSS i počet bitmap po resize a po opakovaném
otevření/zavření. Současné rychlé cache a agregace není důvod přepisovat.

## Výsledky po implementaci

Zopakována stejná syntetická tabulka, počty běhů a zahrnutí I/O i spuštění
procesu. Měření proběhla na stejné stanici, nejsou však náhodně prokládaným
benchmarkem ve vyhrazeném laboratorním prostředí.

| Scénář | Před | Po | Pokles naměřeného času |
|---|---:|---:|---:|
| Import app.main, medián 3 procesů | 1 278 ms | 787,7 ms | 38,4 % |
| Import app.statistics.viewer, medián 3 procesů | 2 351 ms | 1 563,9 ms | 33,5 % |
| Home overview 1 500 slov, medián 5 | 18,75 ms | 9,01 ms | 52,0 % |
| Grammar save 10k/100, medián 3 | 398,0 ms | 90,2 ms | 77,3 % |
| Grammar save 10k/1000, medián 3 | 3 008,7 ms | 89,7 ms | 97,0 % |

Importní a home rozdíly zahrnují zahřátí OS a variabilitu stanice. Nejde o
slib stejného procenta na jiném počítači. U gramatiky příčinu dokládá změna
algoritmu z opakovaných plných masků na jeden index a dávkové přiřazení.
Výukové výsledky a konfliktní celé dávky kontrolují regresní testy.

```text
Po: import main      .8644487, .7860161, .7877245
Po: import viewer    1.5638628, 1.5550560, 1.6174613
Po: home             .0146027, .0116491, .0087677, .0087728, .0090079
Po: grammar 100      .0955405, .0877867, .0902078
Po: grammar 1000     .0926500, .0897086, .0894553
```

### Cache obrázků a skutečná procesová paměť

Stejných 20 velikostí: po opravě jedna varianta, 335 895 pixelů / 1,281 MiB
RGBA odhadu proti 20 variantám a 22,51 MiB. Odhad poklesl o 94,3 %.
Samostatné dva procesy navíc měřily Windows GetProcessMemoryInfo Working Set:

| Mechanismus resize | Před smyčkou | Po 20 velikostech | Přírůstek | Po destroy + GC |
|---|---:|---:|---:|---:|
| Původní configure(size) | 45,84 MiB | 76,66 MiB | 30,82 MiB | 47,55 MiB |
| Omezená cache přes veřejné configure | 45,79 MiB | 51,09 MiB | 5,30 MiB | 46,13 MiB |

Přírůstek Working Set byl v tomto izolovaném pokusu o 82,8 % menší. Jde o
jeden pár běhů stejného bitmapového mechanismu, nikoli o RSS celého několik
hodin používaného VocabPro. Alokátor nemusí po destroy vrátit každý bajt OS.
Integrační test přímo na background helperu ověřuje omezený počet bitmap;
další test ověřuje uvolnění StatisticsController po zavření během workeru.

### Odezva a souborové operace

SynonymCounts: deset nezměněných aktualizací načte relace jednou, změna
souboru je zneplatní. Statistiky mají UI heartbeat během workeru, grafy
se vytvářejí jen v hlavním vlákně a cover nezmizí před dokončením všech.
Skutečné opakované otevření a přepnutí jazyků s Matplotlib prošlo testem.
Samostatné time-to-ready/latence jedné figury nebyly profilovány do detailu;
nelze tvrdit, že každá Matplotlib operace má pevně omezenou latenci.

## Následná optimalizace hoveru bez SciPy

Test ChartRenderingTests.test_hover_raster_benchmark měří 20 aktualizací
stejné anotace na 500×300 pixelové Agg figuře s čárou. Plný draw: 388,08 ms,
obnova podkladu + anotace: 18,59 ms (o 95,2 % méně). Jde o jednorázové měření
rastrové části v témže procesu; nikoli měření Tk přenosu ani startu aplikace.
Přesné obnovení statických pixelů po skrytí detailu ověřuje samostatný test.
SciPy 1.17.0 výše je historické prostředí auditu; současný requirements ji
nevyžaduje a charts ji neimportuje. Prognóza má lineární interpolaci NumPy.

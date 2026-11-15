# Instalace a spuštění

Aktualizované knihovny jsou instalované v projektové `.venv`; systémový Python
zůstává beze změny. VS Code konfigurace VocabPro používá tento interpreter.
Pro přesnou reprodukci celé sestavy použít `pip install -r requirements.lock.txt`;
requirements.txt obsahuje přímé závislosti. Původní manifest je zachovaný v
.refactoring-recovery/requirements_before_update.txt.

Aktualizovaná přímá sestava: CustomTkinter 6.0.0, tksheet 7.6.0,
pandas 3.1.1, NumPy 2.5.4, Matplotlib 3.11.2, Pillow 13.0.0,
requests 2.34.2. pygame 2.6.1, PyAudio 0.2.14 a pywinstyles 1.8 zůstaly
na nejnovější dostupné stabilní verzi vybrané instalátorem pro Python 3.13.
Úplný lock zahrnuje i tranzitivní závislosti; SciPy v čisté .venv není potřeba.

Ověřené prostředí je Windows 11 a Python 3.13.14. Projekt používá nativní
Tk a Windows styling; běh na jiném OS nebyl ověřen a není deklarovanou podporou.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe start.py
```

Instalace vyžaduje dostupné balíčky/wheels pro konkrétní Python. requirements
uvádí ověřené přímé závislosti, nikoli kompletní transitive lock. Samotná čistá
instalace do nové projektové .venv byla provedena z binárních wheelů PyPI.

Distribuce musí obsahovat app, images, locales a platné files/settings.csv.
Složka files není součástí nové automaticky vytvořené instalace se smyšlenými
uživatelskými daty; chybějící settings je nutné obnovit z důvěryhodné vlastní
kopie. Aktivní prázdný slovníkový kurz umí main při výběru jazyka vytvořit.
API a e-mail jsou volitelné a vyžadují vlastní konfiguraci.

Řešení běžných problémů:

- ModuleNotFoundError: ověřit interpreter a instalaci requirements v témže venv.
- Audio zařízení není dostupné: start zaznamená varování, výukové UI může běžet
  bez zvuku; nahrávání vyžaduje mikrofon a oprávnění Windows.
- Neplatné CSV: před opravou zavřít aplikaci a zachovat původní kopii; podle
  hlášky ověřit sloupce, ID a oddělovač. Neodstraňovat historii.
- Konflikt ukládání: neobcházet revizi, otevřít aktuální soubor a znovu aplikovat
  vlastní změny. Nechat běžet jen jednu uživatelskou instanci aplikace.
- Chybějící obrázek/katalog: obnovit příslušné distribuční soubory; asset test
  ověří existenci a dekódování.

Po změně zdrojového kódu aplikaci restartovat. Testy spouštět přes
[oficiální runner](TESTING.md), nikoli nad skutečnými daty.

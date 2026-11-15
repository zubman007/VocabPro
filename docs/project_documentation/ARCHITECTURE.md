# Architektura implementace

Vstup [start.py](../../start.py) vytvoří Tk root, audio mixer a AppContext.
[main.py](../../app/main.py) sestavuje navigaci a hlavní stránku. Nepředává
screenům globální nastavení; kontroléry obdrží kontext se snapshotem
RuntimePreferences, cestami, překladačem a návratem do menu.

| Oblast | Odpovědnost | Hlavní soubory |
|---|---|---|
| Sestavení aplikace | Start, výběr modulů, příprava kurzů | start.py, app/main.py, home/ |
| Kontroléry a modely | Editace a výuková kola v paměti | vocabulary/, grammar/, conjugation/ |
| Prezentace | Layouty, společné komponenty a podklady | ui/, ui/components/ |
| Perzistence | Načítání CSV, validace smluv, konflikty a commit | repositories/, shared/storage.py |
| Vícekrokové ukládání | Obohacení a izolované audio, rollback | vocabulary/save_workflow.py |
| Infrastruktura | HTTP, e-mail, pracovní vlákna, diagnostika | services/, shared/background_task.py, shared/diagnostics.py |
| Statistiky | Výpočty, cache, instanční řízení a grafy | statistics/ |

[ScreenController](../../app/core/screen_controller.py) spravuje zkratky,
časovače, vlastněné dialogy a odchod ze screenu. Session modely nejsou widgety.
Repositories nepřistupují přímo k Tk. Zachovaný repository.save_course je
kompatibilní odložený vstup do skutečného save_workflow, nikoli druhá
implementace obohacování.

StatisticsController vlastní stav jediného okna. Výpočty probíhají ve workeru,
zatímco všechny grafické operace zůstávají v Tk vlákně. Výsledky se předávají
pollingem BackgroundTask. Cache dat má omezený počet položek a zámek.

Přímý importní cyklus editor → theory editor byl odstraněn: směrování je v
editor_navigation a používá odložený výběr vstupu. Legacy shared.settings
stále reexportuje konfiguraci a starší styly pro dosud nemigrované obrazovky.
Nové statistiky používají explicitní kontext a přímé UI importy.

[Systémový diagram](diagrams/SYSTEM_OVERVIEW.md) a
[závislosti](diagrams/MODULE_DEPENDENCIES.md) popisují hlavní vazby.
Detailní přímé importy a jejich odběratelé jsou v [MODULES](MODULES.md).

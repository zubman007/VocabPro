# Technická dokumentace VocabPro

Dokumentace popisuje implementaci po refaktoringu z 15. 11. 2026. Historie
auditu a měření je odděleně v [docs/refactoring](../refactoring/CHANGES.md).

- [Přehled projektu](PROJECT_OVERVIEW.md), [instalace](INSTALLATION.md)
- [Architektura](ARCHITECTURE.md), [katalog všech modulů](MODULES.md)
- [Datové toky](DATA_FLOW.md), [datové úložiště](DATA_STORAGE.md)
- [GUI a životní cyklus](GUI.md), [výuková pravidla](BUSINESS_LOGIC.md)
- [Statistiky](STATISTICS.md), [výkon](PERFORMANCE.md)
- [Audio](AUDIO.md), [externí služby](API_INTEGRATIONS.md)
- [Lokalizace](LOCALIZATION.md), [konfigurace](CONFIGURATION.md)
- [Zálohy a obnova](BACKUP_RECOVERY.md)
- [Testování](TESTING.md), [pravidla dalšího vývoje](DEVELOPMENT_GUIDE.md)
- [Přehled diagramů](diagrams/SYSTEM_OVERVIEW.md)

V příkladech jsou pouze syntetické hodnoty. Dokumentace neobsahuje klíče,
hesla ani obsah skutečných slovníků. Známá omezení jsou uvedena u příslušných
subsystémů; žádný diagram nepředstavuje plánovanou neimplementovanou službu.

## Samostatné diagramy

- [Celkový systém](diagrams/SYSTEM_OVERVIEW.md)
- [Závislosti modulů](diagrams/MODULE_DEPENDENCIES.md)
- [Životní cyklus aplikace](diagrams/APPLICATION_LIFECYCLE.md)
- [Navigace GUI](diagrams/GUI_NAVIGATION.md)
- [Slovíčka](diagrams/VOCABULARY_WORKFLOW.md)
- [Gramatika](diagrams/GRAMMAR_WORKFLOW.md)
- [Časování](diagrams/CONJUGATION_WORKFLOW.md)
- [Statistiky](diagrams/STATISTICS_FLOW.md)
- [Perzistence dat](diagrams/DATA_PERSISTENCE.md)
- [Ukládací transakce](diagrams/SAVE_TRANSACTION.md)
- [Audio](diagrams/AUDIO_WORKFLOW.md)
- [Zálohy](diagrams/BACKUP_WORKFLOW.md)
- [Externí služby](diagrams/EXTERNAL_SERVICES.md)

V DATA_STORAGE je navíc ER diagram synonymních vazeb: celkem 14 Mermaid bloků.

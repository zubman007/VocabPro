# Navigace GUI

```mermaid
flowchart TD
    Home["Hlavní obrazovka"] --> VE["Vocabulary editor"]
    Home --> VP["Vocabulary practise"]
    Home --> GE["Grammar editor"]
    Home --> GP["Grammar practise"]
    Home --> CP["Conjugation practise"]
    Home --> Settings["Settings"]
    Home --> About["About"]
    Home --> Stats["Statistics"]
    GE --> Theory["Theory editor"]
    Theory --> GE
    VP --> Review["Review a synonyma"]
    VE --> Syn["Synonyms editor"]
    GP --> GT["Teorie a filtr kategorií"]
    Stats -->|Kategorie| GP
    Stats -->|Štítek| VP
    GP -->|Close nebo Save při spuštění ze statistik| Stats
    VP -->|Close nebo Save při spuštění ze statistik| Stats
```

Návrat ze cvičení spuštěného ze statistik zachová jazyk a záložku; data se
znovu načtou. Cvičení spuštěná z hlavní nabídky se vracejí na hlavní obrazovku.

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

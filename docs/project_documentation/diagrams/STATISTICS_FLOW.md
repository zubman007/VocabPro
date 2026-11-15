# Tok statistik a vláken

```mermaid
sequenceDiagram
    participant UI as StatisticsWindow
    participant Controller as StatisticsController
    participant Worker as BackgroundTask worker
    participant Cache as StatisticsCache
    UI->>Controller: build a load
    Controller->>Worker: prepare_statistics se snapshotem
    Worker->>Cache: data podle souborů a voleb
    Cache-->>Worker: nezávislé výsledky
    Worker-->>Controller: výsledek přes Tk polling
    Controller->>UI: souhrny a postupně všechny grafy
    Controller->>UI: complete
    UI->>UI: odstranění coveru a ready
    UI->>Controller: destroy
    Controller->>Worker: close bez doručení do zničeného UI
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

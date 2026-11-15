# Celková architektura

```mermaid
flowchart TD
    Start["start.py"] --> Main["main a AppContext"]
    Main --> Screens["Kontroléry modulů"]
    Screens --> UI["Layouty a sdílené UI"]
    Screens --> Sessions["Session a dokumenty"]
    Screens --> Repos["Repositories"]
    Screens --> Save["save_workflow"]
    Save --> Repos
    Save --> API["Externí providery"]
    Repos --> Disk["CSV a audio"]
    Main --> Stats["StatisticsController"]
    Stats --> Worker["Výpočty a omezená cache"]
    Stats --> Figures["Tk a Matplotlib v hlavním vlákně"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

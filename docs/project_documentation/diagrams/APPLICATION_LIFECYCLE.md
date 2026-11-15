# Životní cyklus aplikace

```mermaid
flowchart TD
    A["run"] --> B["Tk root, mixer, AppContext"]
    B --> C["Load_setting a aktivní kurzy"]
    C --> D["Hlavní menu a záloha na pozadí"]
    D --> E["Kontrolér obrazovky"]
    E --> F["Save nebo Close"]
    F --> H["Kontrola dirty stavu"]
    H --> D
    H --> I["Uložení nebo ponechání změn"]
    I --> D
    D --> J["Exit app a cleanup mixeru"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

# Datová perzistence

```mermaid
flowchart TD
    GUI["GUI kontrolér"] --> Model["Session nebo dokument"]
    Model --> Repo["Repository operace"]
    Repo --> Read["Aktuální CSV a obsahová revize"]
    Read --> Delta["Validace a případná třícestná delta"]
    Delta --> Temp["Dočasné CSV, flush a fsync"]
    Temp --> Guard["Kontrola očekávané revize"]
    Guard --> Publish["Replace nebo create-if-absent"]
    Guard --> Conflict["Odmítnutí celé dávky"]
    Publish --> Disk["Cílové CSV"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

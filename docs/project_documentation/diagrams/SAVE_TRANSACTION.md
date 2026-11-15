# Uložení editoru a rollback

```mermaid
flowchart TD
    A["Ověření výchozí revize a cancellation"] --> B["Kopie pracovního audia do stagingu"]
    B --> C["Obohacení ve workeru a progress"]
    C --> D["Cancellation před commitem"]
    D --> Cancel["Zrušení bez změny původních souborů"]
    D --> Lock["Zámky, kontrola CSV, vazeb a audia"]
    Lock --> Backup["Rollback kopie a archivy"]
    Backup --> Audio["Potvrzení změněného audia a vazeb"]
    Audio --> CSV["Atomický commit vocabulary CSV"]
    CSV --> Success["Úklid stagingu a návrat"]
    Audio --> Error["I/O chyba"]
    CSV --> Error
    Error --> Restore["Obnova původních souborů"]
    Restore --> Recovery["Při chybě obnovy zachovat recovery adresář"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

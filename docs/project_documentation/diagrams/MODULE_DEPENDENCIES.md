# Závislosti balíčků

```mermaid
flowchart TD
    Main["app.main"] --> Home["home"]
    Main --> Context["core.context"]
    Main --> V["vocabulary"]
    Main --> G["grammar"]
    Main --> C["conjugation"]
    Main --> S["statistics"]
    V --> UI["ui a ui.components"]
    G --> UI
    C --> UI
    S --> UI
    V --> R["repositories"]
    G --> R
    C --> R
    S --> R
    R --> Storage["shared.storage"]
    V --> Services["services"]
    Services --> R
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

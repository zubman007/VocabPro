# Slovníkový workflow

```mermaid
flowchart TD
    CSV["Vocabulary CSV"] --> Repo["load_editor_snapshot"]
    Repo --> Editor["EditorController a tabulka"]
    Editor --> Merge["merge_table_edits a validace"]
    Merge --> Save["save_workflow"]
    Save --> CSV
    CSV --> Select["course_overview"]
    Select --> Session["PracticeSession"]
    Session --> Answer["S nebo F v paměti"]
    Answer --> Delta["save_practice s original snapshotem"]
    Delta --> CSV
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

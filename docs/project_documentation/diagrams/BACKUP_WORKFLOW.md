# Zálohování a ruční obnova

```mermaid
flowchart TD
    Settings["Příjemce, interval a Next backup"] --> Due["backup_due"]
    Due --> Coordinator["BackupCoordinator"]
    Coordinator --> Worker["BackgroundTask"]
    Worker --> Files["Neprázdné CSV bez settings"]
    Files --> SMTP["SMTP SSL přílohy"]
    SMTP --> Sent["Úspěch"]
    Sent --> Meta["record_success při shodné konfiguraci"]
    SMTP --> Retry["Chyba a prodleva dalšího pokusu"]
    SMTP --> Mail["Uživatelův e-mail"]
    Mail --> Restore["Ruční obnova při vypnuté aplikaci"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

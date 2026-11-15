# Externí služby

```mermaid
flowchart TD
    Workflow["save_workflow"] --> Attr["editor_attributes"]
    Attr --> Facade["services.api"]
    Facade --> Dict["dictionaryapi.dev"]
    Facade --> MW["Merriam-Webster"]
    Facade --> Speech["ElevenLabs"]
    Dict --> HTTP["api_http: session a timeout"]
    MW --> HTTP
    Speech --> HTTP
    Keys["API settings: lokální CSV"] --> Facade
    Env["SMTP proměnné prostředí"] --> Backup["send_backup"]
    Account["Nastavení: odesílací účet"] --> Vault["Windows Credential Manager"]
    Vault --> Backup
    Backup --> SMTP["smtp.seznam.cz přes TLS"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

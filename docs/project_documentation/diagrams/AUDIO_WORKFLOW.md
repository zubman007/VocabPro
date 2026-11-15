# Životní cyklus audia

```mermaid
flowchart TD
    Mic["PyAudio mikrofon"] --> WAV["record_wave: temp WAV a replace"]
    Provider["Slovník nebo ElevenLabs"] --> HTTP["api_http streaming temp MP3"]
    HTTP --> Stage["audio_output staging"]
    Stage --> Commit["save_workflow commit"]
    WAV --> Audio["Audio složka a ID.mp3 nebo ID.wav"]
    Commit --> Audio
    Audio --> Play["pygame výslovnost"]
    Audio --> Archive["deleted archiv při smazání nebo recyklaci"]
    UI["UI efekt"] --> Channel["Samostatný mixer kanál"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

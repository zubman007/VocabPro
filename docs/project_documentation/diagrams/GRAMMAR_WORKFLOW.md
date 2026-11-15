# Gramatický workflow

```mermaid
flowchart TD
    CSV["Grammar CSV"] --> Read["Loader: sloupce a unikátní ID"]
    Read --> Filter["Pouze vybrané kategorie"]
    Filter --> Weights["Váhy: rovnoměrnost, nové, chyby, stáří, pokrytí"]
    Weights --> Order["Vážené náhodné pořadí bez opakování"]
    Order --> Session["GrammarSession: deque"]
    Session --> Pending["choose: pending_answers"]
    Session --> Progress["Skutečná odpověď: pracovní historie podle ID"]
    Progress -->|Další kolo nebo změna filtru| Weights
    Session --> Reveal["reveal: jen session feedback"]
    Pending --> Batch["save_answers: index a validace celé dávky"]
    Batch --> CSV
    Session --> Theory["load_theory a TheoryWindow"]
```

Souvislosti a omezení: [architektura](../ARCHITECTURE.md), [datové smlouvy](../DATA_STORAGE.md), [GUI](../GUI.md).

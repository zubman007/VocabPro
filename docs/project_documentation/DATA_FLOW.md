# Datové toky

1. Start načte settings přes preferences repository, validuje je a vytvoří
   immutable RuntimePreferences. main zajistí aktivní kurzové soubory a načte
   přehledy pro menu.
2. Otevření editoru načte DataFrame spolu s obsahovou revizí. Tabulka zobrazuje
   lokalizované hodnoty výčtů; při synchronizaci je vrátí do kanonického tvaru.
3. Procvičování vytvoří vlastní Session a počáteční snapshot. Odpovědi mění
   paměť, Save předá výsledky repository. Žádné UI datum nebo překlad klíče
   se nesmí stát novým identifikátorem datového pole.
4. Synonyma se ukládají ve vlastním dialogu samostatně. Index počtů editoru se
   obnovuje při změně signatury souboru vazeb; textová změna buňky jej nenačítá znovu.
5. Statistiky připraví všechny datové sady, vrátí je workerem a v hlavním vlákně
   postupně vytvoří všechny grafy. Loading cover se odstraní až po dokončení.
6. Záloha na pozadí čte datová CSV, odešle zprávu a po úspěchu aktualizuje
   pouze metadata termínu, pokud nastavení odpovídá původnímu požadavku.

Každý přechod do souborového systému používá skutečnou cestu z AppContext nebo
explicitního argumentu. Pracovní vlákno nevolá Tk. Diagramy:
[perzistence](diagrams/DATA_PERSISTENCE.md),
[ukládání](diagrams/SAVE_TRANSACTION.md), [statistiky](diagrams/STATISTICS_FLOW.md).

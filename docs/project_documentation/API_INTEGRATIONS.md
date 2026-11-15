# Externí integrace

| Provider | Implementace | Použití |
|---|---|---|
| dictionaryapi.dev | services/api_dictionary.dictionary_entry | Anglická výslovnost, popis a příklad; provider nevyžaduje konfigurovaný klíč. |
| Merriam-Webster | services/api_dictionary.merriam_entry | Angličtina/španělština, nakonfigurovaný klíč příslušného jazyka. |
| ElevenLabs | services/api_speech.generate_audio | Generování MP3 pro jazyk s hlasem ve VOICES; model eleven_v3. |
| SMTP | services/backup.send_backup | E-mailové CSV přílohy přes smtp.seznam.cz:465 s TLS. |

services/api.py zachovává editorové vstupy Dict_api, MW a Eveleven_labs.
Předává snapshot kontextu, vlastní jazyk a skutečnou cestu k settings.
editor_attributes volá providery jen při chybějícím audiu/údajích; ručně
vyplněný Part of Speech nepřepisuje. Po neúspěšném doplnění zachová fallback
No found / No audio. Výjimky providerů se logují bez citlivých URL.

api_http používá sdílenou requests.Session, timeout (5 s připojení, 30 s
čtení), kontrolu HTTP statusu a atomický streamovaný download. 404 slovníku
vrátí prázdný seznam. Odpovědi se spelling suggestions se neberou jako hesla.
Prázdné audio a JSON/HTML místo audia se odmítají. POST generování se
automaticky neopakuje, protože může být účtované.

Nastavení API se cacheuje podle cesty/mtime/velikosti pod zámkem. Sdílená
Session není navržená jako obecný pool pro libovolný počet paralelních save
workerů; aplikace řídí jedno ukládání daného editoru. Živé kvóty, změny API a
hardware nebyly v izolovaných testech kontaktovány. [Diagram](diagrams/EXTERNAL_SERVICES.md).

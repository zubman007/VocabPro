# Návod pro další vývoj

## Obrazovka a životní cyklus

Nový kontrolér obdrží AppContext, vytvoří view/layout a ScreenController.
Použije ModuleHeader a společné session/toolbar komponenty. Zkratky registruje
přes vlastněné bindings, jobs přes lifecycle.after, dialog přes AppDialog.
Při odchodu zaregistruje cleanup pracovních úloh a zachová smlouvu Save/Close.
Vzor: grammar/practise.py; asynchronní save: vocabulary/editor.py.

## Nová kategorie, teorie a jazyk

Kategorii otázky zadat v editoru; správná možnost se při update přesune do
option_1. ensure_theory_categories přidá prázdný protějšek. Popsat teorii v
theory editoru. Normalizaci provádí category_key; neměnit ji bez testu kolizí.
Pro nový studovaný jazyk zajistit volbu v nastavení a datové soubory; pro
časování PERSONS_MAP, pro automatický hlas VOICES a skutečně podporovaného
providera. Pro nový jazyk UI doplnit všechny katalogové klíče, viz LOCALIZATION.

## Změna dat a výukových pravidel

Nejprve čistý test modelu bez Tk. Pravidla patří do session/practise_data,
I/O do repository. Nový CSV sloupec musí mít kompatibilní default při čtení,
zachování extra sloupců, validaci a definované chování při zápisu staršího
souboru. Migrace schématu vyžaduje samostatný návratový postup; nesmí se
automaticky přepisovat skutečné kurzy.

## API provider a bezpečný save

Provider pracuje s frame, explicitními cestami/nastavením a nevolá GUI.
Použije api_http pro timeout a atomický download a api_settings.audio_path,
aby respektoval staging. Zapojení obohacení je v editor_attributes.
Nezavádět automatické retry placených POST. Nezapisovat výjimku s tajným URL
do logu; použít diagnostics.report_error nebo bezpečnou statickou zprávu.

Při úpravě save zachovat snapshot/revizi, třícestnou kontrolu změn a odmítnutí
celé dávky při konfliktu. Cancellation testovat před přípravou, po síti a před
commitem. Po zahájení commit sekce se cancellation zpracuje až po dokončení,
aby nemohla přerušit potvrzení napůl. Otestovat i selhání rollbacku.

## Dokumentace a kontrola

Každý nový produkční modul musí být v MODULES s přímými importy a účelem;
callback/dynamické závislosti popsat zvlášť. U rozhraní uvést vstup, výstup,
vedlejší účinky a vlastnictví. Spustit cílené testy, pak celou sadu pro větší
architektonickou změnu. Ověřit relativní odkazy a Mermaid diagramy. Nepřidávat
abstrakci jen kvůli sjednocení jmen, pokud varianty mají jiné datové smlouvy.

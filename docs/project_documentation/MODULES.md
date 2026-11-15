# Katalog produkčních modulů

## app/services/mail_credentials.py

- **Účel:** Uložení a čtení SMTP odesílatele v aktuálním Windows účtu.
- **Veřejné vstupy:** `load_credentials()` vrací dvojici nebo None;
  `save_credentials(username, password)` validuje a uloží Generic credential.
- **Závislosti a odběratelé:** Standardní ctypes/Win32; používá jej
  services/backup a preferences/backup_account. Bez CSV a síťových operací.
- **Vedlejší účinky:** Explicitní Save zapisuje do Windows Credential Manager.
  Chyby neobsahují heslo, alokace CredRead se vždy uvolní, zapisovací buffer
  se vyprázdní. Původní Python řetězce tím nelze garantovaně vymazat z paměti.
- **Omezení:** Windows, lokální uživatelský profil, nikoli přenosný soubor zálohy.

## app/preferences/backup_account.py

- **Účel:** `BackupAccountDialog` pro lokální konfiguraci SMTP účtu.
- **Vstupy/výstupy:** Parent s AppContext, volitelný callback po uložení;
  validovaný účet ve Windows. Používá jej PreferencesDialog.
- **Závislosti:** AppDialog, theme, mail_credentials, šest lokalizací.
- **Vedlejší účinky:** Až explicitní Save mění uložený účet. Dialog neposílá mail,
  obnovuje modalitu nadřazeného nastavení a zobrazuje chyby bez zavření formuláře.

## Doplněné moduly katalogu štítků

### app/repositories/tag_lessons.py

- **Účel:** Read-only sestavení lekce podle stabilního ID štítku.
- **Vstup/výstup:** Slovníkové a katalogové CSV, jazyková dvojice a ID; DataFrame se všemi přiřazenými slovy podle termínu opakování.
- **Veřejný vstup:** `tag_lesson`; chybějící či nepřiřazený štítek vrací prázdný frame.
- **Závislosti:** pandas, repositories.tags; volá jej statistics.viewer.
- **Vedlejší účinky:** Pouze čtení CSV. `ordered_lesson` v attrs aktivuje stabilní pořadí v PracticeSession.
- **Omezení:** Nejde o výběr pouze splatných slov; záměrně zahrnuje i dosud neučená a budoucí.

### app/statistics/vocabulary_tags.py

- **Účel:** Agregace přiřazených štítků a kompaktní statistický přehled slovní zásoby.
- **Veřejné vstupy:** `TagStatistics`, `tag_statistics(frame, outcomes)`, `VocabularyTagsPanel`.
- **Vstupy/výstupy:** Slovník s Tags a již vypočítané post-learning výsledky; seznam počtů slov a S/F podle štítku, paginované GUI.
- **Závislosti:** dataclasses, customtkinter, ui.theme, vocabulary.tags_data.normalize_tags.
- **Odběratelé:** statistics.data volá čistou agregaci ve workeru; statistics.viewer vytváří a plní panel na UI vlákně.
- **Vedlejší účinky:** GUI widgety pouze při instanci panelu; agregace neprovádí I/O ani nemění vstupní data.
- **Omezení:** Přes více štítků se počty mohou překrývat. Nejvýše 15 řádků na stránku; controller doplňuje i nepřiřazené katalogové položky a správný jazyk názvů.

### app/vocabulary/tags_data.py

- **Účel:** Čistá pravidla seznamů štítků a příslušnosti do katalogu.
- **Veřejné vstupy:** `normalize_tags`, `validate_word_tags`, `translated_tags`, `filter_by_tags`, `UnknownTagError`.
- **Vstupy/výstupy:** DataFrame slovíček a katalog, názvy jazyků; validovaná kopie nebo chyba s ID slova a štítkem.
- **Závislosti:** pandas, unicodedata; bez GUI, souborů a sítě.
- **Odběratelé:** editor_data (kompatibilní reexport normalizace), editor, editor_tag_picker, save_workflow, practise (cílové názvy štítků).
- **Omezení:** Ukládá názvy ve výchozím jazyce; čárka je oddělovač.

### app/vocabulary/editor_tag_picker.py

- **Účel:** Modální `WordTagsDialog` s hledáním a více zaškrtávátky pro jedno slovíčko nebo podmínku filtru (`selection_only=True`).
- **Vstupy/výstupy:** Context, jazyk, ID, zobrazený název, současné štítky a callback; Apply předá ověřený text callbacku.
- **Závislosti:** AppDialog, SearchFilterPanel, repositories.tags, tags_data, pandas, customtkinter, styly.
- **Odběratelé:** EditorController.Open_word_tags a Open_tag_filter (odložené importy).
- **Vedlejší účinky:** GUI a čtení katalogu; samotné přiřazení neukládá CSV. Před Apply znovu čte aktuální katalog.
- **Omezení:** Štítky mimo katalog nelze přidat; Apply nahrazuje sadu přiřazení vybraného slova.

### app/repositories/tags.py

- **Účel:** Datový kontrakt a perzistence katalogu štítků pro jazykovou dvojici.
- **Veřejné vstupy:** `catalog_columns`, `validate_catalog`, `load_catalog`, `save_catalog`, `TagValidationError`.
- **Vstupy a výstupy:** Cesta, jazyky a DataFrame; načtený validovaný DataFrame s revizí nebo bezpečně uložený katalog.
- **Závislosti:** pandas, csv, pathlib, unicodedata, `app.shared.storage`.
- **Odběratelé:** `app.vocabulary.editor_tags`.
- **Vedlejší účinky:** Čtení a atomický zápis katalogového CSV; žádné GUI, audio, síť ani změny slovníku.
- **Omezení:** Názvy štítků neobsahují čárku; vazby slovíček zatím používají text, nikoliv ID katalogu.

### app/vocabulary/editor_tags.py

- **Účel:** Samostatné tabulkové okno `TagsDialog`, správa a validace změn katalogu.
- **Veřejný vstup:** `TagsDialog(owner, language, context=None)`.
- **Vstupy a výstupy:** AppContext, jazyk, uživatelské editace; uložený katalog nebo zavření bez zápisu.
- **Závislosti:** `repositories.tags`, `AppDialog`, sdílené styly/editor_layout, tksheet, pandas, customtkinter, messagebox, diagnostics.
- **Odběratelé:** `EditorController.Open_tags` (odložený import).
- **Vedlejší účinky:** GUI okno, modalita, potvrzení změn, volání repository při Save; bez audia a sítě.
- **Omezení:** Přidává položky katalogu; nepřiřazuje je automaticky k vybranému slovíčku.

Katalog vznikl proti finálním zdrojům. Obsahuje každý Python modul v app mimo tests,
včetně značek balíčků, a vstup start.py. sandbox.py je záměrně ponechaný
vývojový soubor mimo produkční start, nebyl měněn ani spuštěn. Testovací
infrastrukturu popisuje [TESTING](TESTING.md).

Závislosti a odběratelé jsou přímé statické importy včetně lokálních importů.
Neprokazují všechny callbackové/dynamické cesty. editor_navigation směruje
přes import_module do editor/editor_theory; main a GUI tlačítka volají
veřejné vstupy nepřímo. Samotné značky balíčků jsou namespace, ne služby.

## app/__init__.py

- **Modul:** `app` — [zdroj](../../app/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [start](../../start.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/about/__init__.py

- **Modul:** `app.about` — [zdroj](../../app/about/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.about.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/about/dialog.py

- **Modul:** `app.about.dialog` — [zdroj](../../app/about/dialog.py).
- **Účel a odpovědnosti:** Přehled aplikace, průvodce a seznam zkratek.
- **Veřejné vstupy:** `AboutDialog` (metody `present`, `destroy`); `open_about(parent, translate, app_name, learned_by, languages)`.
- **Klíčové vstupy:** Owner, překladač a studované jazyky.
- **Výstupy:** Okno About se záložkami.
- **Přímé projektové závislosti:** [app.about.shortcuts](../../app/about/shortcuts.py), [app.core.context](../../app/core/context.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.sections](../../app/ui/sections.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/about/shortcuts.py

- **Modul:** `app.about.shortcuts` — [zdroj](../../app/about/shortcuts.py).
- **Účel a odpovědnosti:** Jediný katalog zkratek pro nápovědu i About.
- **Veřejné vstupy:** `shortcut_sections(show_synonyms=True)`.
- **Klíčové vstupy:** Volba automatického zobrazení synonym.
- **Výstupy:** Sekce dvojic klávesa/popis.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/conjugation/__init__.py

- **Modul:** `app.conjugation` — [zdroj](../../app/conjugation/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.conjugation.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/conjugation/data.py

- **Modul:** `app.conjugation.data` — [zdroj](../../app/conjugation/data.py).
- **Účel a odpovědnosti:** Verb, osoby jazyků, prioritní dávka a porovnání tvarů.
- **Veřejné vstupy:** `Verb` (metody `copy`); `select_verbs(all_df, sample_size)`; `build_verbs(df, lang, learned_by)`; `record_result(sel, verb_id, result_char)`; `answers_match(verb, answers, persons)`.
- **Klíčové vstupy:** Zdrojová tabulka nebo odpovědi osob.
- **Výstupy:** Vybraná dávka, hodnoty Verb, správnost a R/LR mutace.
- **Přímé projektové závislosti:** [app.shared.learning_data](../../app/shared/learning_data.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py), [app.conjugation.session](../../app/conjugation/session.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/conjugation/layout.py

- **Modul:** `app.conjugation.layout` — [zdroj](../../app/conjugation/layout.py).
- **Účel a odpovědnosti:** Jednotné rozložení tvarů a spodních akcí.
- **Veřejné vstupy:** `build(app, persons, confirm, next_verb, save, exit_app, back)`.
- **Klíčové vstupy:** Root, definice osob a callbacky.
- **Výstupy:** View s entries a ovládáním.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.training_layout](../../app/ui/training_layout.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/conjugation/practise.py

- **Modul:** `app.conjugation.practise` — [zdroj](../../app/conjugation/practise.py).
- **Účel a odpovědnosti:** Kontrolér zadání tvarů, feedbacku, review a save.
- **Veřejné vstupy:** `ConjugationController` (metody `next_verb`, `skip`, `confirm`, `review`, `close_review`, `save`, `back`, `exit_app`); `Conjugation(app_input, lang_input, *, context=None)`.
- **Klíčové vstupy:** Zdroj, výběr, slovesa, osoby, cesta a kontext.
- **Výstupy:** Výukový screen a změněné R/LR.
- **Přímé projektové závislosti:** [app.conjugation.data](../../app/conjugation/data.py), [app.conjugation.layout](../../app/conjugation/layout.py), [app.conjugation.session](../../app/conjugation/session.py), [app.core.context](../../app/core/context.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.repositories.conjugation](../../app/repositories/conjugation.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.diagnostics](../../app/shared/diagnostics.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.learning_review](../../app/ui/learning_review.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/conjugation/session.py

- **Modul:** `app.conjugation.session` — [zdroj](../../app/conjugation/session.py).
- **Účel a odpovědnosti:** Paměťové kolo časování s pravidlem opravy po chybě.
- **Veřejné vstupy:** `ConjugationSession` (metody `advance`, `confirm`).
- **Klíčové vstupy:** Výběr frame, hodnoty Verb a osoby.
- **Výstupy:** Zbývající slovesa, počitadlo a historie výběru.
- **Přímé projektové závislosti:** [app.conjugation.data](../../app/conjugation/data.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/core/__init__.py

- **Modul:** `app.core` — [zdroj](../../app/core/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.core.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/core/context.py

- **Modul:** `app.core.context` — [zdroj](../../app/core/context.py).
- **Účel a odpovědnosti:** Explicitní závislosti aplikace a kompatibilní aktivní kontext.
- **Veřejné vstupy:** `initial_preferences()`; `AppContext` (metody `translate`, `vocabulary_path`, `conjugation_path`, `grammar_path`, `theory_path`, `audio_folder`, `go_home`, `bind`); `get_context(owner=None, context=None)`.
- **Klíčové vstupy:** Preference, root/files cesty a navigační callback.
- **Výstupy:** AppContext, překlady a cesty konkrétního kurzu.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py), [app.preferences.data](../../app/preferences/data.py), [app.shared.translations](../../app/shared/translations.py).
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.editor_theory](../../app/grammar/editor_theory.py), [app.grammar.practise](../../app/grammar/practise.py), [app.main](../../app/main.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.services.api](../../app/services/api.py), [app.shared.settings](../../app/shared/settings.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [start](../../start.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/core/screen_controller.py

- **Modul:** `app.core.screen_controller` — [zdroj](../../app/core/screen_controller.py).
- **Účel a odpovědnosti:** Vlastnictví zdrojů a odchodu jednoho screenu.
- **Veřejné vstupy:** `ScreenController` (metody `add_cleanup`, `trace`, `own_dialog`, `after`, `after_idle`, `cancel_after`, `can_leave`, `finish`, `close`).
- **Klíčové vstupy:** Root, screen, bindingy a cleanup callbacky.
- **Výstupy:** Registrované jobs/dialogy, rozhodnutí can_leave a finish.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.ui.bindings](../../app/ui/bindings.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.practise](../../app/grammar/practise.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** GUI, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/__init__.py

- **Modul:** `app.grammar` — [zdroj](../../app/grammar/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.grammar.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/grammar/category_filter.py

- **Modul:** `app.grammar.category_filter` — [zdroj](../../app/grammar/category_filter.py).
- **Účel a odpovědnosti:** Počty kategorií a dialog vícenásobného výběru.
- **Veřejné vstupy:** `category_options(questions)`; `CategoryFilterDialog` (metody `destroy`).
- **Klíčové vstupy:** Otázky nebo nabídka kategorií a současná množina.
- **Výstupy:** Kategorie s počty; potvrzený nový filtr.
- **Přímé projektové závislosti:** [app.grammar.theory_data](../../app/grammar/theory_data.py), [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/data.py

- **Modul:** `app.grammar.data` — [zdroj](../../app/grammar/data.py).
- **Účel a odpovědnosti:** Vážené náhodné pořadí otázek bez opakování; samostatné rovnoměrné míchání možností odpovědí.
- **Veřejné vstupy:** `question_weights(questions, *, now=None)`; `Shuffle_copy(items, questions, *, rng=None, now=None)`.
- **Klíčové vstupy:** Již filtrované otázky, historie S/F, poslední čas odpovědi; volitelný generátor náhody a čas pro reprodukovatelné testy.
- **Výstupy:** Nový seznam bez mutace vstupu.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.grammar.session](../../app/grammar/session.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/editor.py

- **Modul:** `app.grammar.editor` — [zdroj](../../app/grammar/editor.py).
- **Účel a odpovědnosti:** Kontrolér formulářové editace otázek a sdíleného editorového chování.
- **Veřejné vstupy:** `GrammarEditor` (metody `refresh`, `select`, `filter`, `apply`, `add`, `delete`, `save`, `back`, `close_app`, `open_related`); `Edit_grammar(app, language, *, context=None)`.
- **Klíčové vstupy:** Owner, jazyk, cesta dokumentu, návrat a kontext.
- **Výstupy:** Editor s validací a zachovanou historií; kompatibilní vstup Edit_grammar.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.grammar.editor_data](../../app/grammar/editor_data.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.editor_navigation](../../app/grammar/editor_navigation.py), [app.repositories.grammar_theory](../../app/repositories/grammar_theory.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.diagnostics](../../app/shared/diagnostics.py), [app.shared.settings](../../app/shared/settings.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor_theory](../../app/grammar/editor_theory.py), [app.main](../../app/main.py).
- **Oblasti práce:** GUI, CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/editor_data.py

- **Modul:** `app.grammar.editor_data` — [zdroj](../../app/grammar/editor_data.py).
- **Účel a odpovědnosti:** Dokument otázek, validace odpovědí, ID a historie.
- **Veřejné vstupy:** `QuestionValidationError`; `validate_question(values)`; `GrammarDocument` (metody `question`, `update`, `add`, `delete`, `save`).
- **Klíčové vstupy:** CSV cesta, ID, formulář a volba správné odpovědi.
- **Výstupy:** Pracovní frame, QuestionValidationError nebo revizní save.
- **Přímé projektové závislosti:** [app.repositories.csv_store](../../app/repositories/csv_store.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor](../../app/grammar/editor.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/editor_layout.py

- **Modul:** `app.grammar.editor_layout` — [zdroj](../../app/grammar/editor_layout.py).
- **Účel a odpovědnosti:** Sestavení společného otázkového/teoretického editoru.
- **Veřejné vstupy:** `build(app, language, callbacks, theory=False)`.
- **Klíčové vstupy:** Root, jazyk, callbacky a režim theory.
- **Výstupy:** Header, filtry, tabulka, formulář a spodní toolbar.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.training_layout](../../app/ui/training_layout.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor](../../app/grammar/editor.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/editor_navigation.py

- **Modul:** `app.grammar.editor_navigation` — [zdroj](../../app/grammar/editor_navigation.py).
- **Účel a odpovědnosti:** Odložené směrování mezi otázkami a teorií bez přímého importního cyklu.
- **Veřejné vstupy:** `open_editor(app, language, *, theory=False, context=None)`.
- **Klíčové vstupy:** Root, jazyk, boolean theory a kontext.
- **Výstupy:** Otevření příslušného kompatibilního vstupního bodu.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.grammar.editor](../../app/grammar/editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/editor_theory.py

- **Modul:** `app.grammar.editor_theory` — [zdroj](../../app/grammar/editor_theory.py).
- **Účel a odpovědnosti:** Specializace editoru pro teorie a návrhy kategorií.
- **Veřejné vstupy:** `GrammarTheoryEditor` (metody `refresh`); `Edit_grammar_theory(app, language, *, context=None)`.
- **Klíčové vstupy:** Owner, jazyk a kontext.
- **Výstupy:** GrammarTheoryEditor nad společným chováním výběru/save.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.editor_theory_data](../../app/grammar/editor_theory_data.py).
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** konfigurace.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/editor_theory_data.py

- **Modul:** `app.grammar.editor_theory_data` — [zdroj](../../app/grammar/editor_theory_data.py).
- **Účel a odpovědnosti:** Dokument teorií s interním editačním ID a kompatibilními sloupci.
- **Veřejné vstupy:** `GrammarTheoryDocument` (metody `question`, `update`, `add`, `delete`, `save`).
- **Klíčové vstupy:** Cesta, ID, sekce teorie a kategorie.
- **Výstupy:** Validované změny, placeholdery a CSV bez interního ID.
- **Přímé projektové závislosti:** [app.grammar.theory_data](../../app/grammar/theory_data.py), [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.repositories.grammar_theory](../../app/repositories/grammar_theory.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor_theory](../../app/grammar/editor_theory.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/layout.py

- **Modul:** `app.grammar.layout` — [zdroj](../../app/grammar/layout.py).
- **Účel a odpovědnosti:** Rozložení zadání, čtyř odpovědí a session panelu.
- **Veřejné vstupy:** `reset_option(button, value)`; `build(app, choose, reveal, next_question, back, exit_app, theory=None, category_filter=None, save=None)`.
- **Klíčové vstupy:** Root a callbacky výuky/uložení/navigace.
- **Výstupy:** Pohled s pojmenovanými widgety.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.session_panel](../../app/ui/components/session_panel.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.training_layout](../../app/ui/training_layout.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/practise.py

- **Modul:** `app.grammar.practise` — [zdroj](../../app/grammar/practise.py).
- **Účel a odpovědnosti:** Řízení otázek, feedbacku, filtrů, teorií a pending odpovědí.
- **Veřejné vstupy:** `GrammarController` (metody `open_filter`, `apply_filter`, `answer_shortcut`, `answer_key`, `next_shortcut`, `theory_shortcut`, `filter_shortcut`, `review_previous`, `next_question`, `choose`, `reveal`, `continue_if_revealed`, `reveal_or_next`, `restart`, `back`, `save`, `exit_app`, `show_theory`); `Grammar_training(app_input, lang_input, categories=None, *, context=None)`.
- **Klíčové vstupy:** Otázky, CSV cesta, callback návratu a kontext.
- **Výstupy:** Výukový screen; dávka odpovědí zapsaná až při save.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.session](../../app/grammar/session.py), [app.grammar.theory_data](../../app/grammar/theory_data.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.repositories.grammar](../../app/repositories/grammar.py), [app.repositories.grammar_filters](../../app/repositories/grammar_filters.py), [app.repositories.grammar_theory](../../app/repositories/grammar_theory.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.answer_keys](../../app/ui/answer_keys.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.learning_review](../../app/ui/learning_review.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI, CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/grammar/session.py

- **Modul:** `app.grammar.session` — [zdroj](../../app/grammar/session.py).
- **Účel a odpovědnosti:** Stav vážené otázkové fronty, počitadla kola a pracovní historie pro následující kola/filtry.
- **Veřejné vstupy:** `GrammarSession` (metody `restart`, `advance`, `can_answer`, `is_correct`, `answer`, `reveal`).
- **Klíčové vstupy:** Seznam kanonických otázek, volitelná sdílená mapa `progress` a vybraný index odpovědi; `answer` přijímá volitelný čas `when`.
- **Výstupy:** Aktuální/předchozí otázka, možnosti, skóre a odhalení.
- **Přímé projektové závislosti:** [app.grammar.data](../../app/grammar/data.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/theory_data.py

- **Modul:** `app.grammar.theory_data` — [zdroj](../../app/grammar/theory_data.py).
- **Účel a odpovědnosti:** Jednotný normalizovaný klíč kategorie.
- **Veřejné vstupy:** `category_key(value)`.
- **Klíčové vstupy:** Text kategorie nebo prázdná hodnota.
- **Výstupy:** Klíč pro párování otázky a teorie.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.editor_theory_data](../../app/grammar/editor_theory_data.py), [app.grammar.practise](../../app/grammar/practise.py), [app.repositories.grammar_filters](../../app/repositories/grammar_filters.py), [app.repositories.grammar_theory](../../app/repositories/grammar_theory.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/grammar/theory_window.py

- **Modul:** `app.grammar.theory_window` — [zdroj](../../app/grammar/theory_window.py).
- **Účel a odpovědnosti:** Prezentace sekcí teorie v pomocném okně.
- **Veřejné vstupy:** `TheoryWindow` (metody `destroy`).
- **Klíčové vstupy:** Owner a načtená teorie kategorie.
- **Výstupy:** Čitelný scrollovatelný dialog.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/home/__init__.py

- **Modul:** `app.home` — [zdroj](../../app/home/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.home.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/home/data.py

- **Modul:** `app.home.data` — [zdroj](../../app/home/data.py).
- **Účel a odpovědnosti:** Výběr due slov a učebních dávek pro hlavní nabídku.
- **Veřejné vstupy:** `course_overview(files_dir, learned_by, language, learn_batch, repeat_batch, now=None)`.
- **Klíčové vstupy:** Složka kurzů, jazyky, dávky a volitelný čas.
- **Výstupy:** Slovník počtů a DataFrame vybraných slov.
- **Přímé projektové závislosti:** [app.repositories.courses](../../app/repositories/courses.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.shared.learning_data](../../app/shared/learning_data.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/home/layout.py

- **Modul:** `app.home.layout` — [zdroj](../../app/home/layout.py).
- **Účel a odpovědnosti:** Rozložení hlavní stránky a horní navigace.
- **Veřejné vstupy:** `build_navigation(app, callbacks)`; `build_home(app, stats_by_lang, languages, callbacks)`.
- **Klíčové vstupy:** Root, přehledy jazyků a callbacky akcí.
- **Výstupy:** Karty kurzů a tlačítka.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.brand](../../app/ui/brand.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/main.py

- **Modul:** `app.main` — [zdroj](../../app/main.py).
- **Účel a odpovědnosti:** Sestavení menu, načtení nastavení, příprava kurzů a směrování vstupů.
- **Veřejné vstupy:** `main_proc(app, context=None)`; `Exit(app)`; `Load_setting(context=None)`; `Back_up(app, context=None)`; `About_app(app, context=None)`.
- **Klíčové vstupy:** Root, AppContext a vybraný jazyk.
- **Výstupy:** Hlavní přehled nebo předání konkrétnímu kontroléru.
- **Přímé projektové závislosti:** [app.about.dialog](../../app/about/dialog.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.core.context](../../app/core/context.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.practise](../../app/grammar/practise.py), [app.home.data](../../app/home/data.py), [app.home.layout](../../app/home/layout.py), [app.preferences.data](../../app/preferences/data.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.repositories.courses](../../app/repositories/courses.py), [app.repositories.preferences](../../app/repositories/preferences.py), [app.services.backup](../../app/services/backup.py), [app.services.backup_background](../../app/services/backup_background.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.settings](../../app/shared/settings.py), [app.shared.translations](../../app/shared/translations.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Staticky zjištění odběratelé:** [start](../../start.py).
- **Oblasti práce:** GUI, CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/paths.py

- **Modul:** `app.paths` — [zdroj](../../app/paths.py).
- **Účel a odpovědnosti:** Jednotné kořeny dat, obrázků a katalogů.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Umístění modulu na disku.
- **Výstupy:** ROOT_DIR, FILES_DIR, IMAGES_DIR a LOCALES_DIR.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.core.context](../../app/core/context.py), [app.preferences.data](../../app/preferences/data.py), [app.repositories.api_settings](../../app/repositories/api_settings.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.translations](../../app/shared/translations.py), [app.ui.brand](../../app/ui/brand.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.vocabulary.practise_audio](../../app/vocabulary/practise_audio.py), [start](../../start.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/preferences/__init__.py

- **Modul:** `app.preferences` — [zdroj](../../app/preferences/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.preferences.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/preferences/data.py

- **Modul:** `app.preferences.data` — [zdroj](../../app/preferences/data.py).
- **Účel a odpovědnosti:** Schéma, validace a immutable snapshot preferencí.
- **Veřejné vstupy:** `with_defaults(frame)`; `RuntimePreferences` (metody `from_frame`); `PreferenceError`; `options_for(kind)`; `section_for(name)`; `validate_preferences(frame, values)`.
- **Klíčové vstupy:** Frame Name/Type/Value a změněné hodnoty.
- **Výstupy:** Validovaný frame nebo PreferenceError, RuntimePreferences.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py).
- **Staticky zjištění odběratelé:** [app.core.context](../../app/core/context.py), [app.main](../../app/main.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.repositories.preferences](../../app/repositories/preferences.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/preferences/dialog.py

- **Modul:** `app.preferences.dialog` — [zdroj](../../app/preferences/dialog.py).
- **Účel a odpovědnosti:** Editace nastavení v tematických záložkách.
- **Veřejné vstupy:** `PreferencesDialog` (metody `present`, `destroy`, `toggle_secrets`, `save`); `open_preferences(app, *, context=None)`.
- **Klíčové vstupy:** Owner, překladač a cesta settings.
- **Výstupy:** Dialog; uložené preference nebo zachované chybné pole.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.preferences.data](../../app/preferences/data.py), [app.repositories.preferences](../../app/repositories/preferences.py), [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.sections](../../app/ui/sections.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/repositories/__init__.py

- **Modul:** `app.repositories` — [zdroj](../../app/repositories/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.repositories.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_synonym_columns](../../app/vocabulary/editor_synonym_columns.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/repositories/api_settings.py

- **Modul:** `app.repositories.api_settings` — [zdroj](../../app/repositories/api_settings.py).
- **Účel a odpovědnosti:** Cache hodnot API a lokální přesměrování audio výstupu.
- **Veřejné vstupy:** `audio_output(folder)`; `load_settings(path=None)`; `audio_path(learning_by, language, word_id, settings_path=None)`.
- **Klíčové vstupy:** Cesta settings, jazykové ID a volitelný staging.
- **Výstupy:** Kopie nastavení a cílová MP3 cesta.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py), [app.repositories.csv_store](../../app/repositories/csv_store.py).
- **Staticky zjištění odběratelé:** [app.services.api_dictionary](../../app/services/api_dictionary.py), [app.services.api_speech](../../app/services/api_speech.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/conjugation.py

- **Modul:** `app.repositories.conjugation` — [zdroj](../../app/repositories/conjugation.py).
- **Účel a odpovědnosti:** Validace zdroje časování a bezpečný zápis změn R/LR.
- **Veřejné vstupy:** `load_source(path, language, learned_by)`; `save_results(all_df, selection, path)`.
- **Klíčové vstupy:** Cesta, původní zdroj a výběr session.
- **Výstupy:** Aktuální sloučený zdroj s nezměněnými cizími poli.
- **Přímé projektové závislosti:** [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/courses.py

- **Modul:** `app.repositories.courses` — [zdroj](../../app/repositories/courses.py).
- **Účel a odpovědnosti:** Vytvoření prázdného aktivního kurzu, počty a výběr příloh.
- **Veřejné vstupy:** `ensure_course(files_dir, learned_by, language)`; `remove_unused_empty_courses(files_dir, learned_by, languages)`; `row_count(path)`; `backup_files(files_dir)`.
- `remove_unused_empty_courses` je pouze explicitně volatelná utilita; načtení
  nastavení ani přepnutí aktivních jazyků ji automaticky nevolá.
- **Klíčové vstupy:** Složka files a aktivní páry jazyků.
- **Výstupy:** Počty, jména uklizených prázdných souborů nebo bajty záloh.
- **Přímé projektové závislosti:** [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.home.data](../../app/home/data.py), [app.main](../../app/main.py), [app.services.backup](../../app/services/backup.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/csv_store.py

- **Modul:** `app.repositories.csv_store` — [zdroj](../../app/repositories/csv_store.py).
- **Účel a odpovědnosti:** Společné čtení, revizní dokumenty a třícestná pole.
- **Veřejné vstupy:** `read_csv(path, **options)`; `read_document(path, *, optional=False, columns=None, message='The file changed while it was being read.')`; `commit_document(path, frame, revision, *, message='The file changed. Reopen it before saving.')`; `apply_delta(current, original, edited, columns, *, id_column='ID')`.
- **Klíčové vstupy:** Cesta, frame, původní revize nebo tři snapshoty.
- **Výstupy:** Frame/revize, sloučený frame nebo konflikt celé operace.
- **Přímé projektové závislosti:** [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor_data](../../app/grammar/editor_data.py), [app.grammar.editor_theory_data](../../app/grammar/editor_theory_data.py), [app.repositories.api_settings](../../app/repositories/api_settings.py), [app.repositories.conjugation](../../app/repositories/conjugation.py), [app.repositories.preferences](../../app/repositories/preferences.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.statistics.data](../../app/statistics/data.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/grammar.py

- **Modul:** `app.repositories.grammar` — [zdroj](../../app/repositories/grammar.py).
- **Účel a odpovědnosti:** Validované načtení otázek a indexovaný atomický zápis odpovědí.
- **Veřejné vstupy:** `Load_questions_from_csv(csv_path)`; `save_answers(csv_path, answers)`.
- **Klíčové vstupy:** CSV a uspořádané záznamy ID/SF/expected/čas.
- **Výstupy:** Seznam otázek nebo aktualizované historie na disku.
- **Přímé projektové závislosti:** [app.shared.learning_data](../../app/shared/learning_data.py), [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/grammar_filters.py

- **Modul:** `app.repositories.grammar_filters` — [zdroj](../../app/repositories/grammar_filters.py).
- **Účel a odpovědnosti:** Uložení filtru kategorií do JSON hodnoty nastavení.
- **Veřejné vstupy:** `load_filter(path, learned_by, language, available)`; `save_filter(path, learned_by, language, selected, available)`.
- **Klíčové vstupy:** Pár jazyků, vybrané a dostupné kategorie.
- **Výstupy:** Množina kategorií, žádné omezení nebo zápis settings.
- **Přímé projektové závislosti:** [app.grammar.theory_data](../../app/grammar/theory_data.py), [app.shared.diagnostics](../../app/shared/diagnostics.py), [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/grammar_theory.py

- **Modul:** `app.repositories.grammar_theory` — [zdroj](../../app/repositories/grammar_theory.py).
- **Účel a odpovědnosti:** Načítání teorií a zakládání chybějících kategorií.
- **Veřejné vstupy:** `question_categories_for_theory(path)`; `ensure_theory_categories(path, categories)`; `load_theory(path)`.
- **Klíčové vstupy:** Cesta teorie, související otázky a kategorie.
- **Výstupy:** Mapa teorií, návrhy kategorií nebo počet vložených placeholderů.
- **Přímé projektové závislosti:** [app.grammar.theory_data](../../app/grammar/theory_data.py), [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.editor_theory_data](../../app/grammar/editor_theory_data.py), [app.grammar.practise](../../app/grammar/practise.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/preferences.py

- **Modul:** `app.repositories.preferences` — [zdroj](../../app/repositories/preferences.py).
- **Účel a odpovědnosti:** Načítání/ukládání nastavení a slučování zálohovacích metadat.
- **Veřejné vstupy:** `load_preferences(path=PREFERENCES_FILE)`; `save_preferences(frame, values, path=PREFERENCES_FILE)`; `record_success(path, recipient, period, expected_next, now=None)`.
- **Klíčové vstupy:** Frame, formulářové hodnoty, cesta a očekávané plánování.
- **Výstupy:** Aktualizovaný frame nebo nový termín zálohy.
- **Přímé projektové závislosti:** [app.preferences.data](../../app/preferences/data.py), [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.shared.storage](../../app/shared/storage.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py), [app.preferences.dialog](../../app/preferences/dialog.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/synonyms.py

- **Modul:** `app.repositories.synonyms` — [zdroj](../../app/repositories/synonyms.py).
- **Účel a odpovědnosti:** Neorientované vazby, jejich validace a optimistický zápis.
- **Veřejné vstupy:** `relation_path(course)`; `load(course, words)`; `replace_links(course, word_id, selected, revision)`; `prune_deleted(course)`.
- **Klíčové vstupy:** Kurz, slovíčka, zdrojové ID, cíle a revize.
- **Výstupy:** Normalizovaný frame/revize, náhrada vazeb nebo prořezání.
- **Přímé projektové závislosti:** [app.shared.storage](../../app/shared/storage.py), [app.vocabulary.synonyms](../../app/vocabulary/synonyms.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_synonym_columns](../../app/vocabulary/editor_synonym_columns.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/repositories/vocabulary.py

- **Modul:** `app.repositories.vocabulary` — [zdroj](../../app/repositories/vocabulary.py).
- **Účel a odpovědnosti:** Čtení slovníku a zápis výukové delty; kompatibilní save vstup.
- **Veřejné vstupy:** `read_words(path)`; `load_vocabulary(path, language, learned_by)`; `load_editor_snapshot(path, language, learned_by)`; `save_practice(path, remaining, completed, headers, *, original=None)`; `save_course(*args, **kwargs)`.
- **Klíčové vstupy:** Cesta kurzu, jazyk, session frame a original snapshot.
- **Výstupy:** Slovníková data, revize nebo commit výsledků.
- **Přímé projektové závislosti:** [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.shared.learning_data](../../app/shared/learning_data.py), [app.shared.storage](../../app/shared/storage.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Staticky zjištění odběratelé:** [app.home.data](../../app/home/data.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.editor_synonym_columns](../../app/vocabulary/editor_synonym_columns.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/services/__init__.py

- **Modul:** `app.services` — [zdroj](../../app/services/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.services.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_attributes](../../app/vocabulary/editor_attributes.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/services/api.py

- **Modul:** `app.services.api` — [zdroj](../../app/services/api.py).
- **Účel a odpovědnosti:** Kompatibilní editorová API nad konkrétními providery.
- **Veřejné vstupy:** `Dict_api(i, df, *, context=None)`; `MW(i, df, lang, *, context=None)`; `Eveleven_labs(i, df, lang, *, context=None)`.
- **Klíčové vstupy:** Index řádku, frame, jazyk a kontext workeru.
- **Výstupy:** Obohacený frame se stejnými ID.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.services.api_dictionary](../../app/services/api_dictionary.py), [app.services.api_speech](../../app/services/api_speech.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_attributes](../../app/vocabulary/editor_attributes.py).
- **Oblasti práce:** audio, konfigurace.
- **Vedlejší účinky:** Přístup k mixeru/mikrofonu nebo audio souborům dle účelu.
- **Omezení a rizika:** Zařízení může chybět; soubory a streamy mají vlastní životní cyklus. Viz AUDIO.

## app/services/api_dictionary.py

- **Modul:** `app.services.api_dictionary` — [zdroj](../../app/services/api_dictionary.py).
- **Účel a odpovědnosti:** Parsování slovníkových odpovědí a doplnění údajů/audia.
- **Veřejné vstupy:** `dictionary_entry(i, df, learning_by, *, settings_path=None)`; `merriam_entry(i, df, lang, learning_by, *, settings_path=None)`.
- **Klíčové vstupy:** Řádek, jazyk, vlastní jazyk a cesta API nastavení.
- **Výstupy:** Doplněný frame, případně stažený MP3 soubor.
- **Přímé projektové závislosti:** [app.repositories.api_settings](../../app/repositories/api_settings.py), [app.services.api_http](../../app/services/api_http.py).
- **Staticky zjištění odběratelé:** [app.services.api](../../app/services/api.py).
- **Oblasti práce:** CSV/perzistence, síť, konfigurace.
- **Vedlejší účinky:** HTTP/SMTP požadavky a případný lokální download podle konkrétního vstupu.
- **Omezení a rizika:** Timeout, kvóty a chybné odpovědi; tajné hodnoty nepatří do logu. Testy používají mocky.

## app/services/api_http.py

- **Modul:** `app.services.api_http` — [zdroj](../../app/services/api_http.py).
- **Účel a odpovědnosti:** HTTP session, timeout a atomický streaming download.
- **Veřejné vstupy:** `get_entries(url, **options)`; `download_audio(url, destination, *, method='GET', **options)`.
- **Klíčové vstupy:** URL, HTTP volby a cílová cesta.
- **Výstupy:** Seznam hesel nebo potvrzený audio soubor.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.services.api_dictionary](../../app/services/api_dictionary.py), [app.services.api_speech](../../app/services/api_speech.py).
- **Oblasti práce:** síť.
- **Vedlejší účinky:** HTTP/SMTP požadavky a případný lokální download podle konkrétního vstupu.
- **Omezení a rizika:** Timeout, kvóty a chybné odpovědi; tajné hodnoty nepatří do logu. Testy používají mocky.

## app/services/api_speech.py

- **Modul:** `app.services.api_speech` — [zdroj](../../app/services/api_speech.py).
- **Účel a odpovědnosti:** Generování řeči podporovaným ElevenLabs hlasem.
- **Veřejné vstupy:** `generate_audio(i, frame, language, learning_by, *, settings_path=None)`.
- **Klíčové vstupy:** Řádek, cílový jazyk, vlastní jazyk a nastavení.
- **Výstupy:** Stažené MP3 a Audio=Automatic - 11Labs.
- **Přímé projektové závislosti:** [app.repositories.api_settings](../../app/repositories/api_settings.py), [app.services.api_http](../../app/services/api_http.py).
- **Staticky zjištění odběratelé:** [app.services.api](../../app/services/api.py).
- **Oblasti práce:** CSV/perzistence, síť, konfigurace.
- **Vedlejší účinky:** HTTP/SMTP požadavky a případný lokální download podle konkrétního vstupu.
- **Omezení a rizika:** Timeout, kvóty a chybné odpovědi; tajné hodnoty nepatří do logu. Testy používají mocky.

## app/services/backup.py

- **Modul:** `app.services.backup` — [zdroj](../../app/services/backup.py).
- **Účel a odpovědnosti:** Rozhodnutí o termínu a SMTP transport CSV příloh.
- **Veřejné vstupy:** `backup_due(recipient, period, next_backup, now=None)`; `send_backup(files_dir, recipient, username, password, translate, app_name)`.
- **Klíčové vstupy:** Příjemce, interval, termín, prostředí SMTP a soubory.
- **Výstupy:** Boolean odeslání nebo transportní výjimka.
- **Přímé projektové závislosti:** [app.repositories.courses](../../app/repositories/courses.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** CSV/perzistence, síť.
- **Vedlejší účinky:** HTTP/SMTP požadavky a případný lokální download podle konkrétního vstupu.
- **Omezení a rizika:** Timeout, kvóty a chybné odpovědi; tajné hodnoty nepatří do logu. Testy používají mocky.

## app/services/backup_background.py

- **Modul:** `app.services.backup_background` — [zdroj](../../app/services/backup_background.py).
- **Účel a odpovědnosti:** Koordinace jediné zálohy a prodlevy opakování.
- **Veřejné vstupy:** `BackupCoordinator` (metody `request`).
- **Klíčové vstupy:** Owner, identita konfigurace a send callback.
- **Výstupy:** Asynchronní požadavek a UI oznámení výsledku.
- **Přímé projektové závislosti:** [app.shared.background_task](../../app/shared/background_task.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/__init__.py

- **Modul:** `app.shared` — [zdroj](../../app/shared/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.shared.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.practise](../../app/grammar/practise.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.home.layout](../../app/home/layout.py), [app.main](../../app/main.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.statistics.charts](../../app/statistics/charts.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.statistics.window](../../app/statistics/window.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [app.vocabulary.practise_review](../../app/vocabulary/practise_review.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py), [start](../../start.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/shared/audio_effects.py

- **Modul:** `app.shared.audio_effects` — [zdroj](../../app/shared/audio_effects.py).
- **Účel a odpovědnosti:** Volitelné krátké UI efekty s vlastní hlasitostí a cache.
- **Veřejné vstupy:** `configure(enabled=True, volume=100)`; `play_effect(filename)`.
- **Klíčové vstupy:** Alias efektu, nastavení zvuků a dostupný mixer.
- **Výstupy:** Přehrání na UI kanálu nebo bezpečný fallback.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.practise](../../app/grammar/practise.py), [app.main](../../app/main.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_audio](../../app/vocabulary/practise_audio.py), [start](../../start.py).
- **Oblasti práce:** audio.
- **Vedlejší účinky:** Přístup k mixeru/mikrofonu nebo audio souborům dle účelu.
- **Omezení a rizika:** Zařízení může chybět; soubory a streamy mají vlastní životní cyklus. Viz AUDIO.

## app/shared/background_task.py

- **Modul:** `app.shared.background_task` — [zdroj](../../app/shared/background_task.py).
- **Účel a odpovědnosti:** Jeden daemon worker a polling výsledku/progressu v Tk.
- **Veřejné vstupy:** `BackgroundTask` (metody `start`, `cancel`, `close`); `check_cancelled(event)`.
- **Klíčové vstupy:** Owner, work a callbacky výsledku/chyby/průběhu.
- **Výstupy:** BackgroundTask s cancellation Event a omezenou výsledkovou frontou.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.services.backup_background](../../app/services/backup_background.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.editor_attributes](../../app/vocabulary/editor_attributes.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/config.py

- **Modul:** `app.shared.config` — [zdroj](../../app/shared/config.py).
- **Účel a odpovědnosti:** Výchozí parametry učení nezávislé na uživatelském formuláři.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Statické deklarace aplikace.
- **Výstupy:** Název, mapa intervalů, horizont a ideální PoS.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.shared.settings](../../app/shared/settings.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/diagnostics.py

- **Modul:** `app.shared.diagnostics` — [zdroj](../../app/shared/diagnostics.py).
- **Účel a odpovědnosti:** Diagnostika bez zpráv výjimek obsahujících tajné údaje.
- **Veřejné vstupy:** `report_error(error, *, operation, logger=None)`.
- **Klíčové vstupy:** Výjimka a bezpečný název operace.
- **Výstupy:** Log typu a umístění zásobníku bez lokálních hodnot.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.editor](../../app/grammar/editor.py), [app.repositories.grammar_filters](../../app/repositories/grammar_filters.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/learning_data.py

- **Modul:** `app.shared.learning_data` — [zdroj](../../app/shared/learning_data.py).
- **Účel a odpovědnosti:** Normalizace datových typů a počítání koncových S.
- **Veřejné vstupy:** `Count_trailing_s(value)`; `Set_datatypes(df, lang_desc, learned_by)`.
- **Klíčové vstupy:** Frame/jazyky nebo řetězec historie.
- **Výstupy:** Upravené typy v předaném frame nebo počet koncových S.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.conjugation.data](../../app/conjugation/data.py), [app.home.data](../../app/home/data.py), [app.repositories.grammar](../../app/repositories/grammar.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.statistics.data](../../app/statistics/data.py), [app.vocabulary.editor_data](../../app/vocabulary/editor_data.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/settings.py

- **Modul:** `app.shared.settings` — [zdroj](../../app/shared/settings.py).
- **Účel a odpovědnosti:** Zachovaná facade konfigurace, starých stylů a UI helperů.
- **Veřejné vstupy:** `T(val)`.
- **Klíčové vstupy:** Aktivní kontext a identifikátor zprávy pro T.
- **Výstupy:** Reexporty a lokalizovaný text.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.shared.config](../../app/shared/config.py), [app.ui.helpers](../../app/ui/helpers.py), [app.ui.legacy_styles](../../app/ui/legacy_styles.py), [app.ui.widgets](../../app/ui/widgets.py).
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.editor](../../app/grammar/editor.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.practise](../../app/grammar/practise.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.home.layout](../../app/home/layout.py), [app.main](../../app/main.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.statistics.charts](../../app/statistics/charts.py), [app.statistics.window](../../app/statistics/window.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [app.vocabulary.practise_review](../../app/vocabulary/practise_review.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py), [start](../../start.py).
- **Oblasti práce:** konfigurace.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/shared/storage.py

- **Modul:** `app.shared.storage` — [zdroj](../../app/shared/storage.py).
- **Účel a odpovědnosti:** Hash revize a atomické publikování CSV pod zámkem cíle.
- **Veřejné vstupy:** `file_revision(path: str | os.PathLike)`; `FileChangedError`; `destination_lock(path: str | os.PathLike)`; `save_csv(frame, destination, *, expected_revision=None, expect_missing=False, **options)`.
- **Klíčové vstupy:** Frame, cesta, očekávaná revize/existence a CSV volby.
- **Výstupy:** Bezpečný commit nebo výjimka se zachovaným původním souborem.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.repositories.conjugation](../../app/repositories/conjugation.py), [app.repositories.courses](../../app/repositories/courses.py), [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.repositories.grammar](../../app/repositories/grammar.py), [app.repositories.grammar_filters](../../app/repositories/grammar_filters.py), [app.repositories.grammar_theory](../../app/repositories/grammar_theory.py), [app.repositories.preferences](../../app/repositories/preferences.py), [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Podle volaného vstupu čtení nebo revizně chráněná změna lokálních souborů; API settings pouze čte konfiguraci a přesměruje audio cestu.
- **Omezení a rizika:** Dodržet smlouvu původního snapshotu/revize, nepřepisovat cizí změny; přesné formáty v DATA_STORAGE.

## app/shared/translations.py

- **Modul:** `app.shared.translations` — [zdroj](../../app/shared/translations.py).
- **Účel a odpovědnosti:** Cache katalogů a překlad se záložní angličtinou.
- **Veřejné vstupy:** `get_catalog(language='English')`; `translate(message_id, language='English')`.
- **Klíčové vstupy:** ID zprávy a jazyk nebo kód jazyka.
- **Výstupy:** Řetězec překladu a read-only mapové pohledy.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py).
- **Staticky zjištění odběratelé:** [app.core.context](../../app/core/context.py), [app.main](../../app/main.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/statistics/__init__.py

- **Modul:** `app.statistics` — [zdroj](../../app/statistics/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.statistics.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/statistics/background.py

- **Modul:** `app.statistics.background` — [zdroj](../../app/statistics/background.py).
- **Účel a odpovědnosti:** Scroll-stabilní dlaždice pozadí a panely statistik.
- **Veřejné vstupy:** `ScrollSurface` (metody `refresh`, `region`); `StatisticsBackdrop` (metody `add_panel`, `request`, `paint`, `close`).
- **Klíčové vstupy:** Scroller a existující backdrop.
- **Výstupy:** Opakované pixely bez přepočítávání při samotném scrollu.
- **Přímé projektové závislosti:** [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/cache.py

- **Modul:** `app.statistics.cache` — [zdroj](../../app/statistics/cache.py).
- **Účel a odpovědnosti:** Omezená thread-safe cache statistik s kontrolou zdroje.
- **Veřejné vstupy:** `StatisticsCache` (metody `get`).
- **Klíčové vstupy:** Cesta, namespace, volby a výpočetní callback.
- **Výstupy:** Nezávislá kopie výsledku; nejvýše jedno opakování čtení.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.statistics.data](../../app/statistics/data.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/statistics/chart_style.py

- **Modul:** `app.statistics.chart_style` — [zdroj](../../app/statistics/chart_style.py).
- **Účel a odpovědnosti:** Barevné styly a sazba statistických figur.
- **Veřejné vstupy:** `style_chart(fig, ax, name, title, label_size)`.
- **Klíčové vstupy:** Figura, axes, identifikátor grafu a překlad titulku.
- **Výstupy:** Nastavené pozadí, fonty, popisky a layout.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.statistics.charts](../../app/statistics/charts.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/statistics/charts.py

Aktualizace vykreslování: _HoverBlit vlastní cache pixelů a draw/resize
callbacky. Prognóza používá lineární numpy.interp, bez SciPy. Vstupy a veřejný
Generate_chart zůstávají zachované; mění se pouze spojnice prognózy a způsob
aktualizace hoveru. Viz [STATISTICS](STATISTICS.md).

- **Modul:** `app.statistics.charts` — [zdroj](../../app/statistics/charts.py).
- **Účel a odpovědnosti:** Vykreslení všech typů grafů, hover a odstranění figur.
- **Veřejné vstupy:** `Generate_chart(data, chart_frm, name, chart_row)`.
- **Klíčové vstupy:** Series/tabulky, cílový frame, typ grafu a grid řádek.
- **Výstupy:** FigureCanvas a jeho vlastněné callbacky.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.statistics.chart_style](../../app/statistics/chart_style.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/components.py

- **Modul:** `app.statistics.components` — [zdroj](../../app/statistics/components.py).
- **Účel a odpovědnosti:** Společné souhrnné karty, metriky a vyhlazené koláče.
- **Veřejné vstupy:** `ring_image(diameter, line, surface, accent, rate=None)`; `SuccessRing` (metody `configure`); `arrange_success_ring(ring, caption)`; `summary_metrics(parent, captions, *, first_row=0)`; `summary_cards(parent, titles)`; `style_summary_cards(interiors)`.
- **Klíčové vstupy:** Parent, titulky, hodnoty a míra úspěšnosti.
- **Výstupy:** Widgety karet a supersamplovaný bitmapový prstenec.
- **Přímé projektové závislosti:** [app.ui.legacy_styles](../../app/ui/legacy_styles.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/data.py

- **Modul:** `app.statistics.data` — [zdroj](../../app/statistics/data.py).
- **Účel a odpovědnosti:** Čisté agregace a příprava všech dat pro jazyk.
- **Veřejné vstupy:** `prepare_statistics(files, learned_by, language, horizon, gaps, default_wait, pos_types, pos_ideal)`; `simulate_reps_per_day(frame, horizon, gaps, default_wait, today=None)`; `vocabulary_statistics(path, language, learned_by, horizon, gaps, default_wait, pos_types, pos_ideal, today=None)`; `training_statistics(path, kind)`.
- **Klíčové vstupy:** Cesty, jazyky, horizont, intervaly, PoS a datum.
- **Výstupy:** Souhrny, tabulka, forecast, růst, kategorie a obtížná slova.
- **Přímé projektové závislosti:** [app.repositories.csv_store](../../app/repositories/csv_store.py), [app.shared.learning_data](../../app/shared/learning_data.py), [app.statistics.cache](../../app/statistics/cache.py), [app.statistics.difficult_words](../../app/statistics/difficult_words.py), [app.statistics.grammar_categories](../../app/statistics/grammar_categories.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/statistics/difficult_words.py

- **Modul:** `app.statistics.difficult_words` — [zdroj](../../app/statistics/difficult_words.py).
- **Účel a odpovědnosti:** Výběr slabších slov podle nedávných výsledků a jejich panel.
- **Veřejné vstupy:** `DifficultWord` (metody `errors`); `difficult_words(frame, language, learned_by, limit=6)`; `DifficultWordsPanel` (metody `set_data`, `set_items`).
- **Klíčové vstupy:** Slova s historií, jazykové sloupce a limit.
- **Výstupy:** Nejvýše šest kandidátů a počet všech kandidátů.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.statistics.data](../../app/statistics/data.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/grammar_categories.py

- **Modul:** `app.statistics.grammar_categories` — [zdroj](../../app/statistics/grammar_categories.py).
- **Účel a odpovědnosti:** Agregace výsledků témat a kompaktní porovnávací panel s číselným řazením.
- **Veřejné vstupy:** `GrammarCategory` (metody `attempts`, `accuracy`); `grammar_categories(frame)`; `order_categories(items, key='accuracy', descending=False)`; `GrammarCategoriesPanel` (metody `set_data`, `set_items`, `sort`).
- **Klíčové vstupy:** Frame s R/category nebo hotové GrammarCategory.
- **Výstupy:** Seřazené kategorie, coverage/accuracy, počty výsledků a akce procvičit; sort přesouvá existující řádky a nemění zdrojová data.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py), [app.ui.module_style](../../app/ui/module_style.py).
- **Staticky zjištění odběratelé:** [app.statistics.data](../../app/statistics/data.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/table.py

- **Modul:** `app.statistics.table` — [zdroj](../../app/statistics/table.py).
- **Účel a odpovědnosti:** Zobrazení filtrovatelné statistické tabulky.
- **Veřejné vstupy:** `StatisticsTable` (metody `set_data`, `sort`, `refresh`).
- **Klíčové vstupy:** Parent, překladač a agregovaný DataFrame.
- **Výstupy:** Tabulka statistik bez změn zdrojových CSV.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/tabs.py

- **Modul:** `app.statistics.tabs` — [zdroj](../../app/statistics/tabs.py).
- **Účel a odpovědnosti:** Přepínání částí statistik a dostupnosti časování.
- **Veřejné vstupy:** `StatisticsTabs` (metody `set_conjugation_available`, `select`).
- **Klíčové vstupy:** Parent, překladač a scroll-to-top callback.
- **Výstupy:** Panely Vocabulary/Grammar/Conjugation.
- **Přímé projektové závislosti:** [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/viewer.py

- **Modul:** `app.statistics.viewer` — [zdroj](../../app/statistics/viewer.py).
- **Účel a odpovědnosti:** Instanční řízení statistik a vykreslení připravených dat.
- **Veřejné vstupy:** `Stats(app, *, context=None)`; `StatisticsController` (metody `build`, `load`, `close`).
- **Klíčové vstupy:** Root/StatisticsWindow, AppContext a jazyk.
- **Výstupy:** StatisticsController, všechny připravené grafy a navigace do gramatiky.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.grammar.practise](../../app/grammar/practise.py), [app.shared](../../app/shared/__init__.py), [app.shared.background_task](../../app/shared/background_task.py), [app.shared.config](../../app/shared/config.py), [app.statistics.background](../../app/statistics/background.py), [app.statistics.charts](../../app/statistics/charts.py), [app.statistics.components](../../app/statistics/components.py), [app.statistics.data](../../app/statistics/data.py), [app.statistics.difficult_words](../../app/statistics/difficult_words.py), [app.statistics.grammar_categories](../../app/statistics/grammar_categories.py), [app.statistics.table](../../app/statistics/table.py), [app.statistics.tabs](../../app/statistics/tabs.py), [app.statistics.window](../../app/statistics/window.py), [app.ui.brand](../../app/ui/brand.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.helpers](../../app/ui/helpers.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py), [app.ui.widgets](../../app/ui/widgets.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/statistics/window.py

- **Modul:** `app.statistics.window` — [zdroj](../../app/statistics/window.py).
- **Účel a odpovědnosti:** Loading cover, fronta posledního přepnutí a cleanup okna.
- **Veřejné vstupy:** `StatisticsWindow` (metody `begin`, `load`, `complete`, `fail`, `destroy`).
- **Klíčové vstupy:** Owner a builder callback se synchronním či deferred výsledkem.
- **Výstupy:** Ready okno, bezpečné zavření nebo chybové oznámení.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/__init__.py

- **Modul:** `app.ui` — [zdroj](../../app/ui/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.ui.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.practise](../../app/grammar/practise.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/ui/answer_keys.py

- **Modul:** `app.ui.answer_keys` — [zdroj](../../app/ui/answer_keys.py).
- **Účel a odpovědnosti:** Převod kláves/numpadu na index odpovědi a kontrola modifierů.
- **Veřejné vstupy:** `has_answer_modifier(event)`; `answer_index(event)`.
- **Klíčové vstupy:** Tk event.
- **Výstupy:** Index 0–3 nebo žádná volba; seznam podporovaných sekvencí.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.grammar.practise](../../app/grammar/practise.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/ui/bindings.py

- **Modul:** `app.ui.bindings` — [zdroj](../../app/ui/bindings.py).
- **Účel a odpovědnosti:** Screen-owned připojení a odstranění klávesových callbacků.
- **Veřejné vstupy:** `ScreenBindings` (metody `bind`, `unbind`, `close`).
- **Klíčové vstupy:** Root, screen a mapa sekvencí.
- **Výstupy:** Tokeny vazeb, bezpečné unbind pouze vlastních callbacků.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.core.screen_controller](../../app/core/screen_controller.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/brand.py

- **Modul:** `app.ui.brand` — [zdroj](../../app/ui/brand.py).
- **Účel a odpovědnosti:** Jednotné logo a ikona oken.
- **Veřejné vstupy:** `logo_image(size=72)`; `set_window_icon(window)`.
- **Klíčové vstupy:** Požadovaná velikost nebo cílové okno.
- **Výstupy:** CTkImage loga ze sdílených pixelů a nastavená ikona.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py).
- **Staticky zjištění odběratelé:** [app.home.layout](../../app/home/layout.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [start](../../start.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/__init__.py

- **Modul:** `app.ui.components` — [zdroj](../../app/ui/components/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.ui.components.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/ui/components/app_dialog.py

- **Modul:** `app.ui.components.app_dialog` — [zdroj](../../app/ui/components/app_dialog.py).
- **Účel a odpovědnosti:** Základ pomocného okna s vlastnictvím, centeringem a jobs.
- **Veřejné vstupy:** `AppDialog` (metody `after`, `after_cancel`, `present`, `focus_set`, `apply_background`, `make_background`, `add_heading`, `add_actions`, `destroy`).
- **Klíčové vstupy:** Owner, volby CTk, heading a akce.
- **Výstupy:** AppDialog spravovaný životním cyklem screenu.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.ui.brand](../../app/ui/brand.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py).
- **Oblasti práce:** GUI, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/editor_toolbar.py

- **Modul:** `app.ui.components.editor_toolbar` — [zdroj](../../app/ui/components/editor_toolbar.py).
- **Účel a odpovědnosti:** Spodní editorová lišta počtů, zkratek a nástrojů.
- **Veřejné vstupy:** `EditorToolbar` (metody `add_action`, `set_help`, `attach_background`).
- **Klíčové vstupy:** Parent, texty a modulové akce.
- **Výstupy:** EditorToolbar s přizpůsobenými popisy.
- **Přímé projektové závislosti:** [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/filter_option_menu.py

- **Modul:** `app.ui.components.filter_option_menu` — [zdroj](../../app/ui/components/filter_option_menu.py).
- **Účel a odpovědnosti:** Souvisle vykreslené šipky filtrů a zakulacené volby.
- **Veřejné vstupy:** `FilterOptionMenu`.
- **Klíčové vstupy:** Parent, hodnoty, proměnná a caption.
- **Výstupy:** FilterOptionMenu bez přerušeného podkladu šipky.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/module_header.py

- **Modul:** `app.ui.components.module_header` — [zdroj](../../app/ui/components/module_header.py).
- **Účel a odpovědnosti:** Jednotné hlavní záhlaví s logem a standardními akcemi.
- **Veřejné vstupy:** `ModuleHeader` (metody `add_action`, `set_detail`, `place_extension`, `grid_standard`, `attach_background`, `refresh_action`).
- **Klíčové vstupy:** Parent, titulek, překladač, akce a rozšíření.
- **Výstupy:** Header s tlačítky Save/Close/Exit a místem pro filtr.
- **Přímé projektové závislosti:** [app.ui.brand](../../app/ui/brand.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/save_progress.py

- **Modul:** `app.ui.components.save_progress` — [zdroj](../../app/ui/components/save_progress.py).
- **Účel a odpovědnosti:** Průběh asynchronního uložení s počtem zbývajících slov.
- **Veřejné vstupy:** `SaveProgress` (metody `update_progress`).
- **Klíčové vstupy:** Parent, překladač, completed a total.
- **Výstupy:** Karta průběhu bez blokujícího čekání.
- **Přímé projektové závislosti:** [app.ui.module_style](../../app/ui/module_style.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/search_filter_panel.py

- **Modul:** `app.ui.components.search_filter_panel` — [zdroj](../../app/ui/components/search_filter_panel.py).
- **Účel a odpovědnosti:** Kontejner hledání a filtrů se společným vzhledem.
- **Veřejné vstupy:** `SearchEntry` (metody `read_value`, `destroy`); `SearchFilterPanel` (metody `add_choice`).
- **Klíčové vstupy:** Parent a rozmístěné ovládací prvky.
- **Výstupy:** SearchFilterPanel s jednotnými okraji.
- **Přímé projektové závislosti:** [app.ui.components.filter_option_menu](../../app/ui/components/filter_option_menu.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.vocabulary.editor_filter](../../app/vocabulary/editor_filter.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/session_panel.py

- **Modul:** `app.ui.components.session_panel` — [zdroj](../../app/ui/components/session_panel.py).
- **Účel a odpovědnosti:** Společný obsah session a počitadlo/progress.
- **Veřejné vstupy:** `SessionPanel` (metody `set_progress`, `add_action`, `add_shortcuts`).
- **Klíčové vstupy:** Parent, překladač, průběh a akční callbacky.
- **Výstupy:** SessionPanel a nápověda z jednotného katalogu.
- **Přímé projektové závislosti:** [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.grammar.layout](../../app/grammar/layout.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/shortcut_hint.py

- **Modul:** `app.ui.components.shortcut_hint` — [zdroj](../../app/ui/components/shortcut_hint.py).
- **Účel a odpovědnosti:** Jednotná nápověda s lomem celých položek.
- **Veřejné vstupy:** `ShortcutHint`.
- **Klíčové vstupy:** Sekce zkratek, překladač, režim a šířka.
- **Výstupy:** Label s horizontálním či vertikálním soupisem.
- **Přímé projektové závislosti:** [app.about.shortcuts](../../app/about/shortcuts.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.components.session_panel](../../app/ui/components/session_panel.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/components/synonym_summary.py

- **Modul:** `app.ui.components.synonym_summary` — [zdroj](../../app/ui/components/synonym_summary.py).
- **Účel a odpovědnosti:** Kompaktní adaptivní souhrn vazeb se zvýrazněným cizím slovem.
- **Veřejné vstupy:** `SynonymSummary` (metody `set_text`).
- **Klíčové vstupy:** Parent a textové řádky synonym.
- **Výstupy:** Přizpůsobený souhrn bez zbytečné prázdné karty.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/fitted_text.py

- **Modul:** `app.ui.fitted_text` — [zdroj](../../app/ui/fitted_text.py).
- **Účel a odpovědnosti:** Přizpůsobování delšího textu dostupnému prostoru.
- **Veřejné vstupy:** `fit_question_prompt(label, card)`.
- **Klíčové vstupy:** Textové widgety a geometrie.
- **Výstupy:** Upravený font/wrap při zachování čitelnosti.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/helpers.py

- **Modul:** `app.ui.helpers` — [zdroj](../../app/ui/helpers.py).
- **Účel a odpovědnosti:** Pomocné grid poměry a řízené odstranění starých screenů/oken.
- **Veřejné vstupy:** `Grid_ratio(frame, weight_row, weight_column)`; `Clear_frames(app)`; `Clear_tops(app)`.
- **Klíčové vstupy:** Parent a poměry nebo root.
- **Výstupy:** Konfigurace gridu či zničení existujících potomků.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.shared.settings](../../app/shared/settings.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/learning_layout.py

- **Modul:** `app.ui.learning_layout` — [zdroj](../../app/ui/learning_layout.py).
- **Účel a odpovědnosti:** Podklady výukových oken, reset cache resize a základní styly.
- **Veřejné vstupy:** `background(frame, filename='practice_warm_v4.png')`; `label(widget, size=21, color=TEXT, bold=False)`; `button(widget, accent=TEAL, secondary=False)`; `entry(widget)`; `card(frame, color=SURFACE)`.
- **Klíčové vstupy:** Parent, název obrázku nebo existující widget.
- **Výstupy:** Backdrop label a stylované label/button/entry/card.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.practise](../../app/grammar/practise.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.home.layout](../../app/home/layout.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/learning_review.py

- **Modul:** `app.ui.learning_review` — [zdroj](../../app/ui/learning_review.py).
- **Účel a odpovědnosti:** Společný scrollovatelný review dialog slov/sloves/otázek.
- **Veřejné vstupy:** `ReviewDialog` (metody `destroy`); `open_verb_review(owner, verb, persons)`.
- **Klíčové vstupy:** Owner, heading, subtitle, detaily a akce.
- **Výstupy:** Dialog s vynechanými prázdnými detaily a fitted popisy.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.conjugation.practise](../../app/conjugation/practise.py), [app.grammar.practise](../../app/grammar/practise.py), [app.vocabulary.practise_review](../../app/vocabulary/practise_review.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/legacy_styles.py

- **Modul:** `app.ui.legacy_styles` — [zdroj](../../app/ui/legacy_styles.py).
- **Účel a odpovědnosti:** Původní konfigurační slovníky stále používaných widgetů.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Statické fonty/barvy a pomocný konstruktor stylu.
- **Výstupy:** Reexportované legacy sety; nejde o nevyužitý soubor.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.shared.settings](../../app/shared/settings.py), [app.statistics.components](../../app/statistics/components.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/module_style.py

- **Modul:** `app.ui.module_style` — [zdroj](../../app/ui/module_style.py).
- **Účel a odpovědnosti:** Sdílená pravidla headerů, session, akcí a dialogů.
- **Veřejné vstupy:** `header_button(button)`; `dialog_button(button)`; `dialog_actions(parent, buttons, row=0, pady=(4, 4))`; `session_content(frame)`; `choice_button(button)`; `tool_button(button)`; `primary_action(button, column, row=0)`; `dialog_background(window, filename)`.
- **Klíčové vstupy:** CTk widgety a akční seznamy.
- **Výstupy:** Jednotné rozměry, barvy, caption fitting a rozložení.
- **Přímé projektové závislosti:** [app.ui](../../app/ui/__init__.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.layout](../../app/grammar/layout.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.components.save_progress](../../app/ui/components/save_progress.py), [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py), [app.ui.components.session_panel](../../app/ui/components/session_panel.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/sections.py

- **Modul:** `app.ui.sections` — [zdroj](../../app/ui/sections.py).
- **Účel a odpovědnosti:** Sdílené záložky a průhlednost jejich panelů.
- **Veřejné vstupy:** `SectionTabs` (metody `enable_transparent_panels`).
- **Klíčové vstupy:** Parent a seznam částí.
- **Výstupy:** SectionTabs se zachovaným aktuálním výběrem.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.preferences.dialog](../../app/preferences/dialog.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/surfaces.py

- **Modul:** `app.ui.surfaces` — [zdroj](../../app/ui/surfaces.py).
- **Účel a odpovědnosti:** Skládání podkladu kolem zakulacených widgetů.
- **Veřejné vstupy:** `BackdropSurface` (metody `refresh`, `region`); `PanelSurface` (metody `request`, `paint`, `region`, `close`); `surface(widget, parent, filename=None, wash=0.65)`.
- **Klíčové vstupy:** Widget, poskytovatel pixelů a případný obrazový wash.
- **Výstupy:** BackdropSurface/PanelSurface s omezeným překreslováním.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py).
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.conjugation.layout](../../app/conjugation/layout.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py), [app.grammar.theory_window](../../app/grammar/theory_window.py), [app.home.layout](../../app/home/layout.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.statistics.background](../../app/statistics/background.py), [app.statistics.tabs](../../app/statistics/tabs.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.learning_review](../../app/ui/learning_review.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.training_layout](../../app/ui/training_layout.py), [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/theme.py

- **Modul:** `app.ui.theme` — [zdroj](../../app/ui/theme.py).
- **Účel a odpovědnosti:** Základní paleta, fonty a styling titulku statistik.
- **Veřejné vstupy:** `style_statistics(table_title)`.
- **Klíčové vstupy:** Statické hodnoty nebo title widget.
- **Výstupy:** Konstanty vzhledu a upravený titulek.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.about.dialog](../../app/about/dialog.py), [app.grammar.category_filter](../../app/grammar/category_filter.py), [app.home.layout](../../app/home/layout.py), [app.preferences.dialog](../../app/preferences/dialog.py), [app.statistics.components](../../app/statistics/components.py), [app.statistics.difficult_words](../../app/statistics/difficult_words.py), [app.statistics.grammar_categories](../../app/statistics/grammar_categories.py), [app.statistics.table](../../app/statistics/table.py), [app.statistics.tabs](../../app/statistics/tabs.py), [app.statistics.viewer](../../app/statistics/viewer.py), [app.statistics.window](../../app/statistics/window.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.components.save_progress](../../app/ui/components/save_progress.py), [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py), [app.ui.components.session_panel](../../app/ui/components/session_panel.py), [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.components.synonym_summary](../../app/ui/components/synonym_summary.py), [app.ui.fitted_text](../../app/ui/fitted_text.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.legacy_styles](../../app/ui/legacy_styles.py), [app.ui.sections](../../app/ui/sections.py), [app.ui.widgets](../../app/ui/widgets.py), [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/ui/training_layout.py

- **Modul:** `app.ui.training_layout` — [zdroj](../../app/ui/training_layout.py).
- **Účel a odpovědnosti:** Společné rozložení gramatiky/časování a akčních řádků.
- **Veřejné vstupy:** `shell(app, title, image, actions)`; `text(parent, value='', size=20, bold=False, color=ui.TEXT)`; `action(parent, title, command, accent, secondary=False)`.
- **Klíčové vstupy:** Root, titulek a callbacky akcí.
- **Výstupy:** Frame sestava používaná výukovými layouty.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.conjugation.layout](../../app/conjugation/layout.py), [app.grammar.editor_layout](../../app/grammar/editor_layout.py), [app.grammar.layout](../../app/grammar/layout.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/ui/widgets.py

- **Modul:** `app.ui.widgets` — [zdroj](../../app/ui/widgets.py).
- **Účel a odpovědnosti:** Scrollovací statistický viewport se scoped kolečkem myši.
- **Veřejné vstupy:** `VerticalScrolledFrame_class` (metody `configure_interior`, `configure_canvas`, `on_mousewheel`, `destroy`).
- **Klíčové vstupy:** Tk parent a geometrie obsahu.
- **Výstupy:** Canvas/interior/scrollbar a jejich cleanup.
- **Přímé projektové závislosti:** [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.shared.settings](../../app/shared/settings.py), [app.statistics.viewer](../../app/statistics/viewer.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/__init__.py

- **Modul:** `app.vocabulary` — [zdroj](../../app/vocabulary/__init__.py).
- **Účel a odpovědnosti:** Značka a stručný popis balíčku app.vocabulary.
- **Veřejné vstupy:** Konstanty/reexporty nebo značka balíčku; žádný vlastní veřejný konstruktor operace.
- **Klíčové vstupy:** Import balíčku Pythonem.
- **Výstupy:** Namespace; žádná vlastní pracovní operace.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Žádné vlastní datové ani GUI operace.
- **Omezení a rizika:** Neodstraňovat pouze kvůli absenci funkcí: definuje balíček.

## app/vocabulary/editor.py

- **Modul:** `app.vocabulary.editor` — [zdroj](../../app/vocabulary/editor.py).
- **Účel a odpovědnosti:** Kontrolér tabulkové editace, filtrů, řazení a asynchronního save.
- **Veřejné vstupy:** `EditorController` (metody `Delete_audio`, `Delete_words`, `Open_synonyms`, `Exit`, `Filter`, `Sort`, `Refresh`, `Unsort`, `Sync_changes`, `New_row`, `Cancel`, `Trace_multi_paste`, `Save`, `Load`, `Record_audio`, `Play_audio`); `Edit(app, lang, *, context=None)`.
- **Klíčové vstupy:** Root, jazyk a AppContext.
- **Výstupy:** Obrazovka editoru, pracovní frame a řízené uložení.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.background_task](../../app/shared/background_task.py), [app.shared.diagnostics](../../app/shared/diagnostics.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.components.save_progress](../../app/ui/components/save_progress.py), [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py), [app.vocabulary.editor_data](../../app/vocabulary/editor_data.py), [app.vocabulary.editor_filter](../../app/vocabulary/editor_filter.py), [app.vocabulary.editor_layout](../../app/vocabulary/editor_layout.py), [app.vocabulary.editor_localization](../../app/vocabulary/editor_localization.py), [app.vocabulary.editor_synonym_columns](../../app/vocabulary/editor_synonym_columns.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.id_sequence](../../app/vocabulary/id_sequence.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, CSV/perzistence, audio, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/editor_attributes.py

- **Modul:** `app.vocabulary.editor_attributes` — [zdroj](../../app/vocabulary/editor_attributes.py).
- **Účel a odpovědnosti:** Orchestrace providerů pro chybějící údaje a pravidla audio cleanup.
- **Veřejné vstupy:** `enrich_attributes(main_df, lang_desc, audio_folder, *, progress=None, cancelled=None, cleanup=True, context=None)`; `clean_audio_files(main_df, i, audio_folder, *, destructive=True)`.
- **Klíčové vstupy:** Pracovní frame, staging složka, progress, cancellation a kontext.
- **Výstupy:** Obohacený frame bez změn ručního PoS.
- **Přímé projektové závislosti:** [app.services](../../app/services/__init__.py), [app.services.api](../../app/services/api.py), [app.shared.background_task](../../app/shared/background_task.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_audio.py

- **Modul:** `app.vocabulary.editor_audio` — [zdroj](../../app/vocabulary/editor_audio.py).
- **Účel a odpovědnosti:** Nahrávací/přehrávací dialog s workerem mikrofonu.
- **Veřejné vstupy:** `AudioRecorderPlayer` (metody `Start_rec`, `Record_audio`, `Stop_rec`, `Cancel_rec`, `Next`, `Play_rec`).
- **Klíčové vstupy:** Dialog, označené slovo, tabulka, frame a audio složka.
- **Výstupy:** Nahrávka, aktualizovaná buňka Own a stav dialogu.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py), [app.vocabulary.editor_recording](../../app/vocabulary/editor_recording.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** GUI, audio.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/editor_data.py

- **Modul:** `app.vocabulary.editor_data` — [zdroj](../../app/vocabulary/editor_data.py).
- **Účel a odpovědnosti:** Čisté slučování tabulky, filtr, řazení a příprava metadat.
- **Veřejné vstupy:** `merge_table_edits(source, rows, headers, language, learned_by)`; `filter_vocabulary(frame, column, operator, query)`; `sort_vocabulary(frame, column, descending=False)`; `prepare_save(edited, previous, now=None)`.
- **Klíčové vstupy:** Frame, řádky, kanonické hlavičky a původní dokument.
- **Výstupy:** Sloučené/filtrované/seřazené frame nebo připravený výsledek.
- **Přímé projektové závislosti:** [app.shared.learning_data](../../app/shared/learning_data.py), [app.vocabulary.synonyms](../../app/vocabulary/synonyms.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.save_workflow](../../app/vocabulary/save_workflow.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_filter.py

- **Modul:** `app.vocabulary.editor_filter` — [zdroj](../../app/vocabulary/editor_filter.py).
- **Účel a odpovědnosti:** Řádek volby sloupce, operátoru a hledané hodnoty.
- **Veřejné vstupy:** `VocabularyFilter`.
- **Klíčové vstupy:** Tk proměnné, překlady a callback filter/refresh.
- **Výstupy:** VocabularyFilter s komponentami formuláře.
- **Přímé projektové závislosti:** [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_layout.py

- **Modul:** `app.vocabulary.editor_layout` — [zdroj](../../app/vocabulary/editor_layout.py).
- **Účel a odpovědnosti:** Uspořádání editoru a parametrů tabulky/dropdownů.
- **Veřejné vstupy:** `sheet_options(original)`; `arrange_editor(editor, header, body, filters, table, widgets)`; `restore_after_save_error(save, back, filters)`; `fit_editor_columns(table, headers, language, learned_by)`; `configure_editor_dropdowns(table, definitions)`; `color_editor_columns(table, headers, language, learned_by)`.
- **Klíčové vstupy:** Widgety editoru, hlavičky a callbacky.
- **Výstupy:** Nastavený layout, šířky a vzhled tabulky.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.components.editor_toolbar](../../app/ui/components/editor_toolbar.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.ui.theme](../../app/ui/theme.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_localization.py

- **Modul:** `app.vocabulary.editor_localization` — [zdroj](../../app/vocabulary/editor_localization.py).
- **Účel a odpovědnosti:** Bezeztrátové mapování uložených výčtů do UI a zpět.
- **Veřejné vstupy:** `display_frame(frame, translate)`; `canonical_rows(rows, headers, translate)`.
- **Klíčové vstupy:** Frame nebo řádky s Audio/PoS a překladač.
- **Výstupy:** Zobrazované frame nebo kanonické řádky.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_recording.py

- **Modul:** `app.vocabulary.editor_recording` — [zdroj](../../app/vocabulary/editor_recording.py).
- **Účel a odpovědnosti:** Zachycení mikrofonu do atomicky nahrazeného WAV.
- **Veřejné vstupy:** `record_wave(destination, stop_event)`.
- **Klíčové vstupy:** Cílový soubor a stop Event.
- **Výstupy:** Dokončený WAV; uzavřený stream a zařízení i při chybě.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_audio](../../app/vocabulary/editor_audio.py).
- **Oblasti práce:** audio.
- **Vedlejší účinky:** Přístup k mixeru/mikrofonu nebo audio souborům dle účelu.
- **Omezení a rizika:** Zařízení může chybět; soubory a streamy mají vlastní životní cyklus. Viz AUDIO.

## app/vocabulary/editor_synonym_columns.py

- **Modul:** `app.vocabulary.editor_synonym_columns` — [zdroj](../../app/vocabulary/editor_synonym_columns.py).
- **Účel a odpovědnosti:** Počítané indikátory synonym a editorová cache počtů.
- **Veřejné vstupy:** `SynonymCounts` (metody `get`); `add_columns(frame, course, cache=None)`.
- **Klíčové vstupy:** Frame, cesta kurzu a volitelný SynonymCounts.
- **Výstupy:** Frame s Has synonyms/Synonym count bez změny CSV schématu.
- **Přímé projektové závislosti:** [app.repositories](../../app/repositories/__init__.py), [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.vocabulary.synonyms](../../app/vocabulary/synonyms.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** CSV/perzistence.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/editor_synonyms.py

- **Modul:** `app.vocabulary.editor_synonyms` — [zdroj](../../app/vocabulary/editor_synonyms.py).
- **Účel a odpovědnosti:** Dialog editace vazeb a hledání slov/překladů.
- **Veřejné vstupy:** `SynonymsDialog` (metody `render`, `navigate`, `save`).
- **Klíčové vstupy:** Owner, kurz, ID, jazyky a omezení odhalení odpovědi.
- **Výstupy:** Výběr vazeb; samostatný revizně chráněný save.
- **Přímé projektové závislosti:** [app.repositories](../../app/repositories/__init__.py), [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.app_dialog](../../app/ui/components/app_dialog.py), [app.ui.components.search_filter_panel](../../app/ui/components/search_filter_panel.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.vocabulary.practise_data](../../app/vocabulary/practise_data.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py), [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** GUI, CSV/perzistence.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/id_sequence.py

- **Modul:** `app.vocabulary.id_sequence` — [zdroj](../../app/vocabulary/id_sequence.py).
- **Účel a odpovědnosti:** Přidělení následujícího stabilního ID.
- **Veřejné vstupy:** `next_word_id(course, frame)`.
- **Klíčové vstupy:** Kurz a aktuální frame.
- **Výstupy:** Maximální zbývající ID + 1 nebo 1.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/practise.py

- **Modul:** `app.vocabulary.practise` — [zdroj](../../app/vocabulary/practise.py).
- **Účel a odpovědnosti:** Kontrolér překladu, kontextu a poslechu s review a synonymy.
- **Veřejné vstupy:** `PracticeController` (metody `synonym_text`, `Show_synonyms`, `Synonym_shortcut`, `Answer_key`, `Exit`, `Back`, `Review_w`, `Edit_review_attribute`, `Edit_current_synonyms`, `Edit_review_synonyms`, `Review_w_end`, `Del_desc`, `Del_sentence_example`, `Del_audio`, `Save_rep`, `Conf_resp`, `Show_w_next`, `Skip_resp`, `Skip_shortcut`, `Choice_shortcut`, `Auto_audio`, `Play_audio`, `Resp_change`, `New_repeat`, `Play_btn_ability`); `Rep(app_input, repeat_df_input, lang, lang_ord_desc, *, context=None)`.
- **Klíčové vstupy:** Root, dávka slov, jazyk, pořadí jazyka a kontext.
- **Výstupy:** Výuková obrazovka, session a odložené uložení delty.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.core.screen_controller](../../app/core/screen_controller.py), [app.repositories](../../app/repositories/__init__.py), [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.diagnostics](../../app/shared/diagnostics.py), [app.shared.learning_data](../../app/shared/learning_data.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.answer_keys](../../app/ui/answer_keys.py), [app.ui.components.module_header](../../app/ui/components/module_header.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py), [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise_audio](../../app/vocabulary/practise_audio.py), [app.vocabulary.practise_data](../../app/vocabulary/practise_data.py), [app.vocabulary.practise_layout](../../app/vocabulary/practise_layout.py), [app.vocabulary.practise_review](../../app/vocabulary/practise_review.py), [app.vocabulary.practise_review_editor](../../app/vocabulary/practise_review_editor.py), [app.vocabulary.practise_session](../../app/vocabulary/practise_session.py).
- **Staticky zjištění odběratelé:** [app.main](../../app/main.py).
- **Oblasti práce:** GUI, CSV/perzistence, audio, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/practise_audio.py

- **Modul:** `app.vocabulary.practise_audio` — [zdroj](../../app/vocabulary/practise_audio.py).
- **Účel a odpovědnosti:** Cesty a přehrání/mazání výslovnosti jednoho slova.
- **Veřejné vstupy:** `PracticeAudio` (metody `paths`, `available`, `play`, `delete`).
- **Klíčové vstupy:** ID, jazykový pár, složka a volitelný fallback.
- **Výstupy:** MP3/WAV cesty, přehrání nebo odstranění audia.
- **Přímé projektové závislosti:** [app.paths](../../app/paths.py), [app.shared.audio_effects](../../app/shared/audio_effects.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** audio.
- **Vedlejší účinky:** Přístup k mixeru/mikrofonu nebo audio souborům dle účelu.
- **Omezení a rizika:** Zařízení může chybět; soubory a streamy mají vlastní životní cyklus. Viz AUDIO.

## app/vocabulary/practise_data.py

- **Modul:** `app.vocabulary.practise_data` — [zdroj](../../app/vocabulary/practise_data.py).
- **Účel a odpovědnosti:** Hodnota Word, pravidla odpovědí, hint a termín opakování.
- **Veřejné vstupy:** `Word` (metody `copy`); `answers_match(expected, response)`; `shuffle_letters(word)`; `next_repetition(rep, days_gap_map, default_wait, now=None)`.
- **Klíčové vstupy:** Slovo/odpověď/historie a mapa intervalů.
- **Výstupy:** Výsledek shody, promíchaná písmena nebo čas příštího opakování.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.vocabulary.editor_synonyms](../../app/vocabulary/editor_synonyms.py), [app.vocabulary.practise](../../app/vocabulary/practise.py), [app.vocabulary.practise_session](../../app/vocabulary/practise_session.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/practise_layout.py

- **Modul:** `app.vocabulary.practise_layout` — [zdroj](../../app/vocabulary/practise_layout.py).
- **Účel a odpovědnosti:** Barevné rozložení zadání a slovníkového session panelu.
- **Veřejné vstupy:** `PracticeSidebar` (metody `update_session`); `style_practice(root, header, action, question, hint, choices, answer, type_two, *, prompt, response, word, translation, continue_button, skip_button, review)`.
- **Klíčové vstupy:** Widgety výuky a review callback.
- **Výstupy:** Uspořádané karty, přizpůsobení textu a PracticeSidebar.
- **Přímé projektové závislosti:** [app.core.context](../../app/core/context.py), [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.components.session_panel](../../app/ui/components/session_panel.py), [app.ui.components.shortcut_hint](../../app/ui/components/shortcut_hint.py), [app.ui.components.synonym_summary](../../app/ui/components/synonym_summary.py), [app.ui.fitted_text](../../app/ui/fitted_text.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.module_style](../../app/ui/module_style.py), [app.ui.surfaces](../../app/ui/surfaces.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** GUI, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/practise_review.py

- **Modul:** `app.vocabulary.practise_review` — [zdroj](../../app/vocabulary/practise_review.py).
- **Účel a odpovědnosti:** Sestavení detailů předchozího slova pro ReviewDialog.
- **Veřejné vstupy:** `open_review(app, word, on_audio, on_description, on_example, synonyms='', on_synonyms=None, on_edit_description=None, on_edit_example=None)`.
- **Klíčové vstupy:** Word, synonymní text a editační/mazací callbacky.
- **Výstupy:** Dialog bez prázdných detailů a bez prázdné sekce synonym.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.learning_review](../../app/ui/learning_review.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/practise_review_editor.py

- **Modul:** `app.vocabulary.practise_review_editor` — [zdroj](../../app/vocabulary/practise_review_editor.py).
- **Účel a odpovědnosti:** Pomocná editace textového detailu z review.
- **Veřejné vstupy:** `edit_attribute(owner, title, word, value, on_save)`.
- **Klíčové vstupy:** Owner, titul, výchozí obsah a save callback.
- **Výstupy:** Editační dialog a potvrzená nová hodnota.
- **Přímé projektové závislosti:** [app.shared](../../app/shared/__init__.py), [app.shared.settings](../../app/shared/settings.py), [app.ui](../../app/ui/__init__.py), [app.ui.learning_layout](../../app/ui/learning_layout.py), [app.ui.learning_review](../../app/ui/learning_review.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** GUI.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

## app/vocabulary/practise_session.py

- **Modul:** `app.vocabulary.practise_session` — [zdroj](../../app/vocabulary/practise_session.py).
- **Účel a odpovědnosti:** Indexovaný paměťový stav a pool možností výukového kola.
- **Veřejné vstupy:** `PracticeSession` (metody `pick`, `history`, `introduce`, `succeed`, `fail`, `skip`, `set_attribute`, `frames`); `ChoicePool` (metody `options`).
- **Klíčové vstupy:** Batch frame, plánovací mapa a překlady.
- **Výstupy:** Remaining/completed, historie, atributy a volby odpovědí.
- **Přímé projektové závislosti:** [app.vocabulary.practise_data](../../app/vocabulary/practise_data.py).
- **Staticky zjištění odběratelé:** [app.vocabulary.practise](../../app/vocabulary/practise.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## app/vocabulary/save_workflow.py

- **Modul:** `app.vocabulary.save_workflow` — [zdroj](../../app/vocabulary/save_workflow.py).
- **Účel a odpovědnosti:** Izolovaná příprava audia a commit souvisejících souborů s rollbackem.
- **Veřejné vstupy:** `save_course(edited, path, language, audio_folder, revision, cancelled, progress, *, context=None)`.
- **Klíčové vstupy:** Editovaný frame, revize CSV, audio složka a worker kontrakt.
- **Výstupy:** Uložený frame nebo chyba; při selhání původní soubory/obnovovací kopie.
- **Přímé projektové závislosti:** [app.repositories](../../app/repositories/__init__.py), [app.repositories.api_settings](../../app/repositories/api_settings.py), [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.shared.background_task](../../app/shared/background_task.py), [app.shared.storage](../../app/shared/storage.py), [app.vocabulary.editor_attributes](../../app/vocabulary/editor_attributes.py), [app.vocabulary.editor_data](../../app/vocabulary/editor_data.py).
- **Staticky zjištění odběratelé:** [app.repositories.vocabulary](../../app/repositories/vocabulary.py), [app.vocabulary.editor](../../app/vocabulary/editor.py).
- **Oblasti práce:** CSV/perzistence, konfigurace.
- **Vedlejší účinky:** Síťové obohacení ve stagingu, potvrzení audia/CSV/vazeb, rollback a úklid.
- **Omezení a rizika:** Běžné I/O selhání se obnovuje; pád OS není plná vícesouborová transakce. Viz AUDIO a DATA_STORAGE.

## app/vocabulary/synonyms.py

- **Modul:** `app.vocabulary.synonyms` — [zdroj](../../app/vocabulary/synonyms.py).
- **Účel a odpovědnosti:** Čisté dotazy nad vazbami a jejich textový souhrn.
- **Veřejné vstupy:** `linked_ids(frame, word_id)`; `describe(frame, words, word_id, language, learned_by)`.
- **Klíčové vstupy:** Frame dvojic, slova, ID a dva jazykové sloupce.
- **Výstupy:** Množina sousedních ID nebo jeden synonymní řádek na vazbu.
- **Přímé projektové závislosti:** Žádné přímé projektové importy.
- **Staticky zjištění odběratelé:** [app.repositories.synonyms](../../app/repositories/synonyms.py), [app.vocabulary.editor_data](../../app/vocabulary/editor_data.py), [app.vocabulary.editor_synonym_columns](../../app/vocabulary/editor_synonym_columns.py).
- **Oblasti práce:** čistá logika / konstanty; případné I/O je popsáno v účelu.
- **Vedlejší účinky:** Transformace hodnot nebo předaného frame; cache/konstanty podle konkrétního účelu.
- **Omezení a rizika:** Vstup musí respektovat popsaný datový kontrakt; nesmí se zaměnit UI překlad a kanonická data.

## start.py

- **Modul:** `start` — [zdroj](../../start.py).
- **Účel a odpovědnosti:** Vytvoření hlavního Tk okna, inicializace mixeru a spuštění navigace.
- **Veřejné vstupy:** `run()`.
- **Klíčové vstupy:** Prostředí Windows a distribuční soubory.
- **Výstupy:** Běžící event loop; ukončení mixeru ve finally.
- **Přímé projektové závislosti:** [app](../../app/__init__.py), [app.core.context](../../app/core/context.py), [app.main](../../app/main.py), [app.paths](../../app/paths.py), [app.shared](../../app/shared/__init__.py), [app.shared.audio_effects](../../app/shared/audio_effects.py), [app.shared.settings](../../app/shared/settings.py), [app.ui.brand](../../app/ui/brand.py).
- **Staticky zjištění odběratelé:** Žádný přímý produkční import; vstup může být start, callback nebo odložené směrování.
- **Oblasti práce:** GUI, audio, konfigurace.
- **Vedlejší účinky:** Vytváření nebo konfigurace widgetů, callbacků, obrázků a časovačů dle účelu.
- **Omezení a rizika:** Pouze Tk vlákno; zdroje uvolnit při zavření. Nativní DPI a hardware vyžadují ruční ověření.

Celkem zdokumentováno: **121 produkčních modulů**.
# Sdílené cyklické řazení

`app/ui/sorting.py` je čistá funkční utilita pro `next_sort(current, key)`
a `sort_arrow(current, key)`. Vstupem je volitelná dvojice sloupec/metrika
a příznak sestupného směru, výstupem nový stav nebo None pro původní pořadí.
Používají ji statistiky štítků, kategorií gramatiky, statistická tabulka
a editor slovíček. Nemá závislosti, I/O ani vlastní GUI stav; samotné
porovnávání hodnot a vykreslení zůstává odpovědností příslušného panelu.
# Rekordy gramatiky

`app/repositories/grammar_records.py`: `record_path`, `load_record` a kontext
`update_record`. Per-jazykový maximální rekord session; vstupem je cesta
gramatiky a kandidát, výstupem celé číslo nebo kontext pro uložení odpovědí.
Používají jej grammar/practise a statistics/data. Pracuje s malým CSV,
shared/storage, revizemi a rollbackem; nemá GUI ani síťové závislosti.

# Konfigurace

V záložce Jazyky se spravuje seznam **Studované jazyky**. Tlačítko **Přidat jazyk**
přidá další kurz; každý má vlastní přepínač a procenta kontextových a zvukových
otázek. Alespoň jeden kurz musí být zapnutý. Vypnutí zachová jeho nastavení,
vyplněný slovník, historii i audio. Aktivní jazyky se musí lišit od vlastního jazyka
a v seznamu se nesmějí opakovat. Jazyk rozhraní je samostatná volba.

Seznam se zapisuje do verzovaného JSON řádku `Study courses` až při uložení
nastavení. Pokud chybí, aplikace beze změny dat přečte původní First/Second
learning language a Enable second learning language (chybějící přepínač znamená
zapnuto). Pokud existují oba formáty, přednost má nový seznam; původní řádky
zůstávají zachované. Podrobnosti: [Studované kurzy](../study-courses.md).

Každý kurz má také příznak **Zapnout gramatiku**. Verze 2 JSON jej ukládá jako
`grammar`; verze 1 se načte s výchozím zapnutím. Při uložení se připraví
slovník, katalog štítků, synonyma a audio adresář; zapnutá gramatika přidá
otázky, teorii a prázdnou hlavičku rekordů. Žádné otázky ani slova se nevymýšlejí.

**Zapnout časování** je nezávislý přepínač `conjugation_enabled` v modelu
kurzu, ukládaný jako `conjugation` ve verzi 3 JSON. Starší verze 1/2 a původní
sloty zachovají dosavadní dostupnost podle existence CSV; parser sám na disk
nesahá. Nový kurz má časování vypnuté. Zapnutí po Save připraví chybějící
CSV a `<Language>_con_persons.json`, nikdy nepřepíše existující obsah.
Samostatné vypnutí časování zachová i prázdné CSV a konfiguraci a skryje
modul, jeho statistiky i přímé vstupy. Konfigurace osob se při odebrání celého
kurzu také nemaže.

Tlačítko **Gramatické osoby** je v kartě kurzu a na Home u časování. Dialog
má vlastní Save: názvy a pořadí osob, bezpečnou deaktivaci a oddělený výběr
osob k procvičování. Tato uživatelská konfigurace se vztahuje k cílovému
jazyku, nezávisle na jazyku UI a výchozím jazyku dvojice. Podrobnosti:
[Conjugation, 1. fáze](../conjugation-phase-1.md).

Vypnutý kurz po úspěšném uložení zmizí z formuláře. Vnitřní archiv zachová
jeho volby pro opětovné přidání. Teprve po uložení se odstraní rozpoznané
prázdné CSV a zcela prázdný audio adresář; každý neprázdný datový řádek či
nahrávka zůstanou zachované. Vypnutí gramatiky čistí jen její prázdné soubory
a skryje její nabídku, statistiky i vstupy do editorů/procvičování.

V Nastavení → Učení jsou také preference štítků:

- `Enable tags`: skryje/ukáže štítky v editoru, procvičování a statistikách; nemění uložená přiřazení.
- `Show tags during practice`: ukáže malý popisek dole v tmavém zadání při aktivní otázce. Review a Session řídí hlavní přepínač.
- `Tag display language`: Student language / Learning language, pro editor, Repeat i statistiky. Ukládají se vždy ID.
- `Maximum tags per word`: výchozí 10. Snížení pod počet již přiřazených štítků v kterémkoli slovníku se odmítne bez uložení nastavení.

V Nastavení → Učení je `Letter hints` s volbami Automatic, On request a
Disabled (lokalizované v UI). Výchozí režim při chybějící hodnotě je On request.
Písmena se odhalí tlačítkem Show hint zvlášť pro každou novou otázku;
u poslechu s možnostmi se nápověda z písmen nezobrazuje. Nová preference se
zapíše standardním Save nastavení, nikoli automatickým přepisem starého CSV.

RuntimePreferences v preferences/data.py je immutable snapshot hodnot z
settings.csv. preferences repository ověřuje strukturu Name/Type/Value a
unikátní klíče. validate_preferences kontroluje nezáporná celá čísla, kladné
batch sizes, procenta 0–100, součet kontextu a audia pro každý jazyk nejvýše
100, odlišné jazyky, boolean 0/1, hlasitost 0–100, e-mail a lokální datum termínu.

| Skupina | Příklady nastavení |
|---|---|
| Jazyky | App language, Learned by, Study courses včetně procent pro každý kurz |
| Učení | Learn batch, Random repeat batch - Vocabulary/Conjugation |
| Ovládání | App sounds enabled, App sound volume, Autoplay pronunciation, Remember grammar categories, Automatically show synonyms in repeat |
| Zálohy | Backup mail, Backup period (days), Next backup |
| Integrace | Merriam-Webster API klíče a 11Labs token |
| Interní metadata | Saved grammar category filters — JSON v settings.csv |

with_defaults doplní chybějící novější preference do pracovního frame.
Save odmítne cizí souběžnou změnu běžného nastavení; známé změny Next backup a
uložených filtrů umí sloučit. API klíče zůstávají v čitelném CSV. Odesílací
SMTP účet lze samostatně uložit do Správce pověření Windows přes Zálohy →
Odesílací účet. Je veden pod názvem `VocabPro/SMTP` pro aktuálního uživatele
na tomto počítači; není součástí CSV, repozitáře ani e-mailových příloh.

Proměnné prostředí VOC_SMTP_USER a VOC_SMTP_PASSWORD zůstávají alternativou
pro odesílání záloh. Úplná dvojice z prostředí má přednost, jinak se použije
uložený účet; odlišné zadané jméno z prostředí se s heslem jiného účtu nemíchá.
Jejich hodnoty se neukládají do dokumentace. start.py nastavuje výchozí
SDL_AUDIODRIVER=directsound jen pokud proměnná dosud není nastavena.

Konstanty učení a název aplikace jsou v shared/config.py, barvy/UI v ui/theme.py
a ui/module_style.py. Cesty v app/paths.py jsou odvozené od umístění projektu,
nikoli od aktuálního pracovního adresáře. AppContext může ve scénářích a testech
explicitně měnit root_dir/files_dir bez změny produkčních cest.

Dialog seskupuje položky pomocí `preferences.data.group_for`: obecné, slovíčka,
gramatika, časování, štítky a zvuky. Skupiny odděluje jemná čára a lokalizovaný
nadpis; formát ani pořadí položek uloženého CSV se tím nemění. Vypnutí Enable
tags zneaktivní Show tags during practice, Tag display language a Maximum tags
per word bez vymazání jejich hodnot. Validační chyby se zobrazují ve společném
zaobleném červeném panelu, jehož text se přizpůsobuje šířce okna.
# Závislé nastavení zvuků

Vypnutí `App sounds enabled` okamžitě zneaktivní `App sound volume` a zesvětlí
jeho popisek. Hodnota hlasitosti zůstane zachovaná a po opětovném zapnutí
zvuků je znovu upravitelná. Stav se uplatňuje také při otevření nastavení;
výslovnost slovíček je nadále ovládaná samostatně.

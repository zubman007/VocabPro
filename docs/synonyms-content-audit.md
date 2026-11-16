# Hloubkový obsahový audit synonym VocabPro

Datum: 16. 11. 2026. Rozsah změn: pouze obsah dvou aktivních synonymních CSV a tento samostatný report.

## Rozsah a metoda

Aplikace ukládá neorientované vazby přímo mezi ID slov v souborech `files/Czech_English_synonyms.csv` a `files/Czech_Spanish_synonyms.csv`. Formát je `ID 1;ID 2;Date`. Vazba tedy platí v obou směrech; nevyjadřuje automaticky synonymii ostatních sousedů. Slovníkové CSV neobsahuje další uložené synonymní pole: indikátory Has synonyms/Synonym count jsou dopočítané. Překladové alternativy v textu samotných hesel nejsou těmito vazbami a nebyly měněny.

Inventarizace slovníků obsahuje 5 522 slovníkových záznamů. Individuální sémantická revize se týkala všech 1 423 aktivních vazeb a všech jejich 1 686 koncových slovníkových záznamů (830 anglických a 856 španělských). Navíc bylo přečteno sedm dalších kandidátů: English ID 796, 737, 2098, 2619; Spanish ID 1099, 1472, 1706. Celkem tedy bylo obsahově posouzeno 1 693 slovníkových záznamů. Nejde o tvrzení, že byla provedena jazyková revize všech 5 522 slov bez synonym.

První průchod zahrnul každou dvojici, její oba české významy a slovní druhy. Druhý průchod zahrnul všechny uložené popisy a příklady všech 1 686 zapojených slov. Španělské popisy jsou převážně zástupné No found; taková hodnota není jazykový kontext. Příklady a české významy se přesto četly. U polysémie bylo hledáno skutečné společné užití, nikoliv shoda jednoho českého tokenu. Překryv v jiném výslovně uvedeném významu může být platný i tehdy, když ilustrační věta používá jiný význam. Samotná věta proto nebyla automatickým vylučovacím filtrem.

Byly aktivně zváženy přesnější alternativy. Náhrady používají výhradně existující slovníkové záznamy; kvůli rozšíření seznamu nevzniklo žádné nové slovíčko ani žádná další samostatná vazba. Pokud přesnější alternativa už byla přiřazena, nebo ve slovníku chyběla, chybná vazba se pouze odebrala. Nevznikaly automatické tranzitivní uzávěry.

Verdikty jsou jazykové úsudky o konkrétních uložených významech, doplněné slovníkovým ověřením rizikových hesel. Nejde o samostatné externí slovníkové ověření každé ze všech 1 423 dvojic. Kategorie „diskutabilní / omezený kontext“ zahrnuje také platné regionální a stylistické varianty, které bez dalšího upřesnění nelze prezentovat jako univerzálně zaměnitelné. Zůstaly beze změny; neoznačuji je za jednoznačné chyby.

## Výsledek

| Jazyk | Zapojená slova | Vazby před | Odstraněno | Nahrazeno | Přidáno navíc | Diskutabilní ponecháno | Vazby po |
|---|---:|---:|---:|---:|---:|---:|---:|
| English | 830 | 727 | 172 | 3 | 0 | 125 | 555 |
| Spanish | 856 | 696 | 80 | 1 | 0 | 130 | 616 |
| **Celkem** | **1686** | **1423** | **252** | **4** | **0** | **255** | **1171** |

Náhrady znamenají odebrání čtyř starých a vložení čtyř přesnějších dvojic. Nejsou započteny znovu mezi 252 prostých odstranění ani mezi nová rozšíření.

## Dvacet nejvýznamnějších oprav

- **Scorn → Abomination → Contempt** (English 135, ID 390/1353) → Scorn je pohrdání; abomination ohavná věc či čin. Pocit se zaměňuje s jeho předmětem.
- **Obtuse → Blunt → Dense** (English 637, ID 1775/2227) → Obtuse v tomto hesle znamená nechápavý/omezený; blunt fyzicky tupý nebo přímočarý.
- **Rogue → Drifter → Rascal** (English 32, ID 74/986) → Rogue je nepoctivec či darebák; drifter/bum/vagrant popisuje člověka bez stálého domova, nikoliv jeho nepoctivost.
- **hilarante → irrisorio → gracioso** (Spanish 174, ID 540/1808) → Hilarante je veselý, vyvolávající smích; irrisorio výsměšně směšný či směšně nízký. Pro zábavnost je přesnější gracioso.
- **Content → Content → odstranění** (English 53, ID 161/458) → Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů.
- **Pant → Pant → odstranění** (English 133, ID 387/1001) → Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů.
- **Hogwarts → Wart → odstranění** (English 448, ID 1125/2068) → Hogwarts je vlastní jméno školy Bradavice; wart je kožní bradavice.
- **Pheasant → Rookie → odstranění** (English 684, ID 1987/2258) → Pheasant je pták bažant, rookie nováček zvaný česky bažant.
- **Revenue → Edict → odstranění** (English 532, ID 1408/1882) → Edict je úřední nařízení; yield/revenue výtěžek či příjem. Dva zcela jiné významy českého výnos.
- **Con → Shack → odstranění** (English 588, ID 1589/1783) → Con je podvod/bouda v přeneseném smyslu; shack skutečná bouda/chatrč.
- **Flunk → Snap → odstranění** (English 691, ID 2052/2384) → Flunk znamená propadnout u zkoušky, snap fyzicky prasknout. České rupnout má jiný význam.
- **Inhibit → Defend → odstranění** (English 241, ID 607/1632) → Inhibit znamená bránit něčemu v činnosti; defend bránit něco před ohrožením. České bránit má opačné role.
- **Relent → Mitigate → odstranění** (English 65, ID 200/1223) → Relent je nepřechodné ustoupit nebo obměkčit se; soothe/mitigate/alleviate přechodně uklidňují či zmírňují něco.
- **Harass → Molest → odstranění** (English 16, ID 62/1493) → Molest v současném běžném užití označuje zejména sexuální napadení/zneužití; obecné obtěžování či vyrušování je jiný význam.
- **Liberation → Acquittal → odstranění** (English 326, ID 830/2302) → Liberation je osvobození z útlaku, exemption výjimka z povinnosti a acquittal zproštění obžaloby. Tři odlišné významy osvobození.
- **entretener → incautar → odstranění** (Spanish 148, ID 495/1933) → Entretener znamená bavit/zaměstnat pozornost; incautar zabavit majetek. Dva odlišné významy českého zabavit.
- **la serenidad → la cámara → odstranění** (Spanish 160, ID 522/969) → Serenidad je duševní klid/pokoj, cámara místnost/pokoj či kamera. České pokoj má jiný význam.
- **el incremento → la estatura → odstranění** (Spanish 145, ID 473/580) → Incremento je přírůstek/navýšení, estatura tělesná výška. Dva odlišné významy českého vzrůst.
- **erradicar → alisar → odstranění** (Spanish 389, ID 1260/2792) → Erradicar je vymýtit/vyhladit problém či populaci; alisar fyzicky uhladit povrch.
- **recién → justamente → odstranění** (Spanish 427, ID 1336/1483) → Recién je právě teď/nedávno, justamente/precisamente právě v důrazovém smyslu přesně. Časová blízkost není důrazová přesnost.

## Slovníkové podklady pro rizikové případy

- Obtuse bylo posouzeno ve významu omezený/nechápavý. Nové dense má doložený význam hloupý; fyzicky tupý blunt sem nepatří. [Cambridge: dense](https://dictionary.cambridge.org/us/dictionary/english/dense).
- Nová vazba scorn–contempt vyjadřuje pohrdání, nikoli ohavnou věc abomination. [Cambridge: contempt](https://dictionary.cambridge.org/dictionary/english/contempt).
- Rogue má běžné významy darebáka i sympatického rošťáka, nikoli obecné označení člověka bez bydliště. Náhrada rascal odpovídá tomuto osobnímu významu. [Cambridge: rogue](https://dictionary.cambridge.org/us/dictionary/english/rogue).
- Relent je nepřechodné ustoupení/obměkčení; nelze ho obecně učit jako přechodné alleviate/mitigate. [Cambridge: relent](https://dictionary.cambridge.org/dictionary/english/relent).
- Toss off má běžně význam rychle něco vytvořit a také sexuální použití; uložené odhodit nevytváří bezpečnou vazbu na discard/ditch. [Cambridge: toss off](https://dictionary.cambridge.org/dictionary/english/toss-off).
- Corny označuje otřepanost, banálnost či sentimentální kýč, ne technickou zastaralost obsolete/outdated. [Cambridge: corny](https://dictionary.cambridge.org/dictionary/english/corny).
- Hilarante vyjadřuje zábavnost a RAE uvádí gracioso mezi odpovídajícími výrazy. Irrisorio může být výsměšně směšný nebo zanedbatelně malý; jejich výměna je v kontextu veselého komentáře přesnější. [RAE: hilarante](https://dle.rae.es/hilarante), [RAE: irrisorio](https://dle.rae.es/irrisorio), [RAE: gracioso](https://dle.rae.es/gracioso).
- Obstante není popis vzpurné osoby; heslo se uplatňuje především v no obstante. Nespekulovalo se o opravě slovíčka na obstinado. [RAE: obstante](https://dle.rae.es/obstante).
- Perpetrar je omezeno na spáchání provinění/zločinu; obecné realizar/ejecutar není v běžném projektovém kontextu stejně použitelné. Seznamy „synonyma a příbuzná slova“ se nebraly jako bezpodmínečná zaměnitelnost. [RAE: perpetrar](https://dle.rae.es/perpetrar).
- Aktivní vazba activar–acelerar zůstala: activar má doložený význam oživit/urychlit proces. Týká se procesu, nikoliv samotného zapnutí přístroje. [RAE: activar](https://dle.rae.es/activar).
- Frijol může označovat i zelený plod; chaucha odpovídá zelené fazolce/lusku. Vazba zůstala diskutabilní kvůli příkladu frijol negro, nikoli automaticky odstraněná jako údajně vždy chybná. [RAE: frijol](https://dle.rae.es/frijol), [RAE: chaucha](https://dle.rae.es/chaucha).
- Efectivamente vyjadřuje skutečnost/realizaci a souhlasné potvrzení. Kvůli rozporu českého překladu s příkladem zůstává vazba na eficazmente k rozhodnutí. [RAE: efectivamente](https://dle.rae.es/efectivamente).

Některé přímé požadavky na Cambridge vracely HTTP 403; u dohledatelných hesel byly použity dostupné výsledky stejného vydavatele. Nedostupné stránky nejsou uváděny jako přečtené podklady. Nejisté významy se neopravovaly odhadem.

## Případy vyžadující rozhodnutí uživatele

Tyto záznamy nebyly v rámci auditu upraveny:

1. **Confide–entrust (EN 55):** má být důraz na důvěrném sdělení, nebo svěření odpovědnosti? Liší se i vazby.
2. **Rid of–ditch/purge (EN 75–76):** má heslo znamenat get rid of, nebo rid někoho něčeho? Úplná fráze vyžaduje úpravu slovíčka mimo rozsah auditu.
3. **Rise up–mutiny (EN 89) a endeavour–strive (EN 259):** rozhodnout zamýšlený slovní druh; metadata se neshodují s částí obsahu.
4. **Prick–pecker (EN 620):** rozlišit anatomii od nadávky. U prick si navíc popis a příklad odporují.
5. **Foster–foster (EN 605):** dvě různá ID nejsou technická vazba na sebe sama, ale významy druhého hesla mísí sloveso, přídavné a podstatné jméno.
6. **Frijol–chaucha (ES 194):** rozlišit semeno/fazole a zelený plod/lusk. Regionální ekvivalent je možný, současný příklad ukazuje černé fazole.
7. **Personalmente–presencialmente (ES 205):** zda osobně znamená podle mého názoru/sám, nebo fyzickou přítomnost.
8. **Apropiar–adaptar/ajustar (ES 469, 507):** české přizpůsobit koliduje s příkladem přivlastnění. Automatická oprava lemma/reflexivity by překročila zadání.
9. **Efectivamente–eficazmente (ES 580):** zda má být cílem potvrzení skutečnosti, nebo účinnost provedení. Český překlad a příklad prvního hesla se rozcházejí.
10. **Aleatoriamente–casualmente (ES 675):** zda jde o statistický náhodný výběr, nebo neplánovanou shodu okolností.
11. **Intendente–alcalde (ES 678):** zvolit cílovou zemi; obecná ekvivalence starosty neplatí všude.
12. **Regionální a expresivní vazby**, zejména coger–agarrar, qué piola–qué chulo, al tiro–al toque, pendejo/huevón/tarado a carajo/caramba: určit požadovanou varietu a přijatelnost hrubosti. Samotná regionálnost není chybou.

Úplný seznam všech ponechaných diskutabilních/kontextových vazeb je v registrech níže. U některých dalších slov byly nalezeny rozpory českého překladu, definice, příkladu či slovního druhu (např. content, pant, remote, hose, strain, brief). V souladu se zadáním zůstaly všechny tyto atributy nedotčené. Odstranění vazby mezi jejich různými českými významy není opravou ani sloučením hesel.

## Historické kopie

Byly nalezeny tři historické synonymní kopie s celkem 38 datovými řádky. Všechny jejich dvojice se nacházejí také v původních aktivních datech a byly posouzeny výše. Identifikátory, data a formát prošly kontrolou. Kopie zůstaly bytově beze změny, aby zachovaly historický bod obnovy. **Tehdejší obsah hesel nelze nezávisle ověřit bez odpovídajícího tehdejšího slovníku; sémantické posouzení archivních ID se vztahuje k současným heslům.** Nejde proto o tvrzení kompletní historické rekonstrukce.

- `files/backups/before_synonyms_expansion_4984fd1b/Czech_English_synonyms.csv`: 0 vazeb; SHA-256 `269c29616f50498b718c30d2ed26fc31aed6f17a565bed0dd7a3dca90fe9d20e`.
- `files/backups/before_synonyms_expansion_4984fd1b/Czech_Spanish_synonyms.csv`: 4 vazeb; SHA-256 `9c79f1e92f65398153ee3895651b59ea29b42fb75d270f0c9bdd8e6f7dce4942`.
  Odpovídající původní aktivní záznamy: 1, 451, 29, 12.
- `files/backups/before_synonyms_extension_6f66ae5c/Czech_Spanish_synonyms.csv`: 34 vazeb; SHA-256 `4c0870931e2c5d43854f39195f5dd2d8937609817d0e98f4fb82267725b75199`.
  Odpovídající původní aktivní záznamy: 1, 8, 12, 17, 28, 29, 45, 53, 56, 59, 66, 90, 93, 107, 114, 144, 154, 199, 217, 224, 228, 229, 251, 252, 334, 451, 458, 508, 509, 548, 619, 624, 636, 678.

## Integrita a rozsah zápisu

Oba soubory byly zpracovány po původních bytových řádcích: smazány jen označené vazby a u náhrad změněny jen oba identifikátory vztahu. Hlavičky, oddělovače, kódování, konce řádků, data Date a relativní pořadí všech ponechaných řádků zůstaly zachovány. Přiřazení osob ani slovníkové identity se nepřečíslovávaly. Náhrady jsou na místě původního záznamu; celé CSV nebylo znovu řazeno ani přeformátováno.

Před i po plánované úpravě: **0 duplicitních neorientovaných dvojic, 0 vazeb na sebe sama, 0 odkazů na neexistující ID, 0 neplatných dat**. U náhrad byla zkontrolována i nepřítomnost již existující dvojice. Jiná data slovíček, historie, nastavení, zdrojový kód, UI, testy ani starší dokumentace nebyly zapisovány.

- English: 552 ponechaných řádků je bytově shodných. SHA-256 před `55b452960cdeb3ac552e4a9fc835e088fffc1fc18c1fd40f709f2a32dac7ab63`; po `ee5f0daebbb72774c1c8eb66a6ea339597b3526a90fa070e68c59d49dc24e39d`.
- Spanish: 615 ponechaných řádků je bytově shodných. SHA-256 před `0543fe76510aff9bebb62784e1afdb4dd94aa8fdf2351c27dc609b9927437a10`; po `655a79f4e3966cb9827b3e6d20d90e6c9d0ac54ec07a823ff40ead1b12efbb47`.

Kontrolní otisk 5957 ostatních souborů byl před zápisem shodný s výchozím stavem: `8689fd6272245f8745569224a1c9ef6b27d68b021bad7456a8c5aa02a3532ecf`. Z otisku jsou vyňata jen obě povolená aktivní CSV a tento report; mimo projektový obsah jsou vynechány .git, .venv a __pycache__. Zahrnuty jsou i slovníky, audio, historické zálohy a dříve rozpracované soubory. Závěrečné ověření je uvedeno na konci reportu.

## Úplný registr původních aktivních vazeb

Číslo je pořadí datového řádku **před auditem**, fyzický CSV řádek je o 1 vyšší. ID jsou skutečné identity slov, nikoliv čísla řádků slovníku. Vztah platí v obou směrech, proto není veden zvláštní reverzní záznam.

- **Ponecháno:** nalezen použitelný společný význam; nejde o tvrzení synonymie všech významů slova.
- **Diskutabilní:** ponecháno beze změny, kontextové/stylistické/gramatické omezení nebo nedostatek jistoty; nejde o prohlášení objektivní chyby.
- **Odstraněno:** významově nevhodné přiřazení pro aktuálně uložené významy.
- **Nahrazeno:** původní nevhodný vztah nahrazen konkrétní přesnější dvojicí.

U každé dvojice jsou oba české významy pro dohledatelnost významového posouzení. Popisy a příklady zůstávají ve zdrojových slovnících beze změny.

### English: 727 původních vazeb

| Záznam | ID | Hesla | České významy | Verdikt | Posouzení / náhrada |
|---:|---|---|---|---|---|
| 1 | 6/1422 | Figure out / Untangle | Vyřešit, pochopit / Vyřešit, rozuzlit, rozmotat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 2 | 8/1270 | Dull / Asinine | Nudný, hloupý / Pitomý, hloupý, idiotský | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 3 | 8/2453 | Dull / Daft | Nudný, hloupý / Hloupý, pitomý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 4 | 15/2363 | Audacity / Effrontery | Drzost, smělost / Drzost, nestoudnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 5 | 19/1110 | Decimate / Mar | Zničit / Pokazit, zkazit, zničit | Odstraněno | Decimate znamená rozsáhle zničit či zdecimovat, mar poškodit nebo pokazit vzhled/kvalitu; jiná míra a povaha zásahu. |
| 6 | 21/395 | Tissue / Handkerchief | Kapesník / Kapesník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 7 | 30/1689 | Charming / Glamorous | Okouzlující / Okouzlující, úchvatný, oslnivý, přitažlivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 8 | 31/2301 | Despise / Spurn | Opovrhovat / Zavrhnout, odkopnout, opovrhovat | Odstraněno | Despise je postoj pohrdání; spurn je odmítnutí s pohrdáním. Pocit a provedené odmítnutí se zaměňují. |
| 9 | 38/1635 | Remain / Abide | Zůstat / Zůstat, dodržet, snést | Diskutabilní | Abide ve významu zůstat je literární/zastaralé; pro běžné remain nemusí být vhodné. |
| 10 | 42/604 | Speckled / Spotted | Kropenatý, strakatý, skvrnitý / Puntíkovaný, skvrnitý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 11 | 44/45 | Therefore / Thus | Proto / Tak, tím páden | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 12 | 44/1669 | Therefore / Hence | Proto / Proto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 13 | 54/1094 | Lame / Faint | Chromý, chabý / Slabý, chabý, sotva patrný, nejasný | Odstraněno | Lame excuse je nepřesvědčivá výmluva; faint popisuje slabost či sotva patrnou intenzitu. |
| 14 | 54/1840 | Lame / Feeble | Chromý, chabý / Slabý, chabý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 15 | 57/963 | Patch / Plaster | Náplast, záplata / Náplast | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 16 | 62/1493 | Harass / Molest | Obtěžovat / Obtěžovat | Odstraněno | Molest v současném běžném užití označuje zejména sexuální napadení/zneužití; obecné obtěžování či vyrušování je jiný význam. |
| 17 | 62/1542 | Harass / Intrude | Obtěžovat / Zasahovat, obtěžovat, vyrušovat | Odstraněno | Harass/pester znamená někoho obtěžovat; intrude vstoupit či zasahovat bez pozvání. Odlišný děj i slovesná vazba. |
| 18 | 62/2371 | Harass / Pester | Obtěžovat / Obtěžovat, otravovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 19 | 65/876 | Rejection / Rebuff | Odmítnutí / Odmítnout, odmítnutí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 20 | 66/2040 | Attorney / Solicitor | Advokát / Advokát | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 21 | 68/504 | Rotten / Wretched | Shnilý, zkažený, mizerný / Ubohý, mizerný, bídný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 22 | 68/1054 | Rotten / Lousy | Shnilý, zkažený, mizerný / Mizerný, protivný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 23 | 68/1550 | Rotten / Miserable | Shnilý, zkažený, mizerný / Nešťastný, mizerný, utrápený, bídný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 24 | 68/1595 | Rotten / Abysmal | Shnilý, zkažený, mizerný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 25 | 68/1875 | Rotten / Grotty | Shnilý, zkažený, mizerný / Odporný, hnusný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 26 | 68/2074 | Rotten / Crummy | Shnilý, zkažený, mizerný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 27 | 68/2228 | Rotten / Putrid | Shnilý, zkažený, mizerný / Hnijící, zkažený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 28 | 70/1236 | Dingy / Grubby | Špinavý, omšelý / Umouněný, špinavý, ušmudlaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 29 | 70/1682 | Dingy / Foul | Špinavý, omšelý / Odporný, hnusný, špinavý, znečistit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 30 | 70/2481 | Dingy / Sleazy | Špinavý, omšelý / Špinavý, ubohý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 31 | 74/825 | Rogue / Villain | Ničema, tulák, pobuda / Darebák, padouch, ničema | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 32 | 74/986 | Rogue / Drifter | Ničema, tulák, pobuda / Tulák, darmošlap | Nahrazeno | Rogue je nepoctivec či darebák; drifter/bum/vagrant popisuje člověka bez stálého domova, nikoliv jeho nepoctivost. Nově: Rogue / Rascal. |
| 33 | 74/1322 | Rogue / Bum | Ničema, tulák, pobuda / Vandrák, pobuda | Odstraněno | Rogue je nepoctivec či darebák; drifter/bum/vagrant popisuje člověka bez stálého domova, nikoliv jeho nepoctivost. |
| 34 | 74/1555 | Rogue / Vagrant | Ničema, tulák, pobuda / Tulák, pobuda | Odstraněno | Rogue je nepoctivec či darebák; drifter/bum/vagrant popisuje člověka bez stálého domova, nikoliv jeho nepoctivost. |
| 35 | 75/626 | Deception / Scam | Podvod / Podvod | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 36 | 75/1589 | Deception / Con | Podvod / Podvod, bouda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 37 | 75/2055 | Deception / Fraud | Podvod / Podvod, podvodník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 38 | 85/904 | Toss off / Discard | Odhodit / Vyřadit, odhodit | Odstraněno | Toss off běžně znamená něco rychle a snadno vytvořit nebo má sexuální význam; není synonymem odhození nepotřebné věci. |
| 39 | 85/1192 | Toss off / Ditch | Odhodit / Zbavit se, odhodit | Odstraněno | Toss off běžně znamená něco rychle a snadno vytvořit nebo má sexuální význam; není synonymem odhození nepotřebné věci. |
| 40 | 86/2642 | Take apart / Dismantle | Rozebrat / Rozebrat, rozmontovat, demontovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 41 | 91/2618 | Distinguish / Discern | Rozeznat, rozlišit / Rozpoznat, rozeznat, rozlišit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 42 | 92/225 | Tiresome / Tedious | Únavné / Únavný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 43 | 95/885 | Disheartened / Gloomy | Deprimovaný, dezertovaný, sklíčený / Ponurý, sklíčený, pochmurný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 44 | 100/474 | Earnestly / Gravely | Vážně / Vážně, těžce | Diskutabilní | Earnestly klade důraz na upřímnost, gravely na vážný či ponurý tón; vyžaduje větný kontext. |
| 45 | 102/153 | Contemplation / Reflection | Rozjímání / Odraz, úvaha | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 46 | 112/213 | Little by little / Bit by bit | Kousek po kousku / Kousek po kousku | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 47 | 121/1888 | Overpower / Vanquish | Přemoci, zdolat, zvítězit / Porazit, přemoci, zdolat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 48 | 123/2193 | Consequence / Repercussion | Důsledek, následek, závažnost / Odezva, následek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 49 | 126/349 | Fatigue / Weariness | Únava / Únava | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 50 | 151/381 | Magnificent / Splendid | Velkolepý, vynikající / Nádherný, skvělý, velkolepý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 51 | 155/1891 | Gentle / Gracious | Jemný, mírný, laskavý / Zdvořilý, jemný, laskavý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 52 | 155/2178 | Gentle / Benign | Jemný, mírný, laskavý / Laskavý, neškodný, nezhoubný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 53 | 161/458 | Content / Content | Obsah / Spokojený | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 54 | 164/1315 | Fragrance / Scent | Vůně / Vůně, aroma | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 55 | 165/1215 | Confide / Entrust | Svěřit / Svěřit | Diskutabilní | Confide souvisí se svěřením důvěrnosti (confide in/to), entrust s předáním odpovědnosti (entrust with/to). |
| 56 | 174/607 | Restrain / Inhibit | Omezit, zdržovat, krotit / Potlačit, omezit, bránit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 57 | 178/299 | Painstaking / Thorough | Pečlivý, usilovný, důkladný / Důkladný, pečlivý, svědomitý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 58 | 178/2585 | Painstaking / Meticulous | Pečlivý, usilovný, důkladný / Puntičkářský, pečlivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 59 | 183/679 | Adjust / Alter | Upravit, přizpůsobit, seřídit / Změnit, pozměnit, upravit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 60 | 188/1792 | Fade / Wilt | Slábnout, vyblednout, vadnout / Vadnout, sesychat, usychat | Diskutabilní | Fade a wilt se mohou překrývat při vadnutí květin, ne při blednutí barvy. |
| 61 | 197/1848 | Rage / Wrath | Vztek, hněv, zuřivost / Hněv, zloba, rozhořčení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 62 | 198/309 | Mix up / Bewilder | Pormíchat, zmást, plést si / Zmást, ohromit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 63 | 198/367 | Mix up / Perplex | Pormíchat, zmást, plést si / Poplést, zmást, uvést do rozpaků | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 64 | 200/466 | Relent / Soothe | Povolit, zmírnit, ustoupit / Uklidnit, zmírnit, ukonejšit | Odstraněno | Relent je nepřechodné ustoupit nebo obměkčit se; soothe/mitigate/alleviate přechodně uklidňují či zmírňují něco. |
| 65 | 200/1223 | Relent / Mitigate | Povolit, zmírnit, ustoupit / Zmírnit | Odstraněno | Relent je nepřechodné ustoupit nebo obměkčit se; soothe/mitigate/alleviate přechodně uklidňují či zmírňují něco. |
| 66 | 200/2608 | Relent / Alleviate | Povolit, zmírnit, ustoupit / Zmírnit, zmenšit | Odstraněno | Relent je nepřechodné ustoupit nebo obměkčit se; soothe/mitigate/alleviate přechodně uklidňují či zmírňují něco. |
| 67 | 204/466 | Reassure / Soothe | Uklidnit, ubezpečit, ujistit / Uklidnit, zmírnit, ukonejšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 68 | 204/2639 | Reassure / Appease | Uklidnit, ubezpečit, ujistit / Usmířit, uklidnit | Odstraněno | Reassure odstraňuje obavu ujištěním; appease usmiřuje hněv nebo uspokojuje požadavky. |
| 69 | 205/296 | Resentful / Vexed | Nesnášenlivý, podrážděný, rozlobený, rozmrzelý / Rozmrzelý, citlivý, obtížný, choulostivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 70 | 205/2390 | Resentful / Testy | Nesnášenlivý, podrážděný, rozlobený, rozmrzelý / Nedutklivý, podrážděný | Odstraněno | Resentful znamená cítící zášť/křivdu, testy snadno podrážděný. Jiný emocionální stav. |
| 71 | 206/1497 | Spite / Malice | Vzdor, zášť, zlomyslnost / Zlomyslnost, zášť | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 72 | 206/2304 | Spite / Grudge | Vzdor, zášť, zlomyslnost / Zášť, nevraživost, averze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 73 | 210/534 | Reveal / Unveil | Prozradit, odhalit / Odhalit, zvednout závoj | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 74 | 214/1855 | Parched / Desiccated | Vyprahlý, vyschlý / Vyschlý, vysušený, suchý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 75 | 226/1192 | Rid of / Ditch | Zbavit se / Zbavit se, odhodit | Diskutabilní | Heslo Rid of má příklad get rid of; bez get nebo předmětu je konstrukce neúplná. Obsah hesla nelze v tomto auditu upravit. |
| 76 | 226/2124 | Rid of / Purge | Zbavit se / Očistit, zbavit se, udělat čistku | Diskutabilní | Purge bývá zbavit něco něčeho, get rid of zbavit se něčeho; potřeba celého kontextu a slovesné vazby. |
| 77 | 231/1536 | Among / Amid | Mezi, uprostřed / Uprostřed, mezi | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 78 | 231/1839 | Among / Midst | Mezi, uprostřed / Uprostřed, během, v průběhu | Odstraněno | Midst je podstatné jméno vyžadující konstrukci in the midst of; samotné není předložkou among/amid. |
| 79 | 248/329 | Glitter / Shimmer | Lesk, třpyt, třpytit se / Lesk, třpyt | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 80 | 258/1819 | Plunge / Scurry | Ponořit se, vrhnout se, hnát se / Pelášit, hnát se, pospíchat | Odstraněno | Plunge znamená prudce se ponořit či vrhnout do něčeho; scurry/dash popisují rychlý běh či přesun. |
| 81 | 258/1863 | Plunge / Dash | Ponořit se, vrhnout se, hnát se / Uhánět, hnát se, řítit se | Odstraněno | Plunge znamená prudce se ponořit či vrhnout do něčeho; scurry/dash popisují rychlý běh či přesun. |
| 82 | 260/704 | Handsome / Comely | Hezký, pěkný, pohledný / Pohledný, půvabný, sličný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 83 | 261/2348 | Regard / Deem | Považovat, posuzovat, kvalifikovat / Považovat, pokládat, mínit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 84 | 264/702 | Queer / Peculiar | Podivný, zvláštní, homosexuální / Podivný, zvláštní | Diskutabilní | Queer je použitelně zvláštní, ale má další identitní a někdy urážlivé užití. Vazba platí jen pro zvláštnost. |
| 85 | 272/723 | Grieve / Mourn | Truchlit, trápit / Truchlit, oplakávat, naříkat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 86 | 272/1466 | Grieve / Tantalize | Truchlit, trápit / Trápit, mučit, dráždit | Odstraněno | Grieve znamená truchlit; tantalize dráždit lákavou, obtížně dostupnou věcí. Odlišný důvod i druh prožitku. |
| 87 | 272/1889 | Grieve / Lament | Truchlit, trápit / Naříkat, bědovat, truchlit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 88 | 277/388 | Bulky / Voluminous | Objemný, neskladný, rozměrný / Objemný, obsáhlý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 89 | 279/1348 | Rise up / Mutiny | Povstát, vzbouřit se / Vzpoura, vzbouřit se | Diskutabilní | Mutiny má i slovesné užití vzbouřit se, ale záznam je Noun a příklad jmenný. K rozhodnutí je zamýšlený slovní druh. |
| 90 | 282/1718 | Forsaken / Derelict | Opuštěný, pustý, zpustlý / Opuštěný, zpustlý, zchátralý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 91 | 283/462 | Forsake / Abandon | Zanechat, opustit, vzdát se / Opustit, vzdát se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 92 | 283/1438 | Forsake / Surrender | Zanechat, opustit, vzdát se / Vzdát se | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 93 | 286/294 | Insubordination / Disobedience | Neposlušnost / Neposlušnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 94 | 288/1573 | Mantle / Cloak | Plášť, skrýt, zakrýt / Plášť, plášť neviditelnosti | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 95 | 290/628 | Inquiry / Query | Poptávka, dotaz / Dotaz | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 96 | 299/2585 | Thorough / Meticulous | Důkladný, pečlivý, svědomitý / Puntičkářský, pečlivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 97 | 303/385 | Majestic / Stately | Majestátný / Majestátný, impozantní, vznešený, okázalý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 98 | 307/1437 | Endure / Withstand | Snést, vydržet, přetrpět, přestát / Odolat, vydržet, snést | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 99 | 307/1557 | Endure / Sustain | Snést, vydržet, přetrpět, přestát / Udržet, vydržet | Diskutabilní | Sustain a endure se mohou potkat u utrpění nárazu/škody; sustain však není obecně snášet nepříjemnost. |
| 100 | 307/1635 | Endure / Abide | Snést, vydržet, přetrpět, přestát / Zůstat, dodržet, snést | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 101 | 309/367 | Bewilder / Perplex | Zmást, ohromit / Poplést, zmást, uvést do rozpaků | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 102 | 309/1306 | Bewilder / Astound | Zmást, ohromit / Ohromit, udivit, uvést v úžas | Odstraněno | Bewilder vyvolává zmatek/nepochopení; astound údiv či překvapení. |
| 103 | 321/1318 | Stratagem / Wile | Lest, úskok / Lest | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 104 | 325/2072 | Stroll / Ramble | Procházka, potulovat se / Vycházka, toulat se, procházka, toulka, tůra | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 105 | 326/1541 | Sorrow / Bereavement | Zármutek, žal / Úmrtí, zármutek, žal | Odstraněno | Sorrow je pocit zármutku; bereavement je ztráta blízkého úmrtím a stav pozůstalého, ne obecný název pocitu. |
| 106 | 327/375 | Rough / Harsh | Hrubý, drsný / Drsný, krutý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 107 | 327/1016 | Rough / Crude | Hrubý, drsný / Surový, hrubý, drsný, sprostý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 108 | 327/2261 | Rough / Abrasive | Hrubý, drsný / Drsný, neomalený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 109 | 328/1118 | Nourishment / Sustenance | Výživa / Výživa, potrava, obživa, živobytí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 110 | 351/452 | Hunt for / Seek out | Hledat, shánět / Hledat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 111 | 356/1819 | Rush / Scurry | Pospíchat, hnát se / Pelášit, hnát se, pospíchat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 112 | 356/1863 | Rush / Dash | Pospíchat, hnát se / Uhánět, hnát se, řítit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 113 | 356/2596 | Rush / Hustle | Pospíchat, hnát se / Strkat, pohhánět / tlačenice / spěchat, pospíchat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 114 | 357/1132 | Boast / Brag | Chlubit se, vychloubat se / Chvástat se, chlubit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 115 | 358/755 | Grumble / Mutter | Reptat, stěžovat si, nadávat / Mumlat, reptat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 116 | 358/2357 | Grumble / Scold | Reptat, stěžovat si, nadávat / Nadávat, vynadat | Odstraněno | Grumble je reptat/stěžovat si, scold někoho kárat; odlišný komunikační děj a vazba. |
| 117 | 364/756 | Burrow / Den | Doupě, nora, díra / Doupě, pelech, nora | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 118 | 364/1271 | Burrow / Pothole | Doupě, nora, díra / Výmol na silnici, díra | Odstraněno | Burrow je zvířecí nora, pothole silniční výmol; společné české díra neurčuje synonymii. |
| 119 | 373/508 | Dreadful / Horrid | Hrozný, strašný, strašlivý / Hrozný, špatný, ohavný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 120 | 373/577 | Dreadful / Dire | Hrozný, strašný, strašlivý / Katastrofální, strašný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 121 | 373/1070 | Dreadful / Appalling | Hrozný, strašný, strašlivý / Děsivé, otřesné hrozné | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 122 | 373/1595 | Dreadful / Abysmal | Hrozný, strašný, strašlivý / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 123 | 373/1923 | Dreadful / Excruciating | Hrozný, strašný, strašlivý / Nesnesitelný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 124 | 373/2007 | Dreadful / Hideous | Hrozný, strašný, strašlivý / Škaredý, ohizdný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 125 | 375/818 | Harsh / Cruel | Drsný, krutý / Krutý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 126 | 375/1016 | Harsh / Crude | Drsný, krutý / Surový, hrubý, drsný, sprostý | Diskutabilní | Harsh je tvrdý/nelítostný, crude neopracovaný/hrubě vulgární; vyžaduje kontext drsného projevu. |
| 127 | 375/2261 | Harsh / Abrasive | Drsný, krutý / Drsný, neomalený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 128 | 381/1211 | Splendid / Divine | Nádherný, skvělý, velkolepý / Božský, andělský, nádherný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 129 | 381/1551 | Splendid / Sublime | Nádherný, skvělý, velkolepý / Božský, nádherný, úžasný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 130 | 381/2477 | Splendid / Scrumptious | Nádherný, skvělý, velkolepý / Skvělý, vynikající, lahodný | Odstraněno | Scrumptious vyjadřuje výtečnou chuť jídla; splendid obecnou velkolepost/skvělost. Chybí společný běžný kontext odpovídající oběma heslům. |
| 131 | 385/550 | Stately / Lofty | Majestátný, impozantní, vznešený, okázalý / Vznešený, vysoký, ušlechtilý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 132 | 385/2603 | Stately / Ostentatious | Majestátný, impozantní, vznešený, okázalý / Okázalý, honosný, pompézní | Odstraněno | Stately je důstojně vznešený; ostentatious okázalý s cílem upoutat. Jiný hodnotící odstín. |
| 133 | 387/1001 | Pant / Pant | Supět, těžce oddychovat, vzdychat / Kalhoty | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 134 | 388/1539 | Voluminous / Vast | Objemný, obsáhlý / Obrovský, objemný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 135 | 390/1353 | Scorn / Abomination | Opovržení, pohrdat / Ohavnost, opovržení | Nahrazeno | Scorn je pohrdání; abomination ohavná věc či čin. Pocit se zaměňuje s jeho předmětem. Nově: Scorn / Contempt. |
| 136 | 401/677 | Extraordinary / Exceptional | Mimořádný, zvláštní, neobyčejný / Výjiměčný, mimořádný, nevšední | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 137 | 417/2233 | Inflate / Bloat | Nafouknout, nahustit / Nafouknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 138 | 418/2438 | Boost / Uphold | Pozvednout, prosazovat, propagovat / Prosazovat, dodržovat, podporovat | Diskutabilní | Boost něco zvyšuje či propaguje, uphold zachovává/podporuje; společná podpora má užší kontext. |
| 139 | 431/2514 | Acquisition / Boon | Získávání, přírůstek, nabytí, přínos / Požehnání, přínos, výhoda | Odstraněno | Acquisition je získání či nabytá věc; boon je prospěšná výhoda/dar. Nabytí samo není přínosem. |
| 140 | 431/2589 | Acquisition / Acquisition | Získávání, přírůstek, nabytí, přínos / nabytí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 141 | 434/1996 | Capability / Vocation | Schopnost / Poslání, povolání, schopnost, určení | Odstraněno | Capability je schopnost; vocation povolání či životní poslání. |
| 142 | 441/1569 | Cuddle / Pamper | Hýčkat, mazlit, laskat, objetí / Rozmazlovat, hýčkat | Odstraněno | Cuddle znamená obejmout či mazlit se fyzicky, pamper rozmazlovat péčí a ústupky. |
| 143 | 446/1847 | Maturity / Ripeness | Zralost, dospělost / Zralost, vyzrálost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 144 | 453/1325 | Disrupt / Adjourn | Narušit, přerušit, rozvrátit / Odložit, odročit, přerušit | Odstraněno | Disrupt narušuje průběh; adjourn je plánovaně přerušit/odročit jednání. |
| 145 | 456/1361 | Appetite / Lust | Chuť, chtíč / Chtíč | Diskutabilní | Lust je převážně silná, zejména sexuální touha; appetite má i tento význam, ale aktuální příklad je chuť k jídlu. |
| 146 | 456/1776 | Appetite / Inclination | Chuť, chtíč / Sklon, chuť | Diskutabilní | Appetite for a inclination to mají rozdílné vazby a rozsah; společná chuť něco udělat není univerzální. |
| 147 | 462/1438 | Abandon / Surrender | Opustit, vzdát se / Vzdát se | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 148 | 463/1276 | Malicious / Vicious | Škodlivý, zlomyslný / Zlý, brutální, zlomyslný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 149 | 463/2177 | Malicious / Malignant | Škodlivý, zlomyslný / Zhoubný, zlomyslný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 150 | 463/2611 | Malicious / Detrimental | Škodlivý, zlomyslný / Škodlivý, neblahý, škodící | Odstraněno | Malicious vyjadřuje zlý úmysl, detrimental škodlivý účinek bez nutného úmyslu. |
| 151 | 466/478 | Soothe / Loosen | Uklidnit, zmírnit, ukonejšit / Uvolnit, rozvázat, zmírnit | Odstraněno | Soothe uklidňuje nebo tiší bolest, loosen povoluje sevření či uzel. |
| 152 | 466/1223 | Soothe / Mitigate | Uklidnit, zmírnit, ukonejšit / Zmírnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 153 | 466/2608 | Soothe / Alleviate | Uklidnit, zmírnit, ukonejšit / Zmírnit, zmenšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 154 | 466/2639 | Soothe / Appease | Uklidnit, zmírnit, ukonejšit / Usmířit, uklidnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 155 | 467/1251 | Laughter / Mirth | Smích / Veselí, smích | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 156 | 469/779 | Affair / Incident | Záležitost, aféra, událost / Incident, událost, příhoda | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 157 | 470/1437 | Bear / Withstand | Nést, unést, snést / Odolat, vydržet, snést | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 158 | 470/1635 | Bear / Abide | Nést, unést, snést / Zůstat, dodržet, snést | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 159 | 472/573 | Revive / Renew | Oživit, obnovit / Obnovit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 160 | 472/1287 | Revive / Jazz up | Oživit, obnovit / Oživit, zpestřit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 161 | 472/1476 | Revive / Reinvigorate | Oživit, obnovit / Oživit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 162 | 472/1525 | Revive / Restore | Oživit, obnovit / Obnovit, vrátit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 163 | 472/1606 | Revive / Reinstate | Oživit, obnovit / Obnovit, zpět dosadit do funkce | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 164 | 472/2121 | Revive / Retrieve | Oživit, obnovit / Načíst, získat zpět, obnovit | Odstraněno | Retrieve získává něco zpět či načítá data; revive/renew/restore/reinstate obnovují život, stav, platnost či funkci. |
| 165 | 473/1725 | Abyss / Chasm | Propast / Propast, rokle | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 166 | 474/1920 | Gravely / Sorely | Vážně, těžce / Velice, těžce, intenzivně | Odstraněno | Gravely vyjadřuje vážnost/závažnost; sorely míru nepříjemného pocitu či nedostatku (sorely missed). |
| 167 | 478/1223 | Loosen / Mitigate | Uvolnit, rozvázat, zmírnit / Zmírnit | Odstraněno | Loosen uvolňuje něco pevného/sevřeného; mitigate/alleviate zmírňují závažnost či obtíže. |
| 168 | 478/2608 | Loosen / Alleviate | Uvolnit, rozvázat, zmírnit / Zmírnit, zmenšit | Odstraněno | Loosen uvolňuje něco pevného/sevřeného; mitigate/alleviate zmírňují závažnost či obtíže. |
| 169 | 482/1715 | Tear / Rip | Roztrhnout, rozervat / Roztrhnout, rozpárat, rozervat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 170 | 488/634 | Sombre / Grim | Temný, ponurý / Ponurý, chmurný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 171 | 488/842 | Sombre / Lurid | Temný, ponurý / Děsný, ponurý, smrtelně bledý | Odstraněno | Lurid je křiklavý nebo šokujícím způsobem explicitní; sombre/grim/gloomy ponurý. Jiná kvalita obrazu i nálady. |
| 172 | 488/885 | Sombre / Gloomy | Temný, ponurý / Ponurý, sklíčený, pochmurný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 173 | 491/894 | Armistice / Truce | Příměří / Příměří | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 174 | 492/1616 | Remembrance / Recollection | Vzpomínka / Vzpomínka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 175 | 503/713 | Cunning / Deft | Mazaný, šikovný, lstivý / Obratný, hbitý, šikovný | Diskutabilní | Cunning ve významu zručný je omezenější; běžně vyjadřuje lstivost, deft fyzickou či jinou obratnost. |
| 176 | 503/1571 | Cunning / Dextrous | Mazaný, šikovný, lstivý / Šikovný, zručný, obratný | Diskutabilní | Cunning běžně znamená lstivý, dextrous manuálně zručný; historický význam skilled ponechán k posouzení. |
| 177 | 503/1895 | Cunning / Shrewd | Mazaný, šikovný, lstivý / Chytrý, mazaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 178 | 503/1970 | Cunning / Sly | Mazaný, šikovný, lstivý / Potutelný, šibalský, lišácký, lstivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 179 | 503/2172 | Cunning / Nifty | Mazaný, šikovný, lstivý / Šikovný, mazaný, důmyslný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 180 | 504/1054 | Wretched / Lousy | Ubohý, mizerný, bídný / Mizerný, protivný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 181 | 504/1550 | Wretched / Miserable | Ubohý, mizerný, bídný / Nešťastný, mizerný, utrápený, bídný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 182 | 504/1595 | Wretched / Abysmal | Ubohý, mizerný, bídný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 183 | 504/1875 | Wretched / Grotty | Ubohý, mizerný, bídný / Odporný, hnusný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 184 | 504/2074 | Wretched / Crummy | Ubohý, mizerný, bídný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 185 | 504/2457 | Wretched / Cheesy | Ubohý, mizerný, bídný / Laciný, ubohý | Odstraněno | Wretched je nešťastný či mizerný; cheesy laciný, kýčovitý nebo nuceně sentimentální. |
| 186 | 504/2481 | Wretched / Sleazy | Ubohý, mizerný, bídný / Špinavý, ubohý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 187 | 506/1366 | Fate / Destiny | Osud / Osud, úděl | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 188 | 508/577 | Horrid / Dire | Hrozný, špatný, ohavný / Katastrofální, strašný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 189 | 508/1212 | Horrid / Despicable | Hrozný, špatný, ohavný / Opovrženíhodný, ohavný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 190 | 508/1595 | Horrid / Abysmal | Hrozný, špatný, ohavný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 191 | 508/1923 | Horrid / Excruciating | Hrozný, špatný, ohavný / Nesnesitelný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 192 | 508/1984 | Horrid / Odious | Hrozný, špatný, ohavný / Odporný, ohavný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 193 | 508/2007 | Horrid / Hideous | Hrozný, špatný, ohavný / Škaredý, ohizdný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 194 | 511/759 | Oaf / Knucklehead | Trouba, spratek, ohava / Trouba, típek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 195 | 511/1431 | Oaf / Brat | Trouba, spratek, ohava / Spratek | Odstraněno | Oaf je neohrabaný hlupák, brat nevychované dítě. Věk, chování a mentální vlastnost nejsou totožné. |
| 196 | 511/1690 | Oaf / Mug | Trouba, spratek, ohava / Džbánek, trouba, moula | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 197 | 511/1926 | Oaf / Wally | Trouba, spratek, ohava / Pitomec, blbec, trouba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 198 | 511/2491 | Oaf / Nitwit | Trouba, spratek, ohava / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 199 | 515/633 | Underpin / Bolster | Podepřít, podpírat / Posílit, podepřít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 200 | 515/1425 | Underpin / Corroborate | Podepřít, podpírat / Potvrdit, podepřít, posílit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 201 | 517/633 | Beef up / Bolster | Posílit / Posílit, podepřít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 202 | 517/1425 | Beef up / Corroborate | Posílit / Potvrdit, podepřít, posílit | Odstraněno | Beef up obecně posiluje; corroborate potvrzuje tvrzení podpůrným důkazem. |
| 203 | 520/2548 | Prevent / Stymie | Zabránit, předejít / Zabránit, překážet, stát v cestě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 204 | 526/1896 | Attentive / Observant | Pozorný / Všímavý, pozorný, bystrý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 205 | 528/2613 | Assume / Presume | Předpokládat / Předpokládat, domnívat se, mít za to | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 206 | 533/1297 | Preserve / Retain | Zachovat, chránit, uchovat / Udržet si, ponechat si, zachovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 207 | 535/1848 | Ire / Wrath | Hněv, zloba / Hněv, zloba, rozhořčení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 208 | 541/2438 | Adhere / Uphold | Dodržovat, držet se / Prosazovat, dodržovat, podporovat | Diskutabilní | Adhere to pravidla dodržuje, uphold je hájí či udržuje v platnosti. Rozdílné gramatické vazby. |
| 209 | 541/2498 | Adhere / Cling | Dodržovat, držet se / Držet se, přilnout k | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 210 | 557/2131 | Linger / Loiter | Prodlévat, loudat se / Loudat se, flákat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 211 | 557/2500 | Linger / Dawdle | Prodlévat, loudat se / Loudat se, courat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 212 | 558/2503 | Humid / Damp | Vlhký / Vlhký | Diskutabilní | Humid zpravidla popisuje vlhký vzduch, damp i povrch. Společný kontext je vlhké prostředí. |
| 213 | 563/640 | Refuse / Deny | Odpad, odpadky, Odmítnout / Popřít, odmítnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 214 | 567/1429 | Estate / Asset | Majetek, statek, jmění / Aktiva, jmění, majetek | Odstraněno | Estate označuje majetkový celek, pozůstalost či panství; asset jednotlivé aktivum/přínosnou věc. |
| 215 | 569/2066 | Core / Substance | Jádro / Obsah, jádro, látka, hmota, důležitost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 216 | 569/2108 | Core / Crux | Jádro / Jádro, podstata | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 217 | 573/1525 | Renew / Restore | Obnovit / Obnovit, vrátit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 218 | 573/1606 | Renew / Reinstate | Obnovit / Obnovit, zpět dosadit do funkce | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 219 | 573/2121 | Renew / Retrieve | Obnovit / Načíst, získat zpět, obnovit | Odstraněno | Retrieve získává něco zpět či načítá data; revive/renew/restore/reinstate obnovují život, stav, platnost či funkci. |
| 220 | 575/2548 | Hinder / Stymie | Překážet / Zabránit, překážet, stát v cestě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 221 | 577/1595 | Dire / Abysmal | Katastrofální, strašný, hrozný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 222 | 577/1923 | Dire / Excruciating | Katastrofální, strašný, hrozný / Nesnesitelný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 223 | 577/2007 | Dire / Hideous | Katastrofální, strašný, hrozný / Škaredý, ohizdný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 224 | 578/1191 | Outdated / Corny | Zastaralý / Zastaralý | Odstraněno | Corny je otřepaný, banální či sentimentálně kýčovitý; obsolete/outdated znamená zastaralý nebo překonaný. |
| 225 | 578/1877 | Outdated / Obsolete | Zastaralý / Zastaralý, překonaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 226 | 581/1102 | Gain / Accomplish | Získat, dosáhnout / Dosáhnout, splnit, provést | Odstraněno | Gain získává výhodu/znalost/vítězství, accomplish vykoná či dokončí úkol. Jiná předmětová vazba. |
| 227 | 582/1184 | Exacerbate / Aggravate | Zhoršit, ztížit, zvýšit (negativně) / Zhoršit, přitížit, naštvat, popudit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 228 | 583/899 | Deficiency / Shortage | Nedostatek, schodek, manko / Nedostatek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 229 | 583/1713 | Deficiency / Lack | Nedostatek, schodek, manko / Nedostatek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 230 | 583/1723 | Deficiency / Scarcity | Nedostatek, schodek, manko / Nedostatek, nouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 231 | 586/1654 | Settlement / Hamlet | Osada / Osada, vesnička, víska | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 232 | 590/1530 | Diminish / Abate | Snížit / Slábnout, snížit, omezit, zmenšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 233 | 593/2514 | Benefit / Boon | Výhoda / Požehnání, přínos, výhoda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 234 | 594/1263 | In fact / As a matter of fact | Ve skutečnosti / Ve skutečnosti | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 235 | 596/1221 | Crucial / Paramount | Rozhodující, stěžejní / Rozhodující, nejvyšší, svrchovaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 236 | 605/2268 | Conservation / Retention | Zachování / Zachování, udržení | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 237 | 607/614 | Inhibit / Suppress | Potlačit, omezit, bránit / Potlačit, zatajit, umlčet | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 238 | 607/768 | Inhibit / Repress | Potlačit, omezit, bránit / Potlačit, utlačit, zadržet | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 239 | 607/1530 | Inhibit / Abate | Potlačit, omezit, bránit / Slábnout, snížit, omezit, zmenšit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 240 | 607/1560 | Inhibit / Stifle | Potlačit, omezit, bránit / Potlačit, utlumit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 241 | 607/1632 | Inhibit / Defend | Potlačit, omezit, bránit / Hájit, bránit | Odstraněno | Inhibit znamená bránit něčemu v činnosti; defend bránit něco před ohrožením. České bránit má opačné role. |
| 242 | 609/939 | Commitment / Bond | Závazek / Vázat, spojit, závazek | Diskutabilní | Bond může být právní závazek, ale uložený příklad je citové pouto; commitment závazek/oddanost. |
| 243 | 610/1074 | Incompetent / Incapacitated | Neschopný, neoprávněný / Neschopný | Odstraněno | Incompetent je bez potřebné způsobilosti/dovednosti; incapacitated neschopný činnosti např. zraněním. |
| 244 | 611/2150 | Precisely / Rigorously | Přesně / Přísně, pečlivě, přesně | Odstraněno | Precisely vyjadřuje přesnost, rigorously přísnost a důslednost postupu. |
| 245 | 614/768 | Suppress / Repress | Potlačit, zatajit, umlčet / Potlačit, utlačit, zadržet | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 246 | 614/1560 | Suppress / Stifle | Potlačit, zatajit, umlčet / Potlačit, utlumit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 247 | 616/1549 | Flee / Elope | Uprchnout, utéci / Utéci, zdrhnout | Odstraněno | Elope označuje tajný útěk za účelem sňatku; flee obecný útěk před nebezpečím. |
| 248 | 626/1589 | Scam / Con | Podvod / Podvod, bouda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 249 | 626/2055 | Scam / Fraud | Podvod / Podvod, podvodník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 250 | 626/2247 | Scam / Humbug | Podvod / Habaďůra, podvod, přetvářka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 251 | 629/1453 | Sheer / Overwhelming | Naprostý, čirý / Ohromný, nesmírný, zdrcující, naprostý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 252 | 632/2189 | Further / Hereafter | Dále / Dále, na onom světě | Odstraněno | Further je dále v prostoru, míře či výkladu; hereafter od nynějška v budoucnu. |
| 253 | 633/1425 | Bolster / Corroborate | Posílit, podepřít / Potvrdit, podepřít, posílit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 254 | 634/842 | Grim / Lurid | Ponurý, chmurný / Děsný, ponurý, smrtelně bledý | Odstraněno | Lurid je křiklavý nebo šokujícím způsobem explicitní; sombre/grim/gloomy ponurý. Jiná kvalita obrazu i nálady. |
| 255 | 634/885 | Grim / Gloomy | Ponurý, chmurný / Ponurý, sklíčený, pochmurný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 256 | 636/789 | Dispute / Clash | Spor, pře, brát v pochybnost, debatovat / Střet, spor | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 257 | 636/1376 | Dispute / Strife | Spor, pře, brát v pochybnost, debatovat / Svár, spor, rozboje | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 258 | 638/1386 | Prospective / Anticipated | Budoucí, případný, očekávaný / Očekávaný, předpokládaný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 259 | 644/2034 | Endeavour / Strive | Usilovat / Usilovat | Diskutabilní | Endeavour je uložen jako Noun, český význam i příklad jsou slovesné. Strive odpovídá slovesnému významu. |
| 260 | 645/1916 | Patch up / Enhance | Vylepšit, srovnat / Zlepšit, vylepšit, zvýraznit | Odstraněno | Patch up opravuje poškozený stav či vztahy; enhance zvyšuje kvalitu/hodnotu. Zlepšit není automaticky opravit. |
| 261 | 649/751 | Peril / Hazard | Nebezpečí, riziko / Nebezpečí, risk, hazard | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 262 | 651/1176 | Treachery / Treason | Zdara / Zdara, velezrada | Odstraněno | Treason je velezrada/zrada státu, treachery obecná zrada důvěry. Zde je právní podtyp vydáván za obecnou synonymii. |
| 263 | 660/1285 | Nuisance / Hassle | Otrava, nepříjemnost / Hádka, nepříjemnost, potíž | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 264 | 667/783 | Esteem / Tribute | Úcta, vážit si / Hold, úcta | Odstraněno | Esteem je úcta; tribute její vyjádření nebo pocta. |
| 265 | 676/2607 | Elaborate / Intricate | Propracovaný, komplikovaný, podrobný / Složitý, komplikovaný, spletitý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 266 | 679/1298 | Alter / Amend | Změnit, pozměnit, upravit / Pozměnit, opravit, polepšit, doplinit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 267 | 680/684 | Token / Trace | Znamení, známka, upomínka / Stopa, náznak, známka | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 268 | 680/1265 | Token / Omen | Znamení, známka, upomínka / Znamení | Odstraněno | Token je symbol či doklad; omen předzvěst budoucí události. Nestačí společné české znamení. |
| 269 | 696/2592 | Chieftain / Headman | Náčelník / Náčelník, předák, vedoucí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 270 | 697/875 | Manner / Conduct | Způsob, chování, vystupování / Chování, vedení, řízení, počínání | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 271 | 698/806 | Strain / Strain | Kmen, druh, plemeno / Namáhat, napnout | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 272 | 699/1302 | Mingle / Blend | Míchat, smísit, prolínat se / Míchat, mísit, směs, splinutí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 273 | 707/1722 | Stocky / Pudgy | Zavalitý, robustný, menší a robustní / Vypasený, oplácaný, zavalitý | Diskutabilní | Stocky je krátký a robustní, pudgy mírně obtloustlý; rozdíl tělesného typu. |
| 274 | 708/1951 | Stout / Thick | Statný, silný, tlustý / Tlustý, hustý, silný, těžký | Diskutabilní | Stout člověk je robustní/obtloustlý; thick člověk může být hloupý. Platí pouze fyzická mohutnost. |
| 275 | 708/2531 | Stout / Bouncing | Statný, silný, tlustý / Statný, zdravý, silný | Odstraněno | Bouncing u dítěte znamená zdravý a čilý; stout/hefty robustní, těžký či mohutný. |
| 276 | 708/2555 | Stout / Hefty | Statný, silný, tlustý / Statný, mocný, robustní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 277 | 713/714 | Deft / Nimble | Obratný, hbitý, šikovný / Hbitý, mrštný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 278 | 713/762 | Deft / Adept | Obratný, hbitý, šikovný / Obratný, zběhlý, zkušený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 279 | 713/1571 | Deft / Dextrous | Obratný, hbitý, šikovný / Šikovný, zručný, obratný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 280 | 713/2135 | Deft / Agile | Obratný, hbitý, šikovný / Hbitý, mrštný, čilý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 281 | 713/2172 | Deft / Nifty | Obratný, hbitý, šikovný / Šikovný, mazaný, důmyslný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 282 | 714/2135 | Nimble / Agile | Hbitý, mrštný / Hbitý, mrštný, čilý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 283 | 722/2356 | Tentative / Preliminary | Orientační, předběžný, váhavý / Předběžný, úvodní, přípravný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 284 | 723/1004 | Mourn / Wail | Truchlit, oplakávat, naříkat / Naříkat, kvílet | Odstraněno | Mourn/lament vyjadřují truchlení, whimper/wail způsob vydávání zvuku. Samotné kňučení ani hlasitý pláč nejsou truchlením. |
| 285 | 723/1889 | Mourn / Lament | Truchlit, oplakávat, naříkat / Naříkat, bědovat, truchlit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 286 | 723/2474 | Mourn / Whimper | Truchlit, oplakávat, naříkat / Fňukat, kňučet, naříkat | Odstraněno | Mourn/lament vyjadřují truchlení, whimper/wail způsob vydávání zvuku. Samotné kňučení ani hlasitý pláč nejsou truchlením. |
| 287 | 736/1023 | Petty / Minor | Malý, drobný / Malý, drobný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 288 | 741/1797 | Jaunty / Breezy | Veselý, bezstarostný, bujarý / Živý, veselý, svěží | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 289 | 741/2518 | Jaunty / Jolly | Veselý, bezstarostný, bujarý / Rozjřený, veselý, příjemný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 290 | 758/2050 | Pageantry / Pageant | Sláva, pompa, slavnost / Slavnost, průvod | Diskutabilní | Pageantry je okázalá podívaná/pompa, pageant konkrétní slavnost/průvod. Rozdíl děje a charakteru. |
| 291 | 759/1690 | Knucklehead / Mug | Trouba, típek / Džbánek, trouba, moula | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 292 | 759/1926 | Knucklehead / Wally | Trouba, típek / Pitomec, blbec, trouba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 293 | 759/2491 | Knucklehead / Nitwit | Trouba, típek / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 294 | 760/872 | Menace / Threat | Hrozba, výhružka / Hrozba, výhružka, ohrožení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 295 | 762/1571 | Adept / Dextrous | Obratný, zběhlý, zkušený / Šikovný, zručný, obratný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 296 | 764/1868 | Dork / Dimwit | Trapák, hňup / Tupec, hňup | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 297 | 764/2310 | Dork / Dolt | Trapák, hňup / Blb, hňup, pitomec | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 298 | 764/2512 | Dork / Twit | Trapák, hňup / Pitomec, hňup | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 299 | 766/1502 | Embark / Commence | Nastupovat, začít, pustit se / Zahájit, začít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 300 | 768/1560 | Repress / Stifle | Potlačit, utlačit, zadržet / Potlačit, utlumit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 301 | 775/1016 | Gross / Crude | Hrubý, těžký, nepřípustný / Surový, hrubý, drsný, sprostý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 302 | 775/1187 | Gross / Outrageous | Hrubý, těžký, nepřípustný / Ostudný, urážlivý, hrubý, nemravný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 303 | 784/2165 | Initiative / Incentive | Iniciativa, podnět / Popud, podnět, stimul | Odstraněno | Initiative je iniciativa či počáteční vlastní akce; incentive podnět/motivace k akci. |
| 304 | 785/2468 | Salvation / Redemption | Spása / Vykoupení, spása, splacení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 305 | 789/1376 | Clash / Strife | Střet, spor / Svár, spor, rozboje | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 306 | 791/928 | Remote / Remote | Dálkový, odlehlý / Dálový ovladač | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 307 | 791/1661 | Remote / Far-flung | Dálkový, odlehlý / Vzdálený, odlehlý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 308 | 795/1449 | Yell / Shriek | Křičet, ječet / Ječet, vřískat, křičet, jekot | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 309 | 798/2578 | Contempt / Disdain | Pohrdání / Pohrdání | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 310 | 801/2311 | Suspend / Stall | Pozastavit / Pozastavit, pozdržet se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 311 | 805/2646 | Chiefly / Predominantly | Především, hlavně / Převážně, hlavně, především | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 312 | 807/1629 | Reward / Bounty | Odměna / Odměna, štědrost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 313 | 809/2100 | Tempt / Lure | Pokoušet, svádět, lákat / Lákat, návnada, vábit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 314 | 810/1052 | Crouch / Wiggle | Kroutit, hrbit, dřepnout / Kroutit, vrtět, viklat se, kývat se | Odstraněno | Crouch je snížit tělo pokrčením kolen; wiggle/twist vrtět či kroutit. Rozdílný pohyb. |
| 315 | 810/1205 | Crouch / Twist | Kroutit, hrbit, dřepnout / Kroutit, otáčet, točit | Odstraněno | Crouch je snížit tělo pokrčením kolen; wiggle/twist vrtět či kroutit. Rozdílný pohyb. |
| 316 | 812/1848 | Indignation / Wrath | Rozhořčení, pohoršení / Hněv, zloba, rozhořčení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 317 | 819/953 | Manure / Muck | Hnůj / Hnůj, sviňstvo, zakydat, pošpinit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 318 | 820/1079 | Pierce / Stab | Prorazit, proniknout, probodnout / Bodnout, probodnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 319 | 821/1312 | Haze / Mist | Opar, mlha / Mlha, opar, zamlžení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 320 | 824/844 | Mob / Rabble | Dav, lůza, zástup / Lůza | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 321 | 824/1474 | Mob / Multitude | Dav, lůza, zástup / Zástup, dav | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 322 | 825/1486 | Villain / Crook | Darebák, padouch, ničema / Podvodník, gauner, darebák | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 323 | 825/2242 | Villain / Rascal | Darebák, padouch, ničema / Lump, darebák, lotr | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 324 | 827/2474 | Squeal / Whimper | Kvičet, kňučet, kňourat / Fňukat, kňučet, naříkat | Odstraněno | Squeal/wail jsou pronikavé či hlasité zvuky; whimper tiché, slabé kňučení. Odlišný charakter projevu. |
| 325 | 830/1878 | Liberation / Exemption | Osvobození / Osvobození | Odstraněno | Liberation je osvobození z útlaku, exemption výjimka z povinnosti a acquittal zproštění obžaloby. Tři odlišné významy osvobození. |
| 326 | 830/2302 | Liberation / Acquittal | Osvobození / Osvobození | Odstraněno | Liberation je osvobození z útlaku, exemption výjimka z povinnosti a acquittal zproštění obžaloby. Tři odlišné významy osvobození. |
| 327 | 832/887 | Arouse / Kindle | Vzbudit, vyburcovat / Roznítit, zapálit, vzbudit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 328 | 832/1914 | Arouse / Galvanize | Vzbudit, vyburcovat / Vyburcovat, podnítit, vzbudit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 329 | 833/916 | Soaked / Drenched | Namočený / Promočený, promáčený, namočený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 330 | 842/885 | Lurid / Gloomy | Děsný, ponurý, smrtelně bledý / Ponurý, sklíčený, pochmurný | Odstraněno | Lurid je křiklavý nebo šokujícím způsobem explicitní; sombre/grim/gloomy ponurý. Jiná kvalita obrazu i nálady. |
| 331 | 842/1303 | Lurid / Gruesome | Děsný, ponurý, smrtelně bledý / Příšerný, hrůzný, děsný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 332 | 846/2313 | Upperclass / Gentry | Vyšší třída, aristokracie, asristokratický / Panstvo, šlechta, aristokracie | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 333 | 852/1649 | Wrestle / Grapple | Zápasit / Zápasit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 334 | 868/1416 | Vocal / Tumultuous | Hlasitý / Bouřlivé, prudký, hlasitý | Odstraněno | Vocal zde popisuje hlasité vyjadřování názorů; tumultuous bouřlivý hluk/neuspořádanost. |
| 335 | 868/1594 | Vocal / Vociferous | Hlasitý / Hlasitý, důrazný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 336 | 873/2659 | Assessment / Appraisal | Posouzení, odhad, ohodnocení / Posouzení, zhodnocení, vyhodnocení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 337 | 875/1380 | Conduct / Guidance | Chování, vedení, řízení, počínání / Vedení, navádění, řízení | Odstraněno | Conduct je chování nebo řízení činnosti; guidance rada/navádění poskytované někomu. |
| 338 | 880/1864 | Confidential / Clandestine | Důverný, tajný / Tajný, ilegální | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 339 | 884/1131 | Indict / Accuse | Obvinit / Obvinit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 340 | 887/1914 | Kindle / Galvanize | Roznítit, zapálit, vzbudit / Vyburcovat, podnítit, vzbudit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 341 | 890/1703 | Hose / Hose | Hadice / Punčochy | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 342 | 896/1390 | Encourage / Endorse | Povzbudit, podporovat / Schvalovat, podporovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 343 | 896/1639 | Encourage / Foster | Povzbudit, podporovat / Podporovat, rozvíjet | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 344 | 896/2438 | Encourage / Uphold | Povzbudit, podporovat / Prosazovat, dodržovat, podporovat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 345 | 899/1713 | Shortage / Lack | Nedostatek / Nedostatek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 346 | 899/1723 | Shortage / Scarcity | Nedostatek / Nedostatek, nouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 347 | 900/2030 | Bold / Cheeky | Tučný, smělý, výrazný, troufalý / Troufalý, hubatý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 348 | 904/1192 | Discard / Ditch | Vyřadit, odhodit / Zbavit se, odhodit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 349 | 907/1930 | Shallow / Superficial | Mělký, povrchní / Povrchní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 350 | 908/2023 | Nagging / Pesky | Otravný, stále se ozývající, sekýrování / Otravný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 351 | 911/2387 | Indicate / Insinuate | Ukázat, označit, naznačit / Naznačit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 352 | 912/1621 | Swanky / Ritzy | Elegantní, luxusní, nóbl / Nóbl, hofo fogo, fajnový | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 353 | 914/1267 | Stairwell / Staircase | Schodiště / Schodiště | Odstraněno | Stairwell je prostor/šachta pro schodiště, staircase soustava schodů. Prostor a konstrukce nejsou totéž. |
| 354 | 916/1813 | Drenched / Soggy | Promočený, promáčený, namočený / Nasáklý, promočený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 355 | 917/2584 | Covet / Yearn | Toužit, prahnout / Toužit, stýskat si | Diskutabilní | Covet bývá touha vlastnit, zejména cizí věc; yearn for širší hluboká touha. Odlišná vazba. |
| 356 | 920/984 | Kook / Lunatic | Cvok, blázen / Blázen, šílenec, ztřeštěnec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 357 | 926/1850 | Anguish / Ordeal | Úzkost, muka, bolest / Utrpení, tvrdá zkouška, muka | Odstraněno | Anguish je prožívaná muka, ordeal těžká zkouška či událost, která je způsobuje. |
| 358 | 930/1031 | Faze / Dazzle | Ohromit, vyvést z konceptu, šokovat / Oslnit, uchvátit, ohromit | Odstraněno | Faze znamená vyvést z míry; dazzle/astound oslnit či ohromit údivem. |
| 359 | 930/1306 | Faze / Astound | Ohromit, vyvést z konceptu, šokovat / Ohromit, udivit, uvést v úžas | Odstraněno | Faze znamená vyvést z míry; dazzle/astound oslnit či ohromit údivem. |
| 360 | 931/2579 | Insecurity / Precariousness | Nejistota, vratkost / Nejistota, ošidnost, nebezpečnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 361 | 932/1804 | Eternal / Incessant | Věčný, neustálý, stálý / Neustálý, nepřetržitý, ustavičný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 362 | 933/1335 | Cranky / Sullen | Mrzutý / Mrzutý, zasmušilý, nevrlý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 363 | 940/1527 | Infuriate / Incense | Rozzuřit / Rozlítit, rozzuřit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 364 | 942/2219 | Persuasive / Conclusive | Přesvědčivý / Přesvědčivý, průkazný | Diskutabilní | Conclusive rozhodujícím způsobem prokazuje, persuasive přesvědčuje i bez definitivního důkazu. |
| 365 | 942/2610 | Persuasive / Compelling | Přesvědčivý / Přesvědčivý, pádný, závažný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 366 | 948/1787 | Loo / Lavatory | Toaleta / Záchod, toaleta | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 367 | 950/2587 | Persist / Persevere | Přetrvávají, vytrvat, trvat / Vytrvat, setrvat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 368 | 954/1283 | Snug / Cozy | Pohodlný, útulný / Útulný, pohodlný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 369 | 954/2159 | Snug / Convenient | Pohodlný, útulný / Praktický, pohodlný, příhodný, vhodný | Odstraněno | Snug/cozy znamená útulně pohodlný, convenient prakticky vyhovující či příhodný. |
| 370 | 964/1180 | Slog / Toil | Dřina / Dřina, lopotit se | Diskutabilní | Slog a toil jsou v příkladech i českých významech smíchané jako jména/slovesa; společná dřina je jasná, metadata nikoliv. |
| 371 | 969/2661 | Prone / Susceptible | Náchylný / Snadno podléhající, snadno ovlivnitelný, náchylný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 372 | 971/1026 | Uneventful / Tranquil | Klidný / Klidný, tichý, pokojný,  | Diskutabilní | Uneventful je bez mimořádných událostí, tranquil pokojný; mohou popsat stejnou cestu, ale jiné vlastnosti. |
| 373 | 971/1401 | Uneventful / Serene | Klidný / Klidný, nevzrušený, poklidný | Diskutabilní | Serene je vnitřně/pohledově klidný, uneventful bez událostí. Ponecháno pro kontext poklidného průběhu. |
| 374 | 971/1827 | Uneventful / Placid | Klidný / Klidný, tichý, poklidný | Diskutabilní | Placid znamená nevzrušivý/pokojný, uneventful bez událostí; nehodí se pro tutéž osobní vlastnost. |
| 375 | 976/2232 | Hunch / Not to have a clue | Tušení, předtucha / Nemít ponětí, tušení | Odstraněno | Hunch je intuitivní tušení; not to have a clue znamená nemít ponětí. Odlišná gramatická funkce i sdělení. |
| 376 | 978/1055 | Intestine / Gut | Střevo / Střevo | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 377 | 979/988 | Uptight / Edgy | Nevózní, napjatý, podrážděný / Podrážděný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 378 | 979/2390 | Uptight / Testy | Nevózní, napjatý, podrážděný / Nedutklivý, podrážděný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 379 | 986/1555 | Drifter / Vagrant | Tulák, darmošlap / Tulák, pobuda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 380 | 987/1551 | Terrific / Sublime | Úžasný / Božský, nádherný, úžasný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 381 | 988/2390 | Edgy / Testy | Podrážděný / Nedutklivý, podrážděný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 382 | 989/1447 | Flaw / It is down to you | Kaz, chyba / Je to na Tobě, Je to tvá zodpovědnost, chyba | Odstraněno | It is down to you přisuzuje odpovědnost; flaw/inadequacy/lapse pojmenovávají vadu či selhání. |
| 383 | 989/2395 | Flaw / Inadequacy | Kaz, chyba / Nedostatečnost, chyba, vada | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 384 | 989/2606 | Flaw / Lapse | Kaz, chyba / Poklesek, pochybení, chyba, selhání | Odstraněno | Flaw/inadequacy jsou vada či nedostatečnost; lapse jednotlivé dočasné pochybení/výpadek. |
| 385 | 990/2094 | Pimple / Zit | Vřídek, jebák / Jebák | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 386 | 994/2093 | Spasm / Cramp | Křeč, záchvat / Křeč | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 387 | 999/2557 | Blank / Vacant | Čistý, prázdný / Volný, prázdný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 388 | 1002/2162 | Perimeter / Threshold | Obvod, délka obvodu, hranice / Práh, zápřeží, hranice | Odstraněno | Perimeter je obvod/hranice celého útvaru; threshold práh vstupu či mezní hodnota. |
| 389 | 1004/1889 | Wail / Lament | Naříkat, kvílet / Naříkat, bědovat, truchlit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 390 | 1004/2474 | Wail / Whimper | Naříkat, kvílet / Fňukat, kňučet, naříkat | Odstraněno | Squeal/wail jsou pronikavé či hlasité zvuky; whimper tiché, slabé kňučení. Odlišný charakter projevu. |
| 391 | 1007/2563 | Slacker / Slob | Flákač, ulejvač / Flákač, prase, vepř | Diskutabilní | Slacker se vyhýbá práci, slob je líný a nepořádný. Překryv existuje jen v lenosti. |
| 392 | 1010/1483 | Shipment / Freight | Náklad / Náklad, dopravné, doprava | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 393 | 1011/1335 | Grumpy / Sullen | Nevrlý, nabručený / Mrzutý, zasmušilý, nevrlý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 394 | 1013/1653 | Exclude / Expel | Vyloučit / Vyloučit, vyhostit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 395 | 1016/1187 | Crude / Outrageous | Surový, hrubý, drsný, sprostý / Ostudný, urážlivý, hrubý, nemravný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 396 | 1016/2261 | Crude / Abrasive | Surový, hrubý, drsný, sprostý / Drsný, neomalený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 397 | 1020/1951 | Dense / Thick | Zabedněný, hustý / Tlustý, hustý, silný, těžký | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 398 | 1026/1401 | Tranquil / Serene | Klidný, tichý, pokojný,  / Klidný, nevzrušený, poklidný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 399 | 1026/1827 | Tranquil / Placid | Klidný, tichý, pokojný,  / Klidný, tichý, poklidný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 400 | 1031/1306 | Dazzle / Astound | Oslnit, uchvátit, ohromit / Ohromit, udivit, uvést v úžas | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 401 | 1031/1398 | Dazzle / Daze | Oslnit, uchvátit, ohromit / Omámení, ománit, oslnit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 402 | 1031/2604 | Dazzle / Captivate | Oslnit, uchvátit, ohromit / Uchvátit, upoutat, okouzlit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 403 | 1032/2095 | Wuss / Wimp | Měkota, padavka, slaboch / Slaboch, padavka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 404 | 1033/1837 | Brawl / Scuffle | Rvačka, bitka, potyčka / Rvačka, potyčka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 405 | 1035/2527 | Pact / Covenant | Pakt, smlouva / Smlouva | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 406 | 1037/1042 | Scamper / Scoot | Pelášit, běžet, cupitat, hopsat / Běžet, utíkat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 407 | 1037/1819 | Scamper / Scurry | Pelášit, běžet, cupitat, hopsat / Pelášit, hnát se, pospíchat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 408 | 1039/1136 | Commotion / Fuss | Rozruch, pozdvižení / Povyk, rozruch | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 409 | 1046/1671 | Disorder / Perturbation | Porucha, nepořádek / Porucha, odchylka | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 410 | 1046/1938 | Disorder / Havoc | Porucha, nepořádek / Chaos, zmatek, nepořádek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 411 | 1046/2436 | Disorder / Clutter | Porucha, nepořádek / Nepořádek, zmatek, haraburdí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 412 | 1048/2181 | Compartment / Scope | Přihrádka, prostor / Prostor, příležitost, rámec, rozsah | Odstraněno | Compartment je fyzická oddělená přihrádka; scope rozsah, rámec nebo prostor k činnosti. |
| 413 | 1051/1859 | Spider web / Cobweb | Pavučina / Pavučina | Diskutabilní | Cobweb může označovat především starou/nepoužívanou pavučinu; spider web i čerstvou síť. |
| 414 | 1052/1205 | Wiggle / Twist | Kroutit, vrtět, viklat se, kývat se / Kroutit, otáčet, točit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 415 | 1054/1550 | Lousy / Miserable | Mizerný, protivný / Nešťastný, mizerný, utrápený, bídný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 416 | 1054/1595 | Lousy / Abysmal | Mizerný, protivný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 417 | 1054/1875 | Lousy / Grotty | Mizerný, protivný / Odporný, hnusný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 418 | 1054/2074 | Lousy / Crummy | Mizerný, protivný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 419 | 1057/2473 | Courageous / Spunky | Odvážný, udatný / Odvážný, kurážný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 420 | 1060/2449 | Cub / Calf | Mládě / Tele, mládě | Odstraněno | Cub a calf označují mláďata různých skupin savců, ne dvě označení stejného mláděte. |
| 421 | 1061/2555 | Mighty / Hefty | Mocný, mohutný, silný / Statný, mocný, robustní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 422 | 1062/2317 | Convene / Summon | Svolat, sejít se / Svolat, povolat, předvolat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 423 | 1063/2336 | Vile / Nefarious | Hnusný, odporný, hanebný / Podlý, nekalý, hanebný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 424 | 1065/1455 | Pace / Velocity | Tempo, krok, rychlost, chůze / Rychlost | Diskutabilní | Pace je tempo/rychlost, velocity technická rychlost v určitém směru; technický kontext není totožný. |
| 425 | 1068/2250 | Disapprove / Deprecate | Neschvalovat, nesouhlasit, být proti / Odmítat, neschvalovat, nesouhlasit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 426 | 1069/2161 | Assert / Enforce | Prosadit, uplatnit / Prosadit, vynutit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 427 | 1071/1229 | Saucy / Impudent | Drzý, hubatý, přisprostlý / Drzý, nestoudný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 428 | 1071/1711 | Saucy / Insolent | Drzý, hubatý, přisprostlý / Drzý, nestydatý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 429 | 1071/2030 | Saucy / Cheeky | Drzý, hubatý, přisprostlý / Troufalý, hubatý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 430 | 1072/1692 | Decisively / By all means | Rozhodně, energicky / Rozhodně | Odstraněno | Decisively popisuje způsob rozhodné činnosti; by all means je souhlasné jistě/rozhodně ano. |
| 431 | 1083/2627 | Nausea / Dissent | Nevolnost, ošklivost, odpor / Nesouhlas, odpor, neshoda | Odstraněno | Nausea je nevolnost/odpor z hnusu; dissent názorový nesouhlas. |
| 432 | 1089/1592 | Confusion / Turmoil | Zmatek / Zmatek, vřava, chaos | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 433 | 1089/1938 | Confusion / Havoc | Zmatek / Chaos, zmatek, nepořádek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 434 | 1089/2436 | Confusion / Clutter | Zmatek / Nepořádek, zmatek, haraburdí | Odstraněno | Clutter je nepořádek/nahromaděné věci; confusion/turmoil/havoc zmatek, rozvrat či zpustošení. |
| 435 | 1092/1754 | Leash / Strap | Řemínek, vodítko pro psa / Řemen, řemínek | Odstraněno | Leash je vodítko ke zvířeti, strap obecný řemen/popruh. Funkční podtyp není obecně zaměnitelný. |
| 436 | 1093/1393 | Burden / Liability | Břemeno, přítěž, břímě / Přítěž, překážka, finanční závazek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 437 | 1093/2427 | Burden / Ballast | Břemeno, přítěž, břímě / Zátěž, přítěž | Diskutabilní | Ballast má figurativní přítěž, ale fyzický lodní balast je účelný, ne automaticky nežádoucí burden. |
| 438 | 1094/1154 | Faint / Ambiguous | Slabý, chabý, sotva patrný, nejasný / Nejednoznařný, nejasný, dvojsmyslný | Odstraněno | Ambiguous znamená připouštějící více výkladů, faint/hazy/nebulous slabě patrný či neurčitý. Dvojznačnost není totéž co vágnost. |
| 439 | 1094/1331 | Faint / Hazy | Slabý, chabý, sotva patrný, nejasný / Mlhavý, zamlžený, nejasný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 440 | 1094/1790 | Faint / Nebulous | Slabý, chabý, sotva patrný, nejasný / Mlhavý, nejasný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 441 | 1094/1840 | Faint / Feeble | Slabý, chabý, sotva patrný, nejasný / Slabý, chabý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 442 | 1100/1926 | Doofus / Wally | Blbec / Pitomec, blbec, trouba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 443 | 1100/2485 | Doofus / Dunce | Blbec / Tupec, poleno, blbec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 444 | 1110/1821 | Mar / Spoil | Pokazit, zkazit, zničit / Pokazit, zkazit, zhatit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 445 | 1115/2188 | Abolish / Revoke | Zrušit, odvolat / Zrušit, odvolat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 446 | 1123/2257 | Sanctuary / Sanctum | Útočiště, azyl, útulek / Úkryt, útočiště | Odstraněno | Sanctum je posvátný nebo soukromý chráněný prostor; sanctuary/haven útočiště poskytující bezpečí. |
| 447 | 1123/2554 | Sanctuary / Haven | Útočiště, azyl, útulek / Útočiště, úkryt, útulek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 448 | 1125/2068 | Hogwarts / Wart | Bradavice / Bradavice | Odstraněno | Hogwarts je vlastní jméno školy Bradavice; wart je kožní bradavice. |
| 449 | 1135/1739 | Ward / Partition | Oddělení / Přepážka, oddělení, příčka | Odstraněno | Ward je oddělení instituce, partition přepážka a squad organizovaná skupina. Český výraz oddělení směšuje nesouvisející významy. |
| 450 | 1135/2328 | Ward / Squad | Oddělení / Oddělení, oddíl, skupina | Odstraněno | Ward je oddělení instituce, partition přepážka a squad organizovaná skupina. Český výraz oddělení směšuje nesouvisející významy. |
| 451 | 1136/1301 | Fuss / Uproar | Povyk, rozruch / Vřava, povyk, rámus | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 452 | 1136/2064 | Fuss / Rampage | Povyk, rozruch / Řádění, povyk, divoce vyvádět | Odstraněno | Rampage je násilné ničivé řádění, fuss/uproar rozruch či povyk; hluk není totožný s násilným jednáním. |
| 453 | 1137/1591 | Wit / Acumen | Důvtip, vtip, vtipnost / Bystrost, důvtip | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 454 | 1144/1967 | Imperil / Jeopardize | Ohrozit / Ohrozit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 455 | 1148/1205 | Veer / Twist | Zatáčet, otáčet, měnit směr, stáčet / Kroutit, otáčet, točit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 456 | 1152/1287 | Rejuvenated / Jazz up | Omladit, oživit, osvěžit / Oživit, zpestřit | Odstraněno | Rejuvenated je přídavné jméno/příčestí omlazený; jazz up infinitiv oživit či zpestřit. |
| 457 | 1154/1331 | Ambiguous / Hazy | Nejednoznařný, nejasný, dvojsmyslný / Mlhavý, zamlžený, nejasný | Odstraněno | Ambiguous znamená připouštějící více výkladů, faint/hazy/nebulous slabě patrný či neurčitý. Dvojznačnost není totéž co vágnost. |
| 458 | 1154/1790 | Ambiguous / Nebulous | Nejednoznařný, nejasný, dvojsmyslný / Mlhavý, nejasný | Odstraněno | Ambiguous znamená připouštějící více výkladů, faint/hazy/nebulous slabě patrný či neurčitý. Dvojznačnost není totéž co vágnost. |
| 459 | 1156/2021 | Youngster / Chap | Mladík / Chlápek, mladík | Odstraněno | Youngster je mladý člověk/dítě, chap muž či chlapík bez podmínky nízkého věku. |
| 460 | 1158/2563 | Hog / Slob | Prase / Flákač, prase, vepř | Odstraněno | Hog je v uloženém významu zvíře; slob nepořádný či líný člověk. |
| 461 | 1160/1695 | Shaky / Insecure | Nejistý, vratký / Nejistý, vratký | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 462 | 1160/1705 | Shaky / Rickety | Nejistý, vratký / Vratký, rozvyklaný, chatrný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 463 | 1160/1720 | Shaky / Dubious | Nejistý, vratký / Nejistý, mající pochybnosti | Diskutabilní | Shaky argument může být dubious; nervózní třes nebo nejistý člověk není automaticky pochybovačný. |
| 464 | 1164/1462 | Spear / Lance | Kopí, oštěp, harpuna / Kopí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 465 | 1171/1594 | Emphatic / Vociferous | Důrazný / Hlasitý, důrazný | Diskutabilní | Emphatic je důrazný, vociferous i hlasitý; důraz nemusí být hlučný. |
| 466 | 1181/2059 | Inferior / Menial | Nižší, podřadný / Podřadný, nekvalifikovaný, nádenický | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 467 | 1188/1976 | Jog / Lope | Běhat, klusat / Klusat, běžet dlouhými kroky | Odstraněno | Jog a lope jsou různé způsoby běhu: pomalý klus oproti dlouhým pružným krokům. |
| 468 | 1191/1877 | Corny / Obsolete | Zastaralý / Zastaralý, překonaný | Odstraněno | Corny je otřepaný, banální či sentimentálně kýčovitý; obsolete/outdated znamená zastaralý nebo překonaný. |
| 469 | 1192/2058 | Ditch / Expunge | Zbavit se, odhodit / Zbavit se, zlikvidovat, vymazat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 470 | 1192/2124 | Ditch / Purge | Zbavit se, odhodit / Očistit, zbavit se, udělat čistku | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 471 | 1209/1952 | Misdemeanor / Transgression | Přestupek, přečin / Přestupek, hřích | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 472 | 1211/1551 | Divine / Sublime | Božský, andělský, nádherný / Božský, nádherný, úžasný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 473 | 1212/1984 | Despicable / Odious | Opovrženíhodný, ohavný / Odporný, ohavný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 474 | 1215/1409 | Entrust / Consign | Svěřit / Odevzdat, svěřit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 475 | 1223/2608 | Mitigate / Alleviate | Zmírnit / Zmírnit, zmenšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 476 | 1229/1711 | Impudent / Insolent | Drzý, nestoudný / Drzý, nestydatý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 477 | 1236/1682 | Grubby / Foul | Umouněný, špinavý, ušmudlaný / Odporný, hnusný, špinavý, znečistit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 478 | 1236/2481 | Grubby / Sleazy | Umouněný, špinavý, ušmudlaný / Špinavý, ubohý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 479 | 1237/1817 | Plump / Voluptuous | Baculatý, kyprý / Vnadný, kyprý, požitkářský, smyslný | Diskutabilní | Voluptuous hodnotí smyslné křivky, plump mírnou tloušťku. Zvláště u dítěte/zvířete nejsou zaměnitelné. |
| 480 | 1238/1733 | Jester / Buffoon | Šašek / Šašek, kašpar, klaun | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 481 | 1241/1275 | Rescue / Salvage | Zachránit, vyprostit / Zachránit | Diskutabilní | Rescue je zachránit z nebezpečí, salvage zachránit použitelný zbytek ztraceného/poškozeného majetku. |
| 482 | 1248/1309 | Affirm / Acknowledge | Potvrdit / Potvrdit, uznat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 483 | 1248/1425 | Affirm / Corroborate | Potvrdit / Potvrdit, podepřít, posílit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 484 | 1249/2122 | Allegation / Contention | Tvrzení / Tvrzení, názor, přesvědčení | Odstraněno | Allegation je tvrzení o provinění, contention tvrzení/zastávaný názor. Ne každé tvrzení je obvinění. |
| 485 | 1254/1458 | Pinnacle / Culmination | Vrchol / Vrchol, vyvrcholení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 486 | 1254/1955 | Pinnacle / Climax | Vrchol / Vyvrcholení, vrchol, , orgasmus | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 487 | 1258/1553 | Lewd / Garish | Oplzlý, neslušný / Křiklavý, neslušný | Odstraněno | Lewd je sexuálně oplzlý, garish barevně křiklavý/nevkusně nápadný. |
| 488 | 1258/1756 | Lewd / Salacious | Oplzlý, neslušný / Oplzlý, chlípný, obscénní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 489 | 1268/2451 | Likelihood / Plausibility | Pravděpodobnost / Věrohodnost, pravděpodobnost | Odstraněno | Likelihood je pravděpodobnost události, plausibility věrohodnost či uvěřitelnost tvrzení. |
| 490 | 1270/2088 | Asinine / Goofy | Pitomý, hloupý, idiotský / Pitomý, přihlouplý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 491 | 1270/2453 | Asinine / Daft | Pitomý, hloupý, idiotský / Hloupý, pitomý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 492 | 1270/2546 | Asinine / Sappy | Pitomý, hloupý, idiotský / Šťavnatý, sentimentální, přihlouplý, pitomý | Diskutabilní | Sappy má vedle sentimentálnosti i regionální hloupý; tuto vazbu nelze přenášet na sentimentálnost obecně. |
| 493 | 1276/2177 | Vicious / Malignant | Zlý, brutální, zlomyslný / Zhoubný, zlomyslný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 494 | 1283/2159 | Cozy / Convenient | Útulný, pohodlný / Praktický, pohodlný, příhodný, vhodný | Odstraněno | Snug/cozy znamená útulně pohodlný, convenient prakticky vyhovující či příhodný. |
| 495 | 1285/1885 | Hassle / Quarrel | Hádka, nepříjemnost, potíž / Hádka, roztržka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 496 | 1287/1476 | Jazz up / Reinvigorate | Oživit, zpestřit / Oživit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 497 | 1288/2669 | Phony / Bogus | Podvodník, falešný / Falešný, falšovaný, nepravý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 498 | 1291/1716 | Preposterous / Ludicrous | Pošetilé, absurdní / Naprosto směšné, absurdní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 499 | 1298/1460 | Amend / Mend | Pozměnit, opravit, polepšit, doplinit / Opravit, spravit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 500 | 1301/1592 | Uproar / Turmoil | Vřava, povyk, rámus / Zmatek, vřava, chaos | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 501 | 1301/2064 | Uproar / Rampage | Vřava, povyk, rámus / Řádění, povyk, divoce vyvádět | Odstraněno | Rampage je násilné ničivé řádění, fuss/uproar rozruch či povyk; hluk není totožný s násilným jednáním. |
| 502 | 1303/1513 | Gruesome / Obnoxious | Příšerný, hrůzný, děsný / Příšerný, hnusný, nesnesitelný | Odstraněno | Gruesome vzbuzuje hrůzu/odpor např. krvavým výjevem; obnoxious obtěžuje či je protivný. |
| 503 | 1304/1909 | Portrayal / Impersonation | Ztvárnění, portrét, ztělesnění / Zoosobnění, ztělesnění | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 504 | 1309/1425 | Acknowledge / Corroborate | Potvrdit, uznat / Potvrdit, podepřít, posílit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 505 | 1321/1829 | Chump / Moron | Vůl, pitomec, hlupák / Debil, kretén, pitomec | Diskutabilní | Moron je zpravidla hrubší a silněji znehodnocující než chump. Obě označují hlupáka, registr zůstává problém. |
| 506 | 1321/1926 | Chump / Wally | Vůl, pitomec, hlupák / Pitomec, blbec, trouba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 507 | 1321/2310 | Chump / Dolt | Vůl, pitomec, hlupák / Blb, hňup, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 508 | 1321/2491 | Chump / Nitwit | Vůl, pitomec, hlupák / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 509 | 1321/2512 | Chump / Twit | Vůl, pitomec, hlupák / Pitomec, hňup | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 510 | 1322/1555 | Bum / Vagrant | Vandrák, pobuda / Tulák, pobuda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 511 | 1322/2032 | Bum / Bum | Vandrák, pobuda / Zadek, prdýlka | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 512 | 1323/1681 | Jittery / Terrified | Nervózní, ztrémovaný, vylekaný / Vyděšený, vylekaný | Odstraněno | Jittery je nervózní a neklidný, terrified silně vyděšený; zásadně jiná intenzita a charakter. |
| 513 | 1326/2102 | Deceive / Dupe | Oklamat, podvést, ošálit / Oklamat, ošálit, napálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 514 | 1331/1790 | Hazy / Nebulous | Mlhavý, zamlžený, nejasný / Mlhavý, nejasný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 515 | 1331/2081 | Hazy / Drizzly | Mlhavý, zamlžený, nejasný / mlhavý, sychravý | Odstraněno | Drizzly označuje mrholení, hazy/nebulous mlhavost/nejasnost. Déšť a mlha nejsou synonyma. |
| 516 | 1338/2062 | Entail / Induce | Znamenat, způsobit / Přivodit, přivolat, způsobit | Odstraněno | Entail znamená obnášet či nutně vyžadovat; induce vyvolat příčinu/účinek. |
| 517 | 1340/2084 | Fluster / Jumble | Zmatek / Změs, směsice, zmatek, chaoz, staré krámy | Odstraněno | Fluster je rozrušit/zmást člověka, jumble smísit věci či jejich neuspořádaná směs. |
| 518 | 1347/1427 | Banish / Oust | Vyhnat, vyhostit / Vyhnat, vypudit, vystrnadit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 519 | 1347/1653 | Banish / Expel | Vyhnat, vyhostit / Vyloučit, vyhostit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 520 | 1357/1946 | Potion / Concoction | Lektvar / Směs, lektvar, odvar | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 521 | 1368/1416 | Fierce / Tumultuous | Divoký, prudký, dravý / Bouřlivé, prudký, hlasitý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 522 | 1368/1977 | Fierce / Feral | Divoký, prudký, dravý / Divoký, volně žijící | Odstraněno | Feral znamená divoce žijící/zdivočelý, fierce/ferocious zuřivý či dravý. Život bez domestikace neznamená agresivitu. |
| 523 | 1368/2220 | Fierce / Ferocious | Divoký, prudký, dravý / Divoký, dravý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 524 | 1374/1641 | Copious / Abundant | Hojný, obsažný / Hojný, bohatý, bujný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 525 | 1390/1639 | Endorse / Foster | Schvalovat, podporovat / Podporovat, rozvíjet | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 526 | 1390/2438 | Endorse / Uphold | Schvalovat, podporovat / Prosazovat, dodržovat, podporovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 527 | 1393/2427 | Liability / Ballast | Přítěž, překážka, finanční závazek / Zátěž, přítěž | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 528 | 1401/1827 | Serene / Placid | Klidný, nevzrušený, poklidný / Klidný, tichý, poklidný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 529 | 1402/1879 | Capture / Conquer | Zajmout, ukořistit, dobít / Dobít, podrobit si | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 530 | 1407/1408 | Yield / Revenue | Výtěžek, výnos / Celkový příjem, tržba, výnos | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 531 | 1407/1882 | Yield / Edict | Výtěžek, výnos / Výnos, edikt | Odstraněno | Edict je úřední nařízení; yield/revenue výtěžek či příjem. Dva zcela jiné významy českého výnos. |
| 532 | 1408/1882 | Revenue / Edict | Celkový příjem, tržba, výnos / Výnos, edikt | Odstraněno | Edict je úřední nařízení; yield/revenue výtěžek či příjem. Dva zcela jiné významy českého výnos. |
| 533 | 1416/1594 | Tumultuous / Vociferous | Bouřlivé, prudký, hlasitý / Hlasitý, důrazný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 534 | 1423/1500 | Bloodshed / Carnage | Krveprolití / Krveprolití | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 535 | 1424/1902 | Garner / Nab | Sesbírat, sebrat, získat / Sbalit, sebrat, čapnout, nachytat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 536 | 1434/1975 | Dulcet / Suave | Příjemný, sladký / Zdvořilý, příjemný | Odstraněno | Dulcet je sladce libozvučný, suave uhlazeně společenský a jolly veselý. Obecné příjemný neopravňuje propojení. |
| 537 | 1434/2518 | Dulcet / Jolly | Příjemný, sladký / Rozjřený, veselý, příjemný | Odstraněno | Dulcet je sladce libozvučný, suave uhlazeně společenský a jolly veselý. Obecné příjemný neopravňuje propojení. |
| 538 | 1436/1866 | Posterity / Offspring | Potomstvo, příští generace / Potomek, potomstvo | Diskutabilní | Posterity jsou budoucí generace, offspring vlastní potomstvo; překryv pouze u kolektivních potomků. |
| 539 | 1437/1557 | Withstand / Sustain | Odolat, vydržet, snést / Udržet, vydržet | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 540 | 1437/1635 | Withstand / Abide | Odolat, vydržet, snést / Zůstat, dodržet, snést | Diskutabilní | Abide ve významu snést je zastaralé/literární nebo v can’t abide; není obecné withstand. |
| 541 | 1441/2398 | Swamp / Fen | Bažina / Bažina, močál, mokřina | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 542 | 1441/2399 | Swamp / Bog | Bažina / Bažina, močál, mokřina | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 543 | 1444/1702 | Trifle / Trifle | Zahrávat si, žertovat / Maličkost, drobnost, hloupost | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 544 | 1446/2656 | Impasse / Stalemate | Slepá ulička, patová situace / Patová situace, mrtvý bod | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 545 | 1447/2395 | It is down to you / Inadequacy | Je to na Tobě, Je to tvá zodpovědnost, chyba / Nedostatečnost, chyba, vada | Odstraněno | It is down to you přisuzuje odpovědnost; flaw/inadequacy/lapse pojmenovávají vadu či selhání. |
| 546 | 1447/2606 | It is down to you / Lapse | Je to na Tobě, Je to tvá zodpovědnost, chyba / Poklesek, pochybení, chyba, selhání | Odstraněno | It is down to you přisuzuje odpovědnost; flaw/inadequacy/lapse pojmenovávají vadu či selhání. |
| 547 | 1451/1617 | Pitcher / Jug | Džbán, korbel / Džbán, konvice | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 548 | 1458/1955 | Culmination / Climax | Vrchol, vyvrcholení / Vyvrcholení, vrchol, , orgasmus | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 549 | 1459/1815 | Bashful / Coy | Stydlivý, ostýchavý / Nesmělý, stydlivý, zdrženlivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 550 | 1460/2156 | Mend / Rectify | Opravit, spravit / Napravit, dát do pořádku, spravit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 551 | 1472/1689 | Impressive / Glamorous | Působivý, úchvatný / Okouzlující, úchvatný, oslnivý, přitažlivý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 552 | 1486/2055 | Crook / Fraud | Podvodník, gauner, darebák / Podvod, podvodník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 553 | 1486/2242 | Crook / Rascal | Podvodník, gauner, darebák / Lump, darebák, lotr | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 554 | 1491/1829 | Arse / Moron | Prdel, zadek, debil, prevít / Debil, kretén, pitomec | Diskutabilní | Arse jako nadávka není totéž co moron v každém kontextu a je vulgárnější; anatomický význam sem nepatří. |
| 555 | 1491/2032 | Arse / Bum | Prdel, zadek, debil, prevít / Zadek, prdýlka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 556 | 1493/1542 | Molest / Intrude | Obtěžovat / Zasahovat, obtěžovat, vyrušovat | Odstraněno | Molest v současném běžném užití označuje zejména sexuální napadení/zneužití; obecné obtěžování či vyrušování je jiný význam. |
| 557 | 1493/2371 | Molest / Pester | Obtěžovat / Obtěžovat, otravovat | Odstraněno | Molest v současném běžném užití označuje zejména sexuální napadení/zneužití; obecné obtěžování či vyrušování je jiný význam. |
| 558 | 1495/1684 | Horrified / Aghast | Zděšený, šokovaný, naplněný hrůzou / Zděšený, naplněný hrůzou | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 559 | 1496/2439 | Redundant / Superfluous | Přebytečný, nadpočetný, nepotřebný / Nadbytečný, přebytečný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 560 | 1497/2304 | Malice / Grudge | Zlomyslnost, zášť / Zášť, nevraživost, averze | Diskutabilní | Malice vyjadřuje zlý úmysl, grudge dlouhodobou osobní zášť. Česká zášť oba významy zplošťuje. |
| 561 | 1513/1923 | Obnoxious / Excruciating | Příšerný, hnusný, nesnesitelný / Nesnesitelný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 562 | 1513/2010 | Obnoxious / Intolerable | Příšerný, hnusný, nesnesitelný / Nesnesitelný, neúnosný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 563 | 1516/2024 | Amendment / Betterment | Zlepšení, úprava, dodatek / Zlepšení, zdokonalení | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 564 | 1516/2137 | Amendment / Addendum | Zlepšení, úprava, dodatek / Dodatek, příloha | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 565 | 1525/1606 | Restore / Reinstate | Obnovit, vrátit / Obnovit, zpět dosadit do funkce | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 566 | 1525/2121 | Restore / Retrieve | Obnovit, vrátit / Načíst, získat zpět, obnovit | Odstraněno | Retrieve získává něco zpět či načítá data; revive/renew/restore/reinstate obnovují život, stav, platnost či funkci. |
| 567 | 1529/2193 | Response / Repercussion | Odezva / Odezva, následek | Odstraněno | Response je odpověď/reakce, repercussion typicky nepřímý nepříznivý následek. |
| 568 | 1530/2608 | Abate / Alleviate | Slábnout, snížit, omezit, zmenšit / Zmírnit, zmenšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 569 | 1536/1839 | Amid / Midst | Uprostřed, mezi / Uprostřed, během, v průběhu | Odstraněno | Midst je podstatné jméno vyžadující konstrukci in the midst of; samotné není předložkou among/amid. |
| 570 | 1537/1941 | Wicked / Profane | Zlý, bezbožný, zkažený, podlý / Rouhavý, bezbožný | Odstraněno | Wicked hodnotí mravní špatnost, profane neúctu k posvátnému či světskost; bezbožný má odlišné užití. |
| 571 | 1537/2228 | Wicked / Putrid | Zlý, bezbožný, zkažený, podlý / Hnijící, zkažený | Odstraněno | Wicked vyjadřuje morální zkaženost, putrid/rancid fyzický rozklad či žluknutí. |
| 572 | 1537/2336 | Wicked / Nefarious | Zlý, bezbožný, zkažený, podlý / Podlý, nekalý, hanebný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 573 | 1537/2442 | Wicked / Rancid | Zlý, bezbožný, zkažený, podlý / Žluklý, zkažený, smradlavý | Odstraněno | Wicked vyjadřuje morální zkaženost, putrid/rancid fyzický rozklad či žluknutí. |
| 574 | 1539/2216 | Vast / Ginormous | Obrovský, objemný / Obrovský | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 575 | 1541/2004 | Bereavement / Demise | Úmrtí, zármutek, žal / Konec, zánik, úmrtí | Odstraněno | Bereavement je ztráta blízkého úmrtím; demise samotné úmrtí či zánik. |
| 576 | 1542/1640 | Intrude / Intervene | Zasahovat, obtěžovat, vyrušovat / Zasahovat, zakročit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 577 | 1542/2371 | Intrude / Pester | Zasahovat, obtěžovat, vyrušovat / Obtěžovat, otravovat | Odstraněno | Harass/pester znamená někoho obtěžovat; intrude vstoupit či zasahovat bez pozvání. Odlišný děj i slovesná vazba. |
| 578 | 1542/2417 | Intrude / Tamper | Zasahovat, obtěžovat, vyrušovat / Zasahovat, manipulovat | Odstraněno | Tamper znamená neoprávněně něco pozměnit/manipulovat; intrude/intervene vstoupit či zakročit. |
| 579 | 1544/2415 | Acute / Discerning | Akutní, naléhavý, kritický / Náročný, kritický, bystrý | Odstraněno | Acute je zde akutní/bolestivý/naléhavý; discerning bystrý v úsudku. Jde o jiný než uložený význam acute. |
| 580 | 1545/1783 | Hovel / Shack | Chatrč, barabizna / Bouda, chatrč | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 581 | 1545/1785 | Hovel / Kennel | Chatrč, barabizna / Psí bouda, barabizna | Diskutabilní | Kennel primárně označuje psí boudu; přenesený ponižující název obydlí není běžné označení chatrče. |
| 582 | 1550/1595 | Miserable / Abysmal | Nešťastný, mizerný, utrápený, bídný / Hrozný, otřesný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 583 | 1550/1875 | Miserable / Grotty | Nešťastný, mizerný, utrápený, bídný / Odporný, hnusný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 584 | 1550/2074 | Miserable / Crummy | Nešťastný, mizerný, utrápený, bídný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 585 | 1552/1905 | Hook / Hiccup | Háček, hák / Háček, zádrhel, drobná potíž | Odstraněno | Hook je hák nebo skrytý háček/podmínka; hiccup dočasný drobný zádrhel. |
| 586 | 1553/2590 | Garish / Gaudy | Křiklavý, neslušný / Křiklavý, nevkusný, nápadný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 587 | 1571/2172 | Dextrous / Nifty | Šikovný, zručný, obratný / Šikovný, mazaný, důmyslný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 588 | 1589/1783 | Con / Shack | Podvod, bouda / Bouda, chatrč | Odstraněno | Con je podvod/bouda v přeneseném smyslu; shack skutečná bouda/chatrč. |
| 589 | 1589/2055 | Con / Fraud | Podvod, bouda / Podvod, podvodník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 590 | 1589/2247 | Con / Humbug | Podvod, bouda / Habaďůra, podvod, přetvářka | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 591 | 1591/2134 | Acumen / Agility | Bystrost, důvtip / Hbitost, Bystrost | Odstraněno | Acumen je bystrost úsudku; agility pohybová nebo myšlenková hbitost. Úsudek a rychlost nejsou totéž. |
| 592 | 1592/1938 | Turmoil / Havoc | Zmatek, vřava, chaos / Chaos, zmatek, nepořádek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 593 | 1592/2436 | Turmoil / Clutter | Zmatek, vřava, chaos / Nepořádek, zmatek, haraburdí | Odstraněno | Clutter je nepořádek/nahromaděné věci; confusion/turmoil/havoc zmatek, rozvrat či zpustošení. |
| 594 | 1595/1875 | Abysmal / Grotty | Hrozný, otřesný, mizerný / Odporný, hnusný, mizerný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 595 | 1595/1923 | Abysmal / Excruciating | Hrozný, otřesný, mizerný / Nesnesitelný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 596 | 1595/2007 | Abysmal / Hideous | Hrozný, otřesný, mizerný / Škaredý, ohizdný, hrozný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 597 | 1595/2074 | Abysmal / Crummy | Hrozný, otřesný, mizerný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 598 | 1606/2121 | Reinstate / Retrieve | Obnovit, zpět dosadit do funkce / Načíst, získat zpět, obnovit | Odstraněno | Retrieve získává něco zpět či načítá data; revive/renew/restore/reinstate obnovují život, stav, platnost či funkci. |
| 599 | 1609/2072 | Roam / Ramble | Potulka, toulat se / Vycházka, toulat se, procházka, toulka, tůra | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 600 | 1609/2409 | Roam / Gallivant | Potulka, toulat se / Toulat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 601 | 1623/2378 | Diction / Recitation | Přednes / Přednes, recitace, výčet, popis | Odstraněno | Diction je volba slov/výslovnost, recitation přednes textu zpaměti. Kvalita projevu a konkrétní činnost se zaměňují. |
| 602 | 1629/1992 | Bounty / Generosity | Odměna, štědrost / Štědrost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 603 | 1631/1659 | Bulk / Quantity | Hromada, množství / Množství | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 604 | 1631/2120 | Bulk / Heap | Hromada, množství / Hromada, Kupa | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 605 | 1639/2018 | Foster / Foster | Podporovat, rozvíjet / Pěstounský, pěsnoun, pěstovat | Diskutabilní | Dvě položky Foster mají částečně shodný slovesný význam, ale druhá mísí pěstounský/pěstoun/pěstovat. |
| 606 | 1639/2438 | Foster / Uphold | Podporovat, rozvíjet / Prosazovat, dodržovat, podporovat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 607 | 1640/2417 | Intervene / Tamper | Zasahovat, zakročit / Zasahovat, manipulovat | Odstraněno | Tamper znamená neoprávněně něco pozměnit/manipulovat; intrude/intervene vstoupit či zakročit. |
| 608 | 1641/1786 | Abundant / Lavish | Hojný, bohatý, bujný / Štědrý, nešetřící, bohatý, plýtvající | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 609 | 1641/2648 | Abundant / Affluent | Hojný, bohatý, bujný / Bohatý, majetný, zámožný člověk | Odstraněno | Abundant/lavish popisují hojnost/opulentnost/štědrost, affluent/prosperous v uloženém českém významu majetnost či prosperitu. |
| 610 | 1641/2651 | Abundant / Prosperous | Hojný, bohatý, bujný / Bohatý, zámožný, prosperující | Odstraněno | Abundant/lavish popisují hojnost/opulentnost/štědrost, affluent/prosperous v uloženém českém významu majetnost či prosperitu. |
| 611 | 1651/1989 | Arguably / Presumably | Pravděpodobně / Pravděpodobně | Odstraněno | Arguably znamená podle obhajitelného názoru, presumably podle předpokladu. Nejde o tutéž míru ani zdroj jistoty. |
| 612 | 1662/2454 | Pelt / Fur | Kožešina / Srst, kožešina | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 613 | 1666/1884 | Fidelity / Allegiance | Věrnost , loajalita, oddanost / Věrnost, oddanost, loajalita | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 614 | 1666/1972 | Fidelity / Devotion | Věrnost , loajalita, oddanost / Oddanost, zbožnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 615 | 1670/2000 | Puny / Teeny | Maličký / Maličký, prtavý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 616 | 1671/2355 | Perturbation / Aberration | Porucha, odchylka / Odchylka, výchylka, vybočení | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 617 | 1682/2481 | Foul / Sleazy | Odporný, hnusný, špinavý, znečistit / Špinavý, ubohý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 618 | 1690/1926 | Mug / Wally | Džbánek, trouba, moula / Pitomec, blbec, trouba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 619 | 1690/2491 | Mug / Nitwit | Džbánek, trouba, moula / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 620 | 1693/2045 | Prick / Pecker | Čurák / Pták, čurák, péro | Diskutabilní | Prick může označovat penis i člověka jako nadávku; pecker zde anatomii. Rozhodnout zamýšlený význam čurák. |
| 621 | 1695/1705 | Insecure / Rickety | Nejistý, vratký / Vratký, rozvyklaný, chatrný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 622 | 1695/1720 | Insecure / Dubious | Nejistý, vratký / Nejistý, mající pochybnosti | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 623 | 1697/1835 | Gofer / Stooge | Poskok / Poskok, přisluhovač, panák | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 624 | 1710/2437 | Recklessness / Levity | Lehkovážnost / Lehkovážnost, zlehčování | Odstraněno | Recklessness je riskantní bezohlednost, levity nevhodná lehkovážná žertovnost. |
| 625 | 1713/1723 | Lack / Scarcity | Nedostatek / Nedostatek, nouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 626 | 1717/1826 | Hogwash / Piffle | Blbosti, žvásty / Nesmysly, žvásty | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 627 | 1717/1828 | Hogwash / Pap | Blbosti, žvásty / Blbosti, kaše | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 628 | 1718/2671 | Derelict / ramshackle | Opuštěný, zpustlý, zchátralý / zchátralý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 629 | 1725/1808 | Chasm / Gulch | Propast, rokle / Rokle, roklina | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 630 | 1739/2328 | Partition / Squad | Přepážka, oddělení, příčka / Oddělení, oddíl, skupina | Odstraněno | Ward je oddělení instituce, partition přepážka a squad organizovaná skupina. Český výraz oddělení směšuje nesouvisející významy. |
| 631 | 1755/2203 | Slot / Orifice | Otvor, štěrbina / Otvor, ústí, jícen | Odstraněno | Slot je úzká štěrbina, orifice obecný otvor či ústí. Nejde o plně odpovídající pojmenování typu otvoru. |
| 632 | 1756/2367 | Salacious / Lecherous | Oplzlý, chlípný, obscénní / Chlípný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 633 | 1757/2021 | Fellow / Chap | Člověk, chlapík, chlápek / Chlápek, mladík | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 634 | 1766/2177 | Pernicious / Malignant | Zhoubný / Zhoubný, zlomyslný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 635 | 1768/2225 | Wax / Wax | Ušní maz / Vosk | Odstraněno | Stejná podoba hesla zastupuje jiné české významy či slovní druhy; nejde o synonymii konkrétních uložených významů. |
| 636 | 1769/2575 | Fluke / Serendipity | Šťastná náhoda, klika, haluz / Šťastná náhoda, štěstíčko | Diskutabilní | Fluke je šťastný náhodný úspěch, serendipity zejména nečekané užitečné objevení. Překryv štěstí není úplný. |
| 637 | 1775/2227 | Obtuse / Blunt | Tupý, omezený / Tupý, otupit | Nahrazeno | Obtuse v tomto hesle znamená nechápavý/omezený; blunt fyzicky tupý nebo přímočarý. Nově: Dense / Obtuse. |
| 638 | 1784/2060 | Docile / Subservient | Poslušný, povolný, poddajný / Poslušný, podřízený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 639 | 1786/2648 | Lavish / Affluent | Štědrý, nešetřící, bohatý, plýtvající / Bohatý, majetný, zámožný člověk | Odstraněno | Abundant/lavish popisují hojnost/opulentnost/štědrost, affluent/prosperous v uloženém českém významu majetnost či prosperitu. |
| 640 | 1786/2651 | Lavish / Prosperous | Štědrý, nešetřící, bohatý, plýtvající / Bohatý, zámožný, prosperující | Odstraněno | Abundant/lavish popisují hojnost/opulentnost/štědrost, affluent/prosperous v uloženém českém významu majetnost či prosperitu. |
| 641 | 1790/2081 | Nebulous / Drizzly | Mlhavý, nejasný / mlhavý, sychravý | Odstraněno | Drizzly označuje mrholení, hazy/nebulous mlhavost/nejasnost. Déšť a mlha nejsou synonyma. |
| 642 | 1797/2518 | Breezy / Jolly | Živý, veselý, svěží / Rozjřený, veselý, příjemný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 643 | 1805/1988 | Garment / Attire | Část oděvu, roucho / Oděv, háháv, roucho | Odstraněno | Garment je jednotlivý kus oděvu, attire oděv/oblečení jako celek; odlišná počitatelnost i rozsah. |
| 644 | 1817/1865 | Voluptuous / Carnal | Vnadný, kyprý, požitkářský, smyslný / Tělesný, smyslný, pudový | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 645 | 1817/2385 | Voluptuous / Self-indulgent | Vnadný, kyprý, požitkářský, smyslný / Požitkářský | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 646 | 1819/1863 | Scurry / Dash | Pelášit, hnát se, pospíchat / Uhánět, hnát se, řítit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 647 | 1819/2596 | Scurry / Hustle | Pelášit, hnát se, pospíchat / Strkat, pohhánět / tlačenice / spěchat, pospíchat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 648 | 1829/1926 | Moron / Wally | Debil, kretén, pitomec / Pitomec, blbec, trouba | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 649 | 1829/2310 | Moron / Dolt | Debil, kretén, pitomec / Blb, hňup, pitomec | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 650 | 1829/2491 | Moron / Nitwit | Debil, kretén, pitomec / Trouba, pitomec | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 651 | 1829/2512 | Moron / Twit | Debil, kretén, pitomec / Pitomec, hňup | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 652 | 1858/2247 | Pretence / Humbug | Předstírání, přetvářka / Habaďůra, podvod, přetvářka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 653 | 1868/2310 | Dimwit / Dolt | Tupec, hňup / Blb, hňup, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 654 | 1868/2485 | Dimwit / Dunce | Tupec, hňup / Tupec, poleno, blbec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 655 | 1868/2512 | Dimwit / Twit | Tupec, hňup / Pitomec, hňup | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 656 | 1875/2074 | Grotty / Crummy | Odporný, hnusný, mizerný / Mizerný, prachbírný, hnusný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 657 | 1878/2302 | Exemption / Acquittal | Osvobození / Osvobození | Odstraněno | Liberation je osvobození z útlaku, exemption výjimka z povinnosti a acquittal zproštění obžaloby. Tři odlišné významy osvobození. |
| 658 | 1884/1972 | Allegiance / Devotion | Věrnost, oddanost, loajalita / Oddanost, zbožnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 659 | 1887/2574 | Enmity / Feud | Nepřátelství / Nepřátelství, nevraživost (dlouhá) | Diskutabilní | Enmity je nepřátelský vztah/pocit, feud dlouhodobý spor. Záleží na vztahovém, ne jednotlivě citovém kontextu. |
| 660 | 1889/2474 | Lament / Whimper | Naříkat, bědovat, truchlit / Fňukat, kňučet, naříkat | Odstraněno | Mourn/lament vyjadřují truchlení, whimper/wail způsob vydávání zvuku. Samotné kňučení ani hlasitý pláč nejsou truchlením. |
| 661 | 1891/1975 | Gracious / Suave | Zdvořilý, jemný, laskavý / Zdvořilý, příjemný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 662 | 1891/2178 | Gracious / Benign | Zdvořilý, jemný, laskavý / Laskavý, neškodný, nezhoubný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 663 | 1895/2172 | Shrewd / Nifty | Chytrý, mazaný / Šikovný, mazaný, důmyslný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 664 | 1895/2588 | Shrewd / Astute | Chytrý, mazaný / Prozíravý, bystrý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 665 | 1896/2415 | Observant / Discerning | Všímavý, pozorný, bystrý / Náročný, kritický, bystrý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 666 | 1896/2588 | Observant / Astute | Všímavý, pozorný, bystrý / Prozíravý, bystrý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 667 | 1908/2568 | Wedlock / Matrimony | Manželství / Manželství | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 668 | 1916/2616 | Enhance / Ameliorate | Zlepšit, vylepšit, zvýraznit / Zlepšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 669 | 1923/2007 | Excruciating / Hideous | Nesnesitelný, hrozný / Škaredý, ohizdný, hrozný | Odstraněno | Excruciating znamená intenzivně bolestivý či trýznivý; obecné hrozný/odpudivý nebo nekvalitní nevyjadřuje stejný význam. |
| 670 | 1923/2010 | Excruciating / Intolerable | Nesnesitelný, hrozný / Nesnesitelný, neúnosný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 671 | 1924/2450 | Eerie / Uncanny | Děsivý, tajuplný / Podivné, tajemné, nepřirozené, zvláštní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 672 | 1926/2310 | Wally / Dolt | Pitomec, blbec, trouba / Blb, hňup, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 673 | 1926/2485 | Wally / Dunce | Pitomec, blbec, trouba / Tupec, poleno, blbec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 674 | 1926/2491 | Wally / Nitwit | Pitomec, blbec, trouba / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 675 | 1926/2512 | Wally / Twit | Pitomec, blbec, trouba / Pitomec, hňup | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 676 | 1929/2541 | Barmy / Batty | Trhlý, bláznivý, střelený / Praštěný, trhlý, prdlý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 677 | 1938/2436 | Havoc / Clutter | Chaos, zmatek, nepořádek / Nepořádek, zmatek, haraburdí | Odstraněno | Clutter je nepořádek/nahromaděné věci; confusion/turmoil/havoc zmatek, rozvrat či zpustošení. |
| 678 | 1940/2339 | Surplus / Plethora | Přebytek, nadbytek / Přemíra, nadbytek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 679 | 1946/2002 | Concoction / Assortment | Směs, lektvar, odvar / Směs, sortiment | Odstraněno | Concoction je smíchaná směs ingrediencí, assortment výběr/soubor různých věcí. |
| 680 | 1963/1964 | Squalor / Grime | Bída, špína / Špína | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 681 | 1975/2518 | Suave / Jolly | Zdvořilý, příjemný / Rozjřený, veselý, příjemný | Odstraněno | Dulcet je sladce libozvučný, suave uhlazeně společenský a jolly veselý. Obecné příjemný neopravňuje propojení. |
| 682 | 1977/2220 | Feral / Ferocious | Divoký, volně žijící / Divoký, dravý | Odstraněno | Feral znamená divoce žijící/zdivočelý, fierce/ferocious zuřivý či dravý. Život bez domestikace neznamená agresivitu. |
| 683 | 1981/2364 | Disown / Renounce | Zříci se, neznat / Zřeknout se, zříci se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 684 | 1987/2258 | Pheasant / Rookie | Bažant / Bažant, ucho | Odstraněno | Pheasant je pták bažant, rookie nováček zvaný česky bažant. |
| 685 | 1988/2447 | Attire / Apparel | Oděv, háháv, roucho / Šaty, oděv, oblečení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 686 | 2001/2016 | Bosh / Bollocks | Blbost, kecy / Hovadina, blbost, kravina | Diskutabilní | Bosh je zastarávající/mírnější nesmysl, bollocks vulgární. Významově blízké, ne stejný registr. |
| 687 | 2015/2207 | Subtle / Minuscule | Nepatrný, jemný, sotva partný / Nepatrný, malý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 688 | 2037/2457 | Tacky / Cheesy | Nevkusný, laciný, pouťový / Laciný, ubohý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 689 | 2037/2590 | Tacky / Gaudy | Nevkusný, laciný, pouťový / Křiklavý, nevkusný, nápadný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 690 | 2052/2349 | Flunk / Forfeit | Rupnout, propadnout, vyražení (od zoušky) / Propadnout, ztratit, daň, cena (za chybu) | Odstraněno | Flunk znamená neuspět u zkoušky, forfeit ztratit právo či majetek jako následek pravidla/sankce. |
| 691 | 2052/2384 | Flunk / Snap | Rupnout, propadnout, vyražení (od zoušky) / Prásknout, rupnout, lusknout prsty | Odstraněno | Flunk znamená propadnout u zkoušky, snap fyzicky prasknout. České rupnout má jiný význam. |
| 692 | 2055/2247 | Fraud / Humbug | Podvod, podvodník / Habaďůra, podvod, přetvářka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 693 | 2058/2124 | Expunge / Purge | Zbavit se, zlikvidovat, vymazat / Očistit, zbavit se, udělat čistku | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 694 | 2066/2108 | Substance / Crux | Obsah, jádro, látka, hmota, důležitost / Jádro, podstata | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 695 | 2072/2409 | Ramble / Gallivant | Vycházka, toulat se, procházka, toulka, tůra / Toulat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 696 | 2088/2453 | Goofy / Daft | Pitomý, přihlouplý / Hloupý, pitomý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 697 | 2088/2546 | Goofy / Sappy | Pitomý, přihlouplý / Šťavnatý, sentimentální, přihlouplý, pitomý | Diskutabilní | Goofy je bláznivě přihlouplý, sappy zejména sentimentální; hloupý význam druhého je užší/regionální. |
| 698 | 2102/2532 | Dupe / Bamboozle | Oklamat, ošálit, napálit / Napálit, doběhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 699 | 2111/2422 | Blob / Speck | Kapička, kulička, tečka / Skvrnka, flíček, tečka | Diskutabilní | Blob je kapka/hrudka/skvrna, speck velmi drobná tečka/částice; výrazný rozdíl velikosti. |
| 700 | 2116/2117 | Flimsy / Brittle | Křehký / Křehký, lámavý | Odstraněno | Flimsy je tenký, chabý, snadno roztržitelný; brittle tvrdý a lámavý. Nezaměnitelný mechanismus křehkosti. |
| 701 | 2122/2667 | Contention / Conviction | Tvrzení, názor, přesvědčení / Přesvědčení, nevyvratitelný názor | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 702 | 2131/2500 | Loiter / Dawdle | Loudat se, flákat se / Loudat se, courat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 703 | 2132/2585 | Finicky / Meticulous | Vybíravý, věčně nespokojený, puntičkářský / Puntičkářský, pečlivý | Diskutabilní | Finicky je vybíravě puntičkářský, meticulous pozitivně pečlivý. Stejná pozornost k detailu má jiný postoj. |
| 704 | 2139/2143 | Wobble / Vary | Kymácet se , viklat, kolísat / Lišit se, obměňovat se, kolísat, měnit se | Odstraněno | Wobble je nejistě se viklat/kývat, vary obecně se lišit nebo měnit; obecná proměnlivost neznamená viklání. |
| 705 | 2151/2328 | Batch / Squad | Dávka, várka, skupina / Oddělení, oddíl, skupina | Odstraněno | Batch je dávka či várka věcí, squad tým osob se společným úkolem. |
| 706 | 2167/2469 | Foray / Raid | Průnik, výpad, nájed, útok / Přepadnout, útok, přepadení, šťára | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 707 | 2219/2610 | Conclusive / Compelling | Přesvědčivý, průkazný / Přesvědčivý, pádný, závažný | Diskutabilní | Compelling silně přesvědčuje, conclusive je definitivně průkazný; pádnost není definitivnost důkazu. |
| 708 | 2222/2224 | Woeful / Measly | Žalostný, smutný / Žalostný, mrzácký | Odstraněno | Woeful je žalostný/smutný či velmi špatný; measly pohrdavě malý/nedostatečný množstvím. |
| 709 | 2222/2577 | Woeful / Lachrymose | Žalostný, smutný / Uplakaný, plačtivý člověk, smutný, plačtivá nálada | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 710 | 2228/2442 | Putrid / Rancid | Hnijící, zkažený / Žluklý, zkažený, smradlavý | Diskutabilní | Putrid je hnilobný rozklad, rancid zejména žluknutí tuků. Obecné zkažený skrývá odborný rozdíl. |
| 711 | 2235/2639 | Reconcile / Appease | Urovnat, usmířit, sladit / Usmířit, uklidnit | Odstraněno | Reconcile urovnává vztah dvou stran; appease uklidňuje či usmiřuje něčí hněv/požadavky. |
| 712 | 2236/2581 | Volatile / Fickle | Nestálý, proměnlivý, nestabilní / Nestálý, proměnlivý | Diskutabilní | Fickle jsou nestálé názory/přízeň, volatile rychlé a nepředvídatelné změny či výbušnost. |
| 713 | 2257/2554 | Sanctum / Haven | Úkryt, útočiště / Útočiště, úkryt, útulek | Odstraněno | Sanctum je posvátný nebo soukromý chráněný prostor; sanctuary/haven útočiště poskytující bezpečí. |
| 714 | 2273/2353 | Concise / Apt | Stručný, výstižný / Výstižný, trefný, vhodný | Odstraněno | Concise vyjadřuje stručnost, apt vhodnost či trefnost; stručné nemusí být trefné a naopak. |
| 715 | 2310/2491 | Dolt / Nitwit | Blb, hňup, pitomec / Trouba, pitomec | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 716 | 2310/2512 | Dolt / Twit | Blb, hňup, pitomec / Pitomec, hňup | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 717 | 2341/2342 | Caretaker / Janitor | Domovník, správce / Školník, domovník | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 718 | 2395/2606 | Inadequacy / Lapse | Nedostatečnost, chyba, vada / Poklesek, pochybení, chyba, selhání | Odstraněno | Flaw/inadequacy jsou vada či nedostatečnost; lapse jednotlivé dočasné pochybení/výpadek. |
| 719 | 2398/2399 | Fen / Bog | Bažina, močál, mokřina / Bažina, močál, mokřina | Diskutabilní | Fen a bog se obecně překládají bažina, odborně jde o různé mokřady; ponecháno pro obecný význam. |
| 720 | 2415/2588 | Discerning / Astute | Náročný, kritický, bystrý / Prozíravý, bystrý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 721 | 2452/2496 | Frivolous / Futile | Lehkovážný, rozpustilý, zbytečný / Zbytečný, marný | Odstraněno | Frivolous je neseriózní/lehkovážný, futile marný bez výsledku. Malá hodnota a neúčinnost jsou jiné vlastnosti. |
| 722 | 2453/2546 | Daft / Sappy | Hloupý, pitomý / Šťavnatý, sentimentální, přihlouplý, pitomý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 723 | 2457/2481 | Cheesy / Sleazy | Laciný, ubohý / Špinavý, ubohý | Diskutabilní | Cheesy je lacině kýčovitý, sleazy špinavě pochybný; společný nekvalitní podnik neznamená shodu vždy. |
| 724 | 2491/2512 | Nitwit / Twit | Trouba, pitomec / Pitomec, hňup | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 725 | 2531/2555 | Bouncing / Hefty | Statný, zdravý, silný / Statný, mocný, robustní | Odstraněno | Bouncing u dítěte znamená zdravý a čilý; stout/hefty robustní, těžký či mohutný. |
| 726 | 2603/2678 | Ostentatious / pretentious | Okázalý, honosný, pompézní / domýšlivý, namyšlený, nabubřelý, pompézní | Diskutabilní | Ostentatious je okázalý, pretentious snažící se působit důležitěji. Překryv pompéznosti je částečný. |
| 727 | 2648/2651 | Affluent / Prosperous | Bohatý, majetný, zámožný člověk / Bohatý, zámožný, prosperující | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |

### Spanish: 696 původních vazeb

| Záznam | ID | Hesla | České významy | Verdikt | Posouzení / náhrada |
|---:|---|---|---|---|---|
| 1 | 5/303 | enojado / enfadado | naštvaný / rozzlobený, naštvaný, rozčílený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 2 | 11/1518 | flojo / perezoso | volný, povolený / líný, lenošný / líný, zahálčivý, pohodlný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 3 | 16/472 | subir / aumentar | zvýšit, go up / zvětšit, zvýšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 4 | 16/2250 | subir / acrecentar | zvýšit, go up / zvětšit, zvýšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 5 | 19/1548 | tratar / actuar | zacházet / chovat se / jednat / počínat si, chovat se | Odstraněno | Tratar znamená zacházet s někým či jednat o něčem; actuar chovat se/konat. Jiné role a slovesné vazby. |
| 6 | 20/882 | intentar / esforzarse | pokusit se, snažit se, mít v úmyslu / snažit se | Diskutabilní | Intentar je pokusit se, esforzarse vyvinout úsilí. Pokus nemusí být namáhavá snaha a liší se vazba. |
| 7 | 21/1590 | débil / delicado | slabý / slabý, choulostivý, neduživý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 8 | 22/981 | fuerte / potente | silný / silný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 9 | 22/1358 | fuerte / contundente | silný / silný, přesvědčivý, jednoznačný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 10 | 25/1433 | duro / férreo | tvrdý / železný, pevný (vůle ap.), tvrdý, přísný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 11 | 27/658 | creer / confiar | věřit / spolehnout se, důvěřovat, věřit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 12 | 31/1659 | quitar / retirar | odstranit / vysléct / take away / odstranit, odklidit, odsunout, odtáhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 13 | 31/1779 | quitar / desprender | odstranit / vysléct / take away / odstranit, oddělit, sejmout / vyplývat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 14 | 33/133 | recibir / acoger | přijmout / uvítat, ujmout se, přijmout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 15 | 33/1001 | recibir / admitir | přijmout / přijmout, připustit, uznat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 16 | 39/351 | llegar / acudir | přijít / dorazit / přijít, dostavit se, přijet | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 17 | 41/293 | tal vez / quizá | možná / maybe / snad, asi, možná (formálnější) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 18 | 45/2674 | aspero / crudo | drsný / syrový, drsný, tvrdý | Diskutabilní | Áspero je drsný na dotek či v chování; crudo syrový nebo drsný ve věrném neuhlazeném podání. |
| 19 | 47/1573 | claro / evidente | světlý / jasný, srozumitelný / zřejmý, zjevný, jasný, očividný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 20 | 50/2802 | gracioso / desopilante | zábavný / zábavný, veselý, směšný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 21 | 51/1692 | serio / grave | vážný / těžký, vážný, závažný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 22 | 53/787 | amargo / acre | hořký / hořký, štiplavý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 23 | 54/344 | acido / agrio | kyselý / kyselý / trpký | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 24 | 57/1657 | antiguo / anticuado | starověký, nemoderní / zastaralý, vyšlý z módy, nemoderní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 25 | 64/996 | la esfera / la bola | koule / koule, kulička, klubko | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 26 | 71/1352 | esperanzador / alentador | nadějný / povzbudivý / povzbudivý, povzbuzující | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 27 | 98/814 | feo / feúcho | škaredý / škaredý, šeredný, ohyzdný | Diskutabilní | Feúcho zpravidla zeslabuje ošklivost; český překlad ji naopak zesiluje. Samotný překlad zůstává beze změny. |
| 28 | 110/819 | conseguir / lograr | get / dosáhnout (čeho vítězství apod.), získat (co) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 29 | 110/2436 | conseguir / obtener | get / získat, obdržet, dostat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 30 | 115/1391 | frenar / detener | zastavit, zabrzdit / (po)zastavit, zadržet, potlačit nákazu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 31 | 119/1919 | vencer / superar | překonat, zvítězit, vyhrát , přemoct / vypršet / předčit, překonat, předstihnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 32 | 119/2476 | vencer / sobrepasar | překonat, zvítězit, vyhrát , přemoct / vypršet / přesáhnout, překročit / překonat, zvládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 33 | 122/1802 | invadir / atacar | napadnout / zaútočit / (za)útočit, napadnout, přepadnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 34 | 130/1492 | escoger / optar | vybrat (si) / zvolit (si) / vyvolit si / zvolit, vybrat (si) co, rozhodnout se pro co | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 35 | 131/786 | coger / agarrar | vzít / uchopit / popadnout / zvednout telefon / šukat / vzít, popadnout, chytit | Diskutabilní | Coger je běžné vzít ve Španělsku, v části Latinské Ameriky vulgární sexuální výraz; agarrar platí pro uchopení. |
| 36 | 132/1491 | dirigir / regir | dirigovat, řídit / být platný, platit / řídit, spravovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 37 | 132/1921 | dirigir / liderar | dirigovat, řídit / vést, řídit, šéfovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 38 | 132/2798 | dirigir / regentar | dirigovat, řídit / vést, řídit, spravovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 39 | 133/1001 | acoger / admitir | uvítat, ujmout se, přijmout / přijmout, připustit, uznat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 40 | 134/1593 | proteger / blindar | chránit / obrnit, chránit, oplechovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 41 | 134/1738 | proteger / resguardar | chránit / chránit, bránit, ochraňovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 42 | 135/1206 | exigir / requerir | vyžadovat / požadovat / vyžadovat, potřebovat, požadovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 43 | 140/1498 | sostener / afirmar | držet, nést / tvrdit, zastávat  / potvrdit, tvrdit, upevnit, připevnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 44 | 140/2287 | sostener / aseverar | držet, nést / tvrdit, zastávat  / tvrdit, prohlašovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 45 | 140/2777 | sostener / sujetar | držet, nést / tvrdit, zastávat  / držet, přidržovat, upevnit / zadržet / zkrotit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 46 | 141/1004 | prevenir / prever | předvídat / předejít / zabránit / zamezit škodě / předvídat, tušit / počítat (s čím) | Diskutabilní | Prevenir obvykle předchází/varuje, prever předvídá. U preventivního plánování se překrývají, nejsou vždy zaměnitelné. |
| 47 | 141/1368 | prevenir / anticipar | předvídat / předejít / zabránit / zamezit škodě / předvídat / předjímat / udělat něco dopředu | Diskutabilní | Anticipar předvídá/předjímá či činí předem; prevenir předchází nebo varuje. Nutný konkrétní význam. |
| 48 | 142/1351 | predecir / augurar | předpovídat / predict / věštit, předpovídat, prorokovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 49 | 142/1441 | predecir / vaticinar | předpovídat / predict / předpovídat, věštit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 50 | 142/2290 | predecir / pronosticar | předpovídat / predict / předpovídat, prorokovat, věštit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 51 | 144/1568 | traer / aportar | přinést / dát, přinést, předložit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 52 | 147/1461 | propio / particular | (svůj) vlastní / vhodný, příhodný / jednotlivý, osobitý, vlastní, osobní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 53 | 154/2289 | sin embargo / no obstante | nicméně / nicméně, přesto, avšak, navzdory tomu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 54 | 158/1446 | jactarse / vanagloriarse | vychloubat se, pyšnit se, holedbat se čím / vychloubat se, chlubit se, chvástat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 55 | 158/2557 | jactarse / ufanarse | vychloubat se, pyšnit se, holedbat se čím / vytahovat se, vychloubat se, naparovat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 56 | 164/202 | golpear / pegar | udeřit / lepit, dát ráru / připalovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 57 | 165/1130 | lastimarse / daňar | zranit koho, ublížit komu fyzicky / (z)ranit, poranit (koho/co), ublížit (komu/čemu) | Odstraněno | Lastimarse je reflexivní zranit se, dañar přechodné poškodit/zranit někoho či něco; nezaměnitelné argumenty. |
| 58 | 169/2194 | mientras / en tanto | zatímco, během toho co, while / zatímco, mezitímco / do té míry, že, nakolik | Diskutabilní | En tanto může být mezitím/zatímco, konstrukce s que a další významy jsou odlišné. |
| 59 | 172/2081 | enseguida / inmediatamente | hned, za minutku, za chvilku / okamžitě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 60 | 175/1507 | culpar / acusar | obviňovat / obvinit, dávat vinu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 61 | 184/2210 | en todo caso / de todos modos | v každém případě / každopádně, v každém případě, stejně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 62 | 184/2240 | en todo caso / de todas formas | v každém případě / každopádně, stejně, v každém případě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 63 | 194/1262 | luchar / combatir | bojovat, zápolit / bojovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 64 | 195/2386 | chiquitito / chiquito | drobný, maličký / maličký, malý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 65 | 201/974 | arrancar / arrebatar | vyškubnout / (na)startovat / vyrazit, vyjet / vytrhnout, vyrvat, vyškubnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 66 | 204/2108 | lanzar / arrojar | hodit / mrštit, hodit, vrhnout / vyhodit, vyrazit, vykopnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 67 | 212/1298 | facilitar / aliviar | usnadnit / ulehčit, usnadnit, ulevit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 68 | 212/2100 | facilitar / allanar | usnadnit / odstranit překážky, usnadnit / vyrovnat, uhladit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 69 | 213/2793 | el humor / el estado de ánimo | nálada, rozpoložení / humor / nálada, rozpoložení, duševní rozpoložení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 70 | 214/1841 | ilustre / célebre | proslulý / slavný, proslulý, proslavený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 71 | 215/1294 | proponer / plantear | navrhnout / nastínit, vyložit, vylíčit / navrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 72 | 215/1322 | proponer / sugerir | navrhnout / navrhnout, doporučit, předložit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 73 | 217/1194 | avanzado / adelantado | pokročilý / pokročilý, daleko před ostatními | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 74 | 217/1920 | avanzado / puntero | pokročilý / přední, čelný pozice, pokročilý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 75 | 218/1355 | avanzar / adelantar | posunout, poslat vpřed, předsunout / posunout dopředu, vysunout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 76 | 220/262 | la caminata / el recorrido | cesta, procházka / výšlap / projití, projetí, (okružní) jízda, procházka | Diskutabilní | Caminata je pěší cesta, recorrido průchod/projetá trasa/tour; dopravní prostředek nemusí být tentýž. |
| 77 | 223/982 | rechazar / desechar | odmítnout, zamítnout, nepřijmout / nepřijmout, odmítnout, zavrhnout  / odložit, vyhodit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 78 | 223/1412 | rechazar / descartar | odmítnout, zamítnout, nepřijmout / vyloučit (možnost ap.), odmítnout, zavrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 79 | 223/2685 | rechazar / repudiar | odmítnout, zamítnout, nepřijmout / odmítnout, odsoudit, neschvalovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 80 | 238/2247 | engaňar / embaucar | podvést / oklamat / ošidit / napálit, podvést, ošálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 81 | 238/2718 | engaňar / timar | podvést / oklamat / ošidit / ošidit, okrást, podvést, napálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 82 | 252/2527 | además / adicionalmente | kromě / navíc / vedle toho / dodatečně, navíc | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 83 | 254/1824 | perseguir / rastrear | (proná)sledovat / honit /  (vy)stopovat, sledovat/hledat stopu, jít po stopě | Odstraněno | Perseguir pronásleduje, rastrear vyhledává/sleduje stopy. Sledování kořisti a hledání jejích stop jsou odlišné děje. |
| 84 | 257/1540 | la herramienta / el utensilio | nástroj, nářadí, náčiní / nástroj, nářadí, náčiní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 85 | 261/1592 | seňalar / signar | označit, označkovat, ukazovat na / označit, orazítkovat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 86 | 261/1958 | seňalar / rotular | označit, označkovat, ukazovat na / opatřit popisem (kresbu ap.), označit (plánek ap.) | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 87 | 261/2238 | seňalar / marcar | označit, označkovat, ukazovat na / označit, vyznačit, ukázat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 88 | 268/1113 | el trozo / la pieza | kus, kousek / kus, kousek, část | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 89 | 272/2418 | marcado / llamativo | výrazný / nápadný, výrazný, do očí bijící | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 90 | 274/1141 | destacar / subrayar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, vyzdvihnout, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 91 | 274/1198 | destacar / enfatizar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 92 | 274/2494 | destacar / resaltar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, vyzdvihnout, vyniknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 93 | 274/2661 | destacar / recalcar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, vyzdvihnout, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 94 | 274/2791 | destacar / acentuar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 95 | 279/1343 | revelar / descubrir | odhalit, odkrýt, prozradit / objevit, odhalit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 96 | 285/624 | la bondad / la amabilidad | dobrota / laskavost / laskavost, přívětivost, vstřícnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 97 | 287/859 | por supuesto / desde luego | ovšem, samozřejmě / samozřejmě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 98 | 287/2470 | por supuesto / naturalmente | ovšem, samozřejmě / přirozeně, samozřejmě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 99 | 288/1100 | parecido / afín | podobný / podobný (názory ap.), příbuzný, blízký | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 100 | 288/1819 | parecido / semejante | podobný / podobný, obdobný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 101 | 289/2492 | acerca de / con respecto a | o, stran, ohledně / ohledně, co se týče, ve vztahu k | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 102 | 293/1982 | quizá / posiblemente | snad, asi, možná (formálnější) / možná, případně, možná že | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 103 | 293/2003 | quizá / acaso | snad, asi, možná (formálnější) / možná, snad, třeba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 104 | 294/442 | la tentación / el gusto | pokušení, chuť / chuť | Odstraněno | Tentación je pokušení, gusto chuť/vkus/potěšení. Společné české chuť směšuje touhu a vjem či zálibu. |
| 105 | 295/1130 | sucumbir / daňar | podlehnout komu/čemu / být poražen kým/čím / (z)ranit, poranit (koho/co), ublížit (komu/čemu) | Odstraněno | Sucumbir znamená podlehnout; dañar poškodit někoho/něco. Opačná role podmětu v ději. |
| 106 | 308/1139 | fijo / permanente | pevný (datum), stálý, fixní (cena), pevně připevněný / trvalý, stálý, ustavičný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 107 | 309/2276 | a propósito / por cierto | mimochodem / mimochodem | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 108 | 309/2405 | a propósito / dicho sea de paso | mimochodem / mimochodem, když už je o tom řeč | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 109 | 314/1732 | fingir / simular | předstírat / fingovat / simulovat / napodobovat, předstírat, simulovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 110 | 317/2750 | arreglar / enderezar | dát do pořádku / uspořádat / napravit, dát do pořádku, narovnat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 111 | 325/1075 | el campesino / el labriego | rolník / zemědělec / vesničan / rolník/rolnice, sedlák/selka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 112 | 329/2525 | atónito / pasmado | užaslý / udivený / ohromený / užaslý, zaražený, ohromený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 113 | 332/1136 | mediante / por intermedio de | prostřednictvím / přes / pomocí / prostřednictvím, skrze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 114 | 354/355 | disminuir / reducir | zmenšovat, zeslabovat, snižovat / zmenšit, zredukovat, snížit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 115 | 355/1850 | reducir / achicar | zmenšit, zredukovat, snížit / zmenšit, zkrátit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 116 | 367/944 | tramposo / fraudulento | tricky, podvodnický / podvodný, podvodnický, klamavý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 117 | 373/574 | puerco / el cerdo | zaprasený, zašpiněný / prase, vepř, čuně / vepřové, prase | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 118 | 389/1101 | el voto / el sufragio | hlas ve volbách / volební právo / hlas ve volbách | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 119 | 403/938 | la solicitud / el pedido | žádost / objednávka, zakázka, žádost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 120 | 415/1008 | mitigar / atenuar | zmírnit, snížit / zeslabit, zmírnit, ztišit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 121 | 415/2157 | mitigar / amortiguar | zmírnit, snížit / (z)tlumit, zmírnit, potlačit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 122 | 416/1435 | gestionar / tramitar | zařídit, vyřídit, spravovat / vyřídit, vyjednat, zařídit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 123 | 416/2798 | gestionar / regentar | zařídit, vyřídit, spravovat / vést, řídit, spravovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 124 | 417/419 | promover / fomentar | podporovat / propagovat / podporovat, podněcovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 125 | 417/1493 | promover / respaldar | podporovat / propagovat / podpořit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 126 | 417/2017 | promover / promocionar | podporovat / propagovat / propagovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 127 | 419/1282 | fomentar / incentivar | podporovat, podněcovat / pobízet, podněcovat, povzbuzovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 128 | 419/1495 | fomentar / impulsar | podporovat, podněcovat / pohánět, hnát, podněcovat, povzbuzovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 129 | 420/972 | aprovechar / capitalizar | využít, těžit z / využít, zhodnotit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 130 | 437/750 | la barriga / el vientre | břicho, pupek / břicho | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 131 | 437/2810 | la barriga / el abdomen | břicho, pupek / břicho | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 132 | 446/1358 | grueso / contundente | tlustý, silný  / silný, přesvědčivý, jednoznačný | Odstraněno | Grueso vyjadřuje tloušťku, profundo/hondo hloubku, potente sílu, contundente průraznost/pádnost a mayor srovnávací velikost. Shoda přes české silný/velký nestačí. |
| 133 | 448/524 | doblar / juntar | složit (papír apod.) / ohnout / přehnout / (na)shromáždit, dá(va)t dohromady, složit | Odstraněno | Doblar je ohnout/přeložit, juntar shromáždit či spojit. Dva jiné významy českého složit. |
| 134 | 456/656 | profundo / hondo | hluboký, silný / hluboký, velký, intenzivní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 135 | 456/981 | profundo / potente | hluboký, silný / silný | Odstraněno | Grueso vyjadřuje tloušťku, profundo/hondo hloubku, potente sílu, contundente průraznost/pádnost a mayor srovnávací velikost. Shoda přes české silný/velký nestačí. |
| 136 | 456/1358 | profundo / contundente | hluboký, silný / silný, přesvědčivý, jednoznačný | Odstraněno | Grueso vyjadřuje tloušťku, profundo/hondo hloubku, potente sílu, contundente průraznost/pádnost a mayor srovnávací velikost. Shoda přes české silný/velký nestačí. |
| 137 | 465/835 | el rencor / el aborrecimiento | zloba, zášť, nenávist / nechuť, odpor, nenávist | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 138 | 466/1196 | la rabia / la fiereza | vztek, zuřivost, zlost / divokost, zuřivost, zběsilost | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 139 | 468/2645 | un montón / una pila de | spousta, hromada, strašně moc / hromada..., spousta..., kupa.. | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 140 | 469/1887 | revoltoso / obstante | neklidný, neposedný, vzpurný / vzdorovitý, vzpurný, svéhlavý | Odstraněno | Obstante není označení vzpurné osoby; užívá se zejména v no obstante. Nezaměňovat s obstinado. |
| 141 | 469/2438 | revoltoso / agitado | neklidný, neposedný, vzpurný / rozrušený, nervózní, neklidný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 142 | 472/1032 | aumentar / redoblar | zvětšit, zvýšit / zvýšit, zvětšit, zvojnásobit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 143 | 472/2190 | aumentar / potenciar | zvětšit, zvýšit / umocnit, zvýšit, rozšířit, posilnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 144 | 472/2250 | aumentar / acrecentar | zvětšit, zvýšit / zvětšit, zvýšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 145 | 473/580 | el incremento / la estatura | zvýšení, vzrůst, navýšení / výška, vzrůst | Odstraněno | Incremento je přírůstek/navýšení, estatura tělesná výška. Dva odlišné významy českého vzrůst. |
| 146 | 475/1377 | la onda / la ola | vlna / vlna (na vodě ap.) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 147 | 477/2702 | el baúl / la valija | kufr, zavazadelník auta, truhla / kufr | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 148 | 495/1933 | entretener / incautar | pobavit, zabavit, bavit / zabavit, odebrat, zadržet | Odstraněno | Entretener znamená bavit/zaměstnat pozornost; incautar zabavit majetek. Dva odlišné významy českého zabavit. |
| 149 | 496/2571 | el evento / el acontecimiento | událost / událost, příhoda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 150 | 497/663 | capitular / renunciar | vzdát se / vzdát se, odmítnout co | Diskutabilní | Capitular je kapitulovat, renunciar vzdát se nároku/funkce; odlišná vazba a důvod. |
| 151 | 498/1652 | rendir / apoderar | podrobit (si), podmanit (si), ovládnout / zmocnit se, ovládnout | Odstraněno | Rendir zde znamená podrobit; apoderar udělit plnou moc a apoderarse zmocnit se. Nelze zaměnit přechodnost a reflexivitu. |
| 152 | 498/2831 | rendir / someter | podrobit (si), podmanit (si), ovládnout / podrobit, podřídit / vystavit něčemu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 153 | 501/1950 | el hogar / el domicilio | domov, domácnost / bydliště, domov, adresa | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 154 | 506/1904 | desafortunadamente / desgraciadamente | bohužel / bohužel | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 155 | 506/2319 | desafortunadamente / lastimosamente | bohužel / bohužel, naneštěstí, politováníhodně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 156 | 508/689 | la sombra / la penumbra | stín, přítmí, příšeří / šero, polostín, pološero, přítmí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 157 | 509/741 | la felicidad / la alegría | štěstí - pocit, radost, potěšení / radost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 158 | 509/1807 | la felicidad / la euforia | štěstí - pocit, radost, potěšení / radost, nadšení | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 159 | 514/1821 | la cascada / la catarata | kaskáda, vodopád / vodopád   | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 160 | 522/969 | la serenidad / la cámara | klid, pokoj, klidnost / pokoj, místnost, komnata | Odstraněno | Serenidad je duševní klid/pokoj, cámara místnost/pokoj či kamera. České pokoj má jiný význam. |
| 161 | 524/1626 | juntar / pergeňar | (na)shromáždit, dá(va)t dohromady, složit / dát dohromady, slepit, ušít horkou jehlou | Odstraněno | Juntar shromažďuje či spojuje; pergeñar načrtává/narychlo sestavuje plán/text. Jiné významy dát dohromady. |
| 162 | 524/1632 | juntar / acumular | (na)shromáždit, dá(va)t dohromady, složit / (na)hromadit, shromáždit, (a)kumulovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 163 | 524/1961 | juntar / recopilar | (na)shromáždit, dá(va)t dohromady, složit / sebrat, posbírat, shromáždit (hlavně u abstraktních věcí) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 164 | 524/2390 | juntar / hilvanar | (na)shromáždit, dá(va)t dohromady, složit / pospojovat, dát dohromady, navázat na sebe / sestehovat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 165 | 525/792 | sabroso / apetitoso | chutný, lahodný, dobrý pokrm / chutný, lákavý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 166 | 525/2591 | sabroso / suculento | chutný, lahodný, dobrý pokrm / šťavnatý, chutný, dobrý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 167 | 528/687 | murmurar / susurrar | mumlat, brblat si pod vousy, (za)šeptat / šeptat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 168 | 531/1155 | realizar / perpetrar | uskutečnit, provést, vykonat / spáchat, vykonat | Odstraněno | Perpetrar je spáchat zločin či závažné provinění, realizar/ejecutar obecně něco provést. U běžného projektu nejde o zaměnitelné označení. |
| 169 | 531/2265 | realizar / ejecutar | uskutečnit, provést, vykonat / provést, vykonat, vyřídit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 170 | 532/2351 | quebrar / destrozar | rozbít, (roz)lámat, porušit, porušit (nařízení) / zničit, rozbít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 171 | 533/2676 | dudoso / incierto | pochybný / nejistý, neurčitý, pochybný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 172 | 534/1754 | aconsejar / encuadrar | radit / (za)rámovat, (za)řadit, zahrnout, zahrnovat  | Odstraněno | Aconsejar je radit, encuadrar rámovat/zařadit. Nejde o stejný děj. |
| 173 | 535/795 | entusiasmado / emocionado | nadšený, uchvácený / nadšený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 174 | 540/1808 | hilarante / irrisorio | legrační, úsměvný, směšný / směšný, směšně nízký | Nahrazeno | Hilarante je veselý, vyvolávající smích; irrisorio výsměšně směšný či směšně nízký. Pro zábavnost je přesnější gracioso. Nově: gracioso / hilarante. |
| 175 | 540/2802 | hilarante / desopilante | legrační, úsměvný, směšný / zábavný, veselý, směšný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 176 | 541/626 | la conjetura / la suposición | domněnka, dohad, tušení / domněnka, dohad | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 177 | 542/1756 | perspicaz / ingenioso | bystrý, důvtipný / bystrý, důvtipný, nadaný | Diskutabilní | Perspicaz je bystrý v postřehu/úsudku, ingenioso nápaditý. Důvtip je překryv, nikoliv úplná shoda. |
| 178 | 548/2551 | apacible / sereno | klidný, pokojný, mírný / klidný, vyrovnaný, rozvážný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 179 | 548/2767 | apacible / quieto | klidný, pokojný, mírný / klidný, v klidu, bez hnutí | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 180 | 550/1762 | eficaz / operativo | účinný / účinný, funkční | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 181 | 551/2839 | la travesía / el atropello | let, plavba, přechod, přejití, přejetí / bezpráví, svévole, hrubé porušení práv / sražení, přejetí (vozidlem) | Odstraněno | Travesía je cesta/přechod či plavba; atropello sražení vozidlem nebo bezpráví. Dva jiné významy přejetí. |
| 182 | 554/2497 | inagotable / interminable | nevyčerpatelný, nekonečný / nekonečný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 183 | 557/558 | el embutido / la salchicha | uzenina, klobása, salám / klobása, párek, vuřt | Odstraněno | Embutido je obecná kategorie uzeniny, salchicha a chorizo odlišné konkrétní výrobky. Kategorie a dva její druhy nejsou automaticky synonyma. |
| 184 | 557/559 | el embutido / el chorizo | uzenina, klobása, salám / salám suchý, klobása | Odstraněno | Embutido je obecná kategorie uzeniny, salchicha a chorizo odlišné konkrétní výrobky. Kategorie a dva její druhy nejsou automaticky synonyma. |
| 185 | 558/559 | la salchicha / el chorizo | klobása, párek, vuřt / salám suchý, klobása | Odstraněno | Embutido je obecná kategorie uzeniny, salchicha a chorizo odlišné konkrétní výrobky. Kategorie a dva její druhy nejsou automaticky synonyma. |
| 186 | 574/2583 | el cerdo / el chancho | vepřové, prase / prase, čuně (o člověku) | Diskutabilní | Chancho je regionální název prasete. Platí pro zvíře, ne automaticky pro všechny přenesené významy cerdo. |
| 187 | 578/1934 | imponente / inmenso | ohromný, impozantní, znamenitý / ohromný, obrovský / báječný, bezvadný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 188 | 578/2488 | imponente / enorme | ohromný, impozantní, znamenitý / ohromný, nesmírný, nadměrný, enormní | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 189 | 578/2510 | imponente / sobresaliente | ohromný, impozantní, znamenitý / vynikající, skvělý, znamenitý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 190 | 578/2678 | imponente / magnífico | ohromný, impozantní, znamenitý / úžasný, skvělý, ohromný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 191 | 582/941 | proveer / otorgar | poskytnout, zásobit, vybavit / dát, poskytnout, udělit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 192 | 582/947 | proveer / conceder | poskytnout, zásobit, vybavit / udělit, dát, poskytnout, připustit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 193 | 582/2180 | proveer / brindar | poskytnout, zásobit, vybavit / připít si / poskytnout, nabídnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 194 | 587/1128 | el frijol / la chaucha | fazole, fazolový lusk / fazolový lusk, fazolka | Diskutabilní | Frijol může podle RAE označovat i plod v zelené podobě, chaucha zelený lusk. Příklad frijol negro však míří k semenům; význam je třeba vymezit. |
| 195 | 587/2821 | el frijol / los porotos | fazole, fazolový lusk / fazole | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 196 | 592/1858 | hervir / cocer | vařit / vařit (ve vodě) | Diskutabilní | Hervir je vařit/vřít, cocer tepelně připravovat potravinu; voda vaří, ale sama se necocina/cuece jako potravina. |
| 197 | 597/1678 | colocar / ubicar | dát, umístit, uložit / umístit, postavit, položit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 198 | 597/2353 | colocar / acomodar | dát, umístit, uložit / umístit, usadit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 199 | 609/610 | el cansancio / la fatiga | únava, vyčerpání / únava, vyčerpání | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 200 | 609/1388 | el cansancio / el agotamiento | únava, vyčerpání / vyčerpání, spotřebování  | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 201 | 610/1388 | la fatiga / el agotamiento | únava, vyčerpání / vyčerpání, spotřebování  | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 202 | 611/1429 | la cima / la cumbre | vrchol, vrcholek, vrch  / vrchol / summit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 203 | 636/1599 | dentro / adentro | uvnitř, vevnitř / v rámci / dovnitř, uvnitř, vevnitř | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 204 | 643/2709 | el cántaro / el jarrón | džbán / (ozdobný) džbán, váza | Odstraněno | Cántaro je nádoba/džbán na tekutiny, jarrón ozdobná váza. Podobnost tvaru nestačí. |
| 205 | 645/2473 | personalmente / presencialmente | osobně / osobně, fyzicky na místě | Diskutabilní | Personalmente může být podle mého názoru nebo sám osobně; presencialmente pouze fyzicky na místě. Příklady zde ukazují jiné významy. |
| 206 | 647/2131 | averiguar / escudriňar | zjistit, (vy)zkoumat, přijít na co, figure out / (pro)zkoumat, (pro)zkoušet, (o)testovat | Odstraněno | Averiguar zjišťuje odpověď/výsledek; escudriñar/examinar provádějí zkoumání. Proces není totožný s úspěšným zjištěním. |
| 207 | 647/2429 | averiguar / detectar | zjistit, (vy)zkoumat, přijít na co, figure out / zjistit, objevit, odhalit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 208 | 647/2495 | averiguar / examinar | zjistit, (vy)zkoumat, přijít na co, figure out / zkoumat, přezkoumat, analyzovat, důkladně prohlédnout | Odstraněno | Averiguar zjišťuje odpověď/výsledek; escudriñar/examinar provádějí zkoumání. Proces není totožný s úspěšným zjištěním. |
| 209 | 656/1697 | hondo / mayor | hluboký, velký, intenzivní / větší, velký, starší, hlavní | Odstraněno | Grueso vyjadřuje tloušťku, profundo/hondo hloubku, potente sílu, contundente průraznost/pádnost a mayor srovnávací velikost. Shoda přes české silný/velký nestačí. |
| 210 | 665/1760 | esmerado / minucioso | pečlivý, důkladný / pečlivý, podrobný, důkladný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 211 | 666/1054 | la tempestad / la tormenta | bouře / bouře, bouřka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 212 | 668/673 | refulgente / brillante | zářivý, jasný / zářivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 213 | 668/1573 | refulgente / evidente | zářivý, jasný / zřejmý, zjevný, jasný, očividný | Odstraněno | Refulgente je zářivý/svítivý, evidente zjevný/pochopitelně jasný. Dva jiné významy jasný. |
| 214 | 669/2245 | intrépido / audaz | statečný, nebojácný, neohrožený / odvážný, smělý, neohrožený, troufalý, odhodlaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 215 | 679/2291 | oculto / latente | skrytý, schovaný, ukrytý / latentní, skrytý | Diskutabilní | Latente je dosud neprojevený/potenciálně přítomný, oculto jednoduše skrytý. Latentnost je užší. |
| 216 | 679/2772 | oculto / clandestino | skrytý, schovaný, ukrytý / ilegální, tajný, skrytý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 217 | 683/684 | el terremoto / el seísmo | zemětřesení / zemětřesení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 218 | 688/701 | el susurro / el murmullo | šeptání, šepot / šum, šeptání, mumlání, šepot | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 219 | 698/2582 | arrullador / soporífero | ukolébavý, uspávající / uspávající, nudný, otravný | Diskutabilní | Arrullador ukolébává, soporífero uspává i nudou. Příjemnost či nuda jsou odlišné. |
| 220 | 705/1187 | el baluarte / el respaldo | bašta, pevnost, záštita / podpora, záštita | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 221 | 713/1156 | el valor / la valentía | hodnota, statečnost / odvaha, statečnost, udatnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 222 | 714/835 | la resistencia / el aborrecimiento | odpor, odolnost / nechuť, odpor, nenávist | Odstraněno | Resistencia je odpor vůči síle nebo odolnost, aborrecimiento odpor/nenávist jako emoce. |
| 223 | 717/2733 | el fracaso / el revés | neúspěch, selhání / neúspěch, rána osudu / rub, druhá strana | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 224 | 723/1833 | el propósito / el objetivo | účel, záměr / cíl, záměr, účel | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 225 | 727/2141 | la decisión / la resolución | rozhodnutí / rozhodnutí, usnesení, rezoluce | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 226 | 731/2110 | la confianza / la fe | důvěra, sebevědomí / víra, důvěra, přesvědčení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 227 | 740/1091 | el descubrimiento / el hallazgo | objev / nález, objev | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 228 | 750/2810 | el vientre / el abdomen | břicho / břicho | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 229 | 753/1166 | por otro lado / por otra parte | na druhou stranu / na druhou stranu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 230 | 753/2241 | por otro lado / por su parte | na druhou stranu / ze své strany, pokud jde o něj/ni, na druhou stranu | Diskutabilní | Por otro lado přepíná aspekt/argument, por su parte perspektivu osoby. V některých souvětích se mohou sejít. |
| 231 | 762/763 | el examen / la prueba | zkouška / vyšetření (lékařské) / test, zkouška / důkaz | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 232 | 771/1340 | incorporar / incluir | zahrnout / přidat a vmíchat / zahrnout, zahrnovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 233 | 771/2489 | incorporar / abarcar | zahrnout / přidat a vmíchat / zahrnout, obsáhnout, pojmout | Odstraněno | Incorporar přidává či začleňuje, abarcar zahrnuje/obsahuje určitý rozsah. Přidání a zahrnování nejsou totéž. |
| 234 | 779/1526 | esconder / ocultar | schovat / skrýt, zakrýt, schovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 235 | 792/2478 | apetitoso / apetecible | chutný, lákavý / lákavý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 236 | 792/2591 | apetitoso / suculento | chutný, lákavý / šťavnatý, chutný, dobrý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 237 | 793/1369 | lejano / alejado | vzdálený / daleký, vzdálený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 238 | 810/1011 | la retribución / la remuneración | honorář, odměna, plat, mzda / odměna, výplata mzdy/platu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 239 | 819/2436 | lograr / obtener | dosáhnout (čeho vítězství apod.), získat (co) / získat, obdržet, dostat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 240 | 831/1158 | conjugar / coordinar | spojit, sloučit, sladit / koordinovat, sladit, ujednotit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 241 | 831/1527 | conjugar / conciliar | spojit, sloučit, sladit / smířit se, sladit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 242 | 833/1876 | urgir / insistir | naléhat / naléhat (na co), trvat (na čem) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 243 | 851/2530 | fugazmente / brevemente | krátce, prchavě / stručně, krátce | Diskutabilní | Fugazmente je prchavě, brevemente krátce/stručně. Délka trvání a rozsah výkladu nejsou totéž. |
| 244 | 853/2245 | atrevido / audaz | odvážný, troufalý / odvážný, smělý, neohrožený, troufalý, odhodlaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 245 | 855/983 | aplastar / pulverizar | rozdrtit, zničit / zničit, rozdrtit, rozprášit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 246 | 855/2351 | aplastar / destrozar | rozdrtit, zničit / zničit, rozbít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 247 | 855/2549 | aplastar / deshacer | rozdrtit, zničit / rozdělat, rozebrat, zničit, zrušit, vrátit zpět (co bylo uděláno) | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 248 | 855/2632 | aplastar / arrasar | rozdrtit, zničit / zničit, srovnat se zemí, zdevastovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 249 | 857/1632 | atesorar / acumular | hromadit, střádat / (na)hromadit, shromáždit, (a)kumulovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 250 | 859/2470 | desde luego / naturalmente | samozřejmě / přirozeně, samozřejmě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 251 | 862/1150 | a pesar de / pese a | navzdory, i přes, přestože / navzdory, i přes, přestože | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 252 | 867/1385 | en serio / seriamente | vážně / vážně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 253 | 878/2750 | enmendar / enderezar | napravit / napravit, dát do pořádku, narovnat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 254 | 879/1033 | la contienda / la pelea | spor / spor, rvačka, bitka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 255 | 886/1782 | esparcir / extender | rozšířit, rozptýlit, rozsypat, rozházet / rozšířit, rozprostřít, prodloužit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 256 | 886/2271 | esparcir / verter | rozšířit, rozptýlit, rozsypat, rozházet / rozlít, vylít / rozsypat, vysypat (záměrně) | Odstraněno | Esparcir rozptyluje/rozhazuje, verter vylévá/vysypává. Nalití do jedné nádoby není rozptýlení. |
| 257 | 886/2729 | esparcir / diseminar | rozšířit, rozptýlit, rozsypat, rozházet / rozšířit, rozptýlit, rozesít, rozšířit do různých míst | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 258 | 891/1156 | el atrevimiento / la valentía | odvaha, troufalost / odvaha, statečnost, udatnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 259 | 891/2541 | el atrevimiento / el coraje | odvaha, troufalost / odvaha, kuráž | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 260 | 895/1681 | el anhelo / la avidez | touha, vroucí přání, tužba / dychtivost, touha, lačnost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 261 | 900/2525 | perplejo / pasmado | rozpačitý, zaražený, zmatený / užaslý, zaražený, ohromený | Diskutabilní | Perplejo je zmatený, pasmado užaslý či strnulý překvapením; kombinace může nastat, ale není nutná. |
| 262 | 914/2351 | arruinar / destrozar | zničit, zruinovat, přivést na mizinu / zničit, rozbít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 263 | 914/2549 | arruinar / deshacer | zničit, zruinovat, přivést na mizinu / rozdělat, rozebrat, zničit, zrušit, vrátit zpět (co bylo uděláno) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 264 | 914/2632 | arruinar / arrasar | zničit, zruinovat, přivést na mizinu / zničit, srovnat se zemí, zdevastovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 265 | 915/1033 | la bronca / la pelea | hádka, rvačka, naštvání / spor, rvačka, bitka | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 266 | 920/2796 | perjudicar / estropear | poškodit / zkazit, poškodit, poničit, pokazit, porouchat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 267 | 921/1345 | asomar / aparecer | objevit se, ukázat se, začít být viděn / objevit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 268 | 921/2102 | asomar / surgir | objevit se, ukázat se, začít být viděn / objevit se, vzniknout, vynořit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 269 | 923/1442 | presunto / supuesto | předpokládaný, údajný / domnělý, předpokládaný, možný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 270 | 927/1102 | la asamblea / la tertulia | schůze / setkání, schůzka, dýchánek | Odstraněno | Asamblea je shromáždění/schůze s projednáváním, tertulia společenské debatní setkání. Jiný účel a typ setkání. |
| 271 | 938/1320 | el pedido / la demanda | objednávka, zakázka, žádost / poptávka, žádost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 272 | 941/947 | otorgar / conceder | dát, poskytnout, udělit / udělit, dát, poskytnout, připustit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 273 | 941/1473 | otorgar / adjudicar | dát, poskytnout, udělit / přidělit, udělit, přiřknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 274 | 947/1473 | conceder / adjudicar | udělit, dát, poskytnout, připustit / přidělit, udělit, přiřknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 275 | 950/1742 | restringir / circunscribir | omezit, snížit / omezit, vymezit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 276 | 953/1200 | en disidencia / en contra | proti / proti | Diskutabilní | En disidencia znamená s odlišným stanoviskem, en contra obecně proti; specifický kontext hlasování. |
| 277 | 955/1142 | en ese marco / en esa línea | v tomto rámci / v tomto rámci | Diskutabilní | En ese marco vymezuje rámec, en esa línea směr návazného argumentu; ne vždy stejná funkce. |
| 278 | 958/2823 | pleno / repleto | úplný, plný / plný, přeplněný, napěchovaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 279 | 974/1667 | arrebatar / extraer | vytrhnout, vyrvat, vyškubnout / vytáhnout, vyjmout, vytrhnout, odebrat | Odstraněno | Arrebatar je násilně/překotně vyrvat, extraer vyjmout či vytěžit; jiný způsob a povaha odebrání. |
| 280 | 976/1449 | abocado / enfocado | odsouzený, předurčený / soustředěný (dlouhodobě) / zaměřený, soustředěný (na) | Diskutabilní | Abocado a je v části Latinské Ameriky věnovaný práci, jinde předurčený výsledku; enfocado pouze zaměřený. |
| 281 | 981/1358 | potente / contundente | silný / silný, přesvědčivý, jednoznačný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 282 | 982/1412 | desechar / descartar | nepřijmout, odmítnout, zavrhnout  / odložit, vyhodit / vyloučit (možnost ap.), odmítnout, zavrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 283 | 982/2685 | desechar / repudiar | nepřijmout, odmítnout, zavrhnout  / odložit, vyhodit / odmítnout, odsoudit, neschvalovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 284 | 983/2351 | pulverizar / destrozar | zničit, rozdrtit, rozprášit / zničit, rozbít | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 285 | 983/2549 | pulverizar / deshacer | zničit, rozdrtit, rozprášit / rozdělat, rozebrat, zničit, zrušit, vrátit zpět (co bylo uděláno) | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 286 | 983/2632 | pulverizar / arrasar | zničit, rozdrtit, rozprášit / zničit, srovnat se zemí, zdevastovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 287 | 987/1764 | en torno / en torno a | zhruba, kolem ... / kolem, přibližně | Diskutabilní | En torno je v příkladu součástí en torno a; samostatné heslo je neúplné pro některé vazby. |
| 288 | 989/1408 | predominar / primar | převládat, převažovat počtem, být početnější / převládat, mít přednost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 289 | 989/1425 | predominar / prevalecer | převládat, převažovat počtem, být početnější / převládat, mít převahu (nad čím) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 290 | 989/1844 | predominar / imperar | převládat, převažovat počtem, být početnější / převládat, (za)vládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 291 | 1001/1541 | admitir / confesar | přijmout, připustit, uznat / vyznat, přiznat, doznat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 292 | 1001/1588 | admitir / asumir | přijmout, připustit, uznat / přijmout, uznat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 293 | 1004/1368 | prever / anticipar | předvídat, tušit / počítat (s čím) / předvídat / předjímat / udělat něco dopředu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 294 | 1008/1815 | atenuar / debilitar | zeslabit, zmírnit, ztišit / oslabit, zeslabit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 295 | 1008/2157 | atenuar / amortiguar | zeslabit, zmírnit, ztišit / (z)tlumit, zmírnit, potlačit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 296 | 1010/2109 | esbozar / amagar | načrtnout, naznačit (úsměv ap.) / dát najevo, naznačit / hrozit | Diskutabilní | Esbozar je načrtnout/naznačit, amagar předstírat náznak či hrozit. Platí jen pro začátek gesta/pohybu. |
| 297 | 1018/1402 | aclarar / explicar | vyjasnit, objasnit, vysvětlit / vysvětlit, vyložit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 298 | 1018/1914 | aclarar / definir | vyjasnit, objasnit, vysvětlit / vymezit, určit, definovat, objasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 299 | 1018/2209 | aclarar / esclarecer | vyjasnit, objasnit, vysvětlit / objasnit, vysvětlit, vyjasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 300 | 1023/1407 | derogar / cancelar | zrušit (zákon ap.) / zrušit | Odstraněno | Derogar ruší platnost právní normy, cancelar ruší např. rezervaci/let. Bez právního vymezení se rozdíl ztrácí. |
| 301 | 1024/1426 | advertir / alertar | upozornit, varovat, napomenout / varovat, zalarmovat, burcovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 302 | 1031/2238 | calificar / marcar | označit, prohlásit (za co), ohodnotit / označit, vyznačit, ukázat | Diskutabilní | Calificar hodnotí či označuje jako něco, marcar dává značku/vyznačuje. Překryv při klasifikaci není obecné hodnocení. |
| 303 | 1035/2635 | generar / provocar | způsobit, vyvolat / vyvolat, způsobit, vyprovokovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 304 | 1039/1205 | el acuerdo / el convenio | dohoda, shoda, souhlas / úmluva, smlouva, dohoda | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 305 | 1048/1143 | comprobar / reafirmar | potvrdit, dokázat, prokázat / (znovu) potvrdit | Odstraněno | Comprobar/verificar ověřují pravdivost; reafirmar znovu vyslovuje/potvrzuje stanovisko bez nutného ověřování. |
| 306 | 1048/1463 | comprobar / confirmar | potvrdit, dokázat, prokázat / potvrdit, dotvrdit, stvrdit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 307 | 1048/1490 | comprobar / verificar | potvrdit, dokázat, prokázat / ověřit, potvrdit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 308 | 1048/1828 | comprobar / corroborar | potvrdit, dokázat, prokázat / potvrdit, podpořit (tvrzení ap.), zdůraznit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 309 | 1050/1744 | la seňal / el indicio | znamení, známka, (pří)znak / indicie, známka, stopa, příznak | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 310 | 1051/1063 | la maňa / la astucia | zlozvyk, manýra / šikovnost / vychytralost / vychytralost, mazanost | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 311 | 1055/1509 | la apertura / el inicio | zahájení, slavnostní otevření / začátek, zahájení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 312 | 1061/1062 | presumido / presuntuoso | namyšlený, chlubivý / ješitný, nafoukaný, namyšlený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 313 | 1068/1282 | estimular / incentivar | stimulovat, podnítit, pobízet / pobízet, podněcovat, povzbuzovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 314 | 1073/2102 | irrumpir / surgir | objevit se, (nečekaně) přijít, vynořit se / objevit se, vzniknout, vynořit se | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 315 | 1092/1114 | feroz / salvaje | zuřivý, divoký / divoký | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 316 | 1092/1476 | feroz / furibundo | zuřivý, divoký / vzteklý, rozzuřený, zuřivý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 317 | 1095/1778 | multitudinario / masivo | početný, masový, hromadný / masový, hromadný, obrovský | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 318 | 1100/1819 | afín / semejante | podobný (názory ap.), příbuzný, blízký / podobný, obdobný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 319 | 1121/1186 | estar al día / estar al tanto de | mít vše zaplacené, vyřízené, být v obraze / být informován o, být v obraze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 320 | 1133/1596 | en virtud de / a partir de | na základě, z titulu, v důsledku / od, počínaje, na základě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 321 | 1133/1780 | en virtud de / en base a | na základě, z titulu, v důsledku / na základě, založený na | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 322 | 1135/1191 | garantizar / asegurar | garantovat, zaručit / ujistit, zajistit, zaručit, zabezpečit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 323 | 1137/1498 | fortalecer / afirmar | posílit, upevnit, utvrdit / potvrdit, tvrdit, upevnit, připevnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 324 | 1137/1792 | fortalecer / consolidar | posílit, upevnit, utvrdit / upevnit, utvrdit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 325 | 1137/1838 | fortalecer / reforzar | posílit, upevnit, utvrdit / zpevnit, posílit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 326 | 1137/1846 | fortalecer / fijar | posílit, upevnit, utvrdit / připevnit, upevnit, uchytit | Odstraněno | Fortalecer/consolidar posilují a upevňují stabilitu; fijar připevňuje nebo stanovuje. Jiné významy upevnit. |
| 327 | 1138/2394 | puntualizar / matizar | upřesnit, zpřesnit, doplnit / upřesnit, vysvětlit, objasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 328 | 1139/1148 | permanente / duradero | trvalý, stálý, ustavičný / trvalý, trvající, přetrvávající | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 329 | 1139/1403 | permanente / crónico | trvalý, stálý, ustavičný / zakořeněný, vžitý, trvalý, dlouhodobý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 330 | 1140/2786 | del mismo modo / al igual que | stejně, stejným způsobem, podobně / stejně jako, podobně jako | Diskutabilní | Del mismo modo může stát samostatně, al igual que vyžaduje porovnávaný doplněk. Význam blízký, konstrukce odlišná. |
| 331 | 1141/1198 | subrayar / enfatizar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 332 | 1141/1828 | subrayar / corroborar | zdůraznit, vyzdvihnout, podtrhnout / potvrdit, podpořit (tvrzení ap.), zdůraznit | Odstraněno | Subrayar/enfatizar zdůrazňují důležitost; corroborar potvrzuje správnost či podkládá tvrzení. Důraz není důkaz. |
| 333 | 1141/2494 | subrayar / resaltar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, vyzdvihnout, vyniknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 334 | 1141/2661 | subrayar / recalcar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, vyzdvihnout, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 335 | 1141/2791 | subrayar / acentuar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 336 | 1143/1463 | reafirmar / confirmar | (znovu) potvrdit / potvrdit, dotvrdit, stvrdit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 337 | 1143/1490 | reafirmar / verificar | (znovu) potvrdit / ověřit, potvrdit | Odstraněno | Comprobar/verificar ověřují pravdivost; reafirmar znovu vyslovuje/potvrzuje stanovisko bez nutného ověřování. |
| 338 | 1143/1498 | reafirmar / afirmar | (znovu) potvrdit / potvrdit, tvrdit, upevnit, připevnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 339 | 1143/1828 | reafirmar / corroborar | (znovu) potvrdit / potvrdit, podpořit (tvrzení ap.), zdůraznit | Diskutabilní | Reafirmar posiluje/znovu potvrzuje stanovisko, corroborar ho opírá o potvrzení; nutný kontext. |
| 340 | 1144/1685 | indeclinable / indispensable | nevyhnutelný, neodvratný, nezbytný / nezbytný, nevyhnutelný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 341 | 1144/1745 | indeclinable / esencial | nevyhnutelný, neodvratný, nezbytný / nezbytný, nepostradatelný, zásadní | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 342 | 1144/1864 | indeclinable / inevitable | nevyhnutelný, neodvratný, nezbytný / nevyhnutelný, neodvratný, neodvratitelný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 343 | 1144/2412 | indeclinable / imprescindible | nevyhnutelný, neodvratný, nezbytný / nezbytný, nutný, nepostradatelný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 344 | 1146/2101 | difundir / expandir | (roz)šířit, rozšiřovat / (roz)šířit, rozpínat, roztahovat, roztahovat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 345 | 1148/1403 | duradero / crónico | trvalý, trvající, přetrvávající / zakořeněný, vžitý, trvalý, dlouhodobý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 346 | 1155/2265 | perpetrar / ejecutar | spáchat, vykonat / provést, vykonat, vyřídit | Odstraněno | Perpetrar je spáchat zločin či závažné provinění, realizar/ejecutar obecně něco provést. U běžného projektu nejde o zaměnitelné označení. |
| 347 | 1156/2541 | la valentía / el coraje | odvaha, statečnost, udatnost / odvaha, kuráž | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 348 | 1158/1527 | coordinar / conciliar | koordinovat, sladit, ujednotit / smířit se, sladit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 349 | 1163/1708 | de hecho / en el fondo | ve skutečnosti / v hloubi (duše), na dně, ve skutečnosti | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 350 | 1163/2404 | de hecho / en rigor | ve skutečnosti / přesně vzato, striktně řečeno, ve skutečnosti | Odstraněno | De hecho znamená ve skutečnosti/fakticky, en rigor přesně vzato. Rozdílné vymezení tvrzení. |
| 351 | 1166/2241 | por otra parte / por su parte | na druhou stranu / ze své strany, pokud jde o něj/ni, na druhou stranu | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 352 | 1169/1174 | ya que / puesto que | protože, jelikož / jelikož, protože | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 353 | 1171/1764 | hacia / en torno a | směrem k, kolem (čas) / kolem, přibližně | Diskutabilní | Hacia a en torno a se překrývají u přibližného času, nikoliv při pohybu směrem k. |
| 354 | 1173/1177 | anda / vaya | no teda, hele / no teda, sakra | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 355 | 1175/1439 | por ende / a su vez | tudíž, následně / zase, následně, na oplátku, ze své strany | Odstraněno | Por ende je důsledkové tudíž; a su vez zase/ze své strany či následně. Následnost neznamená příčinný důsledek. |
| 356 | 1177/2312 | vaya / carajo | no teda, sakra / pták, péro, ocas  / sakra!, do prdele!, hergot! | Diskutabilní | Vaya je mírné překvapení, carajo vulgární citoslovce; společná reakce nezaručuje vhodný registr. |
| 357 | 1177/2638 | vaya / caramba | no teda, sakra / sakra!, k čertu!, hrome! | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 358 | 1178/2117 | al contrario / al revés | naopak / naopak | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 359 | 1179/2462 | salvo / por fuera de | kromě, vyjma / mimo, kromě / zvenku, na vnější straně | Diskutabilní | Por fuera de v abstraktním kromě je regionální; salvo jednoznačně vyjímá. Rozhodnout cílovou varietu. |
| 360 | 1191/1953 | asegurar / interceptar | ujistit, zajistit, zaručit, zabezpečit / zadržet, zachytit, zajistit | Odstraněno | Asegurar zajišťuje či ujišťuje, interceptar zachycuje v pohybu. Jiné významy zajistit. |
| 361 | 1192/2135 | desatar / desregular | odvázat, rozvázat, uvolnit / deregulovat, uvolnit | Odstraněno | Desatar je rozvázat či rozpoutat; desregular zrušit regulační pravidla. Metaforická souvislost není běžná synonymie. |
| 362 | 1192/2757 | desatar / soltar | odvázat, rozvázat, uvolnit / rozvázat, uvolnit, povolit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 363 | 1194/1920 | adelantado / puntero | pokročilý, daleko před ostatními / přední, čelný pozice, pokročilý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 364 | 1197/2410 | exponer / exhibir | vystavit, vystavovat, předvést  / vystavit, ukazovat, předvádět | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 365 | 1198/1828 | enfatizar / corroborar | zdůraznit, podtrhnout / potvrdit, podpořit (tvrzení ap.), zdůraznit | Odstraněno | Subrayar/enfatizar zdůrazňují důležitost; corroborar potvrzuje správnost či podkládá tvrzení. Důraz není důkaz. |
| 366 | 1198/2494 | enfatizar / resaltar | zdůraznit, podtrhnout / zdůraznit, vyzdvihnout, vyniknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 367 | 1198/2661 | enfatizar / recalcar | zdůraznit, podtrhnout / zdůraznit, vyzdvihnout, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 368 | 1198/2791 | enfatizar / acentuar | zdůraznit, podtrhnout / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 369 | 1199/1434 | promulgar / anunciar | oznámit, dát na vědomí, zveřejnit / oznámit, ohlásit, zvěstovat | Diskutabilní | Promulgar může slavnostně zveřejnit či vyhlásit zákon, anunciar obecně oznámit. Právní kontext je užší. |
| 370 | 1199/1502 | promulgar / notificar | oznámit, dát na vědomí, zveřejnit / oznámit, sdělit, (vy)hlásit | Diskutabilní | Promulgar je veřejně vyhlásit, notificar vyrozumět adresáta; různé role právního oznámení. |
| 371 | 1201/1707 | compuesto / ordenado | složený, poskládaný, komponovaný / uspořádaný, seřazený, poskládaný | Diskutabilní | Compuesto je sestavený/složený, ordenado uspořádaný; u upraveného vzhledu je překryv, příklady jej nevymezují. |
| 372 | 1202/1698 | habitual / cotidiano | obvyklý, všední, normální / každodenní, dennodenní, obvyklý, normální | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 373 | 1202/2666 | habitual / convencional | obvyklý, všední, normální / konvenční, dohodnutý, obvyklý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 374 | 1203/1482 | habilitar / permitir | povolit, umožnit, aktivovat / povolit, dovolit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 375 | 1203/2757 | habilitar / soltar | povolit, umožnit, aktivovat / rozvázat, uvolnit, povolit | Odstraněno | Habilitar povoluje/umožňuje/zprovozňuje, soltar povoluje sevření nebo pouští. Jiné významy povolit. |
| 376 | 1204/1617 | sustituir / reemplazar | vyměnit, nahradit, vystřídat / nahradit, vyměnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 377 | 1204/2214 | sustituir / mudar | vyměnit, nahradit, vystřídat / změnit, přemístit, přenést, vyměnit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 378 | 1206/1536 | requerir / reivindicar | vyžadovat, potřebovat, požadovat / hájit, obhajovat, očistit / požadovat, žádat co | Diskutabilní | Requerir vyžaduje či požaduje, reivindicar uplatňuje nárok/právo. České požadovat nevymezuje účel. |
| 379 | 1207/1943 | vinculado / asociado | spojený, související / spojený, sdružený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 380 | 1207/2331 | vinculado / ligado | spojený, související / (s)vázaný, spojený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 381 | 1212/1237 | hinchar las bolas / hinchar las pelotas | otravovat, lézt na nervy ("nafukovat balón") / otravovat ("nafukovat balóny") | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 382 | 1213/1237 | romper las bolas / hinchar las pelotas | strašně otravovat ("rozbíjet balón") / otravovat ("nafukovat balóny") | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 383 | 1224/1231 | que culo / que orto | jaké štěstí ("jaký zadek") / jaké štěstí ("jaký zadek") | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 384 | 1250/2045 | ni a palos / ni ahí | ani náhodou ("ani holemi") / ani náhodou, vůbec ne, ani omylem | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 385 | 1253/2354 | el liderazgo / el caudillismo | vedení, vedoucí pozice, vůdcovství / vůdcovství, vůdcovský systém | Odstraněno | Liderazgo je obecně vůdcovství, caudillismo konkrétní politický systém vlády vůdce. Obecný pojem a jeho podtyp. |
| 386 | 1259/2770 | aquejar / torturar | sužovat, trápit, postihnout nemoc ap. / mučit, trápit, trýznit | Diskutabilní | Aquejar je sužovat, torturar mučit; figurativní trápení je možné, intenzita se zásadně liší. |
| 387 | 1259/2775 | aquejar / acongojar | sužovat, trápit, postihnout nemoc ap. / (za)rmoutit, trápit, soužit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 388 | 1260/1454 | erradicar / exterminar | vymýtit, vyhladit, vykořenit / (vy)hubit, vyhladit, zahubit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 389 | 1260/2792 | erradicar / alisar | vymýtit, vyhladit, vykořenit / (u)hladit, vyhladit | Odstraněno | Erradicar je vymýtit/vyhladit problém či populaci; alisar fyzicky uhladit povrch. |
| 390 | 1265/2157 | contrarrestar / amortiguar | zmírnit (následky ap.) / (z)tlumit, zmírnit, potlačit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 391 | 1265/2822 | contrarrestar / ablandar | zmírnit (následky ap.) / změkčit, změkčovat / obměkčit, zmírnit | Odstraněno | Contrarrestar působí proti účinku, ablandar změkčuje či obměkčuje. Zmírnění není zde stejný děj. |
| 392 | 1281/2058 | consecutivo / siguiente | (za sebou) následující, po sobě jdoucí, v řadě / následující, příští, další | Diskutabilní | Consecutivo jsou po sobě jdoucí bez mezery, siguiente následující. Samotná následnost není nepřerušená série. |
| 393 | 1282/1495 | incentivar / impulsar | pobízet, podněcovat, povzbuzovat / pohánět, hnát, podněcovat, povzbuzovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 394 | 1282/1613 | incentivar / alentar | pobízet, podněcovat, povzbuzovat / povzbuzovat, dodávat odvahu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 395 | 1289/1664 | el nacimiento / el principio | narození, počátek, zrod, vznik / začátek, počátek / princip  | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 396 | 1291/1637 | genuino / fiel | opravdový, pravdivý, nefalšovaný / věrný, pravdivý, přesný | Odstraněno | Genuino je autentický/nefalšovaný; fiel věrný člověk nebo věrně odpovídající zobrazení. Pravost není věrnost. |
| 397 | 1294/1322 | plantear / sugerir | nastínit, vyložit, vylíčit / navrhnout / navrhnout, doporučit, předložit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 398 | 1294/1402 | plantear / explicar | nastínit, vyložit, vylíčit / navrhnout / vysvětlit, vyložit | Odstraněno | Plantear předkládá otázku/návrh, explicar ji vysvětluje. Nastolení tématu a výklad se zaměňují. |
| 399 | 1296/1954 | la carga / el cargamento | zátěž, náklad, břemeno / náklad, přepravované zboží | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 400 | 1298/2100 | aliviar / allanar | ulehčit, usnadnit, ulevit / odstranit překážky, usnadnit / vyrovnat, uhladit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 401 | 1299/2210 | como sea / de todos modos | Ať je to jakkoli, každopádně, stejně, anyway / každopádně, v každém případě, stejně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 402 | 1299/2240 | como sea / de todas formas | Ať je to jakkoli, každopádně, stejně, anyway / každopádně, stejně, v každém případě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 403 | 1299/2348 | como sea / sea como sea | Ať je to jakkoli, každopádně, stejně, anyway / ať je to jak chce, tak či onak, každopádně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 404 | 1300/2294 | profundamente / intensamente | hluboce, tvrdě, intenzivně / intenzivně, silně, usilovně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 405 | 1300/2340 | profundamente / duramente | hluboce, tvrdě, intenzivně / tvrdě | Odstraněno | Profundamente je hluboce, duramente tvrdě/přísně. Silné zasažení není totéž co tvrdé zacházení. |
| 406 | 1303/1357 | la brecha / la grieta | trhlina / poranění, tržná rána / mezera, propast / trhlina, puklina | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 407 | 1306/1321 | revertir / retroceder | obrátit se, (na)vrátit se, změnit se  / couvnout, ustoupit, vrátit se | Diskutabilní | Revertir obrací vývoj zpět, retroceder ustupuje/zpětně se pohybuje. Společný návrat jen v některých konstrukcích. |
| 408 | 1306/1416 | revertir / recurrir | obrátit se, (na)vrátit se, změnit se  / uchýlit se, obrátit se (k čemu) | Odstraněno | Revertir je navrátit/obrátit stav; recurrir obrátit se na pomoc/prostředek. |
| 409 | 1306/2112 | revertir / virar | obrátit se, (na)vrátit se, změnit se  / odbočit, zabočit / změnit se (názory ap.) | Odstraněno | Revertir obrací vývoj zpět; virar mění směr. Obrácení předchozího vývoje není libovolná změna směru. |
| 410 | 1307/1521 | altamente / completamente | vysoce, naprosto, zcela / úplně, zcela, naprosto | Odstraněno | Altamente znamená vysoce, completamente/enteramente/totalmente/plenamente úplně/plně. Vysoká míra není úplnost. |
| 411 | 1307/2088 | altamente / enteramente | vysoce, naprosto, zcela / úplně, zcela, naprosto | Odstraněno | Altamente znamená vysoce, completamente/enteramente/totalmente/plenamente úplně/plně. Vysoká míra není úplnost. |
| 412 | 1307/2299 | altamente / totalmente | vysoce, naprosto, zcela / úplně, zcela, naprosto | Odstraněno | Altamente znamená vysoce, completamente/enteramente/totalmente/plenamente úplně/plně. Vysoká míra není úplnost. |
| 413 | 1307/2420 | altamente / plenamente | vysoce, naprosto, zcela / zcela, plně, naprosto | Odstraněno | Altamente znamená vysoce, completamente/enteramente/totalmente/plenamente úplně/plně. Vysoká míra není úplnost. |
| 414 | 1308/2377 | percibir / cobrar | pobírat, dostávat, brát (důchod ap.) / dostávat (plat), brát, (na)účtovat si, (vy)inkasovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 415 | 1310/1755 | inasumible / inaceptable | nepřijatelný / nepřijatelný, neakceptovatelný, netolerovatelný | Diskutabilní | Inasumible je nezvládnutelný/neúnosný jako závazek, inaceptable nepřijatelný hodnotově. |
| 416 | 1313/2390 | encadenar / hilvanar | spojit, navázat na sebe / připoutat, spoutat řetězem / pospojovat, dát dohromady, navázat na sebe / sestehovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 417 | 1318/1576 | impactar / intervenir | mít dopad / zapůsobit / šokovat / zasáhnout / zapojit se, zasáhnout, zakročit | Odstraněno | Impactar znamená zasáhnout účinkem/šokovat, intervenir zapojit se či zakročit. |
| 418 | 1318/2259 | impactar / repercutir | mít dopad / zapůsobit / šokovat / zasáhnout / mít dopad, ovlivnit, promítnout se do | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 419 | 1318/2818 | impactar / escandalizar | mít dopad / zapůsobit / šokovat / zasáhnout / pobouřit, šokovat, pohoršit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 420 | 1322/1457 | sugerir / presentar | navrhnout, doporučit, předložit / předložit, ukázat, představit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 421 | 1322/1568 | sugerir / aportar | navrhnout, doporučit, předložit / dát, přinést, předložit | Odstraněno | Sugerir navrhuje/doporučuje, aportar poskytuje či přináší příspěvek. Jiné významy předložit. |
| 422 | 1323/1469 | encaminar / canalizar | směřovat, zaměřit / směrovat, usměrnit, vést, přesměrovat (tok, energii, zdroje) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 423 | 1323/2642 | encaminar / tender | směřovat, zaměřit / směřovat, mít tendenci / rozvěsit (prádlo), natáhnout, rozprostřít / podat (ruku) | Odstraněno | Encaminar přechodně směruje/zaměřuje něco, tender zde nepřechodně směřuje k cíli či tendenci. Jiné argumenty a konstrukce. |
| 424 | 1324/1362 | contestar / replicar | odpovědět, zodpovědět / odpovědět, oponovat / napodobit, replikovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 425 | 1331/2526 | lentamente / paulatinamente | pomalu / postupně, (po)zvolna, pomalu | Diskutabilní | Lentamente je pomalu, paulatinamente postupně; rychlost a postupnost se mohou lišit. |
| 426 | 1334/2338 | rápidamente / deprisa | rychle / rychle, spěšně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 427 | 1336/1483 | recién / justamente | právě, nedávno / zrovna, právě, přesně | Odstraněno | Recién je právě teď/nedávno, justamente/precisamente právě v důrazovém smyslu přesně. Časová blízkost není důrazová přesnost. |
| 428 | 1336/1687 | recién / precisamente | právě, nedávno / přesně, právě | Odstraněno | Recién je právě teď/nedávno, justamente/precisamente právě v důrazovém smyslu přesně. Časová blízkost není důrazová přesnost. |
| 429 | 1338/2239 | seguramente / definitivamente | určitě, jistě / definitivně, jistě, určitě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 430 | 1338/2341 | seguramente / ciertamente | určitě, jistě / jistě, určitě, zajisté | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 431 | 1338/2677 | seguramente / firmemente | určitě, jistě / pevně, jistě | Odstraněno | Seguramente vyjadřuje jistotu/pravděpodobnost tvrzení, firmemente pevný/důrazný způsob jednání. |
| 432 | 1340/1754 | incluir / encuadrar | zahrnout, zahrnovat / (za)rámovat, (za)řadit, zahrnout, zahrnovat  | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 433 | 1340/2489 | incluir / abarcar | zahrnout, zahrnovat / zahrnout, obsáhnout, pojmout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 434 | 1340/2660 | incluir / colmar | zahrnout, zahrnovat / naplnit až po okraj, zahrnout | Odstraněno | Incluir je zařadit/obsahovat, colmar naplnit či zahrnout někoho dary. Jiné významy zahrnout. |
| 435 | 1343/2429 | descubrir / detectar | objevit, odhalit / zjistit, objevit, odhalit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 436 | 1344/1526 | cubrir / ocultar | pokrýt, zakrýt / skrýt, zakrýt, schovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 437 | 1345/2090 | aparecer / brotar | objevit se / vytrysknout (voda, krev) / vyrašit (rostliny) / objevit se, vzniknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 438 | 1345/2102 | aparecer / surgir | objevit se / objevit se, vzniknout, vynořit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 439 | 1346/2355 | resolver / destrabar | vyřešit / zjednodušit, vyřešit, odstranit překážky | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 440 | 1348/1412 | excluir / descartar | vyloučit, vyřadit / vyloučit (možnost ap.), odmítnout, zavrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 441 | 1348/2655 | excluir / expulsar | vyloučit, vyřadit / vyhnat, vypovědět, vyloučit, vyhodit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 442 | 1351/1441 | augurar / vaticinar | věštit, předpovídat, prorokovat / předpovídat, věštit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 443 | 1351/2290 | augurar / pronosticar | věštit, předpovídat, prorokovat / předpovídat, prorokovat, věštit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 444 | 1353/1915 | la encuesta / el relevamiento | anketa, průzkum / průzkum, sběr dat, šetření | Diskutabilní | Relevamiento je regionální průzkum/sběr dat, encuesta konkrétně šetření dotazováním; cílový region a metoda rozhodují. |
| 445 | 1356/2320 | enfrentar / encarar | čelit, postavit proti sobě, znepřátelit / čelit, postavit se čelem / oslovit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 446 | 1361/2395 | chueco / sinuoso | křivý / spletitý, složitý / křivý, klikatý | Diskutabilní | Chueco je křivě postavený/pokřivený, sinuoso vinutý/klikatý. Jiný tvar křivosti. |
| 447 | 1363/2001 | la postura / el emplazamiento | pozice (názorová) / postoj, držení těla / umístění, poloha, pozice | Odstraněno | Postura je tělesný nebo názorový postoj, emplazamiento umístění objektu. Jiný význam pozice. |
| 448 | 1369/1923 | alejado / apartado | daleký, vzdálený / odlehlý, daleký, vzdálený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 449 | 1375/1400 | repentino / inesperado | náhlý, nečekaný, nenadálý / nečekaný, nenadálý, překvapivý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 450 | 1375/2554 | repentino / sorpresivo | náhlý, nečekaný, nenadálý / překvapivý, nečekaný, nenadálý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 451 | 1383/2218 | suceder / ocurrir | stát se, přihodit se, udát se / stát se, přihodit se, udát se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 452 | 1391/1525 | detener / retener | (po)zastavit, zadržet, potlačit nákazu / zadržet, zadržovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 453 | 1391/1933 | detener / incautar | (po)zastavit, zadržet, potlačit nákazu / zabavit, odebrat, zadržet | Odstraněno | Detener zastavuje/zadržuje, interceptar zachycuje při pohybu, incautar právně zabavuje majetek. Odlišné policejní úkony. |
| 454 | 1391/1953 | detener / interceptar | (po)zastavit, zadržet, potlačit nákazu / zadržet, zachytit, zajistit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 455 | 1391/2313 | detener / paralizar | (po)zastavit, zadržet, potlačit nákazu / ochromit, paralyzovat, zastavit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 456 | 1391/2315 | detener / reprimir | (po)zastavit, zadržet, potlačit nákazu / zadržet, potlačit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 457 | 1391/2777 | detener / sujetar | (po)zastavit, zadržet, potlačit nákazu / držet, přidržovat, upevnit / zadržet / zkrotit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 458 | 1399/2188 | directamente / de forma directa | přímo / přímo | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 459 | 1400/2554 | inesperado / sorpresivo | nečekaný, nenadálý, překvapivý / překvapivý, nečekaný, nenadálý | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 460 | 1401/2756 | pelear / fajarse | prát se, hádat se / zápasit, bít se, prát se | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 461 | 1402/2209 | explicar / esclarecer | vysvětlit, vyložit / objasnit, vysvětlit, vyjasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 462 | 1402/2394 | explicar / matizar | vysvětlit, vyložit / upřesnit, vysvětlit, objasnit | Odstraněno | Explicar vysvětluje, matizar přidává odstín/omezení či kvalifikuje již vyslovené tvrzení. |
| 463 | 1408/1425 | primar / prevalecer | převládat, mít přednost / převládat, mít převahu (nad čím) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 464 | 1408/1844 | primar / imperar | převládat, mít přednost / převládat, (za)vládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 465 | 1412/2685 | descartar / repudiar | vyloučit (možnost ap.), odmítnout, zavrhnout / odmítnout, odsoudit, neschvalovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 466 | 1422/2776 | coincidir / asentir | shodovat se, souhlasit, sejít se, potkat se náhodou / souhlasit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 467 | 1425/1844 | prevalecer / imperar | převládat, mít převahu (nad čím) / převládat, (za)vládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 468 | 1428/2391 | participar / coparticipar | (z)účastnit se, mít podíl/účast / (z)účastnit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 469 | 1430/1513 | adaptar / apropiar | přizpůsobit, uzpůsobit / přizpůsobit | Diskutabilní | Apropiar bez se může slovníkově znamenat přizpůsobit, ale příklad naznačuje přivlastnění finančních prostředků. Rozpor kontextu. |
| 470 | 1430/2477 | adaptar / ajustar | přizpůsobit, uzpůsobit / upravit, seřídit, přizpůsobit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 471 | 1432/1720 | captar / comprender | zachytit / pochopit / (po)rozumět, pochopit, chápat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 472 | 1434/1502 | anunciar / notificar | oznámit, ohlásit, zvěstovat / oznámit, sdělit, (vy)hlásit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 473 | 1435/1629 | tramitar / negociar | vyřídit, vyjednat, zařídit / obchodovat, jednat, vyjednat | Odstraněno | Tramitar vyřizuje administrativní postup, negociar vyjednává podmínky či obchoduje. |
| 474 | 1436/2614 | encarcelar / encerrar | uvěznit, zavřít/dát do vězení / zavřít, uvěznit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 475 | 1439/2241 | a su vez / por su parte | zase, následně, na oplátku, ze své strany / ze své strany, pokud jde o něj/ni, na druhou stranu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 476 | 1441/2290 | vaticinar / pronosticar | předpovídat, věštit / předpovídat, prorokovat, věštit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 477 | 1446/2557 | vanagloriarse / ufanarse | vychloubat se, chlubit se, chvástat se / vytahovat se, vychloubat se, naparovat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 478 | 1448/2383 | proporcionalmente / adecuadamente | poměrně, úměrně, proporčně / adekvátně, přiměřeně, úměrně | Odstraněno | Proporcionalmente vyjadřuje číselný poměr, adecuadamente náležitost/správnost. Přiměřenost není proporcionalita. |
| 479 | 1456/1701 | es decir / en otras palabras | tedy, to znamená, jinými slovy / jinými slovy | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 480 | 1457/1568 | presentar / aportar | předložit, ukázat, představit / dát, přinést, předložit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 481 | 1463/1490 | confirmar / verificar | potvrdit, dotvrdit, stvrdit / ověřit, potvrdit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 482 | 1463/1498 | confirmar / afirmar | potvrdit, dotvrdit, stvrdit / potvrdit, tvrdit, upevnit, připevnit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 483 | 1463/1828 | confirmar / corroborar | potvrdit, dotvrdit, stvrdit / potvrdit, podpořit (tvrzení ap.), zdůraznit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 484 | 1469/2161 | canalizar / morigerar | směrovat, usměrnit, vést, přesměrovat (tok, energii, zdroje) / usměrnit, mírnit (chování) | Odstraněno | Canalizar usměrňuje tok/energii k cíli, morigerar mírní či krotí chování. |
| 485 | 1471/1881 | evaluar / tasar | ocenit, odhadnout, vyčíslit  / stanovit hodnotu/cenu (čeho), ocenit (co) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 486 | 1471/2738 | evaluar / estimar | ocenit, odhadnout, vyčíslit  / odhadnout, ocenit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 487 | 1473/2815 | adjudicar / destinar | přidělit, udělit, přiřknout / určit, vyčlenit, přidělit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 488 | 1474/1760 | detallado / minucioso | podrobný, detailní / pečlivý, podrobný, důkladný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 489 | 1479/2495 | analizar / examinar | analyzovat, rozebrat / zkoumat, přezkoumat, analyzovat, důkladně prohlédnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 490 | 1483/1687 | justamente / precisamente | zrovna, právě, přesně / přesně, právě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 491 | 1483/1967 | justamente / exactamente | zrovna, právě, přesně / přesně, exaktně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 492 | 1484/1844 | dominar / imperar | vládnout, panovat, ovládat / převládat, (za)vládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 493 | 1486/2166 | provisionalmente / temporalmente | dočasně, provizorně / dočasně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 494 | 1490/1828 | verificar / corroborar | ověřit, potvrdit / potvrdit, podpořit (tvrzení ap.), zdůraznit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 495 | 1491/1921 | regir / liderar | být platný, platit / řídit, spravovat / vést, řídit, šéfovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 496 | 1491/2798 | regir / regentar | být platný, platit / řídit, spravovat / vést, řídit, spravovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 497 | 1495/1613 | impulsar / alentar | pohánět, hnát, podněcovat, povzbuzovat / povzbuzovat, dodávat odvahu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 498 | 1497/2259 | afectar / repercutir | týkat se, ovlivnit / mít dopad, ovlivnit, promítnout se do | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 499 | 1498/1828 | afirmar / corroborar | potvrdit, tvrdit, upevnit, připevnit / potvrdit, podpořit (tvrzení ap.), zdůraznit | Diskutabilní | Afirmar vyslovuje/potvrzuje stanovisko, corroborar potvrzuje podpůrnými údaji. Rozdíl jistoty/podložení. |
| 500 | 1498/2287 | afirmar / aseverar | potvrdit, tvrdit, upevnit, připevnit / tvrdit, prohlašovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 501 | 1509/1664 | el inicio / el principio | začátek, zahájení / začátek, počátek / princip  | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 502 | 1510/1659 | marginar / retirar | odsunout, nechat stranou, marginalizovat / odstranit, odklidit, odsunout, odtáhnout | Odstraněno | Marginar sociálně vyčleňuje či opomíjí; retirar odebírá/stahuje. Sociální marginalizace není běžné odstranění předmětu. |
| 503 | 1510/2306 | marginar / desplazar | odsunout, nechat stranou, marginalizovat / přemístit, přesunout, odsunout | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 504 | 1510/2670 | marginar / alejar | odsunout, nechat stranou, marginalizovat / oddálit, odsunout, vzdálit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 505 | 1511/1783 | exclusivamente / solamente | výlučně, pouze, jen, výhradně / jen(om), pouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 506 | 1511/1906 | exclusivamente / únicamente | výlučně, pouze, jen, výhradně / pouze, jen, avšak | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 507 | 1513/2477 | apropiar / ajustar | přizpůsobit / upravit, seřídit, přizpůsobit | Diskutabilní | Apropiar má i přizpůsobit, jeho příklad ale patří přivlastnění. Význam není v datech spolehlivě oddělen. |
| 508 | 1521/2088 | completamente / enteramente | úplně, zcela, naprosto / úplně, zcela, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 509 | 1521/2299 | completamente / totalmente | úplně, zcela, naprosto / úplně, zcela, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 510 | 1521/2420 | completamente / plenamente | úplně, zcela, naprosto / zcela, plně, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 511 | 1523/1818 | refutar / desmentir | vyvrátit, popřít / dementovat, popřít, vyvrátit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 512 | 1526/1533 | ocultar / camuflar | skrýt, zakrýt, schovat / (za)maskovat, ukrýt, skrýt | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 513 | 1531/2589 | la fuga / el escape | útěk, utíkání, únik / útěk, únik, východisko | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 514 | 1534/1982 | eventualmente / posiblemente | možná, popřípadě / možná, případně, možná že | Diskutabilní | Eventualmente obvykle příležitostně/podle okolností; možná je regionální či kontextové. Příklad může být ovlivněn anglickým eventually. |
| 515 | 1566/1570 | diverso / distinto | různý, rozdílný, rozličný / odlišný, rozdílný, jiný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 516 | 1571/1734 | empeorar / agravar | zhoršit / ztížit, zhoršit, udělat těžším | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 517 | 1573/2843 | evidente / flagrante | zřejmý, zjevný, jasný, očividný / do očí bijící, zjevný, očividný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 518 | 1579/1914 | determinar / definir | určit, stanovit, rozhodnout / vymezit, určit, definovat, objasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 519 | 1592/1958 | signar / rotular | označit, orazítkovat / opatřit popisem (kresbu ap.), označit (plánek ap.) | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 520 | 1592/2238 | signar / marcar | označit, orazítkovat / označit, vyznačit, ukázat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 521 | 1593/1738 | blindar / resguardar | obrnit, chránit, oplechovat / chránit, bránit, ochraňovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 522 | 1595/1601 | la desgracia / el infortunio | neštěstí, smůla / neštěstí, pohroma | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 523 | 1596/1780 | a partir de / en base a | od, počínaje, na základě / na základě, založený na | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 524 | 1603/1625 | activar / acelerar | oživit, urychlit, podnítit / zrychlit, urychlit, uspíšit | Diskutabilní | Aktivar má i význam oživit/urychlit proces doložený RAE; není však synonymum acelerar u pouhého zapnutí zařízení. |
| 525 | 1605/1909 | el patrimonio / los bienes | majetek, jmění / majetek | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 526 | 1609/2217 | sintetizar / resumir | shrnout, (z)rekapitulovat, sloučit / shrnout, (z)rekapitulovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 527 | 1617/2214 | reemplazar / mudar | nahradit, vyměnit / změnit, přemístit, přenést, vyměnit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 528 | 1620/2462 | al margen de / por fuera de | mimo, stranou od (spíše abstraktní okraj) / mimo, kromě / zvenku, na vnější straně | Diskutabilní | Al margen de abstraktně mimo/stranou, por fuera de zvenku a regionálně mimo; nutný region/kontext. |
| 529 | 1625/2145 | acelerar / agilizar | zrychlit, urychlit, uspíšit / urychlit, zrychlit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 530 | 1626/2390 | pergeňar / hilvanar | dát dohromady, slepit, ušít horkou jehlou / pospojovat, dát dohromady, navázat na sebe / sestehovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 531 | 1632/1961 | acumular / recopilar | (na)hromadit, shromáždit, (a)kumulovat / sebrat, posbírat, shromáždit (hlavně u abstraktních věcí) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 532 | 1650/2742 | prácticamente / virtualmente | prakticky, téměř, skoro, takřka / prakticky, téměř / virtuálně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 533 | 1651/2343 | abiertamente / francamente | otevřeně, upřímně / upřímně, bezelstně, otevřeně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 534 | 1653/2336 | normalmente  / regularmente | normálně, běžně / obvykle, běžně, pravidelně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 535 | 1653/2422 | normalmente  / comúnmente | normálně, běžně / obecně, celkově, vesměs / běžně, obvykle, často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 536 | 1655/2791 | intensificar / acentuar | zesílit, zintenzivnit, vystupňovat / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 537 | 1659/1779 | retirar / desprender | odstranit, odklidit, odsunout, odtáhnout / odstranit, oddělit, sejmout / vyplývat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 538 | 1659/2306 | retirar / desplazar | odstranit, odklidit, odsunout, odtáhnout / přemístit, přesunout, odsunout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 539 | 1659/2670 | retirar / alejar | odstranit, odklidit, odsunout, odtáhnout / oddálit, odsunout, vzdálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 540 | 1661/2214 | trasladar / mudar | přestěhovat, přesunout, přemístit, přenést / změnit, přemístit, přenést, vyměnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 541 | 1661/2306 | trasladar / desplazar | přestěhovat, přesunout, přemístit, přenést / přemístit, přesunout, odsunout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 542 | 1678/2353 | ubicar / acomodar | umístit, postavit, položit / umístit, usadit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 543 | 1685/1745 | indispensable / esencial | nezbytný, nevyhnutelný / nezbytný, nepostradatelný, zásadní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 544 | 1685/2412 | indispensable / imprescindible | nezbytný, nevyhnutelný / nezbytný, nutný, nepostradatelný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 545 | 1686/1801 | la disminución / el recorte | snížení, zmenšení, pokles / snížení, omezování, redukce / zastřižení, ustřižení | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 546 | 1687/1967 | precisamente / exactamente | přesně, právě / přesně, exaktně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 547 | 1687/2457 | precisamente / tal cual | přesně, právě / přesně tak, přesně | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 548 | 1694/2172 | frecuentemente / con frecuencia | často / často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 549 | 1694/2422 | frecuentemente / comúnmente | často / obecně, celkově, vesměs / běžně, obvykle, často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 550 | 1702/1722 | tener prisa / estar apurado | spěchat mít naspěch / spěchat, mít naspěch, mít naspěch | Diskutabilní | Estar apurado znamená mít naspěch zejména v Latinské Americe, jinde také být v nesnázích. |
| 551 | 1713/1873 | insoportable / insostenible | neúnosný, nesnesitelný (bolest) / nesnesitelný, neúnosný | Diskutabilní | Insoportable je nesnesitelný, insostenible neudržitelný/neobhajitelný; ne každá nesnesitelná bolest je insostenible. |
| 552 | 1715/1716 | suplicar / rogar | prosit, žádat, žadonit / snažně prosit, žádat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 553 | 1715/2333 | suplicar / solicitar | prosit, žádat, žadonit / žádat, požádat | Diskutabilní | Suplicar je naléhavě prosit, solicitar obvykle neutrálně/formálně žádat; ztrácí se naléhavost. |
| 554 | 1716/2333 | rogar / solicitar | snažně prosit, žádat / žádat, požádat | Diskutabilní | Rogar je snažně prosit nebo zdvořile požádat, solicitar formálně žádat. Překryv záleží na intenzitě žádosti. |
| 555 | 1729/1764 | aproximadamente / en torno a | přibližně / kolem, přibližně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 556 | 1730/2500 | finalmente / al fin y al cabo | konečně, nakonec / koneckonců, nakonec, vždyť přece | Odstraněno | Finalmente vyjadřuje konečný okamžik/sled událostí, al fin y al cabo argumentační koneckonců. |
| 557 | 1742/1914 | circunscribir / definir | omezit, vymezit / vymezit, určit, definovat, objasnit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 558 | 1745/2412 | esencial / imprescindible | nezbytný, nepostradatelný, zásadní / nezbytný, nutný, nepostradatelný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 559 | 1754/2489 | encuadrar / abarcar | (za)rámovat, (za)řadit, zahrnout, zahrnovat  / zahrnout, obsáhnout, pojmout | Odstraněno | Encuadrar řadí případ do rámce/kategorie; abarcar zahrnuje rozsah témat. Jiné směry zahrnování. |
| 560 | 1758/2319 | lamentablemente / lastimosamente | naneštěstí / bohužel, naneštěstí, politováníhodně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 561 | 1763/1921 | encabezar / liderar | vést, být první, být v čele / vést, řídit, šéfovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 562 | 1763/2798 | encabezar / regentar | vést, být první, být v čele / vést, řídit, spravovat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 563 | 1780/2728 | en base a / basándose | na základě, založený na / zakládaje se na, na základě | Diskutabilní | Basándose je slovesný přechodník a potřebuje en; en base a předložková vazba. Nejsou hotové konstrukce téže délky. |
| 564 | 1782/1813 | extender / prolongar | rozšířit, rozprostřít, prodloužit / prodloužit, nastavit, protáhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 565 | 1782/2729 | extender / diseminar | rozšířit, rozprostřít, prodloužit / rozšířit, rozptýlit, rozesít, rozšířit do různých míst | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 566 | 1783/1906 | solamente / únicamente | jen(om), pouze / pouze, jen, avšak | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 567 | 1783/2471 | solamente / nomás | jen(om), pouze / jenom, pouze | Diskutabilní | Nomás ve významu pouze je zejména latinskoamerické; další důrazová užití sem nepatří. |
| 568 | 1786/2271 | volcar / verter | převrátit / vysypat, vylít / rozlít, vylít / rozsypat, vysypat (záměrně) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 569 | 1790/2138 | antecedente / previo | předchozí, dřívější, předcházející / předchozí, dřívější | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 570 | 1792/1846 | consolidar / fijar | upevnit, utvrdit / připevnit, upevnit, uchytit | Odstraněno | Fortalecer/consolidar posilují a upevňují stabilitu; fijar připevňuje nebo stanovuje. Jiné významy upevnit. |
| 571 | 1793/1859 | significativo / notable | významný, význačný, důležitý / významný, význačný, značný, nezanedbatelný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 572 | 1797/1957 | nombrado / rotulado | jmenovaný, zmíněný, označený / popsaný, označený (nápisem) | Odstraněno | Nombrado znamená jmenovaný či zmíněný, rotulado opatřený nápisem/štítkem. |
| 573 | 1813/2758 | prolongar / estirar | prodloužit, nastavit, protáhnout / natáhnout, protáhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 574 | 1820/1823 | a la par / en simultáneo | paralelně, bok po boku, současně, stejným tempem / simultánně, současně, zároveň | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 575 | 1820/2168 | a la par / en paralelo | paralelně, bok po boku, současně, stejným tempem / paralelně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 576 | 1820/2223 | a la par / al mismo tiempo | paralelně, bok po boku, současně, stejným tempem / zároveň, současně, ve stejnou dobu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 577 | 1820/2367 | a la par / a la vez | paralelně, bok po boku, současně, stejným tempem / zároveň, současně, najednou, ve stejnou chvíli | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 578 | 1823/2223 | en simultáneo / al mismo tiempo | simultánně, současně, zároveň / zároveň, současně, ve stejnou dobu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 579 | 1823/2367 | en simultáneo / a la vez | simultánně, současně, zároveň / zároveň, současně, najednou, ve stejnou chvíli | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 580 | 1826/2451 | efectivamente / eficazmente | účinně, efektivně / účinně, efektivně z hlediska výsledku | Diskutabilní | Efectivamente zpravidla potvrzuje skutečnost/realizaci, eficazmente úspěšnost účinku. Český překlad prvního míří jinam než příklad; rozhodnout význam hesla. |
| 581 | 1842/2734 | interrumpir / suspender | přerušit, zabránit / odložit, zrušit, přerušit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 582 | 1846/2777 | fijar / sujetar | připevnit, upevnit, uchytit / držet, přidržovat, upevnit / zadržet / zkrotit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 583 | 1854/2832 | antipático / displicente | nesympatický, antipatický, nepříjemný / nepříjemný, protivný, příkrý | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 584 | 1861/2266 | significativamente / sustancialmente | významně, podstatně / podstatně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 585 | 1863/2458 | apropiadamente / debidamente | vhodně, náležitě, patřičně / náležitě, patřičně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 586 | 1880/1894 | hacer volar por los aires / dinamitar | vyhodit do vzduchu, úplně zničit / vyhodit do vzduchu | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 587 | 1883/2257 | con fuerza / poderosamente | silně, výrazně / mocně, silně, výrazně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 588 | 1885/1968 | llanamente / simplemente | jednoduše, prostě / jednoduše, prostě, pouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 589 | 1895/2434 | rematar / terminar | zakončit, ukončit / dorazit / skončit, dokončit, ukončit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 590 | 1898/1929 | inicial / incipiente | počáteční, začáteční, úvodní / začínající, počáteční, počínající | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 591 | 1904/2319 | desgraciadamente / lastimosamente | bohužel / bohužel, naneštěstí, politováníhodně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 592 | 1912/1966 | principalmente / fundamentalmente | předně, především, hlavně / zásadně, v zásadě, především | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 593 | 1914/2209 | definir / esclarecer | vymezit, určit, definovat, objasnit / objasnit, vysvětlit, vyjasnit | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 594 | 1919/2476 | superar / sobrepasar | předčit, překonat, předstihnout / přesáhnout, překročit / překonat, zvládnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 595 | 1925/1945 | explotar / estallar | vybuchnout, explodovat / prudce zvýšit / vykořistovat / vybuchnout, propuknout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 596 | 1930/2365 | poco a poco / paso a paso | postupně, pomalu, krok za krokem / krok za krokem | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 597 | 1933/1953 | incautar / interceptar | zabavit, odebrat, zadržet / zadržet, zachytit, zajistit | Odstraněno | Detener zastavuje/zadržuje, interceptar zachycuje při pohybu, incautar právně zabavuje majetek. Odlišné policejní úkony. |
| 598 | 1934/2368 | inmenso / gigantesco | ohromný, obrovský / báječný, bezvadný / obří, gigantický, obrovský | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 599 | 1934/2488 | inmenso / enorme | ohromný, obrovský / báječný, bezvadný / ohromný, nesmírný, nadměrný, enormní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 600 | 1934/2678 | inmenso / magnífico | ohromný, obrovský / báječný, bezvadný / úžasný, skvělý, ohromný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 601 | 1935/2346 | abusivo / desmesurado | zneužívající / nepřiměřený, přehnaný / bezohledný / nadměrný, přehnaný, nepřiměřený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 602 | 1937/1960 | esporádico / aislado | sporadický, ojedinělý / ojedinělý, výjimečný, izolovaný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 603 | 1943/2331 | asociado / ligado | spojený, sdružený / (s)vázaný, spojený | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 604 | 1953/2315 | interceptar / reprimir | zadržet, zachytit, zajistit / zadržet, potlačit | Odstraněno | Interceptar je zachytit na cestě, reprimir potlačit projev/protest, sujetar přidržet/zkrotit. Jiné významy zadržet. |
| 605 | 1953/2777 | interceptar / sujetar | zadržet, zachytit, zajistit / držet, přidržovat, upevnit / zadržet / zkrotit | Odstraněno | Interceptar je zachytit na cestě, reprimir potlačit projev/protest, sujetar přidržet/zkrotit. Jiné významy zadržet. |
| 606 | 1956/1959 | el bote a motor / la lancha | motorový člun / motorový člun, loďka, člun | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 607 | 1958/2238 | rotular / marcar | opatřit popisem (kresbu ap.), označit (plánek ap.) / označit, vyznačit, ukázat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 608 | 1960/2359 | aislado / extraordinario | ojedinělý, výjimečný, izolovaný / mimořádný, zvláštní, výjimečný, neobyčejný | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 609 | 1963/2380 | indebido / erróneo | nepatřičný, nesprávný, nedovolený / chybný, nesprávný, mylný | Diskutabilní | Indebido je nevhodný/neoprávněný, erróneo chybný fakticky/úsudkem. Společné nesprávný potřebuje kontext. |
| 610 | 1966/1974 | fundamentalmente / básicamente | zásadně, v zásadě, především / v zásadě, v podstatě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 611 | 1967/2457 | exactamente / tal cual | přesně, exaktně / přesně tak, přesně | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 612 | 1968/2471 | simplemente / nomás | jednoduše, prostě, pouze / jenom, pouze | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 613 | 1968/2653 | simplemente / puramente | jednoduše, prostě, pouze / čistě, pouze | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 614 | 1969/2200 | realmente / verdaderamente | opravdu, skutečně / skutečně, opravdu, doopravdy | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 615 | 1971/2225 | claramente / con nitidez | jasně, zřetelně / jasně, zřetelně, ostře | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 616 | 1971/2507 | claramente / inequívocamente | jasně, zřetelně / jednoznačně, jasně, nepochybně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 617 | 1972/1973 | particularmente / especialmente | zvlášť, obzvlášť, zejména / zejména, obzvlášť, zvláště | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 618 | 1974/2393 | básicamente / en esencia | v zásadě, v podstatě / v podstatě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 619 | 1976/2159 | concretamente / en concreto | konkrétně / konkrétně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 620 | 1976/2233 | concretamente / específicamente | konkrétně / specificky, konkrétně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 621 | 1977/2335 | generalmente / habitualmente | obvykle, zpravidla / obvykle | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 622 | 1977/2336 | generalmente / regularmente | obvykle, zpravidla / obvykle, běžně, pravidelně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 623 | 1977/2422 | generalmente / comúnmente | obvykle, zpravidla / obecně, celkově, vesměs / běžně, obvykle, často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 624 | 1980/2274 | supuestamente / presuntamente | údajně, domněle / údajně, domněle | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 625 | 1982/2003 | posiblemente / acaso | možná, případně, možná že / možná, snad, třeba | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 626 | 1989/2396 | en vistas a / de cara a | s ohledem na / s ohledem na, s výhledem na, ve vztahu k, vzhledem k | Diskutabilní | En vistas a a de cara a směřují k cíli; u první vazby navíc zvážit standardní con vistas a. Samotné heslo se v auditu neopravuje. |
| 627 | 1991/2562 | alegar / aducir | uvést (co jako argument ap.), odvolávat se / uvést (jako důvod), argumentovat, odvolávat se na | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 628 | 1994/2375 | a tono con / en línea con | v souladu s, odpovídající / v souladu s | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 629 | 2004/2423 | anteriormente / previamente | dříve / dříve, předtím, předem | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 630 | 2026/2115 | tanto es así que / al punto que | natolik že, do té míry že / do té míry že, až tak že | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 631 | 2032/2411 | reanudar / renovar | obnovit, znovu zahájit, navázat / obnovit, zmodernizovat | Odstraněno | Reanudar navazuje po přerušení, renovar obnovuje platnost/modernizuje. Pokračování není renovace ani prodloužení platnosti. |
| 632 | 2041/2294 | fuertemente / intensamente | silně / intenzivně, silně, usilovně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 633 | 2060/2125 | innecesariamente / inútilmente | zbytečně, nepotřebně / zbytečně | Odstraněno | Innecesariamente je bez potřeby, inútilmente bez výsledku/marně. Zbytečnost a neúspěch nejsou totožné. |
| 634 | 2065/2563 | al lado de / junto a | vedle / vedle, u | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 635 | 2070/2526 | gradualmente / paulatinamente | postupně / postupně, (po)zvolna, pomalu | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 636 | 2088/2299 | enteramente / totalmente | úplně, zcela, naprosto / úplně, zcela, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 637 | 2088/2420 | enteramente / plenamente | úplně, zcela, naprosto / zcela, plně, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 638 | 2090/2102 | brotar / surgir | vytrysknout (voda, krev) / vyrašit (rostliny) / objevit se, vzniknout / objevit se, vzniknout, vynořit se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 639 | 2100/2355 | allanar / destrabar | odstranit překážky, usnadnit / vyrovnat, uhladit / zjednodušit, vyřešit, odstranit překážky | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 640 | 2118/2345 | suficientemente / bastante | dostatečně / dost, dostatečně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 641 | 2121/2678 | asombroso / magnífico | úžasný, udivující, neuvěřitelný / úžasný, skvělý, ohromný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 642 | 2131/2495 | escudriňar / examinar | (pro)zkoumat, (pro)zkoušet, (o)testovat / zkoumat, přezkoumat, analyzovat, důkladně prohlédnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 643 | 2144/2216 | quedar firme / seguir en pie | zůstat v platnosti, stát se definitivním, nabýt právní moci / stále platit, zůstat v platnosti | Odstraněno | Quedar firme je u rozsudku nabýt právní moci/definitivnosti; seguir en pie nadále platit či přetrvávat. |
| 644 | 2151/2370 | originalmente / inicialmente | původně, zpočátku, prvotně / ze začátku, na začátku, zpočátku | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 645 | 2170/2384 | preferiblemente / preferentemente | nejlépe / přednostně, nejlépe, nejraději | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 646 | 2178/2643 | entusiasmar / encandilar | nadchnout, probudit nadšení / nadchnout, oslnit / oslepit, zaslepit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 647 | 2190/2250 | potenciar / acrecentar | umocnit, zvýšit, rozšířit, posilnit / zvětšit, zvýšit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 648 | 2193/2776 | acceder / asentir | přistoupit na něco, souhlasit / dostat se, získat přístup / vstoupit / souhlasit | Diskutabilní | Acceder a vyjadřuje přistoupení na žádost, asentir souhlas s tvrzením, někdy pouze kývnutí. |
| 649 | 2202/2446 | escasamente / ligeramente | nedostatečně, slabě, nepatrně / lehce, mírně, nepatrně | Diskutabilní | Escasamente je sotva/nedostatečně, ligeramente mírně; nedostatečná míra není vždy malá neutrální míra. |
| 650 | 2210/2240 | de todos modos / de todas formas | každopádně, v každém případě, stejně / každopádně, stejně, v každém případě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 651 | 2210/2348 | de todos modos / sea como sea | každopádně, v každém případě, stejně / ať je to jak chce, tak či onak, každopádně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 652 | 2214/2306 | mudar / desplazar | změnit, přemístit, přenést, vyměnit / přemístit, přesunout, odsunout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 653 | 2223/2367 | al mismo tiempo / a la vez | zároveň, současně, ve stejnou dobu / zároveň, současně, najednou, ve stejnou chvíli | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 654 | 2239/2341 | definitivamente / ciertamente | definitivně, jistě, určitě / jistě, určitě, zajisté | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 655 | 2240/2348 | de todas formas / sea como sea | každopádně, stejně, v každém případě / ať je to jak chce, tak či onak, každopádně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 656 | 2247/2718 | embaucar / timar | napálit, podvést, ošálit / ošidit, okrást, podvést, napálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 657 | 2251/2410 | lucir / exhibir | vypadat / nosit, předvádět / zářit, vynikat / vystavit, ukazovat, předvádět | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 658 | 2252/2335 | de costumbre / habitualmente | jako obvykle / obvykle | Diskutabilní | De costumbre je v příkladu až v como de costumbre; habitualmente funguje samostatně. Rozdíl konstrukce. |
| 659 | 2257/2294 | poderosamente / intensamente | mocně, silně, výrazně / intenzivně, silně, usilovně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 660 | 2267/2268 | enfáticamente / vehementemente | důrazně / vášnivě, důrazně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 661 | 2282/2618 | asustar / horrorizar | (po)lekat, (vy)strašit, (vy)děsit / (vy)děsit, poděsit, polekat | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 662 | 2291/2772 | latente / clandestino | latentní, skrytý / ilegální, tajný, skrytý | Odstraněno | Latente je skrytě přítomný/dosud neprojevený, clandestino utajovaný či ilegální. Latentní stav není tajná činnost. |
| 663 | 2298/2300 | tremendamente / espantosamente | strašně, děsivě, ohromně / děsivě, příšerně, strašlivě | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 664 | 2299/2420 | totalmente / plenamente | úplně, zcela, naprosto / zcela, plně, naprosto | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 665 | 2303/2446 | levemente / ligeramente | lehce, mírně / lehce, mírně, nepatrně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 666 | 2306/2670 | desplazar / alejar | přemístit, přesunout, odsunout / oddálit, odsunout, vzdálit | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 667 | 2312/2638 | carajo / caramba | pták, péro, ocas  / sakra!, do prdele!, hergot! / sakra!, k čertu!, hrome! | Diskutabilní | Carajo je výrazně vulgárnější než eufemistické caramba; oba výkřiky mají jiné společenské použití. |
| 668 | 2323/2796 | aguar / estropear | zkazit, pokazit (zábavu) / naředit vodou, zvodnatit / zkazit, poškodit, poničit, pokazit, porouchat se | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 669 | 2335/2336 | habitualmente / regularmente | obvykle / obvykle, běžně, pravidelně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 670 | 2335/2422 | habitualmente / comúnmente | obvykle / obecně, celkově, vesměs / běžně, obvykle, často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 671 | 2336/2422 | regularmente / comúnmente | obvykle, běžně, pravidelně / obecně, celkově, vesměs / běžně, obvykle, často | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 672 | 2346/2488 | desmesurado / enorme | nadměrný, přehnaný, nepřiměřený / ohromný, nesmírný, nadměrný, enormní | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 673 | 2351/2549 | destrozar / deshacer | zničit, rozbít / rozdělat, rozebrat, zničit, zrušit, vrátit zpět (co bylo uděláno) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 674 | 2351/2632 | destrozar / arrasar | zničit, rozbít / zničit, srovnat se zemí, zdevastovat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 675 | 2378/2520 | aleatoriamente / casualmente | náhodně, nahodile / náhodou, náhodně | Diskutabilní | Aleatoriamente je náhodným výběrem, casualmente náhodou/shodou okolností. Statistický a příhodový kontext se liší. |
| 676 | 2426/2457 | así es / tal cual | přesně tak, tak to je, je to tak, to je pravda / přesně tak, přesně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 677 | 2448/2785 | reiteradamente / repetidamente | opakovaně / opakovaně | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 678 | 2465/2784 | el intendente / el alcalde | starosta / starosta | Diskutabilní | Intendente označuje starostu v některých zemích, jinde jiný úřad; alcalde není univerzální ekvivalent funkce. |
| 679 | 2494/2661 | resaltar / recalcar | zdůraznit, vyzdvihnout, vyniknout / zdůraznit, vyzdvihnout, podtrhnout | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 680 | 2494/2791 | resaltar / acentuar | zdůraznit, vyzdvihnout, vyniknout / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 681 | 2510/2601 | sobresaliente / espléndido | vynikající, skvělý, znamenitý / nádherný, skvělý, úchvatný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 682 | 2510/2678 | sobresaliente / magnífico | vynikající, skvělý, znamenitý / úžasný, skvělý, ohromný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 683 | 2511/2573 | qué piola / qué chulo | to je super, to je skvělé (Arg) / jak super, to je skvělé | Diskutabilní | Qué piola je argentinské/rioplatenské, qué chulo typicky španělské. Cool význam je platný, ale regiony se liší. |
| 684 | 2519/2713 | pelotudo / cretino | idiotský, debilní, kreténský / idiot, debil, kretén / pitomý, blbý / pitomec, blbec, kretén | Diskutabilní | Pelotudo je výrazně regionální a vulgární; cretino podobná urážka s odlišným registrem. |
| 685 | 2548/2840 | el pánfilo / el bobo | trouba, naiva, prosťáček, přihlouplý člověk / trouba, blbeček | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 686 | 2551/2767 | sereno / quieto | klidný, vyrovnaný, rozvážný / klidný, v klidu, bez hnutí | Diskutabilní | Kontextový překryv nebo rozdíl vazby, intenzity či registru; přesný rozsah není dost jistý pro změnu. Ponecháno k posouzení. |
| 687 | 2565/2699 | el revuelo / el lío | zmatek, poprask, rozruch / zmatek, chaos, povyk / problém, komplikace | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 688 | 2590/2617 | el pendejo / el huevón | blbec, hlupák/hlupačka / lenoch, flákač, povaleč / blbec, pitomec, tupec | Diskutabilní | Pendejo a huevón se významem i hrubostí mění podle země; společný hlupák je jen jeden kontext. |
| 689 | 2590/2753 | el pendejo / el tarado | blbec, hlupák/hlupačka / idiot, pitomec, debil, hlupák | Diskutabilní | Pendejo může podle regionu znamenat také dítě/mladík, tarado urážlivě hlupák. Příklady nemají jednoznačně stejný význam. |
| 690 | 2601/2678 | espléndido / magnífico | nádherný, skvělý, úchvatný / úžasný, skvělý, ohromný | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 691 | 2607/2826 | al tiro / al toque | hned / hned, okamžitě, obratem | Diskutabilní | Al tiro a al toque platí jako hned v různých latinskoamerických varietách; ponecháno se zeměpisným omezením. |
| 692 | 2617/2753 | el huevón / el tarado | lenoch, flákač, povaleč / blbec, pitomec, tupec / idiot, pitomec, debil, hlupák | Diskutabilní | Huevón může znamenat lenoch, hlupák i oslovení; tarado se kryje jen s urážlivým hlupákem. |
| 693 | 2659/2839 | la injusticia / el atropello | křivda, bezpráví, nespravedlnost / bezpráví, svévole, hrubé porušení práv / sražení, přejetí (vozidlem) | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 694 | 2661/2791 | recalcar / acentuar | zdůraznit, vyzdvihnout, podtrhnout / zdůraznit, zvýraznit, zesílit / prohloubit, dát přízvuk | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 695 | 2789/2795 | manosear / toquetear | osahat, ohmatat, sáhnout / osahat, ohmatat | Ponecháno | Společný uvedený význam je použitelný; bez dostatečně jistého důvodu k zásahu ponecháno. |
| 696 | 2801/2837 | impúdico / descarado | nestydatý, neslušný, nemravný / drzý, hubatý, nestydatý | Diskutabilní | Impúdico zdůrazňuje neslušnou/nemravnou nestoudnost, descarado drzost či nestoudnost obecně. |

## Závěrečné ověření

- Kontrola všech 26 projektových CSV našla právě pět výše uvedených úložišť synonym: dvě aktivní a tři historické kopie. Žádné další CSV nemá synonymní pole.
- Skutečný loader `app.repositories.synonyms.load` načetl **555 anglických a 616 španělských vazeb**, tedy všechny výsledné řádky; žádná vazba nebyla zahozena kvůli chybějícímu ID.
- Integrita výsledků: **0 duplicit, 0 vazeb na sebe, 0 neexistujících ID a 0 neplatných dat Date**. Čtyři náhradní dvojice neexistovaly mezi ostatními vztahy.
- Auditní registr má přesně **1 423 původních záznamů**: 912 ponechaných, 255 diskutabilních/kontextových ponechaných, 252 odstraněných a 4 nahrazené. Součty se shodují s oběma výslednými CSV.
- `python -X utf8 -B -m app.tests.run_all --pattern test_synonyms.py --timeout 180`: **10 testů prošlo, 0 vynecháno, 0 selhání**. Testy používají izolované služby a dočasná data. Nebyly přidávány ani upravovány testy aplikace.
- `git diff --check` pro obě CSV prošel. Git diff ukazuje **3 přidané / 175 odebraných řádků** v anglickém souboru a **1 přidaný / 81 odebraných řádků** ve španělském. To odpovídá 252 odstraněním a 4 náhradám, bez změny hlaviček a jiných polí.
- **Závěrečný otisk všech 5 957 ostatních souborů je totožný s výchozím:** `8689fd6272245f8745569224a1c9ef6b27d68b021bad7456a8c5aa02a3532ecf`. Obsah slovníků včetně všech překladů, kategorií, výslovnosti, příkladů a historie, audio, historické zálohy, kód, testy, konfigurace i předchozí rozpracované změny jsou bytově beze změny.

Git pracovní strom už před auditem obsahoval rozpracovanou práci. Ta zůstala nedotčená; tento audit změnil pouze dvě aktivní synonymní CSV a přidal tento report. Dosavadní změny nebyly resetovány ani přepsány. Technická integrita neznamená úplnou zaměnitelnost ponechaných polysémních slov: 255 případů zůstává výslovně označeno výše. Úplný historický význam archivních ID zůstává neověřený v rozsahu popsaném v části Historické kopie.

### Opakování důkazu nezměněnosti ostatních souborů

Následující kontrola pouze čte soubory. Spouští se z kořene projektu; po dalších vlastních úpravách projektu už očekávaně nemusí vrátit stejný otisk.

```python
import hashlib
import os
from pathlib import Path

allowed = {
    'files/Czech_English_synonyms.csv',
    'files/Czech_Spanish_synonyms.csv',
    'docs/synonyms-content-audit.md',
}
digest = hashlib.sha256()
count = 0
for folder, directories, names in os.walk('.'):
    directories[:] = sorted(
        name for name in directories
        if name not in {'.git', '.venv', '__pycache__'}
    )
    for name in sorted(names):
        path = Path(folder) / name
        relative = path.as_posix()
        if relative in allowed or not path.is_file():
            continue
        digest.update(
            relative.encode('utf-8') + b'\0'
            + hashlib.sha256(path.read_bytes()).digest()
        )
        count += 1
print(count, digest.hexdigest())
# 5957 8689fd6272245f8745569224a1c9ef6b27d68b021bad7456a8c5aa02a3532ecf
```


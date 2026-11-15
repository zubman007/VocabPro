# Audio

Výslovnost je ve `files/audio/<Learned by>_<Language>/<ID>.mp3` nebo `.wav`.
Sloupec Audio je volba zdroje, ne úplná cesta. Editor a PracticeAudio skládají
cesty pomocí Path. Přehrávání používá pygame.mixer.music; volitelné efekty
rozhraní používají vlastní kanál, vlastní hlasitost a potlačení rychlého opakování.

AudioRecorderPlayer obsluhuje dialog; record_wave ve vlákně čte mikrofon přes
PyAudio, zapisuje do dočasného WAV a po flush/fsync jej nahrazuje. Stream a
zařízení se uzavírají ve finally. Zavření během nahrávání požádá o zastavení,
výsledek se pollingem zpracuje v UI. Nic nevolá Tk z nahrávacího vlákna.

Při ukládání slovníku save_workflow kopíruje pracovní audio do izolovaného
staging adresáře. ContextVar audio_output přesměruje výstup providerů jen v
daném workeru, zatímco API nastavení se čte z původní cesty. Recyklované ID
bez Own nedědí starou nahrávku. Nezměněné audio se při commitu nenahrazuje.

Před CSV commitem se související změny připraví s rollback kopiemi. Archiv
smazaného/recyklovaného audia je v podadresáři deleted s náhodným suffixem.
Pokud běžný I/O commit selže, původní soubory se obnoví. Selže-li i obnova,
workflow zachová staging jako `.recovery-*` a vyvolá chybu pro ruční obnovu.
Při úspěchu se pracovní staging uklidí.

Přímé mazání audia uživatelem v review/editoru a nahrávání jsou samostatné
explicitní akce, nejsou odložené do stejné CSV transakce. E-mailová záloha
audio nezahrnuje. Výpadek napájení uprostřed potvrzování více souborů nelze
považovat za plně transakčně ošetřený. [Diagram](diagrams/AUDIO_WORKFLOW.md).

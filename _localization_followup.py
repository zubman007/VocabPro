"""Reviewed display-value edits; message IDs and course data stay untouched."""
import json
from pathlib import Path
import re
from app.shared.translations import _unique_object

root = Path(__file__).parent
replacements = {
 'cs': {
  'Tvůj':'Váš','tvůj':'váš','Tvoje':'Vaše','tvoje':'vaše',
  'Vyplň':'Vyplňte','vyplň':'vyplňte','Nahraj':'Nahrajte','nahraj':'nahrajte',
  'Vyber':'Vyberte','vyber':'vyberte','Zadej':'Zadejte','zadej':'zadejte',
  'Vytvářej':'Vytvářejte','vytvářej':'vytvářejte','upravuj':'upravujte',
  'Filtruj':'Filtrujte','filtruj':'filtrujte','Vkládej':'Vkládejte','vkládej':'vkládejte',
  'nahrávej':'nahrávejte','zadávej':'zadávejte','maž':'mažte','doplňuj':'doplňujte',
  'Ulož':'Uložte','ulož':'uložte','můžeš':'můžete','Sleduj':'Sledujte','nastavíš':'nastavíte',
  'Procvičuj':'Procvičujte','Poslechni':'Poslechněte','Poznej':'Poznejte','upřesni':'upřesněte',
  'Prohlédni':'Prohlédněte','Označ':'Označte','Otevři':'Otevřete','otevři':'otevřete',
  'Přelož':'Přeložte','Použij':'Použijte','použij':'použijte',
 },
 'sk': {
  'Tvoj':'Váš','tvoj':'váš','Tvoja':'Vaša','tvoja':'vaša','Tvoje':'Vaše','tvoje':'vaše',
  'Vyplň':'Vyplňte','vyplň':'vyplňte','Nahraj':'Nahrajte','nahraj':'nahrajte',
  'Vyber':'Vyberte','vyber':'vyberte','Zadaj':'Zadajte','zadaj':'zadajte',
  'Vytváraj':'Vytvárajte','vytváraj':'vytvárajte','upravuj':'upravujte',
  'Filtruj':'Filtrujte','filtruj':'filtrujte','Vkladaj':'Vkladajte','vkladaj':'vkladajte',
  'nahrávaj':'nahrávajte','zadávaj':'zadávajte','maž':'odstraňujte','dopĺňaj':'dopĺňajte',
  'Ulož':'Uložte','ulož':'uložte','môžeš':'môžete','Sleduj':'Sledujte','nastavíš':'nastavíte',
  'Precvičuj':'Precvičujte','Vypočuj':'Vypočujte','Spoznaj':'Spoznajte','spresni':'spresnite',
  'Pozri':'Pozrite','Označ':'Označte','Otvor':'Otvorte','otvor':'otvorte',
  'Prelož':'Preložte','Použi':'Použite','použi':'použite',
  'Zmazať':'Odstrániť','zmazať':'odstrániť','Vymazať':'Odstrániť','vymazať':'odstrániť',
  'Popis':'Opis','popis':'opis','popisy':'opisy',
 },
}
edits = {
 'cs': {
  'Hello user,':'Vítejte,',
  'Press Next for a new round.':'Nové kolo spustíte tlačítkem Další.',
  'You have completed the whole grammar round.':'Celé kolo gramatiky je dokončené.',
 },
 'sk': {
  'Hello user,':'Vitajte,','Clear contents':'Vyprázdniť obsah',
  'Press Next for a new round.':'Nové kolo spustíte tlačidlom Ďalšie.',
  'You have completed the whole grammar round.':'Celé kolo gramatiky je dokončené.',
 },
 'de': {
  'Configure the sending account in Settings → Backups → Sending account.':'Richte das Absenderkonto unter Einstellungen → Sicherungen → Absenderkonto ein.',
  'Enable at least one study course.':'Aktiviere mindestens einen Kurs.',
  'Enter the SMTP password.':'Gib das SMTP-Passwort ein.',
  'Study course source does not match your own language.':'Die Kurskonfiguration stimmt nicht mit deiner eigenen Sprache überein. Aktualisiere die Kurse in den Einstellungen.',
  'Study courses help':'Füge eine Sprache hinzu und aktiviere die gewünschten Kurse. Jeder Kurs behält seinen Wortschatz, Lernfortschritt und seine Frageneinstellungen. Beim Deaktivieren bleiben die Daten erhalten.',
  'The course file changed. Reopen the editor before saving.':'Die Kursdatei wurde inzwischen geändert. Öffne den Editor vor dem Speichern erneut.',
  'Use the sending account for smtp.seznam.cz. The recipient stays in Backup mail.':'Gib das Absenderkonto für smtp.seznam.cz ein. Der Empfänger bleibt unter Sicherungs-E-Mail.',
 },
 'es': {
  ' words to repeat':' palabras para repasar','Repeat':'Repasar','Repetition':'Repasos','Save repeat':'Guardar repaso',
  'Next repetition asc':'Próximo repaso ascendente','Next repetition desc':'Próximo repaso descendente',
  'Enable at least one study course.':'Activa al menos un curso.',
  'Study course source does not match your own language.':'La configuración de cursos no coincide con tu idioma. Actualiza los cursos en Ajustes.',
  'Study courses help':'Añade un idioma y activa los cursos que utilices. Cada curso conserva su vocabulario, progreso y configuración de preguntas. Desactivar un curso conserva sus datos.',
 },
 'en': {
  'Guide practice':'Practise with translations, context or audio. Your answers determine the next review date.',
  'Practice in context':'Practise in context','Not practiced':'Not practised',
 },
}
new_messages = {
 'en':{'Yes':'Yes','No':'No','Information':'Information','Warning':'Warning','Confirm':'Confirm'},
 'cs':{'Yes':'Ano','No':'Ne','Information':'Informace','Warning':'Upozornění','Confirm':'Potvrzení'},
 'sk':{'Yes':'Áno','No':'Nie','Information':'Informácia','Warning':'Upozornenie','Confirm':'Potvrdenie'},
 'es':{'Yes':'Sí','No':'No','Information':'Información','Warning':'Advertencia','Confirm':'Confirmación'},
 'fr':{'Yes':'Oui','No':'Non','Information':'Information','Warning':'Avertissement','Confirm':'Confirmation'},
 'de':{'Yes':'Ja','No':'Nein','Information':'Information','Warning':'Warnung','Confirm':'Bestätigung'},
}
counts = {}
for path in (root/'locales').glob('*.json'):
    code = path.stem
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
    original = dict(data)
    words = replacements.get(code, {})
    if words:
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, words)) + r')\b')
        data = {key: pattern.sub(lambda match: words[match[0]], value) for key, value in data.items()}
    data.update(edits.get(code, {}))
    if code == 'fr':
        data = {key: value.replace('propose de sauvegarder les modifications non enregistrées',
                                   'propose d’enregistrer les modifications non enregistrées') for key,value in data.items()}
    data.update(new_messages[code])
    counts[code] = sum(data[key] != value for key,value in original.items())
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')

changed_sources=[]
for path in (root/'app').rglob('*.py'):
    if 'tests' in path.parts: continue
    source = path.read_text(encoding='utf-8')
    updated = source.replace('from tkinter import messagebox', 'from app.ui import messagebox')
    if updated != source:
        path.write_text(updated, encoding='utf-8'); changed_sources.append(path.relative_to(root).as_posix())
runtime = root/'app/tests/test_localization_runtime.py'
runtime.write_text(runtime.read_text(encoding='utf-8').replace("patch('tkinter.messagebox.showerror'", "patch('app.ui.messagebox.showerror'"), encoding='utf-8')
print(json.dumps({'changed_values':counts,'messagebox_modules':changed_sources},ensure_ascii=False,indent=2))

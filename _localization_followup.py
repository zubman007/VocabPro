import json, re
from pathlib import Path
patterns = {
    'cs': r'\b(Tvůj|tvůj|Tvého|tvého|Tvoje|tvoje|Tvoji|tvoji|Tvé|tvé|Vyber|vyber|Zvol|zvol|Ulož|ulož|Otevři|otevři|Použij|použij|Zadej|zadej|Přidej|přidej|Vyplň|vyplň|Napiš|napiš|Stiskni|stiskni|Prohlédni|prohlédni|Opakuj|opakuj|můžeš|Dokončil|zahájíš|Upřesni|upřesni|Procvičuj|procvičuj|Poslechni|Poznej|Označ|Vytvářej|Vkládej|Zavři|Přelož|maž|zadávej|doplňuj|filtruj)\b',
    'sk': r'\b(Tvoj|tvoj|Tvoja|tvoja|Tvoje|tvoje|Tvoju|tvoju|Tvojho|tvojho|Vyber|vyber|Zvoľ|zvoľ|Ulož|ulož|Otvor|otvor|Použi|použi|Zadaj|zadaj|Pridaj|pridaj|Vyplň|vyplň|Napíš|napíš|Stlač|stlač|Prezri|prezri|Opakuj|opakuj|môžeš|Dokončil|začneš|Spresni|spresni|Precvičuj|Vypočuj|Spoznaj|Označ|Vytváraj|Vkladaj|Zavri|Prelož|maž|zadávaj|dopĺňaj|filtruj|zmazať|vymazať|Zmazať|Vymazať)\b',
    'de': r'\b(Sie|Ihnen|Ihr|Ihre|Ihren|Ihrem|Ihres|Ih|Phrase)\b',
    'es': r'repet|Repet',
    'en': r'practic|practis|Practic|Practis',
}
for code, pattern in patterns.items():
    if code in ('cs', 'sk'): continue
    print('\n'+code)
    data=json.loads((Path('locales')/(code+'.json')).read_text(encoding='utf-8'))
    for key,value in data.items():
        if re.search(pattern,value): print(json.dumps([key,value],ensure_ascii=False))

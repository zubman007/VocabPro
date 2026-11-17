"""Self-contained interactive HTML and a printable, paginated PDF."""
from html import escape
from pathlib import Path
import shutil
from tools.quality.common import atomic,write_json,redact,regressions


def display(value):
    if value is None:return 'Nedostupné'
    if isinstance(value,float):return f'{value:.3f}' if abs(value)<1 else f'{value:.2f}'
    return str(value)


def html_cell(value):
    text=escape(redact(display(value)))
    if value in ('passed','failed','warning','unavailable','skipped','expected_failure'):
        return '<span class="status '+str(value)+'">'+text+'</span>'
    return text


def dependency_rows(report,history):
    """Count one advisory per installed package/version/ID, retaining raw evidence."""
    check=report['checks'].get('Dependency vulnerabilities',{})
    if check.get('status') not in ('passed','warning'):return []
    groups={};raw_count=0
    for dependency in check.get('data',{}).get('dependencies',[]):
        for finding in dependency.get('vulns',[]):
            raw_count+=1
            key=(dependency['name'].casefold().replace('_','-'),dependency['version'],finding['id'])
            item=groups.setdefault(key,{'name':dependency['name'],'version':dependency['version'],
                'id':finding['id'],'description':finding.get('description',''),'fix_versions':set()})
            item['fix_versions'].update(finding.get('fix_versions',[]))
    rows=[(item['name'],item['version'],item['id'],', '.join(sorted(item['fix_versions'])),item['description']) for item in groups.values()]
    report['vulnerability_evidence']={'raw_advisory_records':raw_count,'unique_package_advisories':len(rows),
        'deduplication':'Installed package name/version and advisory ID. Raw tool output remains in diagnostics.'}
    report['summary']['dependency_vulnerabilities']=len(rows)
    bandit=report['checks'].get('Bandit',{})
    if bandit.get('status') in ('passed','warning'):
        report['summary']['bandit_findings']=len(bandit.get('data',{}).get('results',[]))
        report['summary']['security_findings']=report['summary']['bandit_findings']+len(rows)
    previous=next((h for h in history if h['id']==report.get('baseline_id')),None)
    report['regressions']=regressions(report['summary'],previous.get('summary') if previous else None)
    return rows


def table(headings,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+escape(str(h))+'</th>' for h in headings)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+html_cell(value)+'</td>' for value in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def trend(history,key,title,performance=False):
    values=[(item['date'],item['summary'].get('performance',{}).get(key) if performance else item['summary'].get(key)) for item in history]
    values=[(date,value) for date,value in values if isinstance(value,(int,float))][-30:]
    if not values:return '<p>'+escape(title)+': měření není dostupné.</p>'
    lo=min(v for _,v in values);hi=max(v for _,v in values);span=max(hi-lo,1)
    points=[(20+i*560/max(1,len(values)-1),120-(v-lo)*90/span) for i,(_,v) in enumerate(values)]
    return ('<figure><figcaption>'+escape(title)+'</figcaption><svg viewBox="0 0 600 155" role="img"><polyline fill="none" stroke="#397d77" stroke-width="3" points="'+ ' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+'"/>'+''.join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#a77732"><title>{escape(date)}: {value:.2f}</title></circle>' for (x,y),(date,value) in zip(points,values))+
        f'<text x="20" y="147">{lo:.2f}–{hi:.2f} · {len(values)} měření</text></svg></figure>')


def render(report,history,quality,run):
    vuln_rows=dependency_rows(report,history)
    summary=report['summary'];checks=report['checks'];analysis=report.get('analysis',{})
    jobs=checks.get('Tests',{}).get('modules',[]);tests=[r for j in jobs for r in j.get('records',[])]
    coverage=checks.get('Coverage',{});cards=[]
    unavailable=[j for j in jobs if j.get('status')=='unavailable']
    if summary['failed']:
        overall=f'Neúspěšné testy: {summary["failed"]}. Podrobnosti jsou v diagnostice.'
    elif unavailable:
        overall=f'Audit není úplný: {len(unavailable)} testovací moduly nebylo možné dokončit.'
    elif any(c['status']=='unavailable' for c in checks.values()):
        overall='Některé kontroly nejsou dostupné. Jejich výsledky nejsou považovány za úspěšné.'
    elif any(c['status']=='warning' for c in checks.values()):
        overall='Testy prošly. Audit obsahuje nálezy k posouzení.'
    else:overall='Všechny provedené kontroly prošly.'
    for label,value in [('Testy',summary['tests']),('Úspěšné',summary['passed']),('Neúspěšné',summary['failed']),
        ('GUI testy',summary['gui_tests']),('Coverage řádků', 'Nedostupné' if summary['coverage_percent'] is None else f'{summary["coverage_percent"]:.1f}%'),
        ('Statické nálezy',summary['lint_findings'])]:
        cards.append(f'<div class="card"><small>{label}</small><strong>{value if value is not None else "Nedostupné"}</strong></div>')
    status_rows=[(name,item['status'],item.get('reason',''),f'{item.get("seconds",0):.2f} s') for name,item in checks.items()]
    test_rows=[(r['id'],r['status'],'GUI' if r['gui'] else 'Automatický',f'{r["duration"]:.3f}', '\n'.join(r.get('details',[]))) for r in tests]
    gui_rows=[(r['id'],r['status'],f'{r["duration"]:.3f}',r.get('screenshot_unavailable','')) for r in tests if r['gui']]
    screenshot_html=''.join('<a href="'+escape(name,quote=True)+'"><img loading="lazy" width="360" src="'+escape(name,quote=True)+'" alt="Screenshot neúspěšného GUI testu"></a>' for r in tests for name in r['screenshots'])
    lint=checks.get('Ruff',{}).get('data',[])
    security=checks.get('Bandit',{}).get('data',{}).get('results',[])
    vulnerabilities=checks.get('Dependency vulnerabilities',{}).get('data',{}).get('dependencies',[])
    unavailable_packages=[(d.get('name'),d.get('version',''),d.get('skip_reason','')) for d in vulnerabilities if 'skip_reason' in d]
    complexity=[(f['file'],c['name'],c['line'],c['complexity']) for f in analysis.get('files',[]) for c in f.get('complexity',[]) if c['complexity']>10]
    biggest=sorted(analysis.get('files',[]),key=lambda f:f['sloc'],reverse=True)[:30]
    comparable=[h for h in history if h['mode']==report['mode']]
    comparable.append({'date':report['date'],'summary':summary})
    content=f'''<header><p>VocabPro / QUALITY AUDIT</p><h1>Stav projektu · {escape(report['mode'])}</h1><p>{escape(report['date'])} · ID {escape(report['id'])}</p></header>
    <nav><a href="#overview">Dashboard</a><a href="#gui">GUI Testing</a><a href="#tests">Testy</a><a href="#coverage">Coverage</a><a href="#code">Kód</a><a href="#security">Bezpečnost</a><a href="#history">Historie</a></nav>
    <main><section id="overview"><h2>Dashboard</h2><p class="banner">{escape(overall)}</p><div class="cards">{''.join(cards)}</div>
    <p>Coverage větví: {display(coverage.get('branch_percent'))} %. GUI testy jsou podmnožinou celkového počtu. Varování runtime GUI: {summary['runtime_warnings']}.</p>
    <p>Kontroly nic neopravují. Statické kandidáty nelze považovat za důkaz nepoužívaného nebo zastaralého kódu.</p>
    {table(('Kontrola','Stav','Poznámka','Doba'),status_rows)}</section>
    <section id="gui"><h2>GUI Testing</h2><p>Úspěšné: {summary['gui_passed']} · Neúspěšné: {summary['gui_failed']} · Přeskočené: {summary['gui_skipped']}.</p>
    <p>Klasifikace vychází ze skutečného pokusu o vytvoření Tk okna při daném testu. Snímek zachycuje pouze okno aplikace, pokud je při selhání ještě dostupné.</p>
    {table(('Test / krok','Stav','Sekundy','Screenshot nedostupný'),gui_rows)}{screenshot_html}</section>
    <section id="tests"><h2>Všechny automatické testy</h2><input id="search" placeholder="Filtrovat testy, chyby nebo modul…" aria-label="Filtrovat testy">
    <div id="test-table">{table(('Test','Stav','Typ','Sekundy','Chyba / traceback'),test_rows)}</div>
    <h3>Diagnostika modulů</h3>{''.join('<p><a href="'+escape(j['diagnostics'].replace(chr(92),'/'),quote=True)+'">'+escape(j['module'])+'</a> · '+escape(j['status'])+'</p>' for j in jobs)}</section>
    <section id="coverage"><h2>Coverage a doporučené testy</h2><p>Měří se aplikační Python, bez testů a auditních nástrojů. Nepokrytí neznamená automaticky chybějící nebo nefunkční funkci.</p>
    {table(('Soubor','Funkce','Řádek','Chybějící příkazy'),[(f['file'],f['name'],f['line'],f['missing_statements']) for f in coverage.get('uncovered_functions',[])])}
    <p>Priorita doplnění: datové transakce a chybové stavy, řídicí logika modulů, pak alternativní GUI cesty.</p></section>
    <section id="code"><h2>Statistiky a udržitelnost kódu</h2>{table(('Jazyk','Soubory','Řádky','SLOC','Třídy','Funkce','Metody'),[(k,*[v.get(n,0) for n in ('files','lines','sloc','classes','functions','methods')]) for k,v in analysis.get('languages',{}).items()])}
    <details><summary>Rozdělení podle modulů</summary>{table(('Modul','Soubory','SLOC','Třídy','Funkce','Metody'),[(k,*[v.get(n,0) for n in ('files','sloc','classes','functions','methods')]) for k,v in analysis.get('modules',{}).items()])}</details>
    <h3>Největší soubory</h3>{table(('Soubor','SLOC','Maintainability index'),[(f['file'],f['sloc'],f.get('maintainability','N/A')) for f in biggest])}
    <h3>Složitost nad 10</h3>{table(('Soubor','Funkce','Řádek','Cyklomatická složitost'),sorted(complexity,key=lambda x:x[3],reverse=True))}
    <details><summary>Statické nálezy Ruff ({len(lint)})</summary>{table(('Soubor','Řádek','Kód','Zpráva'),[(Path(r['filename']).name,r['location']['row'],r['code'],r['message']) for r in lint])}</details>
    <details><summary>Kandidáti bez statické reference</summary>{table(('Soubor','Funkce','Řádek'),[(f['file'],f['name'],f['line']) for f in analysis.get('unused_candidates',[])])}</details>
    <details><summary>Strukturální duplicity funkcí: {len(analysis.get('duplicates',[]))} skupin</summary>{table(('Skupina','Soubor','Funkce','Řádek'),[(i,f['file'],f['name'],f['line']) for i,group in enumerate(analysis.get('duplicates',[]),1) for f in group])}</details>
    <details><summary>Opakované bloky příkazů: {len(analysis['block_duplicates']) if 'block_duplicates' in analysis else 'Nedostupné v tomto běhu'}</summary>
    <p>Python AST: celé funkce alespoň 8 řádků / 3 příkazů a bloky 4 příkazů alespoň 6 řádků. Porovnání ignoruje komentáře a pozice, nikoli názvy proměnných. Skupiny se mohou překrývat; nejsou důkazem nutného refaktoringu.</p>
    {table(('Skupina','Soubor','Začátek','Konec'),[(i,f['file'],f['line'],f['end_line']) for i,group in enumerate(analysis.get('block_duplicates',[]),1) for f in group])}</details>
    <details><summary>Audit testů · kandidáti k ruční kontrole</summary>{table(('Soubor','Test','Důvod'),[(f['file'],f['name'],f['reason']) for f in analysis.get('test_review',[])])}</details>
    <details><summary>Potenciální cykly přímých importů</summary>{table(('Cyklus',),[(' → '.join(c),) for c in analysis.get('eager_import_cycles',[])])}</details></section>
    <section id="security"><h2>Bezpečnost</h2><p>Bandit a detekce literálů vytvářejí kandidáty, nikoli potvrzené zranitelnosti. Hodnoty podezřelých tajných údajů nejsou zveřejněny. Závislosti jsou dotazovány proti aktuálnímu poradnímu zdroji pip-audit.</p>
    <p>Bandit: {checks.get('Bandit',{}).get('status','unavailable')} · Zranitelnosti závislostí: {checks.get('Dependency vulnerabilities',{}).get('status','unavailable')}. Přeskočená kontrola neznamená nulový počet rizik.</p>
    <p>Unikátní upozornění na balíčky: {summary.get('dependency_vulnerabilities') if summary.get('dependency_vulnerabilities') is not None else 'Nedostupné'}. Opakované záznamy stejného advisory ID pro stejný balíček a verzi se počítají jednou; původní výstup je zachován.</p>
    {table(('Soubor','Řádek','Pravidlo','Závažnost','Zpráva'),[(Path(r['filename']).name,r['line_number'],r['test_id'],r['issue_severity'],r['issue_text']) for r in security])}
    {table(('Balíček','Verze','Advisory','Opravené verze','Popis'),vuln_rows)}
    <h3>Neověřitelné balíčky</h3>{table(('Balíček','Verze','Důvod'),unavailable_packages)}
    <details><summary>Potenciální tajné literály (bez hodnot)</summary>{table(('Soubor','Řádek','Proměnná'),[(f['file'],f['line'],f['name']) for f in analysis.get('secret_candidates',[])])}</details>
    <h3>Dostupné aktualizace závislostí</h3>{table(('Balíček','Instalovaná','Dostupná'),[(r['name'],r['version'],r['latest_version']) for r in checks.get('Outdated dependencies',{}).get('data',[])])}</section>
    <section id="history"><h2>Výkon a historie</h2>{table(('Metrika','Naměřená hodnota'),summary['performance'].items())}
    <p>Časy jsou v ms, paměť je vzorkovaný vrchol RSS v MiB. Datové benchmarky používají 10 000 syntetických záznamů a medián pěti opakování; studený výpočet a první vykreslení se měří jednou. GUI testy běží sekvenčně.</p>
    <p>startup_ready_ms měří start.run() po importech. startup_process_to_ready_ms zahrnuje i spuštění instrumentovaného testovacího procesu. startup_process_rss_mb je RSS tohoto procesu při zobrazení domovské obrazovky, nikoli paměť sestaveného EXE.</p>
    <div class="charts">{trend(comparable,'coverage_percent','Pokrytí příkazů (%)')}{trend(comparable,'failed','Neúspěšné testy')}{trend(comparable,'load_10000_ms','Načtení 10 000 záznamů (ms)',True)}{trend(comparable,'startup_ready_ms','První zobrazení aplikace (ms)',True)}</div>
    <p>Baseline: {escape(str(report.get('baseline_id') or 'První srovnatelné měření – regrese nelze vyhodnotit.'))}</p>
    {table(('Metrika','Dříve','Nyní','Interpretace'),[(r['metric'],r['before'],r['after'],r['reason']) for r in report.get('regressions',[])])}</section>
    <section><h2>Bezpečnost vstupů a omezení</h2><p>Kontrolované vstupní soubory: {checks.get('Protected inputs',{}).get('checked_files','N/A')}. Změny: {escape(str(checks.get('Protected inputs',{}).get('changed',[])))}.</p><ul>{''.join('<li>'+escape(s)+'</li>' for s in report['limitations'])}</ul>
    <p><a href="diagnostics/{escape(report['id'])}/result.json">Úplná strojově čitelná data</a> · <a href="latest.pdf">Tisknutelný PDF report</a></p></section></main>'''
    html='''<!doctype html><html lang="cs"><head><meta charset="utf-8"><base href="./"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VocabPro · Quality audit</title><style>
    :root{font-family:Segoe UI,Arial,sans-serif;color:#244743;background:#eee9df}body{margin:0}header,main,nav{max-width:1400px;margin:auto;padding:24px}header{padding-top:44px}h1{font-size:38px}h2{font-size:25px}nav{position:sticky;top:0;background:#40695b;display:flex;gap:22px;flex-wrap:wrap;border-radius:18px;z-index:2}nav a{color:#fffcf5}a{color:#397d77}section{background:#fffcf5;padding:28px;margin:22px 0;border-radius:22px;box-shadow:0 4px 18px #2447430b}.cards,.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}.card{background:#e1d6bf;padding:20px;border-radius:16px}.card strong{display:block;font-size:34px;margin-top:8px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:10px;border-bottom:1px solid #ded4c1;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}th{background:#e1d6bf;position:sticky;top:0}tr:nth-child(even){background:#f4f1e9}.scroll{overflow:auto;max-height:620px;margin:16px 0}input{padding:12px;width:90%;border:1px solid #b5c3a4;border-radius:10px;font:inherit}details{margin:18px 0}summary{cursor:pointer;font-weight:bold}figure{margin:8px;padding:15px;background:#eee9df;border-radius:14px}svg{width:100%}text{font-size:13px;fill:#657671}@media print{nav,input{display:none}.scroll{max-height:none;overflow:visible}section{break-inside:avoid;box-shadow:none}body{background:white}}
    .banner{padding:14px 18px;background:#f0e5ce;border-left:5px solid #a77732;border-radius:10px}.status{font-weight:600;padding:3px 7px;border-radius:6px}.status.passed{background:#d9eadc}.status.failed{background:#f3ddd5;color:#963f32}.status.warning,.status.unavailable{background:#f0e5ce;color:#895d2f}.status.skipped,.status.expected_failure{background:#eee9df;color:#657671}
    </style></head><body>'''+content+'''<script>document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.toLocaleLowerCase();document.querySelectorAll('#test-table tbody tr').forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase().includes(q));});</script></body></html>'''
    archive=quality/'archive';archive.mkdir(exist_ok=True)
    pdf_error=None
    try:
        create_pdf(report,analysis,tests,coverage,biggest,complexity,security,vuln_rows,archive/(report['id']+'.pdf'),comparable)
        temporary=quality/'latest.pdf.tmp'
        try:
            shutil.copyfile(archive/(report['id']+'.pdf'),temporary)
            temporary.replace(quality/'latest.pdf')
        finally:temporary.unlink(missing_ok=True)
    except Exception as error:pdf_error=type(error).__name__+': '+redact(str(error))
    html=html.replace('href="latest.pdf"',f'href="archive/{report["id"]}.pdf"')
    if pdf_error:html=html.replace(f'<a href="archive/{report["id"]}.pdf">Tisknutelný PDF report</a>','<span>PDF tohoto běhu není dostupné: '+escape(pdf_error)+'</span>')
    previous_full=next((h for h in reversed(history) if h['mode']=='Full'),None)
    if report['mode']=='Quick' and previous_full:
        link='<p><a href="archive/'+escape(previous_full['id'],quote=True)+'.html">Poslední úplný Full audit</a></p>'
        html=html.replace('<main>','<main>'+link)
    atomic(archive/(report['id']+'.html'),html.replace('<base href="./">','<base href="../">'))
    atomic(quality/'latest.html',html)
    write_json(archive/(report['id']+'.json'),report)
    return {'status':'unavailable' if pdf_error else 'passed','reason':pdf_error or '',
        'html':'latest.html','pdf':'latest.pdf' if pdf_error is None else None}


def create_pdf(report,analysis,tests,coverage,biggest,complexity,security,vulnerabilities,path,history):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,LongTable,TableStyle
    font=Path('C:/Windows/Fonts/arial.ttf')
    if not font.exists():
        import reportlab
        font=Path(reportlab.__file__).parent/'fonts/Vera.ttf'
    pdfmetrics.registerFont(TTFont('Quality',str(font)))
    styles=getSampleStyleSheet()
    for style in styles.byName.values():style.fontName='Quality'
    styles['BodyText'].fontSize=8;styles['BodyText'].leading=11
    story=[]
    def p(text,style='BodyText'):story.append(Paragraph(escape(redact(display(text))),styles[style]))
    def grid(headings,rows,widths=None):
        cells=[[Paragraph(escape(redact(display(value))),styles['BodyText']) for value in headings]]
        cells.extend([Paragraph(escape(redact(display(value))),styles['BodyText']) for value in row] for row in rows)
        if len(cells)==1:p('Žádné položky / metrika nedostupná podle uvedeného stavu.');return
        value=LongTable(cells,colWidths=widths or [180*mm/len(headings)]*len(headings),repeatRows=1,hAlign='LEFT')
        value.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1d6bf')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#ded4c1')),('LEFTPADDING',(0,0),(-1,-1),5)]))
        story.extend([value,Spacer(1,5*mm)])
    p('VocabPro – audit kvality','Title');p(report['date']+' · '+report['mode']);s=report['summary']
    grid(('Metrika','Výsledek'),[(key,value) for key,value in s.items() if key!='performance'])
    p('Stavy kontrol','Heading1');grid(('Kontrola','Stav','Poznámka'),[(name,c['status'],c.get('reason','')) for name,c in report['checks'].items()])
    p('Výkon','Heading1');grid(('Metrika','Hodnota'),s['performance'].items())
    p('Historie a regrese','Heading1');p('Baseline: '+str(report.get('baseline_id') or 'První srovnatelné měření'))
    grid(('Metrika','Dříve','Nyní'),[(r['metric'],r['before'],r['after']) for r in report.get('regressions',[])])
    from reportlab.graphics.shapes import Drawing,PolyLine,Circle,String
    for key,title,is_performance in (('coverage_percent','Coverage (%)',False),('failed','Neúspěšné testy',False),('load_10000_ms','Načtení dat (ms)',True),('startup_ready_ms','První zobrazení (ms)',True)):
        values=[h['summary'].get('performance',{}).get(key) if is_performance else h['summary'].get(key) for h in history]
        values=[v for v in values if isinstance(v,(int,float))][-30:]
        if not values:continue
        drawing=Drawing(480,145);drawing.add(String(12,130,title,fontName='Quality',fontSize=11))
        low,high=min(values),max(values);span=max(high-low,1)
        points=[(12+i*450/max(1,len(values)-1),25+(v-low)*85/span) for i,v in enumerate(values)]
        if len(points)>1:drawing.add(PolyLine([n for point in points for n in point],strokeColor=colors.HexColor('#397d77'),strokeWidth=2))
        for x,y in points:drawing.add(Circle(x,y,3,fillColor=colors.HexColor('#a77732'),strokeColor=None))
        drawing.add(String(12,8,f'{low:.2f} - {high:.2f}; {len(values)} měření',fontName='Quality',fontSize=8));story.append(drawing)
    p('GUI Testing','Heading1');p(f'Úspěšné: {s["gui_passed"]}, neúspěšné: {s["gui_failed"]}, přeskočené: {s["gui_skipped"]}. GUI je podmnožinou testů.')
    grid(('GUI test','Stav','Sekundy'),[(r['id'],r['status'],round(r['duration'],3)) for r in tests if r['gui']])
    p('Všechny automatické testy','Heading1');grid(('Test','Stav'),[(r['id'],r['status']) for r in tests])
    p('Chyby a tracebacky','Heading1')
    for r in tests:
        if r['status']=='failed':p(r['id'],'Heading2');p('\n'.join(r['details']))
    p('Coverage – nepokryté funkce','Heading1');grid(('Soubor / funkce','Chybějící příkazy'),[(f['file']+':'+f['name'],f['missing_statements']) for f in coverage.get('uncovered_functions',[])])
    p('Největší soubory','Heading1');grid(('Soubor','SLOC','MI'),[(f['file'],f['sloc'],f.get('maintainability','N/A')) for f in biggest])
    p('Nejsložitější funkce','Heading1');grid(('Soubor / funkce','Složitost'),[(f+':'+name,cc) for f,name,line,cc in sorted(complexity,key=lambda x:x[3],reverse=True)[:60]])
    p('Bezpečnost','Heading1');grid(('Soubor','Pravidlo','Závažnost'),[(Path(r['filename']).name,r['test_id'],r['issue_severity']) for r in security])
    grid(('Balíček','Verze','Advisory','Opravené verze'),[r[:4] for r in vulnerabilities])
    p('Omezení a doporučení','Heading1')
    for limitation in report['limitations']:p(limitation)
    p('Podrobné statické nálezy, diagnostika, screenshoty a interaktivní grafy jsou v HTML reportu a strojově čitelném JSON. Kandidáty vždy ověřte ručně.')
    def footer(canvas,doc):
        canvas.setFont('Quality',8);canvas.drawString(15*mm,10*mm,'VocabPro · '+report['id']);canvas.drawRightString(195*mm,10*mm,str(doc.page))
    temporary=path.with_suffix('.pdf.tmp')
    try:
        SimpleDocTemplate(str(temporary),leftMargin=15*mm,rightMargin=15*mm,topMargin=15*mm,bottomMargin=18*mm).build(story,onFirstPage=footer,onLaterPages=footer)
        temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)

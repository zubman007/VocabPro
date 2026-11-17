"""One audit, isolated module processes, real measurements and durable reports."""
import argparse
from collections import Counter
import csv
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.quality.common import write_json,atomic,redact,sanitize,protected_snapshot,regressions

QUICK=('test_storage','test_preferences_data','test_data_integrity','test_background_task',
       'test_training_data','test_localization_validation','test_repositories','test_editor_async_ui','test_vocabulary_editor_dropdowns',
       'test_learning_ui','test_translations')


def environment(run):
    env={key:value for key,value in os.environ.items()
        if not re.search(r'token|password|secret|smtp|api[_-]?key|credential',key,re.I)}
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',PYTHONUTF8='1',
        PYGAME_HIDE_SUPPORT_PROMPT='1',PYTHONPATH='',MPLCONFIGDIR=str(run/'cache/matplotlib'),
        PIP_CACHE_DIR=str(run/'cache/pip'),TEMP=str(run/'temporary'),TMP=str(run/'temporary'))
    for name in ('temporary','cache/matplotlib','cache/pip'):(run/name).mkdir(parents=True,exist_ok=True)
    return env


def command(arguments,root,env,timeout=180):
    try:import psutil
    except ImportError:psutil=None
    started=time.perf_counter();child_env=dict(env,QUALITY_PROCESS_STARTED=str(started))
    process=subprocess.Popen([str(x) for x in arguments],cwd=root,env=child_env,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    peak=0;timed_out=False
    while True:
        if psutil is not None:
            try:
                watched=psutil.Process(process.pid)
                peak=max(peak,sum(p.memory_info().rss for p in [watched,*watched.children(recursive=True)] if p.is_running()))
            except (psutil.Error,OSError):pass
        try:
            stdout,stderr=process.communicate(timeout=.15);break
        except subprocess.TimeoutExpired:
            if time.perf_counter()-started>timeout:
                timed_out=True
                if psutil is not None:
                    try:
                        for child in psutil.Process(process.pid).children(recursive=True):child.kill()
                    except psutil.Error:pass
                process.kill();stdout,stderr=process.communicate();break
    return {'returncode':process.returncode,'stdout':stdout,'stderr':stderr,
        'seconds':time.perf_counter()-started,'peak_rss_mb':round(peak/1024**2,2) if psutil is not None else None,'timeout':timed_out}


def stage(report,name,callback):
    print(name+'…',flush=True);started=time.perf_counter()
    try:
        value=callback()
        if not isinstance(value,dict):value={'data':value}
        value.setdefault('status','passed')
    except Exception as error:
        value={'status':'unavailable','reason':redact(type(error).__name__+': '+str(error))}
    value['seconds']=time.perf_counter()-started
    report['checks'][name]=value
    print(name+': '+value['status'],flush=True)
    return value


def shadow_project(root,destination):
    for name in ('app','images','locales','tools'):
        shutil.copytree(root/name,destination/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'),symlinks=False)
    for name in ('start.py','requirements.txt','requirements.lock.txt'):
        shutil.copy2(root/name,destination/name)
    # No learning histories/settings/credentials are copied. Only the supplied
    # catalog tests' read-only inputs and packaged UI sounds are needed.
    (destination/'files').mkdir()
    schema=[]
    if (root/'files/settings.csv').exists():
        with (root/'files/settings.csv').open(encoding='utf-8-sig',newline='') as stream:
            schema=[{'Name':row['Name'],'Type':row['Type']} for row in csv.DictReader(stream,delimiter=';')]
    write_json(destination/'preference-schema.json',schema)
    for language in ('Spanish','English'):
        source=root/'files'/f'Czech_{language}_tags.csv'
        if source.exists() and not source.is_symlink():shutil.copy2(source,destination/'files'/source.name)
        # Some legacy UI tests mock their main loader but still consult the
        # default course for revision/synonym counts. Never copy a user's words.
        headers=['ID',language,'Czech','Audio','Description','Example','Part of Speech',
            'Repetition','Next repetition','Created','Tags','Custom']
        if language=='English':headers.insert(3,'Phonetic')
        row=dict.fromkeys(headers,'')
        row.update(ID='1',Czech='null',Audio='No audio',Description='manual',Example='manual example',
            Repetition='SF',Created='2025-01-01',Custom='007;keep',**{language:'NA','Part of Speech':'Noun','Next repetition':'2026-11-13 10:00:00'})
        with (destination/'files'/f'Czech_{language}_voc.csv').open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=headers,delimiter=';');writer.writeheader();writer.writerow(row)
    conjugation=['ID','Spanish','Czech','Description','s1','s2','s3','m1','m2','m3','R','LR']
    with (destination/'files/Czech_Spanish_con.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=conjugation,delimiter=';');writer.writeheader()
        writer.writerow(dict(ID='1',Spanish='hablar',Czech='mluvit',Description='present',
            **dict.fromkeys(('s1','s2','s3','m1','m2','m3'),'form'),R='',LR=''))
    sound=root/'files/audio/sounds'
    if sound.exists():shutil.copytree(sound,destination/'files/audio/sounds')


def run_tests(args,shadow,run,env,report):
    modules=sorted('app.tests.'+p.stem for p in (shadow/'app/tests').glob('test_*.py')) if args.mode=='Full' else ['app.tests.'+m for m in QUICK]
    modules+=['tools.quality.harness_tests','tools.quality.gui_tests']
    jobs=[]
    for number,module in enumerate(modules,1):
        output=run/'diagnostics'/module;output.mkdir(parents=True)
        cli=[args.python,'-X','utf8','-B',shadow/'tools/quality/worker.py','--root',shadow,
            '--production',args.root,'--output',output,'--tool-site',args.tool_site,'--module',module]
        if args.mode=='Full':cli+=['--coverage']
        value=command(cli,shadow,env,args.timeout)
        atomic(output/'console.txt',redact(value['stdout']+'\n'+value['stderr']).replace(str(shadow),'<isolated-project>'))
        path=output/'result.json'
        if path.exists():job=json.loads(path.read_text(encoding='utf-8'))
        else:job={'module':module,'records':[],'tests':0,'status':'unavailable','reason':'Worker timeout' if value['timeout'] else 'Worker ended without a structured result.'}
        if value['returncode']!=0 and job.get('status')=='passed':job['status']='failed'
        job.update(seconds=value['seconds'],peak_rss_mb=value['peak_rss_mb'],diagnostics=str((output/'console.txt').relative_to(run.parent.parent)))
        job['runtime_warnings']=len(re.findall(r'invalid command name|Exception in Tkinter callback',value['stdout']+value['stderr']))
        for record in job['records']:
            record['screenshots']=[str((output/name).relative_to(run.parent.parent)).replace('\\','/') for name in record['screenshots']]
        jobs.append(job)
        print(f'[{number}/{len(modules)}] {module}: {job["status"]} ({job["tests"]} tests)',flush=True)
        write_json(run/'tests.partial.json',jobs)
    return {'status':'failed' if any(j['status']=='failed' for j in jobs) else 'unavailable' if any(j['status']=='unavailable' for j in jobs) else 'passed','modules':jobs}


def combine_coverage(shadow,run,analysis):
    from coverage import Coverage
    paths=[str(p) for p in (run/'diagnostics').glob('*/coverage') if p.is_file()]
    if not paths:raise RuntimeError('No coverage data produced by workers.')
    cov=Coverage(data_file=str(run/'combined.coverage'),source=[str(shadow/'app')],branch=True,config_file=False)
    cov.combine(data_paths=paths,keep=True);cov.save()
    target=run/'coverage.json';cov.json_report(outfile=str(target))
    value=json.loads(target.read_text(encoding='utf-8'));files={}
    for name,item in value['files'].items():
        path=Path(name)
        relative=path.relative_to(shadow).as_posix() if path.is_absolute() else path.as_posix()
        files[relative]=item
    total=value['totals'];uncovered=[]
    for function in analysis.get('functions',[]):
        item=files.get(function['file'])
        if not item:continue
        lines=set(range(function['line']+1,function['end_line']+1))
        statements=(set(item['missing_lines'])|set(item['executed_lines'])) & lines
        missing=set(item['missing_lines']) & statements
        if statements and len(missing)==len(statements):
            uncovered.append({**function,'missing_statements':len(missing),'recommendation':'Add an isolated behavior/error-path test; prioritize data writes and application controllers.'})
    return {'status':'passed','statement_percent':100*total['covered_lines']/max(1,total['num_statements']),
        'branch_percent':100*total.get('covered_branches',0)/max(1,total.get('num_branches',0)),
        'totals':total,'files':files,'uncovered_functions':uncovered}


def tool_check(name,cli,root,run,env,success_codes=(0,1),timeout=180):
    result=command(cli,root,env,timeout)
    # Bandit's source snippets may contain the very secret it reports. Keep
    # locations/rules, never the source snippet, in either JSON or raw logs.
    if name!='bandit':atomic(run/(name+'.log'),redact(result['stdout']+'\n'+result['stderr']))
    else:atomic(run/(name+'.log'),redact(result['stderr']))
    if result['timeout'] or result['returncode'] not in success_codes:
        return {'status':'unavailable','reason':'Tool timeout or execution failure; see diagnostics.','diagnostic':name+'.log'}
    try:data=sanitize(json.loads(result['stdout']))
    except json.JSONDecodeError:return {'status':'unavailable','reason':'Tool did not return valid JSON.','diagnostic':name+'.log'}
    status='warning' if result['returncode'] else 'passed'
    if name=='bandit':
        for finding in data.get('results',[]):finding.pop('code',None)
    if name=='outdated' and data:status='warning'
    if name=='powershell' and data:status='failed'
    if name=='pip-audit' and any('skip_reason' in item for item in data.get('dependencies',[])):status='warning'
    return {'status':status,'data':data,'seconds':result['seconds']}


def main():
    parser=argparse.ArgumentParser()
    for key in ('root','python','tools-python'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--mode',choices=['Quick','Full'],default='Full');parser.add_argument('--timeout',type=int,default=180)
    parser.add_argument('--no-open',action='store_true');parser.add_argument('--fail-on-findings',action='store_true')
    args=parser.parse_args();args.root=Path(args.root).resolve();root=args.root
    args.tool_site=str(Path(args.tools_python).resolve().parent.parent/'Lib/site-packages');sys.path.append(args.tool_site)
    quality=root/'reports/quality';quality.mkdir(parents=True,exist_ok=True)
    # Exclusive OS lock is automatically released after crashes; never delete a
    # guessed stale lock or let concurrent audits overwrite history/latest.
    import msvcrt
    lock=None
    try:
        lock=(quality/'audit.lock').open('a+b')
        if (quality/'audit.lock').stat().st_size==0:lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        if lock is not None:lock.close()
        print('Another quality audit is running, or its lock is unavailable. No report/history was overwritten.');return 2
    identity=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
    run=quality/'diagnostics'/identity;index=0
    while run.exists():index+=1;identity=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')+f'-{index:03d}';run=quality/'diagnostics'/identity
    run.mkdir(parents=True);env=environment(run)
    report={'version':1,'id':identity,'date':datetime.now(timezone.utc).isoformat(),'mode':args.mode,'checks':{},
        'limitations':['GUI coverage describes tests that actually attempted Tk, not all visual states.',
            'Real SMTP/OAuth/Internet/audio devices and the OS credential vault are blocked in tests.',
            'No application backup-restore screen exists: only isolated byte restoration/reload is tested.',
            'Default shadow vocabulary files are synthetic fixtures; supplied tag catalogs are tested using read-only isolated copies.',
            'No Nuitka EXE build or exhaustive pixel/visual review is performed.',
            'Unused/duplicate/obsolete-code candidates require manual review; no automatic fixes are applied.']}
    began=time.perf_counter()
    baseline_errors={};baseline=protected_snapshot(root,errors=baseline_errors)
    try:
        from tools.quality.analysis import inspect_sources
        analysis=stage(report,'Source analysis',lambda:inspect_sources(root))
        report['analysis']=analysis
        inventory_result=command([args.python,'-B','-c','import importlib.metadata as m,json;print(json.dumps({d.metadata["Name"]:d.version for d in m.distributions()}))'],root,env,30)
        versions={}
        for name in ('ruff','coverage','radon','bandit','pip-audit','psutil','reportlab'):
            try:versions[name]=importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:versions[name]=None
        inventory=json.loads(inventory_result['stdout']);report['environment']={'python':platform.python_version(),'platform':platform.platform(),'packages':inventory,'tools':versions}
        if versions['psutil'] is None:report['checks']['Memory sampling']={'status':'unavailable','reason':'psutil is unavailable; no RAM metric inferred.'}
        requirements=run/'audited-requirements.txt'
        atomic(requirements,'\n'.join(name+'=='+version for name,version in sorted(inventory.items()))+'\n')
        stage(report,'Ruff',lambda:tool_check('ruff',[args.tools_python,'-m','ruff','check','--no-cache','--output-format','json',
            '--config',root/'tools/quality/ruff.toml',root/'app',root/'start.py',root/'tools'],root,run,env))
        ps_env=dict(env,QUALITY_SCRIPT_ROOT=str(root))
        ps_parser="ConvertTo-Json -InputObject @(Get-ChildItem -LiteralPath $env:QUALITY_SCRIPT_ROOT -Filter '*.ps1' -File | ForEach-Object { $qf=$_; $qt=$null; $qe=$null; [System.Management.Automation.Language.Parser]::ParseFile($qf.FullName,[ref]$qt,[ref]$qe) | Out-Null; $qe | ForEach-Object { @{File=$qf.Name; Line=$_.Extent.StartLineNumber; Message=$_.Message} } }) -Compress"
        stage(report,'PowerShell syntax',lambda:tool_check('powershell',[shutil.which('powershell') or 'powershell','-NoProfile','-Command',ps_parser],root,run,ps_env,success_codes=(0,)))
        if args.mode=='Full':
            stage(report,'Bandit',lambda:tool_check('bandit',[args.tools_python,'-m','bandit','-r',root/'app',root/'start.py','-x',str(root/'app/tests'),'-f','json','-q'],root,run,env))
            stage(report,'Dependency vulnerabilities',lambda:tool_check('pip-audit',[args.tools_python,'-m','pip_audit','-r',requirements,
                '--no-deps','--disable-pip','--format','json','--progress-spinner','off','--timeout','15'],root,run,env,timeout=240))
            stage(report,'Outdated dependencies',lambda:tool_check('outdated',[args.python,'-m','pip','list','--outdated','--format','json',
                '--disable-pip-version-check','--timeout','10','--retries','0'],root,run,env,timeout=180))
        else:
            for name in ('Bandit','Dependency vulnerabilities','Outdated dependencies','Coverage','Benchmarks'):
                report['checks'][name]={'status':'skipped','reason':'Full mode only; no value inferred.'}
        with tempfile.TemporaryDirectory(prefix='vocabpro-quality-') as temporary:
            shadow=Path(temporary)
            def prepare():
                shadow_project(root,shadow)
                result=command([args.python,'-X','utf8','-B',shadow/'tools/quality/fixtures.py','--root',shadow],shadow,env,60)
                atomic(run/'fixtures.log',redact(result['stdout']+'\n'+result['stderr']))
                if result['returncode']:raise RuntimeError('Synthetic fixture preparation failed; see fixtures.log. Production tests were not run.')
                return {'status':'passed','fixture_schema':2}
            stage(report,'Isolated project',prepare)
            if report['checks']['Isolated project']['status']=='passed':
                stage(report,'Tests',lambda:run_tests(args,shadow,run,env,report))
                if args.mode=='Full':
                    stage(report,'Coverage',lambda:combine_coverage(shadow,run,analysis))
                    output=run/'diagnostics/benchmarks';output.mkdir()
                    def bench():
                        result=command([args.python,'-X','utf8','-B',shadow/'tools/quality/worker.py','--root',shadow,'--production',root,
                            '--output',output,'--tool-site',args.tool_site,'--benchmark'],shadow,env,args.timeout)
                        atomic(output/'console.txt',redact(result['stdout']+'\n'+result['stderr']))
                        data=json.loads((output/'result.json').read_text(encoding='utf-8'))
                        data['peak_rss_mb']=result['peak_rss_mb'];return data
                    stage(report,'Benchmarks',bench)
        after_errors={};after=protected_snapshot(root,errors=after_errors)
        changed=sorted(name for name in baseline.keys()|after.keys() if baseline.get(name)!=after.get(name))
        report['checks']['Protected inputs']={'status':'unavailable' if baseline_errors or after_errors else 'warning' if changed else 'passed',
            'checked_files':len(baseline),'changed':changed,'unreadable':dict(baseline_errors,**after_errors),
            'reason':'Some protected inputs could not be read; complete hash verification is unavailable.' if baseline_errors or after_errors else '',
            'note':'A change may also come from concurrent external edits. Workers cannot write production inputs.'}
        jobs=report['checks'].get('Tests',{}).get('modules',[]);records=[r for j in jobs for r in j.get('records',[]) if not r.get('fixture')]
        counts=Counter(r['status'] for r in records);gui=Counter(r['status'] for r in records if r['gui'])
        performance=dict(report['checks'].get('Benchmarks',{}).get('performance',{}))
        for record in records:performance.update(record.get('metrics',{}))
        measured_memory=[j['peak_rss_mb'] for j in jobs if j['peak_rss_mb'] is not None]
        if measured_memory:performance['tests_peak_rss_mb']=max(measured_memory)
        coverage=report['checks'].get('Coverage',{})
        lint=report['checks'].get('Ruff',{}).get('data',[])
        bandit=report['checks'].get('Bandit',{}).get('data',{}).get('results',[])
        dependency_findings=sum(len(d.get('vulns',[])) for d in report['checks'].get('Dependency vulnerabilities',{}).get('data',{}).get('dependencies',[]))
        bandit_count=len(bandit) if report['checks'].get('Bandit',{}).get('status') in ('passed','warning') else None
        dependency_count=dependency_findings if report['checks'].get('Dependency vulnerabilities',{}).get('status') in ('passed','warning') else None
        lint_count=len(lint) if report['checks'].get('Ruff',{}).get('status') in ('passed','warning') else None
        report['summary']={'tests':len(records),'passed':counts['passed'],'failed':counts['failed'],'skipped':counts['skipped'],
            'expected_failure':counts['expected_failure'],'gui_tests':sum(gui.values()),'gui_passed':gui['passed'],'gui_failed':gui['failed'],
            'gui_skipped':gui['skipped'],'coverage_percent':coverage.get('statement_percent'),'branch_percent':coverage.get('branch_percent'),
            'lint_findings':lint_count,'bandit_findings':bandit_count,'dependency_vulnerabilities':dependency_count,
            'security_findings':bandit_count+dependency_count if bandit_count is not None and dependency_count is not None else None,'performance':performance,
            'runtime_warnings':sum(j['runtime_warnings'] for j in jobs),'module_failures':sum(j['status']!='passed' for j in jobs)}
        report['summary'].update({'source_'+key:value for key,value in analysis.get('totals',{}).items()})
        if 'files' in analysis:
            report['summary']['high_complexity_functions']=sum(c['complexity']>10 for f in analysis['files'] for c in f.get('complexity',[]))
            report['summary']['duplicate_groups']=len(analysis.get('duplicates',[]))+len(analysis.get('block_duplicates',[]))
        normalized_inputs={k.replace('\\','/'):v for k,v in baseline.items()}
        report['source_fingerprint']=hashlib.sha256(json.dumps({k:v for k,v in normalized_inputs.items() if k.startswith('app/') or k=='start.py'},sort_keys=True).encode()).hexdigest()
        history_path=quality/'history.json'
        history_writable=True
        try:
            history=json.loads(history_path.read_text(encoding='utf-8')) if history_path.exists() else []
            if not isinstance(history,list) or any(not isinstance(item,dict) or not {'id','mode','summary','date'}<=set(item) for item in history):raise ValueError
        except (ValueError,OSError):
            history=[];history_writable=False
            report['checks']['History']={'status':'unavailable','reason':'History is unreadable. Existing history was preserved; this run still has its own report.'}
        previous=next((item for item in reversed(history) if item['mode']==args.mode and item.get('python')==report['environment']['python']
            and item.get('platform',report['environment']['platform'])==report['environment']['platform']),None)
        report['regressions']=regressions(report['summary'],previous.get('summary') if previous else None)
        report['baseline_id']=previous['id'] if previous else None
        report['seconds']=time.perf_counter()-began
        write_json(run/'result.json',report)
        from tools.quality.report import render
        stage(report,'Reports',lambda:render(report,history,quality,run))
        write_json(run/'result.json',report)
        write_json(quality/'archive'/(identity+'.json'),report)
        write_json(quality/'latest.json',{'version':1,'id':identity,'date':report['date'],'mode':args.mode,'summary':report['summary'],
            'checks':{name:{'status':value['status'],'reason':value.get('reason','')} for name,value in report['checks'].items()},
            'html':report['checks']['Reports'].get('html'),'pdf':report['checks']['Reports'].get('pdf')})
        # Publish history only once, after recording report generation outcomes.
        history.append({'id':identity,'date':report['date'],'mode':args.mode,'python':report['environment']['python'],
            'platform':report['environment']['platform'],'source_fingerprint':report['source_fingerprint'],'summary':report['summary']})
        if history_writable:write_json(history_path,history)
        print(json.dumps(report['summary'],ensure_ascii=False,indent=2),flush=True)
        html_available=bool(report['checks']['Reports'].get('html'))
        print('HTML: '+str(quality/'latest.html') if html_available else 'HTML unavailable; per-run diagnostics were preserved.',flush=True)
        if not args.no_open and html_available:webbrowser.open((quality/'latest.html').as_uri())
        if report['summary']['failed'] or report['summary']['module_failures'] or any(c['status']=='failed' for c in report['checks'].values()):return 1
        if any(check['status']=='unavailable' for check in report['checks'].values()):return 2
        if args.fail_on_findings and (any(c['status']=='warning' for c in report['checks'].values()) or report['regressions']):return 3
        return 0
    finally:lock.close()


if __name__=='__main__':
    raise SystemExit(main())

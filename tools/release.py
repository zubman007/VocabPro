"""Nuitka staging, offline probes and conservative directory-swap releases."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.version import __version__


def write_json(path,value):
    path=Path(path);temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    temporary.replace(path)


@contextmanager
def release_lock(path):
    import msvcrt
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as stream:
        if not path.stat().st_size:stream.write(b'1');stream.flush()
        stream.seek(0)
        try:msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:raise RuntimeError('VocabPro is running or another update is in progress. Close it and retry.') from None
        try:yield
        finally:stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)


def managed(folder):
    path=Path(folder)/'release.json'
    if not path.is_file():return False
    try:return json.loads(path.read_text(encoding='utf-8')).get('application')=='VocabPro'
    except (OSError,ValueError):return False


def assert_closed(folder):
    import psutil
    wanted=str((Path(folder)/'VocabPro.exe').resolve()).casefold()
    for process in psutil.process_iter(['name','exe']):
        if (process.info['name'] or '').casefold()!='vocabpro.exe':continue
        if not process.info['exe'] or process.info['exe'].casefold()==wanted:
            raise RuntimeError('VocabPro.exe is running. Close the application and run the update again.')


def check_assets(folder):
    folder=Path(folder)
    for path in folder.rglob('*'):
        relative=path.relative_to(folder)
        if (path.is_file() and path.suffix.lower() in ('.csv','.bak')
                and (len(relative.parts)==1 or relative.parts[0] in ('app','files'))):
            raise ValueError('Unexpected user data in compiled distribution.')


def deploy(candidate,target,archive,verify):
    """Only managed asset directories move. No data directory is ever deleted."""
    candidate,target,archive=map(Path,(candidate,target,archive))
    if not managed(candidate):raise ValueError('Candidate is not a managed VocabPro release.')
    if target.exists() and not managed(target):raise ValueError('Existing target has no valid release manifest; refusing to replace it.')
    if target.exists() and (target/'files').exists() and any(
            p.is_file() and not p.relative_to(target/'files').as_posix().startswith('audio/Sounds/')
            for p in (target/'files').rglob('*')):
        raise ValueError('Target contains legacy user data; deployment requires a reviewed migration.')
    if archive.exists():raise FileExistsError(archive)
    archive.parent.mkdir(parents=True,exist_ok=True)
    old=False;installed=False
    try:
        if target.exists():target.rename(archive);old=True
        candidate.rename(target);installed=True
        verify(target)
    except BaseException:
        if installed:target.rename(candidate)
        if old:archive.rename(target)
        raise


def fixture(folder):
    """Synthetic content only; never loads real settings or credentials."""
    from app.tests.test_preferences_data import sample_preferences
    from app.tests.test_editor_save import course
    from app.tests.test_conjugation_model import verbs
    from app.tests.test_grammar_editor import questions
    from app.preferences.data import with_defaults
    from app.preferences.courses import COURSE_FIELD,StudyCourse,encode_courses
    import pandas as pd
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    settings=with_defaults(sample_preferences())
    settings.loc[settings.Name.isin(('11Labs token','Next backup','Backup mail')),'Value']=''
    settings.loc[settings.Name.isin(('Backup period (days)','App sounds enabled','Autoplay pronunciation')),'Value']='0'
    settings.loc[len(settings)]=[COURSE_FIELD,'JSON',encode_courses('cs',[
        StudyCourse('es',conjugation_enabled=True),StudyCourse('en',conjugation_enabled=True)])]
    settings.to_csv(folder/'settings.csv',sep=';',index=False)
    for language in ('English','Spanish'):
        course().rename(columns={'English':language}).to_csv(folder/f'Czech_{language}_voc.csv',sep=';',index=False)
        verbs().rename(columns={'Spanish':language}).to_csv(folder/f'Czech_{language}_con.csv',sep=';',index=False)
        questions().to_csv(folder/f'{language}_gra.csv',sep=';',index=False)
        pd.DataFrame(columns=['ID','Czech',language,'Note']).to_csv(folder/f'Czech_{language}_tags.csv',sep=';',index=False)
    (folder/'RELEASE_TEST_ONLY').write_text('Synthetic release verification only.',encoding='utf-8')


def probe(executable,work,*,python=False):
    work=Path(work);work.mkdir(parents=True,exist_ok=True)
    files=work/'files';fixture(files)
    output=work/'probe.json';env=dict(os.environ)
    for key in list(env):
        if any(word in key.upper() for word in ('TOKEN','PASSWORD','SECRET','CREDENTIAL','API_KEY')):env.pop(key,None)
    env.update(VOCABPRO_DATA_DIR=str(files.resolve()),SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
    temporary=work/'temp';temporary.mkdir(exist_ok=True)
    env.update(TEMP=str(temporary.resolve()),TMP=str(temporary.resolve()),
               MPLCONFIGDIR=str((work/'matplotlib').resolve()),XDG_CACHE_HOME=str((work/'cache').resolve()))
    if not python:
        # Verify dependency resolution without Python on PATH or PYTHONPATH.
        env['PATH']=str(Path(os.environ['SystemRoot'])/'System32')+';'+os.environ['SystemRoot']
        for key in ('PYTHONPATH','PYTHONHOME','VIRTUAL_ENV'):env.pop(key,None)
    command=[str(executable)]
    if python:command+=['-X','utf8','-B',str(ROOT/'start.py')]
    command+=['--release-smoke',str(output.resolve())]
    start=time.perf_counter();env['VOCABPRO_PROBE_STARTED']=str(start)
    import psutil
    peak=0
    with (work/'stdout.log').open('w',encoding='utf-8') as stdout,(work/'stderr.log').open('w',encoding='utf-8') as stderr:
        try:
            process=subprocess.Popen(command,cwd=work,env=env,stdout=stdout,stderr=stderr)
        except OSError as error:
            if getattr(error,'winerror',None)==4551:
                raise RuntimeError(
                    'Windows App Control blocked this executable (WinError 4551). '
                    'The new release was not validated. Keep the previous release and '
                    'arrange trusted code signing or an approved administrator review. '
                    'Do not disable Windows protection. Executable: '+str(executable)
                ) from error
            raise
        while process.poll() is None:
            try:
                owner=psutil.Process(process.pid)
                peak=max(peak,sum(p.memory_info().rss for p in [owner,*owner.children(recursive=True)]))
            except psutil.Error:pass
            if time.perf_counter()-start>120:process.kill();process.wait();raise TimeoutError('EXE verification timed out.')
            time.sleep(.05)
    if process.returncode or not output.exists():raise RuntimeError('Release probe failed; inspect '+str(work))
    report=json.loads(output.read_text(encoding='utf-8'))
    report.update(process_ms=(time.perf_counter()-start)*1000,peak_rss_mib=peak/1048576)
    write_json(output,report)
    if (not report.get('passed') or report.get('version')!=__version__
            or report.get('compiled') is not (not python)):
        raise RuntimeError('Release probe failed or its version/runtime mode is incorrect; inspect '+str(output))
    return report


def git(*args):
    result=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
    return result.stdout.strip() if result.returncode==0 else None


def source_snapshot(folder):
    folder.mkdir(parents=True)
    for name in ('app','images','locales'):
        shutil.copytree(ROOT/name,folder/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc','tests'))
    shutil.copy2(ROOT/'start.py',folder/'start.py')
    sounds=ROOT/'files/audio/Sounds'
    if sounds.exists():shutil.copytree(sounds,folder/'files/audio/Sounds')
    hashes={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--python',required=True)
    parser.add_argument('--quality-mode',choices=('Quick','Full'),default='Quick')
    parser.add_argument('--rollback',action='store_true')
    args=parser.parse_args()
    target=ROOT.parent/'VocabPro_exe';data=ROOT.parent/'VocabPro_data';archives=ROOT.parent/'.VocabPro_releases'
    identity=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S_%f')
    work=ROOT/'.release-build'/identity;work.mkdir(parents=True)
    with release_lock(ROOT.parent/'.VocabPro_exe.update.lock'):
        assert_closed(target)
        previous=json.loads((target/'release.json').read_text(encoding='utf-8')) if managed(target) else {}
        if args.rollback:
            candidates=sorted(p for p in archives.glob('*') if managed(p))
            if not candidates:raise RuntimeError('No preserved release is available for rollback.')
            deploy(candidates[-1],target,archives/identity,lambda path:probe(path/'VocabPro.exe',work/'rollback-probe'))
            print('Rollback verified. User data unchanged.',flush=True);return
        snapshot=work/'source';fingerprint=source_snapshot(snapshot)
        commit=git('rev-parse','HEAD')
        dirty_files=(git('status','--porcelain','--untracked-files=all') or '').splitlines()
        print('Quality gate: '+args.quality_mode,flush=True)
        quality=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'check_quality.ps1'),
                                '-Mode',args.quality_mode,'-NoOpen'])
        if quality.returncode:raise RuntimeError('Quality gate failed; existing distribution was preserved.')
        if source_snapshot(work/'after-quality')!=fingerprint:
            raise RuntimeError('Source changed during quality checks; retry with a stable working tree.')
        build=work/'compiled';build.mkdir()
        import psutil
        available=psutil.virtual_memory().available
        jobs=max(1,min(3,os.cpu_count() or 1,int((available-1.5*1024**3)/(.75*1024**3))))
        command=[args.python,'-m','nuitka','--mode=standalone','--enable-plugin=tk-inter','--zig',
            '--include-package=pandas.plotting._matplotlib',
            '--noinclude-custom-mode=pandas:bytecode','--noinclude-custom-mode=matplotlib:bytecode',
            '--noinclude-custom-mode=tksheet:bytecode','--noinclude-custom-mode=pyparsing:bytecode',
            '--assume-yes-for-downloads','--windows-console-mode=disable','--include-package=app','--nofollow-import-to=app.tests',
            '--include-package-data=customtkinter','--include-data-dir='+str(snapshot/'images')+'=images',
            '--include-data-dir='+str(snapshot/'locales')+'=locales',
            '--include-data-dir='+str(snapshot/'files/audio/Sounds')+'=files/audio/Sounds',
            '--windows-icon-from-ico='+str(snapshot/'images/vocabpro_logo_v2.ico'),
            '--product-name=VocabPro','--file-description=VocabPro','--product-version='+__version__,
            '--file-version='+__version__,'--output-filename=VocabPro.exe','--output-dir='+str(build),
            '--report='+str(work/'compilation.xml'),'--jobs='+str(jobs),str(snapshot/'start.py')]
        print('Nuitka standalone build. Log: '+str(work/'build.log'),flush=True)
        with (work/'build.log').open('w',encoding='utf-8') as log:
            process=subprocess.Popen(command,cwd=snapshot,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                     text=True,encoding='utf-8',errors='replace',
                                     creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            for line in process.stdout:
                log.write(line);log.flush()
                if not line.startswith('Nuitka-Options:'):print(line.rstrip(),flush=True)
            returncode=process.wait()
        if returncode:raise RuntimeError('Build failed. Previous release unchanged. See '+str(work/'build.log'))
        candidate=build/'start.dist'
        if not (candidate/'VocabPro.exe').is_file():raise RuntimeError('Build produced no VocabPro.exe.')
        # No user data may enter the replaceable asset directory.
        check_assets(candidate)
        print('Offline Python and EXE GUI verification…',flush=True)
        python_metrics=probe(args.python,work/'python-probe',python=True)
        exe_metrics=probe(candidate/'VocabPro.exe',work/'exe-probe')
        old_commit=previous.get('commit')
        log_args=['log','-10','--format=%h %s',commit] if commit else []
        if old_commit and commit:log_args=['log',old_commit+'..'+commit,'--format=%h %s']
        manifest={'application':'VocabPro','version':__version__,'build':identity,'commit':commit,
            'source_fingerprint':fingerprint,'dirty_files':dirty_files,
            'git_changes':(git(*log_args) or '').splitlines() if log_args else [],'python':python_metrics,'exe':exe_metrics,
            'data_directory':'../VocabPro_data/files','bytes':sum(p.stat().st_size for p in candidate.rglob('*') if p.is_file())}
        write_json(candidate/'release.json',manifest)
        (candidate/'CHANGELOG.txt').write_text('VocabPro '+__version__+' / '+identity+'\n\nGit commits:\n'+
            '\n'.join(manifest['git_changes'])+'\n\nWorking tree status at build time (not all paths are distribution assets):\n'+
            '\n'.join(manifest['dirty_files'])+'\n',encoding='utf-8')
        if not data.exists():
            seed=work/'initial-data';seed.mkdir()
            shutil.copytree(ROOT/'files',seed/'files')
            # Never seed from a moving/partially written source tree.
            for p in (ROOT/'files').rglob('*'):
                if p.is_file() and hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256((seed/'files'/p.relative_to(ROOT/'files')).read_bytes()).digest():
                    raise RuntimeError('Source data changed while copying; retry after closing Python VocabPro.')
            seed.rename(data)
        if not (data/'files/settings.csv').is_file():raise RuntimeError('External user data has no settings.csv; refusing to overwrite it.')
        assert_closed(target)
        deploy(candidate,target,archives/identity,lambda path:probe(path/'VocabPro.exe',work/'deployed-probe'))
        write_json(work/'result.json',manifest)
        print('Released '+str(target/'VocabPro.exe'),flush=True)
        print(json.dumps({'version':__version__,'MiB':manifest['bytes']/1048576,'python':python_metrics,'exe':exe_metrics},indent=2),flush=True)


if __name__=='__main__':main()

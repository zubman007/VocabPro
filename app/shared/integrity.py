"""Read-only integrity rules, bounded startup checks and validated write boundaries."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime, date as calendar_date
from threading import RLock
from time import perf_counter
from contextlib import contextmanager
from concurrent.futures import CancelledError
import csv
import io
import json
import logging
import pandas as pd
from app.shared.messages import UserMessageError

_blocked = {}
_state_lock = RLock()


def protect(report, folder, checked=()):
    """Remember confirmed damage without changing a byte of the user's files."""
    if not report.completed:
        return
    damaged={Path(folder)/finding.file for finding in report.findings if finding.severity=='Critical' and finding.file}
    signatures={}
    for path in damaged:
        try:
            if path.is_file():signatures[path.resolve()]=(_signature(path),report.mode)
        except OSError:pass
    verified={path.resolve() for path in checked}-set(signatures)
    with _state_lock:
        for path in verified:
            previous=_blocked.get(path)
            # A header-only check cannot clear damage found by a full audit.
            # A completed full audit can clear a resolved read/access problem.
            if previous is not None and (report.mode=='full' or previous[1]=='quick'):
                _blocked.pop(path,None)
        _blocked.update(signatures)


def check_writable(path):
    path = Path(path)
    with _state_lock:
        entry = _blocked.get(path.resolve())
    if entry is not None and path.exists() and _signature(path) == entry[0]:
        raise UserMessageError('Integrity write rejected')


@dataclass(frozen=True)
class Finding:
    severity: str
    module: str
    file: str
    code: str
    row: int | None = None


@dataclass
class Report:
    findings: list = field(default_factory=list)
    files: int = 0
    records: int = 0
    completed: bool = False
    finished: str = ''
    mode: str = 'full'
    elapsed: float = 0

    def export(self, translate=None):
        # Codes, basenames and row numbers only: never values, paths or exception text.
        if translate is None:
            from app.shared.translations import translate as translator
            translate=lambda key:translator(key,'English')
        data=asdict(self)
        data['version']=1
        for finding in data['findings']:
            finding['description']=translate(finding['code'])
            finding['recommendation']=translate('Integrity advice')
        data['limitations']=['Backups and operating-system credentials are not read.',
            'Audio presence is checked, but audio contents are not decoded.',
            'Historical per-person results are never inferred from whole-round history.']
        return json.dumps(data,ensure_ascii=False,indent=2)


def kind(path):
    name=Path(path).name
    if name=='settings.csv':return 'Settings'
    if name.endswith('_con_persons.json'):return 'Persons'
    for suffix,area in (('_con_categories.csv','Categories'),('_records.csv','Records'),
                        ('_synonyms.csv','Synonyms'),('_tags.csv','Tags'),('_gra_ex.csv','Theory'),
                        ('_voc.csv','Vocabulary'),('_gra.csv','Grammar'),('_con.csv','Conjugation')):
        if name.endswith(suffix):return area
    return 'Other'


def columns_required(path):
    area=kind(path)
    return {'Settings':{'Name','Type','Value'},'Vocabulary':{'ID','Repetition','Next repetition'},
        'Grammar':{'question_id','prompt','anchor',*(f'option_{i}' for i in range(1,5))},
        'Conjugation':{'ID','R','LR'},'Tags':{'ID'},'Synonyms':{'ID 1','ID 2','Date'},
        'Records':{'best_streak'},'Theory':{'category'},'Categories':{'ID','Name','Description'}}.get(area,set())


def frame_findings(frame,path, *, references=None,complete=True):
    path=Path(path);area=kind(path);issues=[]
    def issue(code,row=None,severity='Critical'):
        issues.append(Finding(severity,area,path.name,code,row))
    if area=='Theory':
        frame=frame.rename(columns=lambda value:str(value).strip().casefold())
    if not frame.columns.is_unique or not columns_required(path)<=set(frame.columns):
        issue('Integrity structure');return issues
    values=frame.fillna('').astype(str)
    if complete and area in ('Vocabulary','Conjugation'):
        suffix='_voc' if area=='Vocabulary' else '_con'
        languages=path.stem.removesuffix(suffix).split('_')
        required=set(languages)|({'Audio','Description','Example'} if area=='Vocabulary' else {'Description'})
        if len(languages)!=2 or not required<=set(values):issue('Integrity structure')
    identifier='Name' if area=='Settings' else 'question_id' if area=='Grammar' else 'ID'
    if identifier in values:
        # Grammar normalizes IDs on load. Conjugation/category string IDs are
        # opaque; normalizing them here would merge otherwise distinct records.
        ids=values[identifier].str.strip() if area=='Grammar' else values[identifier]
        for position,bad in enumerate(ids.str.strip().eq('')|ids.duplicated(keep=False),2):
            if bad:issue('Integrity identifier',position)
    try:
        if area=='Settings':
            from app.preferences.data import RuntimePreferences,validate_preferences
            if complete:RuntimePreferences.from_frame(values)
            else:validate_preferences(values,{})
            from app.repositories.grammar_filters import _filters
            for setting in ('Saved grammar category filters','Saved conjugation category filters'):
                if setting in set(values.Name):
                    try:_filters(values,setting)
                    except (ValueError,TypeError):
                        position=next(i for i,name in enumerate(values.Name,2) if name==setting)
                        issue('Integrity values',position,'Warning')
        elif area=='Categories':
            from app.conjugation.categories import validate_catalog
            validate_catalog(values)
        elif area=='Tags':
            from app.repositories.tags import validate_catalog
            source,target=path.stem.removesuffix('_tags').split('_',1)
            validate_catalog(values,source,target)
        elif area=='Records':
            if list(values) not in (['best_streak'],['best_streak','best_correct']) or len(values)>1:issue('Integrity record')
            for column in values:
                for value in values[column]:
                    if column=='best_correct' and not value:continue
                    if not value.isascii() or not value.isdigit():issue('Integrity record')
        elif area=='Synonyms':
            if list(values)!=['ID 1','ID 2','Date']:issue('Integrity structure')
            pairs=set()
            words=None if references is None else references.get(path.with_name(path.stem.removesuffix('_synonyms')+'_voc.csv'))
            word_ids=set(words.ID.astype(int)) if words is not None and 'ID' in words else set()
            if words is not None and len(word_ids)!=len(words):issue('Integrity reference')
            for row,(a,b,date) in enumerate(values[['ID 1','ID 2','Date']].itertuples(index=False,name=None),2):
                pair=tuple(sorted((int(a),int(b))))
                calendar_date.fromisoformat(date)
                if pair[0]==pair[1] or pair in pairs:issue('Integrity relation',row)
                pairs.add(pair)
                if references is not None:
                    if not set(pair)<=word_ids:issue('Integrity reference',row)
        elif area=='Conjugation' and 'Person history' in values:
            from app.conjugation.history import decode_history
            for value in values['Person history']:decode_history(value)
    except (ValueError,TypeError,KeyError,OverflowError):issue('Integrity values')
    if area=='Vocabulary':
        numbers=set()
        for row,value in enumerate(values.ID,2):
            try:
                number=int(value)
                if number in numbers:issue('Integrity identifier',row)
                numbers.add(number)
            except ValueError:issue('Integrity values',row)
    if area=='Grammar':
        required=['prompt','anchor',*(f'option_{i}' for i in range(1,5))]
        for row,record in enumerate(values.to_dict('records'),2):
            if any(not record[key].strip() for key in required):issue('Integrity values',row)
            if len({record[key].strip().casefold() for key in required[2:]})!=4:
                issue('Integrity alternatives',row,'Warning')
    for history in ('R','Repetition'):
        if history in values:
            for row,value in enumerate(values[history],2):
                if set(value)-set('SF'):issue('Integrity legacy history',row,'Warning')
    for date in ('LR','Next repetition','Created'):
        if date in values:
            invalid=values[date].ne('') & pd.to_datetime(values[date],format='mixed',errors='coerce').isna()
            for row,bad in enumerate(invalid,2):
                if bad:issue('Integrity date',row,'Warning')
    if references is not None and area=='Conjugation':
        catalog=references.get(path.with_name(path.stem+'_categories.csv'))
        if 'Category' in values:
            assigned=set(values.Category)-{''}
            if assigned and (catalog is None or 'ID' not in catalog or not assigned <= set(catalog.ID)):
                issue('Integrity reference')
    if references is not None and area=='Vocabulary' and 'Tags' in values:
        catalog=references.get(path.with_name(path.stem.removesuffix('_voc')+'_tags.csv'))
        if catalog is not None:
            try:
                from app.repositories.tags import encode_tags,validate_catalog
                source,target=path.stem.removesuffix('_voc').split('_',1)
                catalog=validate_catalog(catalog,source,target)
                encode_tags(values,catalog,source,target,maximum=100000)
            except (ValueError,KeyError,AttributeError):issue('Integrity reference')
        elif values.Tags.str.strip().ne('').any():issue('Integrity reference',severity='Warning')
    if area=='Theory':
        categories=values['category'].str.strip()
        if categories.duplicated().any():issue('Integrity theory duplicate',severity='Warning')
    if values.empty:issue('Integrity empty',severity='Info')
    return issues


def _signature(path):
    info=path.stat();return info.st_mtime_ns,info.st_size,info.st_ctime_ns


def _paths(folder):
    return sorted(p for p in Path(folder).iterdir() if p.suffix.lower()=='.csv' or p.name.endswith('_con_persons.json'))


@contextmanager
def _read_lock(path, cancelled):
    from app.shared.storage import destination_lock
    lock=destination_lock(path)
    while not lock.acquire(timeout=.05):
        if cancelled is not None and cancelled.is_set():raise CancelledError
    try:
        if cancelled is not None and cancelled.is_set():raise CancelledError
        yield
    finally:lock.release()


def _relationships(frames, folder, cancelled):
    """Optional legacy assets are warnings; disabled courses keep their data."""
    issues=[]
    settings=frames.get(folder/'settings.csv')
    if settings is not None:
        try:
            from app.preferences.data import RuntimePreferences
            from app.repositories.course_files import course_assets
            preferences=RuntimePreferences.from_frame(settings)
            for course in preferences.study_courses:
                if not course.enabled:continue
                assets=course_assets(folder,preferences.learned_by,course.target)
                names=['vocabulary','tags','synonyms']
                if course.grammar_enabled:names+=['grammar','theory']
                if course.conjugation_enabled:names+=['conjugation']
                for name in names:
                    path=assets[name][0]
                    if not path.exists():issues.append(Finding('Warning',kind(path),path.name,'Integrity missing'))
        except (ValueError,KeyError):pass  # Settings already have their own finding.
    for path,frame in frames.items():
        if cancelled is not None and cancelled.is_set():break
        area=kind(path)
        if area=='Records':
            parent=path.with_name(path.stem.removesuffix('_records')+'.csv')
            if not parent.exists():issues.append(Finding('Warning',area,path.name,'Integrity orphan'))
        if area=='Theory':
            from app.grammar.theory_data import category_key
            questions=frames.get(path.with_name(path.stem.removesuffix('_gra_ex').rsplit('_',1)[-1]+'_gra.csv'))
            if questions is not None:
                categories=questions.get('category',questions.get('Category',pd.Series(dtype=str)))
                known=set(categories.map(category_key))
                column=next((c for c in frame if c.casefold()=='category'),None)
                if column:
                    for row,value in enumerate(frame[column],2):
                        if category_key(value) and category_key(value) not in known:
                            issues.append(Finding('Warning',area,path.name,'Integrity orphan',row))
        if area=='Vocabulary' and {'ID','Audio'}<=set(frame):
            directory=folder/'audio'/path.stem.removesuffix('_voc')
            for row,(identifier,flag) in enumerate(frame[['ID','Audio']].itertuples(index=False,name=None),2):
                if cancelled is not None and cancelled.is_set():break
                # Only numeric IDs can identify audio files; never follow user paths.
                if str(identifier).lstrip('-').isdigit() and ('Automatic' in flag or flag=='Own'):
                    if not any((directory/f'{identifier}.{ext}').is_file() for ext in ('mp3','wav')):
                        issues.append(Finding('Warning',area,path.name,'Integrity audio',row))
    return issues


def audit(folder, *, quick=False, cancelled=None, progress=None):
    started=perf_counter()
    report=Report(mode='quick' if quick else 'full');frames={};signatures={};folder=Path(folder)
    if not (folder/'settings.csv').exists():
        report.findings.append(Finding('Critical','Settings','settings.csv','Integrity missing'))
    if not folder.exists():return report
    try:paths=_paths(folder)
    except OSError:
        report.findings.append(Finding('Critical','Settings','','Integrity unreadable'));return report
    for offset,path in enumerate(paths):
        if cancelled is not None and cancelled.is_set():return report
        area=kind(path)
        if progress:progress((offset,area,report.records),len(paths))
        if area=='Other':
            report.findings.append(Finding('Info',area,path.name,'Integrity unknown'))
            continue
        if path.is_symlink():
            report.findings.append(Finding('Warning',area,path.name,'Integrity link'));continue
        try:
            with _read_lock(path,cancelled):
                signatures[path]=_signature(path)
                if area=='Persons':
                    from app.conjugation.persons import decode_configuration
                    if quick and path.stat().st_size>65536:
                        report.findings.append(Finding('Warning',area,path.name,'Integrity deferred'));continue
                    decode_configuration(path.read_text(encoding='utf-8-sig'),path.stem.removesuffix('_con_persons'))
                else:
                    with path.open(encoding='utf-8-sig',newline='') as stream:
                        if quick:
                            header=next(csv.reader(io.StringIO(stream.read(65536)),delimiter=';',strict=True),[])
                            checked=[cell.strip().casefold() for cell in header] if area=='Theory' else header
                            if not header or len(set(checked))!=len(checked) or not columns_required(path)<=set(checked):
                                report.findings.append(Finding('Critical',area,path.name,'Integrity structure'))
                            if area not in ('Settings','Records'):
                                report.files+=1;continue
                            if path.stat().st_size>1048576:
                                report.findings.append(Finding('Warning',area,path.name,'Integrity deferred'))
                                report.files+=1;continue
                            stream.seek(0)
                        reader=csv.reader(stream,delimiter=';',strict=True)
                        header=next(reader,[])
                        if not header or len(header)!=len(set(header)):raise ValueError
                        rows=[]
                        for row in reader:
                            if cancelled is not None and cancelled.is_set():return report
                            if not row:continue
                            if len(row)>len(header):raise ValueError
                            if area=='Tags' and len(row)!=len(header):raise ValueError
                            if any(row) or area not in ('Grammar','Theory'):
                                rows.append(row+['']*(len(header)-len(row)))
                            if progress and len(rows)%1000==0:
                                progress((offset,area,report.records+len(rows)),len(paths))
                        frames[path]=pd.DataFrame(rows,columns=header)
                        report.records+=len(rows)
                if signatures[path]!=_signature(path):raise OSError
            report.files+=1
        except CancelledError:return report
        except (OSError,ValueError,UnicodeError,csv.Error,KeyError):
            report.findings.append(Finding('Critical',area,path.name,'Integrity unreadable'))
    for path,frame in frames.items():
        if cancelled is not None and cancelled.is_set():return report
        report.findings.extend(frame_findings(frame,path,references=None if quick else frames))
    if not quick:
        report.findings.extend(_relationships(frames,folder,cancelled))
    if cancelled is not None and cancelled.is_set():return report
    try:
        if paths!=_paths(folder) or any(_signature(p)!=sig for p,sig in signatures.items()):
            report.findings=[Finding('Warning','Settings','','Integrity changed')]
            return report
    except OSError:
        report.findings=[Finding('Warning','Settings','','Integrity changed')];return report
    if progress:progress((len(paths),'',report.records),len(paths))
    report.findings.sort(key=lambda item:(item.module,('Critical','Warning','Info').index(item.severity),item.file,item.row or 0))
    report.completed=True;report.finished=datetime.now().isoformat(timespec='seconds')
    report.elapsed=perf_counter()-started
    protect(report,folder,signatures)
    return report


def validate_write(frame,path):
    check_writable(path)
    if not isinstance(frame,pd.DataFrame) or kind(path)=='Other':return
    # Existing repositories keep their domain-specific validation. This common
    # boundary also protects direct CSV writers and future import/restore paths.
    references={}
    path=Path(path)
    # A failed reader must never turn an existing damaged document into defaults.
    # Header inspection is bounded and does not repeat a full data scan on save.
    if path.exists():
        try:
            with path.open(encoding='utf-8-sig',newline='') as stream:
                header=next(csv.reader(io.StringIO(stream.read(65536)),delimiter=';',strict=True),[])
        except (csv.Error,UnicodeError):
            logging.getLogger('vocabpro.integrity').warning('Unreadable %s header',kind(path))
            raise UserMessageError('Integrity write rejected') from None
        checked=[cell.strip().casefold() for cell in header] if kind(path)=='Theory' else header
        if not checked or len(checked)!=len(set(checked)) or not columns_required(path)<=set(checked):
            raise UserMessageError('Integrity write rejected')
    dependent=None
    if kind(path)=='Synonyms':dependent=path.with_name(path.stem.removesuffix('_synonyms')+'_voc.csv')
    elif kind(path)=='Vocabulary':dependent=path.with_name(path.stem.removesuffix('_voc')+'_tags.csv')
    elif kind(path)=='Conjugation' and 'Category' in frame:dependent=path.with_name(path.stem+'_categories.csv')
    if dependent is not None and dependent.exists():
        references[dependent]=pd.read_csv(dependent,sep=';',dtype=str,keep_default_na=False)
    issues=frame_findings(frame,path,references=references,complete=False)
    optional=[item for item in issues if kind(path)=='Settings' and item.severity=='Warning' and item.code=='Integrity values']
    if optional:
        previous=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False) if path.exists() else pd.DataFrame(columns=['Name','Value'])
        before=dict(zip(previous.Name,previous.Value))
        for item in optional:
            row=frame.iloc[item.row-2]
            if before.get(str(row.Name))!=str(row.Value):
                issues.append(Finding('Critical','Settings',path.name,item.code,item.row))
    # Preserve opaque historical values, but prevent writers from introducing
    # NEW broken dates/history symbols. Read the old rows only for this rare case.
    suspicious=[item for item in issues if item.code in ('Integrity legacy history','Integrity date')]
    if suspicious:
        previous=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False) if path.exists() else pd.DataFrame()
        identifier='question_id' if kind(path)=='Grammar' else 'ID'
        before={str(row[identifier]):row for row in previous.to_dict('records')} if identifier in previous else {}
        for item in suspicious:
            record=frame.iloc[item.row-2].fillna('').astype(str)
            original=before.get(record.get(identifier,''),{})
            fields=('R','Repetition') if item.code=='Integrity legacy history' else ('LR','Next repetition','Created')
            for column in fields:
                value=record.get(column,'')
                invalid=(bool(set(value)-set('SF')) if item.code=='Integrity legacy history'
                         else bool(value) and pd.isna(pd.to_datetime(value,format='mixed',errors='coerce')))
                if item.code=='Integrity legacy history' and isinstance(original.get(column),str):
                    old=original[column]
                    if value.startswith(old) and not set(value[len(old):])-set('SF'):
                        continue  # New answers may extend an opaque legacy prefix.
                if invalid and original.get(column)!=value:
                    issues.append(Finding('Critical',kind(path),path.name,item.code,item.row))
    if any(item.severity=='Critical' for item in issues):
        details=[(item.code,item.row) for item in issues if item.severity=='Critical'][:5]
        logging.getLogger('vocabpro.integrity').warning('Rejected invalid %s document: %s',kind(path),details)
        raise UserMessageError('Integrity write rejected')

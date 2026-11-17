"""Safe artifacts and deterministic input selection for the quality harness."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def atomic(path, text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temporary=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8',newline='') as stream:
            stream.write(text);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)


def write_json(path, value):
    atomic(path,json.dumps(sanitize(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def sanitize(value):
    if isinstance(value,str):return redact(value)
    if isinstance(value,dict):
        return {key:('[redacted]' if re.fullmatch(r'password|passwd|secret|token|api[_ -]?key|authorization|access_token|refresh_token',str(key),re.I) else sanitize(item)) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [sanitize(item) for item in value]
    return value


def redact(text):
    text=re.sub(r'(?i)(https?://)[^\s/@:]+:[^\s/@]+@',r'\1[redacted]@',str(text))
    text=re.sub(r'(?i)((?:password|passwd|token|api[_ -]?key|secret|authorization)\s*[=:]\s*)([\"\'])(.*?)\2',lambda match:match[1]+match[2]+'[redacted]'+match[2],text)
    text=re.sub(r'(?i)(authorization\s*[:=]\s*)(?:Bearer|Basic)\s+\S+',r'\1[redacted]',text)
    text=re.sub(r'(?i)((?:password|passwd|token|api[_ -]?key|secret|authorization)\s*[=:]\s*[\"\']?)[^\s\"\',;]+',r'\1[redacted]',text)
    return re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b','[redacted]',text)


def sources(root):
    root=Path(root)
    paths=[root/'start.py',root/'check_quality.ps1']
    for folder in ('app','tools/quality','locales'):
        paths.extend(p for p in (root/folder).rglob('*')
            if p.suffix.lower() in ('.py','.ps1','.json','.toml') and '__pycache__' not in p.parts and not p.is_symlink())
    return sorted(p for p in paths if p.is_file())


def digest(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):value.update(chunk)
    return value.hexdigest()


def protected_snapshot(root,errors=None):
    root=Path(root)
    paths=[]
    for folder in ('app','files','locales','images','docs'):
        paths.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink())
    paths.extend(root/name for name in ('start.py','sandbox.py','README.md','requirements.txt','requirements.lock.txt') if (root/name).exists())
    result={}
    for path in paths:
        name=str(path.relative_to(root))
        try:result[name]=digest(path)
        except OSError as error:
            if errors is None:raise
            errors[name]=type(error).__name__
    return result


def regressions(current, previous):
    if not previous:return []
    found=[]
    old_coverage=previous.get('coverage_percent');new_coverage=current.get('coverage_percent')
    if old_coverage is not None and new_coverage is not None and old_coverage-new_coverage>1:
        found.append({'metric':'coverage_percent','before':old_coverage,'after':new_coverage,'reason':'Coverage decreased by more than one percentage point.'})
    for key,value in current.get('performance',{}).items():
        before=previous.get('performance',{}).get(key)
        if isinstance(value,(int,float)) and isinstance(before,(int,float)) and before>0 and value>before*1.25:
            found.append({'metric':key,'before':before,'after':value,'reason':'More than 25% slower/larger; repeat on an idle machine before concluding a regression.'})
    for key in ('failed','gui_failed','lint_findings','security_findings','high_complexity_functions','duplicate_groups'):
        before=previous.get(key);after=current.get(key)
        if isinstance(before,(int,float)) and isinstance(after,(int,float)) and after>before:
            found.append({'metric':key,'before':before,'after':after,'reason':'Finding/failure count increased. Review code and test-environment changes.'})
    return found

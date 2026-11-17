"""Static evidence and conservative review candidates; never automatic fixes."""
import ast
from collections import Counter,defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import tomllib
from tools.quality.common import sources


def fingerprint(node):
    return hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()


def is_docstring(node):
    return isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str)


class PythonEvidence(ast.NodeVisitor):
    def __init__(self,tree,path):
        self.tree,self.path=tree,path
        self.parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        self.classes=0;self.functions=[];self.references=set();self.strings=set()
        self.imports=[];self.secrets=[];self.test_review=[];self.duplicates=defaultdict(list)

    def visit_Name(self,node):
        if isinstance(node.ctx,ast.Load):self.references.add(node.id)

    def visit_Attribute(self,node):
        self.references.add(node.attr);self.generic_visit(node)

    def visit_Constant(self,node):
        if not isinstance(node.value,str):return
        self.strings.add(node.value)
        if re.search(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b',node.value):
            self.secrets.append({'file':self.path,'line':node.lineno,'name':'token-like literal',
                'reason':'Known credential prefix; value omitted. May be an intentional test fixture.'})

    def visit_ClassDef(self,node):
        self.classes+=1;self.generic_visit(node)

    def visit_Import(self,node):
        self.imports.extend({'name':a.name,'eager':self.parents.get(node) is self.tree} for a in node.names)

    def visit_ImportFrom(self,node):
        base=node.module or ''
        if node.level:
            package=self.path.removesuffix('.py').replace('/','.').split('.')[:-1]
            base='.'.join(package[:len(package)-node.level+1]+([base] if base else []))
        self.imports.extend({'name':name,'eager':self.parents.get(node) is self.tree}
            for name in [base,*[base+'.'+a.name for a in node.names]])

    def visit_FunctionDef(self,node):
        item={'file':self.path,'name':node.name,'line':node.lineno,'end_line':node.end_lineno,
            'lines':node.end_lineno-node.lineno+1,'method':isinstance(self.parents.get(node),ast.ClassDef)}
        self.functions.append(item)
        normalized=copy.deepcopy(node);normalized.name='_function'
        if normalized.body and is_docstring(normalized.body[0]):normalized.body.pop(0)
        if item['lines']>=8 and len(normalized.body)>=3:self.duplicates[fingerprint(normalized)].append(item)
        if node.name.startswith('test_'):
            calls=[n.func for n in ast.walk(node) if isinstance(n,ast.Call)]
            if not any(isinstance(call,ast.Attribute) and (call.attr.startswith('assert') or call.attr in ('fail','check','invoke')) for call in calls):
                self.test_review.append({**item,'reason':'No direct unittest assertion detected. Helper/context-manager assertions may make this valid; manual review required.'})
        self.generic_visit(node)

    visit_AsyncFunctionDef=visit_FunctionDef

    def sensitive_assignment(self,target,value,line):
        name=target.id if isinstance(target,ast.Name) else target.attr if isinstance(target,ast.Attribute) else ''
        if any(word in name.casefold() for word in ('password','token','api_key','secret')) and isinstance(value,ast.Constant) and isinstance(value.value,str) and len(value.value)>12:
            self.secrets.append({'file':self.path,'line':line,'name':name,
                'reason':'Literal assigned to sensitive-looking name; value omitted. Test fixtures may be intentional.'})

    def visit_Assign(self,node):
        for target in node.targets:self.sensitive_assignment(target,node.value,node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self,node):
        self.sensitive_assignment(node.target,node.value,node.lineno);self.generic_visit(node)


def duplicate_blocks(tree,path):
    blocks=defaultdict(list)
    for node in ast.walk(tree):
        for field in ('body','orelse','finalbody'):
            body=getattr(node,field,None)
            if not isinstance(body,list):continue
            for index in range(max(0,len(body)-3)):
                chunk=body[index:index+4]
                if any(not isinstance(n,ast.stmt) or isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom)) for n in chunk):continue
                span=chunk[-1].end_lineno-chunk[0].lineno+1
                if span<6:continue
                blocks[fingerprint(ast.Module(body=chunk,type_ignores=[]))].append(
                    {'file':path,'line':chunk[0].lineno,'end_line':chunk[-1].end_lineno,'lines':span})
    return blocks


def import_cycles(imports,modules):
    graph={name:set() for name in modules}
    for file,links in imports.items():
        name=file.removesuffix('.py').replace('/','.')
        graph[name].update(link['name'] for link in links if link['eager'] and link['name'] in modules)
    seen=set();active=[];cycles=[]
    def visit(name):
        if name in active:
            cycle=active[active.index(name):]+[name]
            if cycle not in cycles:cycles.append(cycle)
            return
        if name in seen:return
        seen.add(name);active.append(name)
        for dependency in sorted(graph[name]):visit(dependency)
        active.pop()
    for name in sorted(graph):visit(name)
    return cycles


def unique_json(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('Duplicate JSON key')
        result[key]=value
    return result


def file_record(path,root,text):
    parts=path.relative_to(root).parts
    return {'file':path.relative_to(root).as_posix(),
        'language':{'.py':'Python','.ps1':'PowerShell','.json':'JSON','.toml':'TOML'}[path.suffix],
        'module':'/'.join(parts[:2]) if len(parts)>2 else parts[0] if len(parts)>1 else 'root',
        'lines':len(text.splitlines()),'sloc':sum(bool(line.strip()) for line in text.splitlines()),
        'classes':0,'functions':0,'methods':0}


def inspect_sources(root):
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    from radon.raw import analyze
    root=Path(root);files=[];functions=[];references=set();strings=set();imports={}
    duplicates=defaultdict(list);blocks=defaultdict(list);secrets=[];test_candidates=[];errors=[]
    paths=sources(root)
    for path in paths:
        text=path.read_text(encoding='utf-8-sig');record=file_record(path,root,text);relative=record['file'];files.append(record)
        try:
            if path.suffix=='.json':json.loads(text,object_pairs_hook=unique_json)
            if path.suffix=='.toml':tomllib.loads(text)
            if path.suffix!='.py':continue
            tree=ast.parse(text,filename=relative)
        except (SyntaxError,ValueError) as error:
            errors.append({'file':relative,'line':getattr(error,'lineno',None),'message':type(error).__name__});continue
        evidence=PythonEvidence(tree,relative);evidence.visit(tree)
        raw=analyze(text)
        record.update(sloc=raw.sloc,comments=raw.comments,maintainability=round(mi_visit(text,True),2),classes=evidence.classes,
            functions=sum(not f['method'] for f in evidence.functions),methods=sum(f['method'] for f in evidence.functions))
        functions.extend(evidence.functions);references.update(evidence.references);strings.update(evidence.strings)
        imports[relative]=evidence.imports;secrets.extend(evidence.secrets);test_candidates.extend(evidence.test_review)
        for key,items in evidence.duplicates.items():duplicates[key].extend(items)
        for key,items in duplicate_blocks(tree,relative).items():blocks[key].extend(items)
        complexities=[]
        for block in cc_visit(text):
            complexities.append({'name':block.name,'line':block.lineno,'complexity':block.complexity})
            complexities.extend({'name':block.name+'.'+m.name,'line':m.lineno,'complexity':m.complexity} for m in getattr(block,'methods',[]))
        record['complexity']=sorted(complexities,key=lambda item:item['complexity'],reverse=True)
    languages=defaultdict(Counter);modules=defaultdict(Counter)
    for item in files:
        for group,key in ((languages,item['language']),(modules,item['module'])):
            group[key].update({name:item.get(name,0) for name in ('lines','sloc','classes','functions','methods')});group[key]['files']+=1
    module_names={p.relative_to(root).with_suffix('').as_posix().replace('/','.') for p in paths if p.suffix=='.py'}
    return {'status':'failed' if errors else 'passed','files':files,
        'totals':{'files':len(files),**{key:sum(f.get(key,0) for f in files) for key in ('lines','sloc','classes','functions','methods')}},
        'languages':dict(languages),'modules':dict(modules),'functions':functions,'syntax_errors':errors,
        'unused_candidates':[{**item,'reason':'No static name/attribute/string reference; dynamic use and callbacks may still make this live code.'}
            for item in functions if item['name'] not in references|strings and not item['name'].startswith(('test_','__'))],
        'duplicates':[items for items in duplicates.values() if len(items)>1],
        'block_duplicates':[items for items in blocks.values() if len(items)>1],
        'test_review':test_candidates,'secret_candidates':secrets,'eager_import_cycles':import_cycles(imports,module_names),'imports':imports}

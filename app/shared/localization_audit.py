"""Read-only catalog/source audit: python -B -m app.shared.localization_audit.

Static findings are conservative. Unreferenced entries are review candidates,
not proof of dead code; data-driven labels and external course content differ.
"""
import argparse
import ast
from collections import Counter
import csv
import json
from pathlib import Path
from string import Formatter
import unicodedata
import re
from app.paths import ROOT_DIR
from app.shared.translations import LANGUAGE_CODES, _unique_object

TRANSLATORS = {'T', 'translate', 'tr'}
SINKS = {'text', 'placeholder_text', 'title', 'message'}
POSITIONAL_SINKS = {'title', 'set_xlabel', 'set_ylabel', 'set_title', 'set_label', 'set_tooltip', 'set_content'}
# Technical identifiers/symbols, not English prose. Keep this list explicit.
UI_LITERALS = {'ID', 'VocabPro'}
MESSAGE_WRAPPERS = {'can_leave', 'read_document', 'commit_document'}


def format_contract(text):
    """Compare fields, conversions and format specs; allow translator reordering."""
    fields = Counter()
    for _, field, spec, conversion in Formatter().parse(text):
        if field is not None:
            if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', field) or conversion not in (None, 's', 'r', 'a'):
                raise ValueError('Use named fields and supported conversions')
            if '{' not in spec:
                sample = 7 if field in ('count', 'row', 'word_id') or spec.endswith(('d', 'f', '%')) else 'sample'
                if conversion:
                    sample = Formatter().convert_field(sample, conversion)
                format(sample, spec)
            fields[(field, conversion, spec)] += 1
            if spec:
                fields.update(format_contract(spec))
    return fields


def catalog_findings(catalogs):
    issues = []
    english = catalogs.get('en', {})
    for code, catalog in catalogs.items():
        for key in sorted(set(english) - set(catalog)):
            issues.append(dict(kind='missing', language=code, key=key))
        for key in sorted(set(catalog) - set(english)):
            issues.append(dict(kind='extra', language=code, key=key))
        for key, text in catalog.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(text, str) or not text.strip():
                issues.append(dict(kind='invalid', language=code, key=key))
                continue
            if unicodedata.normalize('NFC', text) != text or '\ufffd' in text:
                issues.append(dict(kind='encoding', language=code, key=key))
            try:
                contract = format_contract(text)
                expected = format_contract(english.get(key, text))
                if code == 'en' and ('{' in key or '}' in key) and contract != format_contract(key):
                    issues.append(dict(kind='source_placeholder', language=code, key=key))
                if contract != expected:
                    issues.append(dict(kind='placeholder', language=code, key=key))
            except ValueError as error:
                issues.append(dict(kind='format', language=code, key=key, detail=str(error)))
    return issues


def _name(call):
    return getattr(call.func, 'attr', getattr(call.func, 'id', ''))


def literal_fragments(node):
    """Only surface literals, excluding translated expressions and variables."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        return [part.value for part in node.values if isinstance(part, ast.Constant) and isinstance(part.value, str)]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return literal_fragments(node.left) + literal_fragments(node.right)
    if isinstance(node, ast.IfExp):
        return literal_fragments(node.body) + literal_fragments(node.orelse)
    if isinstance(node, ast.Call) and _name(node) == 'format' and isinstance(node.func, ast.Attribute):
        return literal_fragments(node.func.value)
    return []


def source_findings(source, filename, keys):
    tree = ast.parse(source, filename=filename)
    missing, hardcoded, errors = [], [], []
    literals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Subscript)
                and isinstance(target.slice, ast.Constant) and target.slice.value == 'Subject' for target in node.targets):
            for fragment in literal_fragments(node.value):
                if any(char.isalpha() for char in fragment) and fragment.strip() not in UI_LITERALS:
                    hardcoded.append(dict(file=filename, line=node.lineno, text=fragment))
        if not isinstance(node, ast.Call):
            continue
        name = _name(node)
        if name == 'UserMessageError' and node.args and isinstance(node.args[0], ast.Constant):
            message_id = node.args[0].value
            if isinstance(message_id, str) and message_id not in keys:
                missing.append(dict(file=filename, line=node.lineno, key=message_id))
        if name in TRANSLATORS and node.args:
            value = node.args[0]
            if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value not in keys:
                missing.append(dict(file=filename, line=node.lineno, key=value.value))
            elif isinstance(value, (ast.JoinedStr, ast.BinOp)):
                missing.append(dict(file=filename, line=node.lineno, key='<format after translation, not before>'))
        values = [option.value for option in node.keywords if option.arg in SINKS]
        if name in POSITIONAL_SINKS and node.args:
            values.append(node.args[0])
        for value in values:
            raw_error = (isinstance(value, ast.Name) and value.id in ('error', 'exception', 'e')) or (
                isinstance(value, ast.Call) and _name(value) == 'str' and value.args
                and isinstance(value.args[0], ast.Name) and value.args[0].id in ('error', 'exception', 'e'))
            if raw_error:
                hardcoded.append(dict(file=filename, line=node.lineno, text='<raw exception; translate at UI boundary>'))
            for fragment in literal_fragments(value):
                if name in MESSAGE_WRAPPERS:
                    if fragment not in keys:
                        missing.append(dict(file=filename, line=node.lineno, key=fragment))
                    continue
                if any(char.isalpha() for char in fragment) and fragment.strip(' \t\n·:') not in UI_LITERALS:
                    hardcoded.append(dict(file=filename, line=node.lineno, text=fragment))
        if name.endswith(('Error', 'Exception')) and node.args:
            for value in node.args:
                if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value not in keys:
                    errors.append(dict(file=filename, line=node.lineno, text=value.value))
    return missing, hardcoded, errors, literals


def audit(root=ROOT_DIR):
    root = Path(root)
    catalogs, loading = {}, []
    for code in LANGUAGE_CODES.values():
        try:
            with (root / 'locales' / f'{code}.json').open(encoding='utf-8') as stream:
                data = json.load(stream, object_pairs_hook=_unique_object)
            if not isinstance(data, dict):
                raise ValueError('Catalog must be an object')
            catalogs[code] = data
        except (ValueError, OSError) as error:
            loading.append(dict(kind='load', language=code, detail=str(error)))
    issues = loading + catalog_findings(catalogs)
    keys = set(catalogs.get('en', {}))
    missing, hardcoded, errors, literals = [], [], [], set()
    paths = [root / 'start.py', *(root / 'app').rglob('*.py')]
    for path in sorted(paths):
        if not path.exists() or 'tests' in path.parts or path.name == 'localization_audit.py':
            continue
        findings = source_findings(path.read_text(encoding='utf-8-sig'), path.relative_to(root).as_posix(), keys)
        missing.extend(findings[0]); hardcoded.extend(findings[1]); errors.extend(findings[2]); literals.update(findings[3])
    # Preferences are data-driven UI captions, not literal translate() arguments.
    settings = root / 'files' / 'settings.csv'
    if settings.exists():
        with settings.open(encoding='utf-8-sig', newline='') as stream:
            for index, row in enumerate(csv.DictReader(stream, delimiter=';'), 2):
                required = [row['Name']]
                kind = row.get('Type', '')
                if kind.startswith('Options[') and kind.endswith(']'):
                    required += [value.strip() for value in kind[8:-1].split(',')]
                literals.update(required)
                missing.extend(dict(file='files/settings.csv', line=index, key=value) for value in required if value not in keys)
    duplicates = {}
    for code, catalog in catalogs.items():
        values = {}
        for key, value in catalog.items():
            if isinstance(value, str): values.setdefault(value, []).append(key)
        duplicates[code] = {value: items for value, items in values.items() if len(items) > 1}
    return dict(languages=len(LANGUAGE_CODES), keys=len(keys), duplicate_values=duplicates,
        catalog_sizes={code: len(catalog) for code, catalog in catalogs.items()},
        catalog_issues=issues, missing_source_keys=missing, hardcoded_candidates=hardcoded,
        exception_candidates=errors, unreferenced_candidates=sorted(keys - literals),
        identical_to_english={code: [key for key, value in catalog.items() if value == catalogs.get('en', {}).get(key)]
                              for code, catalog in catalogs.items() if code != 'en'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write the full inventory as UTF-8 JSON')
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items()
        if key not in ('identical_to_english', 'unreferenced_candidates', 'duplicate_values')}, ensure_ascii=False, indent=2))
    return int(bool(result['catalog_issues'] or result['missing_source_keys'] or result['hardcoded_candidates']))


if __name__ == '__main__':
    raise SystemExit(main())

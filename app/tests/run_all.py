"""Run the complete suite in isolated processes: python -B -m app.tests.run_all."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from app.paths import ROOT_DIR

MARKER = 'VOC_TEST_RESULT='


def worker(module):
    from app.tests.safety import isolated_services
    with isolated_services():
        suite = unittest.defaultTestLoader.loadTestsFromName(module)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(MARKER+json.dumps(dict(tests=result.testsRun, failures=len(result.failures),
        errors=len(result.errors), skipped=len(result.skipped))), flush=True)
    return 0 if result.wasSuccessful() else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pattern', default='test_*.py', help='Test module filename pattern')
    parser.add_argument('--timeout', type=float, default=120, help='Timeout per module in seconds')
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return worker(args.worker)
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    modules = sorted('app.tests.'+path.stem for path in Path(__file__).parent.glob(args.pattern)
        if path.is_file() and path.name.startswith('test_'))
    if not modules:
        print('No test modules matched.', file=sys.stderr)
        return 2
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYGAME_HIDE_SUPPORT_PROMPT='1', PYTHONIOENCODING='utf-8')
    total = skipped = failed = 0
    for module in modules:
        try:
            process = subprocess.run([sys.executable, '-B', '-m', 'app.tests.run_all', '--worker', module],
                cwd=ROOT_DIR, env=environment, capture_output=True, text=True, encoding='utf-8',
                errors='replace', timeout=args.timeout)
        except subprocess.TimeoutExpired:
            failed += 1
            print(f'FAIL {module}: timeout after {args.timeout:g} seconds', flush=True)
            continue
        record = next((line[len(MARKER):] for line in process.stdout.splitlines() if line.startswith(MARKER)), None)
        details = json.loads(record) if record else {}
        total += details.get('tests', 0)
        skipped += details.get('skipped', 0)
        ok = process.returncode == 0 and record is not None and details.get('tests', 0) > 0
        failed += not ok
        print(f'{"PASS" if ok else "FAIL"} {module} ({details.get("tests", 0)} tests)', flush=True)
        if ok:
            for line in process.stdout.splitlines():
                if line.startswith('PERF '):
                    print('  '+line, flush=True)
        if not ok:
            print(process.stdout, end='')
            print(process.stderr, end='', file=sys.stderr)
    print(f'\n{total} tests; {skipped} skipped; {failed} failed modules / {len(modules)}.', flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())

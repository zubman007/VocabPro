"""Regression checks for the auditor, independent of application tests."""
from pathlib import Path
import tempfile
from unittest import TestCase
from tools.quality.common import write_json,redact,regressions,protected_snapshot
import json


class HarnessTests(TestCase):
    def test_powershell_parse_errors_fail_the_quality_gate_even_with_exit_zero(self):
        from unittest.mock import patch
        from tools.quality.run import tool_check
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            evidence={'returncode':0,'stdout':'[{"File":"update_exe.ps1","Line":1,"Message":"syntax"}]',
                      'stderr':'','seconds':.01,'timeout':False}
            with patch('tools.quality.run.command',return_value=evidence):
                result=tool_check('powershell',[],folder,folder,{})
            self.assertEqual(result['status'],'failed')

    def test_reports_are_atomic_valid_json_and_leave_no_temporary_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'history.json'
            write_json(path,[{'value':1}]);write_json(path,[{'value':2}])
            self.assertEqual(json.loads(path.read_text()),[{'value':2}])
            self.assertEqual(list(Path(folder).iterdir()),[path])

    def test_redaction_covers_tokens_passwords_and_authenticated_urls(self):
        for value in ('password=very-secret','token: private-token','https://user:private@example.test'):
            self.assertNotIn('private',redact(value));self.assertNotIn('very-secret',redact(value))

    def test_history_only_compares_available_metrics(self):
        previous={'coverage_percent':90,'performance':{'load_ms':10},'failed':0}
        current={'coverage_percent':None,'performance':{'load_ms':20},'failed':1}
        self.assertEqual({row['metric'] for row in regressions(current,previous)},{'load_ms','failed'})
        from tools.quality.report import dependency_rows
        report={'checks':{'Dependency vulnerabilities':{'status':'warning','data':{'dependencies':[
            {'name':'sample','version':'1','vulns':[{'id':'ADV-1','fix_versions':['2']},{'id':'ADV-1','fix_versions':['2.0']}]}]}},
            'Bandit':{'status':'passed','data':{'results':[]}}},'summary':{}}
        self.assertEqual(len(dependency_rows(report,[])),1)
        self.assertEqual(report['vulnerability_evidence']['raw_advisory_records'],2)
        self.assertEqual(report['summary']['dependency_vulnerabilities'],1)

    def test_first_run_has_no_invented_baseline(self):
        self.assertEqual(regressions({'failed':9},None),[])
        self.assertEqual(regressions({'security_findings':None},{'security_findings':0}),[])

    def test_json_redaction_preserves_escaped_quotes_and_json_syntax(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'result.json'
            write_json(path,{'code':'password = "private-value with spaces"\nnext()','token':'private-token'})
            value=json.loads(path.read_text())
            self.assertNotIn('private-value',value['code'])
            self.assertNotIn('with spaces',value['code']);self.assertEqual(value['token'],'[redacted]')

    def test_snapshot_detects_changes_without_reading_ignored_environments(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'app').mkdir();(root/'app/test.py').write_text('x=1')
            before=protected_snapshot(root);(root/'app/test.py').write_text('x=2')
            self.assertNotEqual(before,protected_snapshot(root))
            from unittest.mock import patch
            errors={}
            with patch('tools.quality.common.digest',side_effect=PermissionError):
                self.assertEqual(protected_snapshot(root,errors=errors),{})
            self.assertEqual(list(errors.values()),['PermissionError'])

    def test_static_statistics_and_duplicates_come_from_actual_ast(self):
        from tools.quality.analysis import inspect_sources
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'app').mkdir()
            source='def a(x):\n    x += 1\n    x += 2\n    x += 3\n    x += 4\n    x += 5\n    x += 6\n    return x\n'
            (root/'app/sample.py').write_text(source+source.replace('def a','def b'))
            value=inspect_sources(root)
            self.assertEqual(value['totals']['functions'],2)
            self.assertEqual(len(value['duplicates']),1)

    def test_regression_boundary_does_not_flag_small_noise(self):
        self.assertEqual(regressions({'performance':{'load_ms':12}}, {'performance':{'load_ms':10}}),[])

    def test_shadow_has_synthetic_defaults_and_never_copies_user_words(self):
        from tools.quality.run import shadow_project
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'source';shadow=Path(directory)/'shadow';root.mkdir();shadow.mkdir()
            for name in ('app','images','locales','tools','files'):(root/name).mkdir()
            for name in ('start.py','requirements.txt','requirements.lock.txt'):(root/name).write_text('')
            private=root/'files/Czech_English_voc.csv';private.write_text('private user data')
            shadow_project(root,shadow)
            self.assertEqual(private.read_text(),'private user data')
            self.assertIn('NA',(shadow/'files/Czech_English_voc.csv').read_text())
            self.assertNotIn('private user data',(shadow/'files/Czech_English_voc.csv').read_text())
            self.assertTrue((shadow/'files/Czech_Spanish_con.csv').is_file())

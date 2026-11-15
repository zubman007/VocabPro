"""The aggregate runner must propagate failures and timeouts, never report false success."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from app.tests.run_all import main, MARKER


class RunnerTests(unittest.TestCase):
    def invoke(self, **kwargs):
        with patch('app.tests.run_all.subprocess.run',**kwargs),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            return main(['--pattern','test_storage.py','--timeout','1'])

    def test_success_and_failure_return_codes(self):
        result=MARKER+json.dumps(dict(tests=3,failures=0,errors=0,skipped=0))
        self.assertEqual(self.invoke(return_value=subprocess.CompletedProcess([],0,result,'')),0)
        self.assertEqual(self.invoke(return_value=subprocess.CompletedProcess([],1,result,'Failure')),1)

    def test_missing_results_and_empty_suites_are_failures(self):
        self.assertEqual(self.invoke(return_value=subprocess.CompletedProcess([],0,'','')),1)
        result=MARKER+json.dumps(dict(tests=0,failures=0,errors=0,skipped=0))
        self.assertEqual(self.invoke(return_value=subprocess.CompletedProcess([],0,result,'')),1)

    def test_timeout_is_reported_as_failure(self):
        self.assertEqual(self.invoke(side_effect=subprocess.TimeoutExpired('worker',1)),1)

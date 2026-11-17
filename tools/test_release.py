"""Release failure injection; every path belongs to TemporaryDirectory."""
import json
from pathlib import Path
import tempfile
import os
import runpy
import sys
import unittest
from unittest.mock import patch,Mock
from tools.release import deploy,managed,release_lock,source_snapshot,fixture,check_assets


class ReleaseTests(unittest.TestCase):
    def test_failed_compilation_never_replaces_existing_distribution_or_data(self):
        from tools.release import main
        project=self.root/'source-project';project.mkdir()
        def snapshot(folder):
            folder.mkdir(parents=True)
            return 'stable-source-fingerprint'
        compiler=Mock(stdout=iter(()));compiler.wait.return_value=7
        with patch('tools.release.ROOT',project),patch.object(sys,'argv',['release','--python',sys.executable]),\
                patch('tools.release.source_snapshot',side_effect=snapshot),\
                patch('tools.release.assert_closed'),patch('tools.release.git',return_value=None),\
                patch('tools.release.subprocess.run',return_value=Mock(returncode=0)),\
                patch('tools.release.subprocess.Popen',return_value=compiler),patch('builtins.print'):
            with self.assertRaisesRegex(RuntimeError,'Build failed'):main()
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')
        self.assertEqual((self.data/'words.csv').read_bytes(),b'user data')

    def test_distribution_rejects_user_csv_but_keeps_library_sample_data(self):
        library=self.new/'matplotlib/mpl-data/sample_data';library.mkdir(parents=True)
        (library/'Stocks.csv').write_text('library sample',encoding='utf-8')
        check_assets(self.new)
        for name in ('settings.csv','files/Czech_Spanish_voc.csv','app/data/private.csv'):
            path=self.new/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('private',encoding='utf-8')
            with self.assertRaises(ValueError):check_assets(self.new)
            path.unlink()

    def test_running_exe_lock_refuses_start_during_update(self):
        from app.release_runtime import distribution_lock
        lock=self.root/'.VocabPro_exe.update.lock'
        with release_lock(lock),patch('app.release_runtime.COMPILED',True),\
                patch('app.release_runtime.ROOT_DIR',self.old),\
                patch('app.repositories.preferences.load_preferences',side_effect=ValueError('invalid test settings')),\
                patch('ctypes.windll.user32.MessageBoxW') as message:
            with self.assertRaises(SystemExit),distribution_lock():
                self.fail('A running EXE must not enter while deployment owns the lock.')
            message.assert_called_once()
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')

    def test_python_keeps_source_data_and_compiled_paths_are_external(self):
        from tools.release import ROOT
        environment={key:value for key,value in os.environ.items() if key!='VOCABPRO_DATA_DIR'}
        with patch.dict(os.environ,environment,clear=True):
            source=runpy.run_path(str(ROOT/'app/paths.py'))
            self.assertEqual(source['FILES_DIR'],ROOT/'files')
            exe=self.root/'VocabPro_exe'/'VocabPro.exe'
            with patch.object(sys,'executable',str(exe)):
                compiled=runpy.run_path(str(ROOT/'app/paths.py'),init_globals={'__compiled__':True})
            self.assertEqual(compiled['ROOT_DIR'],exe.parent)
            self.assertEqual(compiled['FILES_DIR'],self.root/'VocabPro_data'/'files')
            self.assertFalse(compiled['FILES_DIR'].exists())

    def test_explicit_fixture_directory_overrides_default_without_creating_it(self):
        from tools.release import ROOT
        with patch.dict(os.environ,{'VOCABPRO_DATA_DIR':str(self.root/'isolated')}):
            paths=runpy.run_path(str(ROOT/'app/paths.py'))
        self.assertEqual(paths['FILES_DIR'],self.root/'isolated')
        self.assertFalse(paths['FILES_DIR'].exists())

    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        self.old=self.make('VocabPro_exe','old')
        self.new=self.make('candidate','new')
        self.archive=self.root/'archive'/'previous'
        self.data=self.root/'VocabPro_data';self.data.mkdir();(self.data/'words.csv').write_bytes(b'user data')

    def make(self,name,version):
        path=self.root/name;path.mkdir()
        (path/'release.json').write_text(json.dumps({'application':'VocabPro','version':version}),encoding='utf-8')
        (path/'VocabPro.exe').write_bytes(version.encode())
        return path

    def verify(self,path):self.assertEqual((path/'VocabPro.exe').read_bytes(),b'new')

    def test_success_swaps_assets_and_preserves_previous_and_user_data(self):
        deploy(self.new,self.old,self.archive,self.verify)
        self.assertEqual((self.archive/'VocabPro.exe').read_bytes(),b'old')
        self.assertEqual((self.data/'words.csv').read_bytes(),b'user data')

    def test_failed_verification_restores_previous_release(self):
        with self.assertRaises(RuntimeError):
            deploy(self.new,self.old,self.archive,lambda _:(_ for _ in ()).throw(RuntimeError('probe failed')))
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')
        self.assertEqual((self.new/'VocabPro.exe').read_bytes(),b'new')
        self.assertEqual((self.data/'words.csv').read_bytes(),b'user data')

    def test_failed_directory_move_restores_previous_release(self):
        original=Path.rename
        def rename(path,target):
            if path==self.new:raise PermissionError('simulated locked EXE')
            return original(path,target)
        with patch.object(Path,'rename',rename),self.assertRaises(PermissionError):
            deploy(self.new,self.old,self.archive,self.verify)
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')

    def test_unmanaged_target_and_legacy_data_are_never_replaced(self):
        (self.old/'release.json').unlink()
        with self.assertRaises(ValueError):deploy(self.new,self.old,self.archive,self.verify)
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')
        (self.old/'release.json').write_text('{"application":"VocabPro"}',encoding='utf-8')
        (self.old/'files').mkdir();(self.old/'files/settings.csv').write_bytes(b'private')
        with self.assertRaises(ValueError):deploy(self.new,self.old,self.archive,self.verify)
        self.assertEqual((self.old/'files/settings.csv').read_bytes(),b'private')

    def test_repeated_update_then_rollback(self):
        deploy(self.new,self.old,self.archive,self.verify)
        third=self.make('third','third')
        deploy(third,self.old,self.root/'archive'/'second',lambda _:None)
        deploy(self.archive,self.old,self.root/'archive'/'third',lambda _:None)
        self.assertEqual((self.old/'VocabPro.exe').read_bytes(),b'old')
        self.assertEqual((self.data/'words.csv').read_bytes(),b'user data')

    def test_update_lock_excludes_other_process_owners(self):
        with release_lock(self.root/'update.lock'):
            with self.assertRaises(RuntimeError),release_lock(self.root/'update.lock'):pass

    def test_snapshot_excludes_settings_dictionaries_tests_and_credentials(self):
        target=self.root/'snapshot';digest=source_snapshot(target)
        self.assertEqual(len(digest),64)
        self.assertFalse((target/'files/settings.csv').exists())
        self.assertFalse((target/'app/tests').exists())
        self.assertFalse(list(target.rglob('*.csv')))
        self.assertTrue((target/'images/vocabpro_logo_v2.ico').exists())

    def test_synthetic_fixture_is_marked_and_has_no_backup_or_api_secret(self):
        folder=self.root/'fixture';fixture(folder)
        import pandas as pd
        settings=pd.read_csv(folder/'settings.csv',sep=';',keep_default_na=False).set_index('Name')
        self.assertEqual(settings.at['11Labs token','Value'],'')
        self.assertEqual(settings.at['Backup period (days)','Value'],'0')
        self.assertTrue((folder/'RELEASE_TEST_ONLY').exists())
        self.assertTrue(managed(self.new))


if __name__=='__main__':unittest.main()

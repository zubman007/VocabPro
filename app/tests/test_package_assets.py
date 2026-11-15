"""Check real packaged assets, import topology, and runner side-effect guards."""
import ast
import importlib
import pkgutil
import socket
import tempfile
from pathlib import Path
import unittest
from PIL import Image
import app
from app.paths import ROOT_DIR, IMAGES_DIR, FILES_DIR
from app.tests.safety import check_write, isolated_services


class PackageAssetTests(unittest.TestCase):
    def test_every_runtime_asset_exists_and_every_image_is_used(self):
        used=set()
        for path in (ROOT_DIR/'app').rglob('*.py'):
            if 'tests' in path.relative_to(ROOT_DIR/'app').parts:continue
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node,ast.Constant) and isinstance(node.value,str):
                    name=Path(node.value)
                    if name.suffix.lower() in ('.png','.ico','.jpg','.jpeg','.webp') and name.name==node.value:
                        used.add(name.name)
        used.add('vocabpro_logo_v2.ico')
        actual={path.name for path in IMAGES_DIR.iterdir() if path.is_file()}
        self.assertEqual(actual,used)
        for name in used:
            with self.subTest(asset=name),Image.open(IMAGES_DIR/name) as source:
                source.verify()

    def test_all_runtime_packages_import_without_old_root_modules(self):
        for module in pkgutil.walk_packages(app.__path__,'app.'):
            if module.name.startswith('app.tests'):continue
            with self.subTest(module=module.name):importlib.import_module(module.name)
        from app import main
        self.assertEqual(Path(main.__file__).resolve(),ROOT_DIR/'app'/'main.py')

    def test_runner_blocks_project_data_writes_but_allows_temporary_files(self):
        with self.assertRaises(AssertionError):check_write(FILES_DIR/'must_not_be_created.csv')
        with tempfile.TemporaryDirectory() as directory,isolated_services():
            path=Path(directory)/'allowed.csv';path.write_text('ID\n1\n',encoding='utf-8')
            self.assertTrue(path.exists())
            with self.assertRaises(AssertionError):(FILES_DIR/'must_not_be_created.csv').write_text('x')
            with self.assertRaises(AssertionError):socket.create_connection(('example.com',443))

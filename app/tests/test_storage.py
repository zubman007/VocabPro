import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.shared.storage import save_csv


class Frame:
    def __init__(self, fail=False):
        self.fail = fail

    def to_csv(self, stream, **options):
        stream.write("word;translation\nhello;ahoj\n")
        if self.fail:
            raise OSError("Simulated interrupted write")


class StorageTests(unittest.TestCase):
    def test_complete_write_replaces_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "words.csv"
            path.write_text("original", encoding="utf-8")
            save_csv(Frame(), path, sep=";", index=False)
            self.assertIn("hello;ahoj", path.read_text(encoding="utf-8"))
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_failed_write_preserves_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "words.csv"
            path.write_text("original", encoding="utf-8")
            with self.assertRaises(OSError):
                save_csv(Frame(fail=True), path)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_failed_replace_preserves_original_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "words.csv"
            path.write_text("original", encoding="utf-8")
            with patch("app.shared.storage.os.replace", side_effect=PermissionError("File locked")):
                with self.assertRaises(PermissionError):
                    save_csv(Frame(), path)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(list(Path(directory).iterdir()), [path])
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.shared.storage import save_csv, file_revision, FileChangedError
from app.shared.atomic_bytes import save_bytes


class Frame:
    def __init__(self, fail=False):
        self.fail = fail

    def to_csv(self, stream, **options):
        stream.write("word;translation\nhello;ahoj\n")
        if self.fail:
            raise OSError("Simulated interrupted write")


class StorageTests(unittest.TestCase):
    def writers(self, path, **options):
        return (
            lambda: save_csv(Frame(), path, **options),
            lambda: save_bytes(path, b'new bytes', **{
                ('revision' if key == 'expected_revision' else key): value
                for key, value in options.items()}),
        )

    def test_csv_unicode_quoting_and_binary_documents_round_trip_without_conversion(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            frame = pd.DataFrame({'word': ['příliš; žluťoučký\n"kůň"'], 'ID': ['001']})
            save_csv(frame, path, sep=';', index=False)
            pd.testing.assert_frame_equal(pd.read_csv(path, sep=';', dtype=str), frame)
            payload = bytes(range(256)) + b'\r\n\x00'
            save_bytes(path, payload)
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_stale_revision_preserves_external_changes_in_both_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            path.write_bytes(b'original')
            revision = file_revision(path)
            path.write_bytes(b'external change')
            for write in self.writers(path, expected_revision=revision):
                with self.subTest(writer=write), self.assertRaises(FileChangedError):
                    write()
                self.assertEqual(path.read_bytes(), b'external change')
                self.assertEqual(list(path.parent.iterdir()), [path])

    def test_deleted_revision_retains_each_existing_error_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            path.write_bytes(b'original')
            revision = file_revision(path)
            path.unlink()
            for write, error in zip(self.writers(path, expected_revision=revision),
                                    (FileNotFoundError, FileChangedError)):
                with self.subTest(error=error), self.assertRaises(error):
                    write()
                self.assertEqual(list(path.parent.iterdir()), [])

    def test_create_if_absent_rejects_a_competitor_at_publish_for_both_formats(self):
        import os
        link = os.link
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            def concurrent(source, destination):
                Path(destination).write_bytes(b'competitor')
                return link(source, destination)
            for write in self.writers(path, expect_missing=True):
                with patch('app.shared.storage.os.link', side_effect=concurrent):
                    with self.assertRaises(FileChangedError):
                        write()
                self.assertEqual(path.read_bytes(), b'competitor')
                self.assertEqual(list(path.parent.iterdir()), [path])
                path.unlink()

    def test_flush_and_publish_failures_keep_original_and_clean_both_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            path.write_bytes(b'original')
            for operation in ('fsync', 'replace'):
                for write in self.writers(path):
                    with self.subTest(operation=operation, writer=write):
                        with patch('app.shared.storage.os.' + operation, side_effect=OSError('disk failure')):
                            with self.assertRaises(OSError):
                                write()
                        self.assertEqual(path.read_bytes(), b'original')
                        self.assertEqual(list(path.parent.iterdir()), [path])

    def test_invalid_binary_payload_never_replaces_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'document'
            path.write_bytes(b'original')
            with self.assertRaises(TypeError):
                save_bytes(path, object())
            self.assertEqual(path.read_bytes(), b'original')
            self.assertEqual(list(path.parent.iterdir()), [path])

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

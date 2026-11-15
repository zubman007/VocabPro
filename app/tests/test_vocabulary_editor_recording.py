from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import wave
from app.vocabulary.editor_recording import record_wave


class RecordingTests(unittest.TestCase):
    def test_success_publishes_complete_wave(self):
        stop=threading.Event()
        audio=Mock()
        audio.get_sample_size.return_value=2
        stream=audio.open.return_value
        def read(*args,**kwargs):
            stop.set()
            return bytes(4096)
        stream.read.side_effect=read
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recording.wav'
            path.write_bytes(b'old audio')
            with patch('app.vocabulary.editor_recording.pyaudio.PyAudio',return_value=audio):
                record_wave(path,stop)
            with wave.open(str(path),'rb') as saved:
                self.assertEqual(saved.getnchannels(),2)
                self.assertEqual(saved.getframerate(),44100)
                self.assertEqual(saved.getnframes(),1024)
            self.assertEqual(list(Path(directory).iterdir()),[path])
        stream.close.assert_called_once()
        audio.terminate.assert_called_once()

    def test_capture_failure_preserves_original_audio(self):
        audio=Mock()
        audio.get_sample_size.return_value=2
        audio.open.return_value.read.side_effect=OSError('microphone failed')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recording.wav'
            path.write_bytes(b'original')
            with patch('app.vocabulary.editor_recording.pyaudio.PyAudio',return_value=audio):
                with self.assertRaises(OSError):
                    record_wave(path,threading.Event())
            self.assertEqual(path.read_bytes(),b'original')
        audio.open.return_value.close.assert_called_once()
        audio.terminate.assert_called_once()

    def test_failure_after_partial_capture_never_publishes_partial_audio(self):
        audio=Mock()
        audio.get_sample_size.return_value=2
        audio.open.return_value.read.side_effect=[bytes(4096), OSError('capture interrupted')]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recording.wav'
            path.write_bytes(b'original')
            with patch('app.vocabulary.editor_recording.pyaudio.PyAudio',return_value=audio):
                with self.assertRaises(OSError):
                    record_wave(path,threading.Event())
            self.assertEqual(path.read_bytes(),b'original')
            self.assertEqual(list(Path(directory).iterdir()),[path])

    def test_immediate_stop_does_not_replace_audio_with_empty_recording(self):
        audio=Mock()
        audio.get_sample_size.return_value=2
        stop=threading.Event()
        stop.set()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recording.wav'
            path.write_bytes(b'original')
            with patch('app.vocabulary.editor_recording.pyaudio.PyAudio',return_value=audio):
                with self.assertRaises(ValueError):
                    record_wave(path,stop)
            self.assertEqual(path.read_bytes(),b'original')
        audio.terminate.assert_called_once()

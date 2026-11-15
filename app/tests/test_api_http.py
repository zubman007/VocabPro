"""Transport tests never contact external services or use real API credentials."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import pandas as pd
import requests
from app.services import api_http
from app.repositories import api_settings as api_config
from app.services.api_speech import generate_audio


def response(chunks=(b'audio',), status=200, content_type='audio/mpeg'):
    value = Mock()
    value.__enter__ = Mock(return_value=value)
    value.__exit__ = Mock(return_value=False)
    value.status_code = status
    value.headers = {'Content-Type': content_type}
    value.iter_content.return_value = iter(chunks)
    return value


class AudioTransportTests(unittest.TestCase):
    def check_download(self, reply, error=None):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'word.mp3'
            destination.write_bytes(b'original')
            with patch.object(api_http.SESSION, 'request', return_value=reply) as request:
                if error:
                    with self.assertRaises(error):
                        api_http.download_audio('https://example.invalid/audio', destination)
                    self.assertEqual(destination.read_bytes(), b'original')
                else:
                    api_http.download_audio('https://example.invalid/audio', destination)
                    self.assertEqual(destination.read_bytes(), b'audio')
                self.assertEqual(list(Path(directory).iterdir()), [destination])
                self.assertEqual(request.call_args.kwargs['timeout'], (5, 30))
            reply.__exit__.assert_called_once()

    def test_success(self):
        self.check_download(response())

    def test_empty_response_preserves_audio(self):
        self.check_download(response(chunks=()), ValueError)

    def test_interruption_preserves_audio(self):
        reply = response()
        def interrupted(chunk_size):
            yield b'partial'
            raise requests.ConnectionError('interrupted')
        reply.iter_content.side_effect = interrupted
        self.check_download(reply, requests.ConnectionError)

    def test_http_error_preserves_audio(self):
        reply = response()
        reply.raise_for_status.side_effect = requests.HTTPError('failed')
        self.check_download(reply, requests.HTTPError)

    def test_json_is_not_saved_as_audio(self):
        self.check_download(response(content_type='application/json'), ValueError)

    def test_suggestions_are_filtered(self):
        reply = response()
        reply.json.return_value = ['suggestion', {'meanings': []}]
        with patch.object(api_http.SESSION, 'get', return_value=reply):
            self.assertEqual(api_http.get_entries('https://example.invalid'), [{'meanings': []}])

    def test_not_found_is_no_entry(self):
        reply = response(status=404)
        with patch.object(api_http.SESSION, 'get', return_value=reply):
            self.assertEqual(api_http.get_entries('https://example.invalid'), [])
        reply.raise_for_status.assert_not_called()

    def test_failed_speech_does_not_mark_audio_available(self):
        frame = pd.DataFrame({'ID': [1], 'English': ['hello'], 'Audio': ['Automatic']})
        with patch('app.services.api_speech.load_settings', return_value={'11Labs token': 'test'}), \
                patch('app.services.api_speech.download_audio', side_effect=requests.ConnectionError):
            with self.assertRaises(requests.ConnectionError):
                generate_audio(0, frame, 'English', 'Czech')
        self.assertEqual(frame.loc[0, 'Audio'], 'Automatic')

    def test_config_cache_refreshes_after_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.csv'
            path.write_text('Name;Value\n11Labs token;first\n', encoding='utf-8')
            with patch.object(api_config, 'SETTINGS_PATH', path), \
                    patch.object(api_config, 'read_csv', wraps=api_config.read_csv) as read:
                self.assertEqual(api_config.load_settings()['11Labs token'], 'first')
                api_config.load_settings()
                self.assertEqual(read.call_count, 1)
                path.write_text('Name;Value\n11Labs token;replacement\n', encoding='utf-8')
                self.assertEqual(api_config.load_settings()['11Labs token'], 'replacement')
                self.assertEqual(read.call_count, 2)
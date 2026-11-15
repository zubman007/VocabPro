"""UI cues never use the pronunciation stream; no real playback in these tests."""
from unittest.mock import Mock, patch
import hashlib
import unittest
import wave
from app.shared import audio_effects as effects


class AudioEffectTests(unittest.TestCase):
    def setUp(self):
        effects._last_played.clear()

    def test_feedback_uses_cached_sound_on_one_channel_without_touching_music(self):
        sound=Mock();channel=Mock()
        with patch.object(effects.pygame.mixer,'get_init',return_value=(44100,-16,2)), \
             patch.object(effects.pygame.mixer.music,'get_busy',return_value=False), \
             patch.object(effects.pygame.mixer.music,'load') as music, \
             patch.object(effects,'_load_sound',return_value=sound) as load, \
             patch.object(effects.pygame.mixer,'Channel',return_value=channel), \
             patch.object(effects,'monotonic',return_value=10):
            self.assertTrue(effects.play_effect('success.FLAC'))
            self.assertFalse(effects.play_effect('success.FLAC'))
            load.assert_called_once_with('ui_success.wav',(44100,-16,2))
            channel.play.assert_called_once_with(sound)
            music.assert_not_called()

    def test_pronunciation_has_priority(self):
        with patch.object(effects.pygame.mixer,'get_init',return_value=(44100,-16,2)), \
             patch.object(effects.pygame.mixer.music,'get_busy',return_value=True), \
             patch.object(effects,'_load_sound') as load:
            self.assertFalse(effects.play_effect('wrong.wav'))
            load.assert_not_called()

    def test_word_audio_falls_back_to_the_shared_ui_effect(self):
        from app.vocabulary.practise_audio import PracticeAudio
        player=PracticeAudio('test','test')
        path=Mock();path.is_file.return_value=False
        with patch.object(player,'paths',return_value=(path,)), \
             patch('app.vocabulary.practise_audio.play_effect',return_value=True) as effect:
            self.assertTrue(player.play(1,'wrong.wav'))
            effect.assert_called_once_with('wrong.wav')

    def test_original_editor_sound_and_short_wave_assets(self):
        path=effects.SOUNDS/'edit_start.mp3'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
            'd16c0c36627d4f304222fec450f74e44d4c9689f131de5a058be0bc6592088cc')
        for name in ('ui_success.wav','ui_retry.wav','ui_saved.wav','ui_start.wav'):
            with wave.open(str(effects.SOUNDS/name),'rb') as stream:
                self.assertLessEqual(stream.getnframes()/stream.getframerate(),.5)
                self.assertEqual(stream.getsampwidth(),2)

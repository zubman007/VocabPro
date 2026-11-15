"""Automatic pronunciation is independent of manual playback and feedback effects."""
from app.core.context import get_context
from app.tests.context_helpers import patch_preferences
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace
from app import main
from app.vocabulary.practise import PracticeController
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import load_preferences, save_preferences
from app.tests.test_preferences_data import sample_preferences


class AutoplayTests(unittest.TestCase):
    def test_legacy_default_and_saved_disabled_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv'
            frame=sample_preferences().loc[lambda data:data.Name.ne('Autoplay pronunciation')]
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            loaded=load_preferences(path)
            self.assertTrue(RuntimePreferences.from_frame(loaded).autoplay_pronunciation)
            self.assertEqual(path.read_bytes(),before)
            save_preferences(loaded,{'Autoplay pronunciation':'0'},path)
            self.assertFalse(RuntimePreferences.from_frame(load_preferences(path)).autoplay_pronunciation)

    def test_disabled_autoplay_preserves_feedback_and_manual_audio(self):
        controller=PracticeController.__new__(PracticeController)
        controller.context=get_context()
        controller.Play_audio=Mock()
        with patch_preferences(autoplay_pronunciation=False),patch('app.vocabulary.practise.play_effect') as effect:
            controller.Auto_audio('None','new')
            controller.Auto_audio('wrong.wav','new')
            controller.Play_audio.assert_not_called()
            effect.assert_called_once_with('wrong.wav')
            controller.audio=Mock()
            controller.w_new=SimpleNamespace(id=7)
            PracticeController.Play_audio(controller,'None','new',None)
            controller.audio.play.assert_called_once_with(7,'None')

    def test_enabled_autoplay_keeps_previous_behaviour(self):
        controller=PracticeController.__new__(PracticeController);controller.Play_audio=Mock()
        controller.context=get_context()
        with patch_preferences(autoplay_pronunciation=True):controller.Auto_audio('None','new')
        controller.Play_audio.assert_called_once_with('None','new','')

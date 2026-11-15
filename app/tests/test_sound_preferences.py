"""Legacy defaults, persistence, validation and independent interface volume."""
from pathlib import Path
import tempfile
import unittest
import tkinter as tk
import customtkinter as cst
from unittest.mock import Mock, patch
from app.shared import audio_effects as effects
from app.repositories.preferences import load_preferences, save_preferences
from app.preferences.data import RuntimePreferences, PreferenceError, with_defaults
from app.tests.test_preferences_data import sample_preferences


class SoundPreferenceTests(unittest.TestCase):
    def tearDown(self):
        with patch.object(effects.pygame.mixer,'get_init',return_value=None):effects.configure(True,100)
        effects._last_played.clear()

    def test_legacy_preferences_are_extended_only_on_explicit_save(self):
        legacy=sample_preferences().loc[lambda frame:~frame.Name.isin(['App sounds enabled','App sound volume'])].copy()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';legacy.to_csv(path,sep=';',index=False)
            original=path.read_bytes();frame=load_preferences(path)
            defaults=RuntimePreferences.from_frame(frame)
            self.assertTrue(defaults.sounds_enabled);self.assertEqual(defaults.sound_volume,100)
            self.assertEqual(path.read_bytes(),original)
            self.assertIn('App sound volume',with_defaults(frame).Name.tolist())
            save_preferences(frame,{'App sounds enabled':'0','App sound volume':'35'},path)
            loaded=RuntimePreferences.from_frame(load_preferences(path))
            self.assertFalse(loaded.sounds_enabled);self.assertEqual(loaded.sound_volume,35)

    def test_invalid_volume_never_changes_the_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
            frame=load_preferences(path);before=path.read_bytes()
            for value in ('-1','101','half','50.5'):
                with self.subTest(value=value),self.assertRaises(PreferenceError):
                    save_preferences(frame,{'App sound volume':value},path)
                self.assertEqual(path.read_bytes(),before)

    def test_mute_and_zero_volume_skip_loading_and_do_not_touch_pronunciation(self):
        with patch.object(effects.pygame.mixer,'get_init',return_value=(44100,-16,2)), \
             patch.object(effects.pygame.mixer,'Channel',return_value=Mock()) as channel, \
             patch.object(effects.pygame.mixer.music,'set_volume') as word_volume, \
             patch.object(effects,'_load_sound') as load:
            effects.configure(False,60)
            self.assertFalse(effects.play_effect('edit'))
            effects.configure(True,0)
            self.assertFalse(effects.play_effect('success.FLAC'))
            load.assert_not_called();word_volume.assert_not_called()
            self.assertEqual(channel.return_value.stop.call_count,2)

    def test_volume_multiplies_existing_gain_and_restores_sound(self):
        channel=Mock()
        with patch.object(effects.pygame.mixer,'get_init',return_value=(44100,-16,2)), \
             patch.object(effects.pygame.mixer,'Channel',return_value=channel), \
             patch.object(effects.pygame.mixer.music,'get_busy',return_value=False), \
             patch.object(effects,'_load_sound',return_value=Mock()):
            effects.configure(True,40)
            self.assertTrue(effects.play_effect('success.FLAC'))
            self.assertAlmostEqual(channel.set_volume.call_args.args[0],.3)
            self.assertTrue(effects.play_effect('edit'))
            self.assertAlmostEqual(channel.set_volume.call_args.args[0],.4)

    def test_dialog_shows_new_fields_for_legacy_file_and_saves_them(self):
        from app.preferences.dialog import PreferencesDialog
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw();root.update()
        try:
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'settings.csv'
                frame=sample_preferences().loc[lambda data:~data.Name.isin(['App sounds enabled','App sound volume'])]
                frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
                dialog=PreferencesDialog(root,lambda key:key,path)
                self.assertIsInstance(dialog.fields['App sounds enabled'],cst.CTkCheckBox)
                self.assertIn('App sound volume',dialog.variables)
                self.assertEqual(path.read_bytes(),before)
                dialog.variables['App sounds enabled'].set('0')
                dialog.variables['App sound volume'].set('25')
                dialog.save()
                result=RuntimePreferences.from_frame(load_preferences(path))
                self.assertFalse(result.sounds_enabled);self.assertEqual(result.sound_volume,25)
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

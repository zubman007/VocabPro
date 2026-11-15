"""On-demand letters reset per question and persist through normal preferences."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
import customtkinter as cst
from app.preferences.data import RuntimePreferences, PreferenceError, with_defaults, validate_preferences
from app.repositories.preferences import load_preferences, save_preferences
from app.tests.test_preferences_data import sample_preferences
from app.vocabulary.practise import PracticeController
from app.shared.translations import get_catalog, LANGUAGES


class LetterHintTests(TestCase):
    def test_legacy_preferences_default_to_request_without_writing(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
            before=path.read_bytes();frame=load_preferences(path)
            self.assertEqual(RuntimePreferences.from_frame(frame).letter_hints,'On request')
            self.assertEqual(path.read_bytes(),before)
            for mode in ('Automatic','Disabled','On request'):
                frame=save_preferences(frame,{'Letter hints':mode},path)
                self.assertEqual(RuntimePreferences.from_frame(load_preferences(path)).letter_hints,mode)
            with self.assertRaises(PreferenceError):
                validate_preferences(with_defaults(frame),{'Letter hints':'invalid'})

    def test_new_texts_exist_in_all_languages(self):
        for language in LANGUAGES:
            for key in ('Letter hints','Show hint','Automatic','On request','Disabled'):
                self.assertIn(key,get_catalog(language))

    def test_actual_widgets_reveal_reset_modes_and_audio(self):
        root=cst.CTk();root.geometry('600x250')
        try:
            controller=PracticeController.__new__(PracticeController)
            controller.context=SimpleNamespace(preferences=SimpleNamespace(letter_hints='On request'))
            controller.lifecycle=SimpleNamespace(closed=False);controller._audio_question=False
            controller.letters_frm=cst.CTkFrame(root);controller.letters_frm.grid()
            controller.letters_lbl=cst.CTkLabel(controller.letters_frm,text='a b c');controller.letters_lbl.grid()
            controller.hint_button=cst.CTkButton(controller.letters_frm,command=controller.Show_hint)
            controller._reset_letter_hint();root.update()
            self.assertFalse(controller.letters_lbl.winfo_ismapped())
            self.assertTrue(controller.hint_button.winfo_ismapped())
            controller.hint_button.invoke();root.update()
            self.assertTrue(controller.letters_lbl.winfo_ismapped())
            self.assertFalse(controller.hint_button.winfo_ismapped())
            controller._reset_letter_hint();root.update()
            self.assertFalse(controller.letters_lbl.winfo_ismapped())
            controller.context.preferences.letter_hints='Automatic'
            controller._reset_letter_hint();root.update()
            self.assertTrue(controller.letters_lbl.winfo_ismapped())
            controller.context.preferences.letter_hints='Disabled'
            controller._reset_letter_hint();root.update()
            self.assertFalse(controller.letters_frm.winfo_ismapped())
            controller.letters_frm.grid();controller.context.preferences.letter_hints='On request'
            controller._audio_question=True;controller._reset_letter_hint();controller.Show_hint();root.update()
            self.assertFalse(controller.letters_frm.winfo_ismapped())
        finally:
            for job in root.tk.call('after','info'):root.after_cancel(job)
            root.destroy()

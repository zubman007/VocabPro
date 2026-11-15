"""Target-language tags on current, previous and reviewed vocabulary words."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.tests.test_preferences_data import sample_preferences
from app.repositories.tags import save_catalog
from app.vocabulary.practise import PracticeController
from app.vocabulary.practise_data import Word
from app.vocabulary.tags_data import translated_tags


class PracticeTagTests(TestCase):
    def test_translation_deduplicates_and_falls_back_without_changing_labels(self):
        self.assertEqual(translated_tags(' Zvířata, zvířata, Nadávky ',
            {'zvířata':'Animales','nadávky':'Insultos'}),'Animales · Insultos')
        self.assertEqual(translated_tags('Zvířata, Nadávky',{'zvířata':'Animals','nadávky':''}),'Animals · Nadávky')
        self.assertEqual(translated_tags('',{}),'')

    def test_current_answer_review_and_session_use_target_language_not_app_language(self):
        root=cst.CTk();root.geometry('1400x950')
        errors=[];root.report_callback_exception=lambda *error:errors.append(error)
        try:
            for language,target in [('Spanish','Animales'),('English','Animals')]:
                with TemporaryDirectory() as directory:
                    preferences=replace(RuntimePreferences.from_frame(sample_preferences()),
                        learned_by='Czech',app_language='English',context_probabilities=(0,0),audio_probabilities=(0,0))
                    context=AppContext(files_dir=Path(directory),preferences=preferences)
                    context.bind(root)
                    frame=pd.DataFrame({'ID':[1,2,3,4],language:['uno','dos','tres','cuatro'],
                        'Czech':['jedna','dva','tři','čtyři'],'Repetition':['SSSSS']*4,
                        'Audio':['No audio']*4,'Description':['description']*4,'Example':['example']*4,
                        'Part of Speech':['Noun']*4,'Tags':['Zvířata','Zvířata','',''],
                        'Next repetition':['2026-11-12 10:00:00']*4})
                    frame.to_csv(context.vocabulary_path(language),sep=';',index=False)
                    catalog=pd.DataFrame({'ID':['1'],'Czech':['Zvířata'],language:[target],'Note':['']})
                    save_catalog(context.tags_path(language),catalog,'Czech',language,None)
                    before=context.vocabulary_path(language).read_bytes()
                    with patch.object(PracticeController,'Play_audio'),patch('app.vocabulary.practise.random.choice',return_value=1):
                        controller=PracticeController(root,frame,language,1,context=context)
                        root.update()
                        self.assertEqual(controller.current_tags_label.cget('text'),target)
                        self.assertTrue(controller.current_tags_label.winfo_ismapped())
                        self.assertEqual(controller.answer_tags_label.cget('text'),target)
                        controller.Conf_resp('',None);root.update()
                        self.assertTrue(controller.answer_tags_label.winfo_ismapped())
                        self.assertEqual(controller.answer_tags_label.cget('text'),target)
                        controller.Show_w_next(None);root.update()
                        controller.w_old.copy(Word(2,'dos','','description','example','dva','Noun'))
                        controller.sidebar.update_session(controller.w_old,controller.w_new,1,4,
                            tags=controller.tag_text(2))
                        self.assertEqual(controller.sidebar.tags.cget('text'),target)
                        controller.Review_w(None)
                        dialog=controller._review_dialog
                        labels=[widget.cget('text') for widget in dialog.detail_body.winfo_children()
                                if isinstance(widget,cst.CTkLabel)]
                        self.assertIn('Tags',labels);self.assertIn(target,labels)
                        dialog.destroy()
                        controller.w_new.id=3
                        controller._show_question(1,None,0);controller._show_answer_details();root.update()
                        self.assertFalse(controller.current_tags_label.winfo_ismapped())
                        self.assertFalse(controller.answer_tags_label.winfo_manager())
                        controller.sidebar.update_session(controller.w_old,controller.w_new,1,4,tags='')
                        self.assertFalse(controller.sidebar.tags.winfo_manager())
                        self.assertEqual(context.vocabulary_path(language).read_bytes(),before)
                        controller.lifecycle.close()
        finally:
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()
        self.assertEqual(errors,[])

    def test_review_omits_empty_tags_section(self):
        from app.vocabulary.practise_review import open_review
        root=cst.CTk()
        try:
            dialog=open_review(root,Word(1,'word','','','','translation','Noun'),
                lambda:None,lambda:None,lambda:None,tags='')
            texts=[widget.cget('text') for widget in dialog.detail_body.winfo_children()
                   if isinstance(widget,cst.CTkLabel)]
            self.assertNotIn('Tags',texts)
            dialog.destroy()
        finally:
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()

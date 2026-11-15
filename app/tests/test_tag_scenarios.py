"""Seeded tag workloads and localized layout scenarios; synthetic data only."""
from dataclasses import replace
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.preferences.dialog import PreferencesDialog
from app.repositories.tags import encode_tags, decode_tags, save_catalog
from app.shared.translations import LANGUAGES
from app.tests.test_preferences_data import sample_preferences
from app.vocabulary.tags_data import filter_by_tags, UnknownTagError
from app.vocabulary.editor_tag_picker import WordTagsDialog


class TagWorkloadTests(TestCase):
    def test_seeded_filters_match_set_model_and_preserve_source(self):
        rng=Random(2081)
        labels=[f'Tag {i}' for i in range(40)]
        sets=[set(rng.sample(labels,rng.randrange(11))) for _ in range(400)]
        source=pd.DataFrame({'ID':range(400),'Tags':[', '.join(sorted(s)) for s in sets],
                             'History':['SSFS']*400})
        before=source.copy(deep=True)
        for _ in range(30):
            wanted=set(rng.sample(labels,rng.randrange(5)))
            for mode in ('all','none','exact'):
                expected=[i for i,s in enumerate(sets) if
                          (wanted<=s if mode=='all' else wanted.isdisjoint(s) if mode=='none' else wanted==s)]
                self.assertEqual(filter_by_tags(source,wanted,mode).ID.tolist(),expected)
        pd.testing.assert_frame_equal(source,before)

    def test_large_bilingual_roundtrip_filter_and_invalid_last_row_are_atomic(self):
        catalog=pd.DataFrame({'ID':[str(i) for i in range(1,101)],
            'Czech':[f'Český štítek {i}' for i in range(1,101)],
            'English':[f'Learning tag {i}' for i in range(1,101)],'Note':['']*100})
        source=pd.DataFrame({'ID':range(1,10001),'Tags':['Český štítek 1, Learning tag 2, 1']*10000,
                             'History':['SSFF']*10000})
        before=source.copy(deep=True)
        started=perf_counter()
        encoded=encode_tags(source,catalog,'Czech','English')
        self.assertTrue(encoded.Tags.eq('1, 2').all())
        with TemporaryDirectory() as folder:
            path=Path(folder)/'Czech_English_tags.csv'
            save_catalog(path,catalog,'Czech','English',None)
            shown=decode_tags(encoded,path,'Czech','English',target=True)
            self.assertTrue(shown.Tags.eq('Learning tag 1, Learning tag 2').all())
        self.assertEqual(len(filter_by_tags(encoded,'1, 2','exact')),10000)
        invalid=source.copy();invalid.loc[len(invalid)-1,'Tags']='invented'
        with self.assertRaises(UnknownTagError) as error:encode_tags(invalid,catalog,'Czech','English')
        self.assertEqual(error.exception.word_id,10000)
        pd.testing.assert_frame_equal(source,before)
        elapsed=perf_counter()-started
        print(f'PERF tags: 10000 bilingual rows, roundtrip/filter/invalid batch {elapsed*1000:.1f} ms')
        self.assertLess(elapsed,30,'Unexpectedly slow 10k-row tag processing')


class LocalizedTagScenarioTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory()
        self.root=cst.CTk();self.root.geometry('1400x900');self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)
        self.context=AppContext(files_dir=Path(self.folder.name),
            preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):self.root.after_cancel(token)
        self.root.destroy();self.folder.cleanup()
        self.assertEqual(self.errors,[])

    def test_all_settings_labels_and_fields_fit_minimum_and_large_windows(self):
        path=Path(self.folder.name)/'settings.csv'
        frame=sample_preferences();frame.loc[frame.Name=='App sounds enabled','Value']='0'
        frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            dialog=PreferencesDialog(self.root,self.context.translate,path)
            dialog.deiconify()
            self.assertEqual(dialog.fields['App sound volume'].cget('state'),'disabled')
            for geometry in ('950x650','1400x900'):
                dialog.geometry(geometry)
                for tab in ('Languages','Learning','Backups','API services'):
                    dialog.tabs.set(self.context.translate(tab));self.root.update()
                    for name,label in dialog.field_labels.items():
                        if dialog.field_sections[name]!=self.context.translate(tab):continue
                        with self.subTest(language=language,geometry=geometry,field=name):
                            self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                            self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2)
                            widget=dialog.fields[name]
                            self.assertGreaterEqual(widget.winfo_rootx(),dialog.winfo_rootx())
                            self.assertLessEqual(widget.winfo_rootx()+widget.winfo_width(),
                                                 dialog.winfo_rootx()+dialog.winfo_width()-10)
            dialog.destroy()
        self.assertEqual(path.read_bytes(),before)

    def test_long_tag_picker_translations_resize_search_and_ten_tag_apply(self):
        catalog=pd.DataFrame({'ID':[str(i) for i in range(1,121)],
            'Czech':[f'Štítek {i} s podrobným významem a delším názvem' for i in range(1,121)],
            'English':[f'Tag {i} with a detailed meaning and a longer name' for i in range(1,121)],
            'Note':['']*120})
        save_catalog(self.context.tags_path('English'),catalog,'Czech','English',None)
        before=self.context.tags_path('English').read_bytes()
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language,
                tag_display_language='Student language')
            applied=[]
            dialog=WordTagsDialog(self.root,'English',7,'a long word '*10,'',applied.append,context=self.context)
            dialog.deiconify();dialog.geometry('620x480');self.root.update()
            for checkbox in dialog.checkboxes[:10]:checkbox.toggle()
            dialog.list._parent_canvas.yview_moveto(1)
            dialog.query.set('Tag 120 ');self.root.update()
            self.assertEqual(len(dialog.checkboxes),1)
            self.assertAlmostEqual(dialog.list._parent_canvas.yview()[0],0,places=3)
            dialog.query.set('');self.root.update()
            for checkbox in dialog.checkboxes[:10]:
                self.assertLessEqual(checkbox._text_label.winfo_reqwidth(),checkbox.winfo_width())
                self.assertLessEqual(checkbox._text_label.winfo_reqheight(),checkbox.winfo_height())
            for button in self.buttons(dialog):
                self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height())
            dialog.apply()
            self.assertEqual(len(applied[0].split(', ')),10)
        self.assertEqual(self.context.tags_path('English').read_bytes(),before)

    def test_session_long_tags_and_translations_fit_sidebar_and_empty_tags_hide(self):
        from app.vocabulary.practise_layout import PracticeSidebar
        from app.vocabulary.practise_data import Word
        previous=Word(1,'a moderately long foreign word','','','','dlouhý český překlad '*5,'Noun')
        current=Word(2,'next','','','','další','Noun')
        tags=' · '.join(f'Tag {i} with a long explanatory label' for i in range(10))
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language,show_synonyms=False)
            sidebar=PracticeSidebar(self.root,lambda:None)
            sidebar.pack(side='right',fill='y');self.root.update()
            for i in range(20):sidebar.update_session(previous,current,i,100,tags=tags if i%2 else '')
            self.root.update()
            for label in (sidebar.word,sidebar.translation,sidebar.tags,sidebar.shortcuts):
                self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2,language)
                self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2,language)
            sidebar.update_session(previous,current,20,100,tags='');self.root.update()
            self.assertFalse(sidebar.tags.winfo_manager())
            sidebar.destroy()

    def test_repeated_unchanged_resize_does_not_reconfigure_tag_labels(self):
        catalog=pd.DataFrame({'ID':['1'],'Czech':['Zvířata'],'English':['Animals'],'Note':['']})
        save_catalog(self.context.tags_path('English'),catalog,'Czech','English',None)
        dialog=WordTagsDialog(self.root,'English',1,'word','',lambda value:None,context=self.context)
        dialog.deiconify();self.root.update();dialog._resize()
        label=dialog.checkboxes[0]._text_label
        with patch.object(label,'configure',wraps=label.configure) as configure:
            for _ in range(200):dialog._resize()
            configure.assert_not_called()
        dialog.destroy()

    def test_ten_long_tags_do_not_overlap_the_current_word(self):
        self.root.geometry('1150x800');self.root.update()
        from app.tests.test_editor_save import course
        from app.vocabulary.practise import PracticeController
        labels=[f'Regional and specialised expressions in everyday communication {i}' for i in range(10)]
        catalog=pd.DataFrame({'ID':[str(i+1) for i in range(10)],
            'Czech':[f'Oblast {i}' for i in range(10)],'English':labels,'Note':['']*10})
        save_catalog(self.context.tags_path('English'),catalog,'Czech','English',None)
        self.context.preferences=replace(self.context.preferences,tag_display_language='Learning language',
            autoplay_pronunciation=False,context_probabilities=(0,0),audio_probabilities=(0,0))
        frame=pd.concat([course().assign(ID=i+1,English=f'word {i}',Repetition='SSSSS',
            Tags=', '.join(catalog.Czech),Audio='No audio',Description='A description',
            Example='Use this word in a sentence.') for i in range(4)],ignore_index=True)
        frame.to_csv(self.context.vocabulary_path('English'),sep=';',index=False)
        with patch.object(PracticeController,'Play_audio'),patch('app.vocabulary.practise.random.choice',return_value=1):
            controller=PracticeController(self.root,frame,'English',1,context=self.context)
            for mode,prompt in ((1,controller.transl_lbl),(2,controller.type_2_frm),(3,controller.play_type_3_btn)):
                controller._show_question(mode,['one','two','three','four'] if mode==3 else None,0)
                self.root.update()
                tags=controller.current_tags_label
                self.assertTrue(tags.winfo_ismapped())
                self.assertLessEqual(prompt.winfo_rooty()+prompt.winfo_height()+8,tags.winfo_rooty(),mode)
                self.assertLessEqual(tags._label.winfo_reqheight(),tags.winfo_height()+2)
                self.assertLessEqual(controller.skip_btn.winfo_rooty()+controller.skip_btn.winfo_height(),
                                     self.root.winfo_rooty()+self.root.winfo_height())
            self.context.preferences=replace(self.context.preferences,show_practice_tags=False)
            controller._show_question(3,['one','two','three','four'],0);self.root.update()
            self.assertFalse(controller.current_tags_label.winfo_manager())
            self.assertEqual(controller.lbl_frm.cget('height'),260)
            controller.lifecycle.close()

    @staticmethod
    def buttons(owner):
        for widget in owner.winfo_children():
            if isinstance(widget,cst.CTkButton):yield widget
            yield from LocalizedTagScenarioTests.buttons(widget)

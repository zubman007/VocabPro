"""Tag counts, weighted review accuracy, cache refresh and compact GUI pages."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
import customtkinter as cst

from app.statistics.vocabulary_tags import tag_statistics, TagStatistics, VocabularyTagsPanel
from app.statistics.data import vocabulary_statistics
from app.statistics.cache import StatisticsCache
from app.tests.test_editor_save import course
from app.shared.translations import LANGUAGES, translate


class TagStatisticsTests(TestCase):
    def test_counts_multiple_tags_once_per_word_and_weights_accuracy_by_answers(self):
        source=pd.DataFrame({'Tags':['Zvířata, Nadávky, zvířata','Zvířata',None,'Nadávky']},index=[10,20,30,40])
        outcomes=pd.DataFrame({'Success':[1,9,99],'Failure':[1,0,99]},index=[10,20,30])
        before=source.copy(deep=True)
        values={item.name:item for item in tag_statistics(source,outcomes)}
        self.assertEqual(values['Zvířata'].words,2)
        self.assertEqual(values['Zvířata'].attempts,11)
        self.assertAlmostEqual(values['Zvířata'].accuracy,10/11)
        self.assertEqual(values['Nadávky'].words,2)
        self.assertEqual(values['Nadávky'].accuracy,.5)
        pd.testing.assert_frame_equal(source,before)

    def test_missing_tags_blank_tags_and_no_recorded_reviews(self):
        outcomes=pd.DataFrame(columns=['Success','Failure'])
        self.assertEqual(tag_statistics(pd.DataFrame({'ID':[1]}),outcomes),[])
        self.assertEqual(tag_statistics(pd.DataFrame({'Tags':['',None]}),outcomes),[])
        item=tag_statistics(pd.DataFrame({'Tags':['Zvířata']}),outcomes)[0]
        self.assertEqual(item.words,1)
        self.assertIsNone(item.accuracy)

    def test_cached_dataset_uses_existing_learning_rules_and_invalidates_tags(self):
        from app.statistics import data
        with TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv'
            frame=pd.concat([course().assign(Tags='Zvířata',Repetition=history,ID=index)
                for index,history in enumerate(('SSSSSSF','SSSSS','SSSS'),1)],ignore_index=True)
            frame.to_csv(path,sep=';',index=False)
            def calculate():
                return vocabulary_statistics(path,'English','Czech',7,{1:1},30,
                    ['Noun'],{'Noun':100},today=date(2026,11,13))
            with patch.object(data,'cache',StatisticsCache()),patch('app.statistics.data.read_csv',wraps=data.read_csv) as read:
                result=calculate();item=result['tags'][0]
                self.assertEqual((item.words,item.successes,item.failures),(3,1,1))
                self.assertEqual(result['summary'],(3,1,1))
                self.assertEqual(calculate()['tags'],result['tags'])
                self.assertEqual(read.call_count,1)
                frame['Tags']='Nadávky';frame.to_csv(path,sep=';',index=False)
                self.assertEqual(calculate()['tags'][0].name,'Nadávky')
                self.assertEqual(read.call_count,2)


class TagStatisticsUiTests(TestCase):
    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1150x800')
        self.errors=[]
        self.root.report_callback_exception=lambda *error:self.errors.append(error)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def test_pagination_search_sort_and_reset_when_language_data_changes(self):
        panel=VocabularyTagsPanel(self.root,lambda text:text);panel.pack(fill='x')
        items=[TagStatistics(f'Tag {index}',index,1,index) for index in range(1,14)]
        panel.set_items(items);self.root.update()
        self.assertEqual(panel.visible,items)
        self.assertEqual(panel.previous.cget('state'),'disabled')
        panel.turn(1);self.assertEqual(panel.page,0)
        panel.sort('accuracy')
        self.assertEqual([item.words for item in panel.visible],list(range(13,0,-1)))
        self.assertEqual(panel.page,0)
        panel.sort('accuracy')
        self.assertEqual(panel.visible[0].words,1)
        panel.sort('accuracy')
        self.assertIsNone(panel.sort_key)
        self.assertEqual(panel.visible,items)
        panel.turn(1);panel.search.insert(0,'Tag 13');panel._search_changed()
        self.assertEqual(panel.page,0)
        self.assertEqual([item.name for item in panel.visible],['Tag 13'])
        panel.set_items([TagStatistics('No answers',2,0,0)]);self.root.update()
        self.assertEqual(panel.search.get(),'')
        self.assertIsNone(panel.visible[0].accuracy)
        panel.set_items([]);self.assertEqual(panel.visible,[])
        self.assertEqual(panel.next.cget('state'),'disabled')

    def test_direction_keeps_unknown_accuracy_last_and_resets_with_new_data(self):
        panel=VocabularyTagsPanel(self.root,lambda text:text);panel.pack(fill='x')
        panel.set_items([TagStatistics('No answers',9,0,0),
                         TagStatistics('Low',2,1,3),TagStatistics('High',1,3,1)])
        panel.sort('words')
        self.assertEqual([item.words for item in panel.visible],[1,2,9])
        panel.sort('attempts')
        self.assertEqual([item.attempts for item in panel.visible],[0,4,4])
        panel.sort('accuracy')
        self.assertEqual([item.name for item in panel.visible],['Low','High','No answers'])
        panel.sort('accuracy')
        self.assertEqual([item.name for item in panel.visible],['High','Low','No answers'])
        panel.set_items([TagStatistics('One',1,0,0)])
        self.assertIsNone(panel.sort_key)

    def test_sort_direction_captions_fit_in_all_translations(self):
        for language in LANGUAGES:
            panel=VocabularyTagsPanel(self.root,lambda text:translate(text,language));panel.pack(fill='x')
            panel.set_items([TagStatistics('Tag',1,1,0)])
            self.root.update()
            for button,caption in panel.sort_buttons.values():
                font=cst.CTkFont(family=button.cget('font')[0],size=button.cget('font')[1])
                self.assertLessEqual(font.measure(button.cget('text')),
                                     button.winfo_width()-16,language)
            self.assertLessEqual(panel.next.winfo_x()+panel.next.winfo_width(),
                                 panel.next.master.winfo_width(),language)
            panel.destroy()

    def test_bounded_height_and_long_names_in_all_translations(self):
        for language in LANGUAGES:
            panel=VocabularyTagsPanel(self.root,lambda text:translate(text,language));panel.pack(fill='x')
            panel.set_items([TagStatistics('Very long custom tag name '*12+str(index),index,1,1)
                            for index in range(1,92)])
            self.root.update()
            self.assertEqual(len(panel.visible),15)
            self.assertLess(panel.winfo_height()/panel._get_widget_scaling(),850,language)
            panel.destroy()

    def test_real_statistics_controller_receives_tag_data_from_worker(self):
        from dataclasses import replace
        from time import monotonic, sleep
        from app.core.context import AppContext
        from app.preferences.data import RuntimePreferences
        from app.tests.test_preferences_data import sample_preferences
        from app.statistics.viewer import StatisticsController
        from app.statistics.window import StatisticsWindow
        with TemporaryDirectory() as directory:
            folder=Path(directory)
            course().assign(Tags='Zvířata, Nadávky',Repetition='SSSSSSF').to_csv(
                folder/'Czech_English_voc.csv',sep=';',index=False)
            preferences=replace(RuntimePreferences.from_frame(sample_preferences()),
                first_language='English',second_language='Spanish',learned_by='Czech')
            context=AppContext(files_dir=folder,preferences=preferences)
            context.bind(self.root)
            window=StatisticsWindow(self.root)
            window.app_context=context
            controller=StatisticsController(window);window.controller=controller
            with patch('app.statistics.viewer.Generate_chart'):
                window.load(controller.build)
                deadline=monotonic()+15
                while not window.ready and monotonic()<deadline:
                    self.root.update();sleep(.005)
                self.assertTrue(window.ready)
                self.assertEqual(len(controller.vocabulary_tags_panel.visible),2)
                for item in controller.vocabulary_tags_panel.visible:
                    self.assertEqual((item.words,item.successes,item.failures),(1,1,1))
            window.destroy()

"""Transaction failures, cache invalidation and responsive statistics lifecycle."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, get_ident
from time import perf_counter, sleep
from unittest import TestCase
from unittest.mock import patch
import gc
import weakref
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.tests.context_helpers import patch_preferences
from app.tests.test_editor_save import course
from app.shared.storage import save_csv, file_revision, FileChangedError
from app.repositories.csv_store import commit_document
from app.vocabulary import save_workflow
from app.vocabulary.editor_synonym_columns import SynonymCounts, add_columns


class TransactionTests(TestCase):
    def test_unchanged_conjugation_dates_do_not_become_nat_text(self):
        from app.repositories.conjugation import save_results
        from app.conjugation.data import select_verbs
        with TemporaryDirectory() as directory:
            path=Path(directory)/'verbs.csv'
            original=pd.DataFrame({'ID':[1], 'R':['S'], 'LR':['']})
            original.to_csv(path,sep=';',index=False)
            save_results(original,select_verbs(original,1),path)
            self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False).LR.tolist(),[''])

    def test_diagnostics_never_logs_exception_secret_text(self):
        from app.shared.diagnostics import report_error
        with self.assertLogs('vocabpro',level='ERROR') as logs:
            try:raise ValueError('https://service.invalid?key=secret-token')
            except ValueError as error:report_error(error,operation='test provider')
        self.assertNotIn('secret-token','\n'.join(logs.output))
        self.assertIn('ValueError','\n'.join(logs.output))

    def test_new_file_collision_at_publish_never_overwrites_competitor(self):
        import os
        with TemporaryDirectory() as directory:
            path=Path(directory)/'new.csv';link=os.link
            def concurrent(source,target):
                Path(target).write_text('external',encoding='utf-8')
                return link(source,target)
            with patch('app.shared.storage.os.link',side_effect=concurrent):
                with self.assertRaises(FileChangedError):commit_document(path,pd.DataFrame({'ID':[1]}),None)
            self.assertEqual(path.read_text(encoding='utf-8'),'external')

    def test_failed_csv_commit_rolls_back_audio_and_synonyms(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'Czech_English_voc.csv'
            frame=course();frame.to_csv(path,sep=';',index=False)
            audio=folder/'1.mp3';audio.write_bytes(b'original')
            before=path.read_bytes()
            def enrich(edited,language,stage,**kwargs):
                (Path(stage)/'1.mp3').write_bytes(b'generated')
                return edited
            with patch.object(save_workflow,'enrich_attributes',side_effect=enrich),patch.object(save_workflow,'save_csv',side_effect=PermissionError):
                with self.assertRaises(PermissionError):
                    save_workflow.save_course(frame,path,'English',folder,file_revision(path),Event(),None)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(audio.read_bytes(),b'original')

    def test_synonym_count_cache_reuses_reads_and_invalidates_on_disk_change(self):
        from app.repositories import synonyms
        with TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_voc.csv'
            words=pd.concat([course(),course()],ignore_index=True);words['ID']=[1,2];words.to_csv(path,sep=';',index=False)
            cache=SynonymCounts()
            with patch.object(synonyms,'load',wraps=synonyms.load) as read:
                for _ in range(10):self.assertEqual(add_columns(words,path,cache)['Synonym count'].tolist(),[0,0])
                self.assertEqual(read.call_count,1)
                pd.DataFrame([[1,2,'2026-11-15']],columns=synonyms.COLUMNS).to_csv(synonyms.relation_path(path),sep=';',index=False)
                self.assertEqual(add_columns(words,path,cache)['Synonym count'].tolist(),[1,1])
                self.assertEqual(read.call_count,2)

    def test_recycled_id_does_not_inherit_stale_links_and_failed_save_restores_them(self):
        from app.repositories import synonyms
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'Czech_English_voc.csv'
            original=course();original.to_csv(path,sep=';',index=False)
            relation=synonyms.relation_path(path)
            pd.DataFrame([[1,2,'2026-11-15']],columns=synonyms.COLUMNS).to_csv(relation,sep=';',index=False)
            before=relation.read_bytes();edited=pd.concat([original,original],ignore_index=True)
            edited['ID']=[1,2];edited=edited.drop(columns='Created')
            real_save=save_workflow.save_csv
            def fail_final(frame,target,**kwargs):
                if Path(target)==path:raise PermissionError('CSV locked')
                return real_save(frame,target,**kwargs)
            with patch.object(save_workflow,'enrich_attributes',side_effect=lambda frame,*a,**kw:frame):
                with patch.object(save_workflow,'save_csv',side_effect=fail_final):
                    with self.assertRaises(PermissionError):
                        save_workflow.save_course(edited,path,'English',folder,file_revision(path),Event(),None)
                self.assertEqual(relation.read_bytes(),before)
                save_workflow.save_course(edited,path,'English',folder,file_revision(path),Event(),None)
            self.assertTrue(synonyms.load(path,edited)[0].empty)

    def test_archive_failure_leaves_original_audio_and_csv_retryable(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'course.csv';frame=course()
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            audio=folder/'1.mp3';audio.write_bytes(b'original')
            with patch.object(save_workflow,'enrich_attributes',side_effect=lambda frame,*a,**kw:frame), \
                    patch.object(save_workflow,'_archive_audio',side_effect=PermissionError('archive locked')):
                with self.assertRaises(PermissionError):
                    save_workflow.save_course(frame.iloc[:0].drop(columns='Created'),path,'English',folder,file_revision(path),Event(),None)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(audio.read_bytes(),b'original')

    def test_provider_failure_before_commit_preserves_audio(self):
        with TemporaryDirectory() as directory:
            folder=Path(directory);path=folder/'course.csv';frame=course()
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            audio=folder/'1.mp3';audio.write_bytes(b'original')
            with patch.object(save_workflow,'enrich_attributes',side_effect=OSError('provider unavailable')):
                with self.assertRaises(OSError):
                    save_workflow.save_course(frame.drop(columns='Created'),path,'English',folder,file_revision(path),Event(),None)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(audio.read_bytes(),b'original')


class StatisticsLifecycleTests(TestCase):
    def setUp(self):
        self.root=cst.CTk();self.root.geometry('1000x750');self.root.update()
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def wait_until(self,condition,timeout=15):
        end=perf_counter()+timeout
        while not condition() and perf_counter()<end:
            self.root.update();sleep(.005)
        self.assertTrue(condition())

    def test_all_graphs_prepared_with_ui_heartbeat_and_worker_only_calculations(self):
        from app.statistics import viewer
        from app.statistics.window import StatisticsWindow
        with TemporaryDirectory() as directory,patch_preferences(first_language='English',second_language='Spanish',learned_by='Czech'):
            folder=Path(directory);course().to_csv(folder/'Czech_English_voc.csv',sep=';',index=False)
            window=StatisticsWindow(self.root);window.app_context=AppContext(files_dir=folder)
            # Use the patched active preferences snapshot explicitly for the new owner.
            from app.core.context import get_context
            window.app_context.preferences=get_context(self.root).preferences
            controller=viewer.StatisticsController(window);window.controller=controller
            main_thread=get_ident();workers=[];charts=[];beats=[]
            calculate=viewer.prepare_statistics
            def work(*args):workers.append(get_ident());return calculate(*args)
            def chart(*args):charts.append(get_ident())
            def heartbeat():
                if window.winfo_exists() and not window.ready:
                    beats.append(True);self.root.after(5,heartbeat)
            with patch.object(viewer,'prepare_statistics',side_effect=work),patch.object(viewer,'Generate_chart',side_effect=chart):
                window.load(controller.build);heartbeat()
                self.wait_until(lambda:window.ready)
            self.assertEqual(len(charts),4)
            self.assertTrue(all(thread==main_thread for thread in charts))
            self.assertTrue(all(thread!=main_thread for thread in workers))
            self.assertGreater(len(beats),3)
            self.assertFalse(window.statistics_tabs.navigation.cget('values') is None)
            window.destroy()

    def test_close_while_calculating_cancels_delivery_and_releases_controller(self):
        from app.statistics import viewer
        from app.statistics.window import StatisticsWindow
        release=Event();started=Event()
        window=StatisticsWindow(self.root);controller=viewer.StatisticsController(window)
        window.controller=controller;controller.lang_var=cst.StringVar(value='English')
        def slow(*args):started.set();release.wait(5);return None
        with patch.object(viewer,'prepare_statistics',side_effect=slow):
            controller.load();self.assertTrue(started.wait(2))
            task=controller.task;window.destroy();release.set();task.thread.join(2)
            self.assertTrue(task.closed);self.assertFalse(task.thread.is_alive())
        ref=weakref.ref(controller);del controller,window,task;gc.collect()
        self.assertIsNone(ref())

    def test_background_resize_cache_is_bounded(self):
        from app.ui.learning_layout import background
        label=background(self.root)
        photo=label.cget('image')
        for i in range(20):
            self.root.geometry(f'{800+i*4}x{600+i*2}');self.root.update()
            self.root.after(30,self.root.quit);self.root.mainloop()
        self.assertLessEqual(len(photo._scaled_light_photo_images),2)
        label.destroy()

    def test_loading_queues_latest_language_change_without_revealing_stale_content(self):
        from app.statistics.window import StatisticsWindow
        window=StatisticsWindow(self.root);calls=[]
        def initial():calls.append('initial')
        def intermediate():calls.append('intermediate')
        def latest():calls.append('latest')
        window.load(initial);window.load(intermediate);window.load(latest)
        self.wait_until(lambda:window.ready)
        self.assertEqual(calls,['initial','latest'])
        window.destroy()

    def test_real_statistics_reopen_and_language_switch_prepare_all_figures(self):
        from dataclasses import replace
        from app.statistics.viewer import Stats
        with TemporaryDirectory() as directory:
            folder=Path(directory);context=AppContext(files_dir=folder)
            context.preferences=replace(context.preferences,learned_by='Czech',first_language='English',second_language='Spanish')
            english=course().drop(columns='Enabled')
            english.to_csv(folder/'Czech_English_voc.csv',sep=';',index=False)
            english.rename(columns={'English':'Spanish'}).drop(columns='Phonetic').to_csv(folder/'Czech_Spanish_voc.csv',sep=';',index=False)
            pd.DataFrame({'ID':[1],'R':['SF'],'LR':['']}).to_csv(folder/'Czech_Spanish_con.csv',sep=';',index=False)
            pd.DataFrame({'category':['Articles'],'R':['SF']}).to_csv(folder/'Spanish_gra.csv',sep=';',index=False)
            for _ in range(2):
                window=Stats(self.root,context=context)
                self.wait_until(lambda:window.ready,timeout=30)
                controller=window.controller
                self.assertIsNotNone(controller.chart_rep_frm._chart_canvas)
                controller.lang_var.set('Spanish');window.load(controller.load)
                self.wait_until(lambda:window.ready,timeout=30)
                self.assertIsNotNone(controller.chart_con_frm._chart_canvas)
                self.assertFalse(hasattr(window,'grammar_topics_chart'))
                categories=controller.grammar_categories_panel
                self.assertEqual([(item.name,item.questions) for item in categories.visible],[('Articles',1)])
                categories.sort_buttons['questions'].invoke()
                self.assertEqual(categories.sort_key,'questions')
                self.assertFalse(categories.descending)
                window.geometry('1100x760');self.root.update()
                window.destroy()

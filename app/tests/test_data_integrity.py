"""Integrity protection against synthetic damage; never audit production data."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from time import perf_counter
from statistics import median
from unittest import TestCase
from unittest.mock import patch
import json
import pandas as pd
from app.shared.integrity import audit, frame_findings, validate_write, Report, Finding
from app.shared.storage import save_csv
from app.shared.atomic_bytes import save_bytes
from app.shared.messages import UserMessageError
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_grammar_editor import questions


def words(count=2):
    return pd.DataFrame({'ID':[str(i) for i in range(count)], 'Czech':['slovo']*count,
        'Spanish':['palabra']*count,'Audio':['No audio']*count,'Description':['']*count,
        'Example':['']*count,'Repetition':['SF']*count,'Next repetition':['']*count})


class IntegrityTests(TestCase):
    def test_vocabulary_is_reported_even_when_it_has_no_findings(self):
        words().rename(columns={'Spanish':'English'}).to_csv(
            self.folder/'Czech_English_voc.csv',sep=';',index=False)
        report=audit(self.folder)
        self.assertIn('Vocabulary',report.modules)
        self.assertFalse([f for f in report.findings if f.module=='Vocabulary'])
        self.assertIn('Vocabulary',json.loads(report.export())['modules'])

    def test_vocabulary_column_names_are_checked_in_both_audit_modes(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        for column in words().columns:
            frame=words().rename(columns={column:column+' typo'})
            frame.to_csv(path,sep=';',index=False);before=path.read_bytes()
            for quick in (True,False):
                with self.subTest(column=column,quick=quick):
                    report=audit(self.folder,quick=quick)
                    self.assertTrue(any(f.file==path.name and f.code=='Integrity structure' for f in report.findings))
                    self.assertEqual(path.read_bytes(),before)
            with self.assertRaises(UserMessageError):save_csv(frame,path,sep=';',index=False)
            self.assertEqual(path.read_bytes(),before)

    def test_blank_headers_are_invalid_but_custom_columns_are_preserved(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        for column in ('','   '):
            frame=words();frame[column]='custom'
            frame.to_csv(path,sep=';',index=False)
            for quick in (True,False):
                self.assertTrue(any(f.severity=='Critical' for f in audit(self.folder,quick=quick).findings))
        frame=words();frame['Custom note']='custom'
        frame.to_csv(path,sep=';',index=False)
        self.assertFalse([f for f in audit(self.folder).findings if f.severity=='Critical'])

    def setUp(self):
        self.directory=TemporaryDirectory()
        self.folder=Path(self.directory.name)
        sample_preferences().to_csv(self.folder/'settings.csv',sep=';',index=False)
        words().to_csv(self.folder/'Czech_Spanish_voc.csv',sep=';',index=False)

    def tearDown(self):
        self.directory.cleanup()

    def test_valid_data_empty_optional_fields_and_legacy_records_are_supported(self):
        questions().to_csv(self.folder/'Spanish_gra.csv',sep=';',index=False)
        pd.DataFrame({'best_streak':['5']}).to_csv(self.folder/'Spanish_gra_records.csv',sep=';',index=False)
        pd.DataFrame({'Category':[],'Title':[]}).to_csv(self.folder/'Czech_Spanish_gra_ex.csv',sep=';',index=False)
        report=audit(self.folder)
        self.assertTrue(report.completed)
        self.assertFalse([f for f in report.findings if f.severity=='Critical'])
        self.assertGreater(report.records,2)

    def test_duplicate_headers_missing_fields_and_malformed_csv(self):
        path=self.folder/'Spanish_gra.csv'
        for content in ('question_id;question_id\n1;2\n','question_id\n1\n',
                        'question_id;prompt\n1;"unterminated'):
            with self.subTest(content=content):
                path.write_text(content,encoding='utf-8')
                report=audit(self.folder)
                self.assertTrue(any(f.file==path.name and f.severity=='Critical' for f in report.findings))
                self.assertEqual(path.read_text(encoding='utf-8'),content)
        duplicated=questions();duplicated=pd.concat([duplicated.iloc[:1],duplicated.iloc[:1]],ignore_index=True)
        duplicated.to_csv(path,sep=';',index=False)
        self.assertTrue(any(f.file==path.name and f.code=='Integrity identifier' for f in audit(self.folder).findings))

    def test_numeric_identifier_aliases_and_bad_types_are_rejected(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        for identifiers in (['1','01'],['x','2'],['','2']):
            frame=words();frame.ID=identifiers
            self.assertTrue(any(f.severity=='Critical' for f in frame_findings(frame,path)))
        blank=words().iloc[:0].copy();blank.loc[0]=['']*len(blank.columns)
        blank.to_csv(path,sep=';',index=False)
        self.assertTrue(any(f.code=='Integrity identifier' for f in audit(self.folder).findings))

    def test_synonyms_validate_references_self_links_and_undirected_duplicates(self):
        path=self.folder/'Czech_Spanish_synonyms.csv'
        for pairs in ((('0','9'),),(('0','0'),),(('0','1'),('1','0'))):
            pd.DataFrame([(a,b,'2026-11-17') for a,b in pairs],columns=['ID 1','ID 2','Date']).to_csv(path,sep=';',index=False)
            report=audit(self.folder)
            self.assertTrue(any(f.file==path.name and f.severity=='Critical' for f in report.findings))

    def test_valid_synonyms_and_optional_blank_translation_in_tag_catalog(self):
        pd.DataFrame([('0','1','2026-11-17')],columns=['ID 1','ID 2','Date']).to_csv(
            self.folder/'Czech_Spanish_synonyms.csv',sep=';',index=False)
        pd.DataFrame([('1','zvířata','','')],columns=['ID','Czech','Spanish','Note']).to_csv(
            self.folder/'Czech_Spanish_tags.csv',sep=';',index=False)
        self.assertFalse([f for f in audit(self.folder).findings if f.severity=='Critical'])

        # Tag readers require exact row widths even when a translation is empty.
        catalog=self.folder/'Czech_Spanish_tags.csv'
        catalog.write_text('ID;Czech;Spanish;Note\n1;zvirata;\n',encoding='utf-8')
        self.assertTrue(any(f.file==catalog.name and f.severity=='Critical' for f in audit(self.folder).findings))
        ambiguous=words(3);ambiguous.ID=['0','0','1']
        ambiguous.to_csv(self.folder/'Czech_Spanish_voc.csv',sep=';',index=False)
        relations=pd.DataFrame([('0','1','2026-11-17')],columns=['ID 1','ID 2','Date'])
        with self.assertRaises(UserMessageError):
            save_csv(relations,self.folder/'Czech_Spanish_synonyms.csv',sep=';',index=False)

    def test_unknown_tag_and_conjugation_category_references(self):
        path=self.folder/'Czech_Spanish_con.csv'
        frame=pd.DataFrame({'ID':['a'],'R':['SF'],'LR':[''],'Description':['presente'],
            'Czech':['být'],'Spanish':['ser'],'Category':['missing']})
        frame.to_csv(path,sep=';',index=False)
        self.assertTrue(any(f.code=='Integrity reference' for f in audit(self.folder).findings))
        new_path=self.folder/'Czech_English_con.csv'
        with self.assertRaises(UserMessageError):save_csv(frame,new_path,sep=';',index=False)
        self.assertFalse(new_path.exists())
        frame.Category='';frame.to_csv(path,sep=';',index=False)
        self.assertFalse([f for f in audit(self.folder).findings if f.severity=='Critical'])

    def test_person_configuration_versions_and_history_are_checked_without_inference(self):
        from app.conjugation.persons import default_configuration
        config=default_configuration('Spanish').to_json()
        path=self.folder/'Spanish_con_persons.json'
        path.write_text(config,encoding='utf-8')
        self.assertFalse([f for f in audit(self.folder).findings if f.severity=='Critical'])
        data=json.loads(config);data['version']=99
        path.write_text(json.dumps(data),encoding='utf-8')
        self.assertTrue(any(f.file==path.name and f.severity=='Critical' for f in audit(self.folder).findings))
        frame=pd.DataFrame({'ID':['a'],'R':['S'],'LR':[''],'Person history':['{"version":1,"results":{"s1":"Q"}}']})
        self.assertTrue(any(f.severity=='Critical' for f in frame_findings(frame,self.folder/'Czech_Spanish_con.csv',complete=False)))

    def test_invalid_settings_and_negative_or_multirow_records(self):
        settings=sample_preferences();settings.loc[settings.Name.eq('Learn batch'),'Value']='no'
        self.assertTrue(any(f.severity=='Critical' for f in frame_findings(settings,self.folder/'settings.csv')))
        for frame in (pd.DataFrame({'best_streak':['-1']}),pd.DataFrame({'best_streak':['1','2']})):
            self.assertTrue(any(f.severity=='Critical' for f in frame_findings(frame,self.folder/'Spanish_gra_records.csv')))
        (self.folder/'settings.csv').unlink()
        self.assertTrue(any(f.file=='settings.csv' and f.code=='Integrity missing' and f.severity=='Critical'
            for f in audit(self.folder,quick=True).findings))

    def test_legacy_history_and_invalid_optional_date_are_warnings_only(self):
        frame=words();frame.Repetition='S?F';frame['Next repetition']='not-a-date'
        issues=frame_findings(frame,self.folder/'Czech_Spanish_voc.csv')
        self.assertFalse([f for f in issues if f.severity=='Critical'])
        self.assertEqual({f.code for f in issues},{'Integrity legacy history','Integrity date'})

    def test_audit_does_not_change_any_bytes_or_create_files(self):
        (self.folder/'Czech_Spanish_voc.csv').write_bytes(b'corrupt\xff')
        before={p.name:p.read_bytes() for p in self.folder.iterdir()}
        for quick in (True,False):audit(self.folder,quick=quick)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.folder.iterdir()})

    def test_cancelled_audit_is_incomplete_and_never_claims_success(self):
        stop=Event()
        report=audit(self.folder,cancelled=stop,progress=lambda *_:stop.set())
        self.assertFalse(report.completed)
        self.assertEqual(report.finished,'')

    def test_concurrent_change_discards_cross_file_findings(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        def change(state,total):
            if state[0]==1:path.write_text('ID\nchanged\n',encoding='utf-8')
        report=audit(self.folder,progress=change)
        self.assertFalse(report.completed)
        self.assertEqual([f.code for f in report.findings],['Integrity changed'])

    def test_invalid_write_and_atomic_failure_preserve_original_file(self):
        path=self.folder/'Czech_Spanish_voc.csv';before=path.read_bytes()
        frame=words();frame.ID=['1','1']
        with self.assertRaises(UserMessageError):save_csv(frame,path,sep=';',index=False)
        self.assertEqual(path.read_bytes(),before)
        with patch('app.shared.storage.os.replace',side_effect=OSError('simulated')):
            with self.assertRaises(OSError):save_csv(words(),path,sep=';',index=False)
        self.assertEqual(path.read_bytes(),before)
        self.assertFalse(list(self.folder.glob('*.tmp')))

    def test_known_damage_cannot_be_silently_overwritten_but_external_restore_is_allowed(self):
        path=self.folder/'Czech_Spanish_voc.csv';path.write_text('broken',encoding='utf-8')
        audit(self.folder,quick=True)
        with self.assertRaises(UserMessageError):save_csv(words(),path,sep=';',index=False)
        self.assertEqual(path.read_text(encoding='utf-8'),'broken')
        words().to_csv(path,sep=';',index=False)
        save_csv(words(),path,sep=';',index=False)
        from app.shared.integrity import protect
        # Simulate a resolved permission/read failure with unchanged file bytes.
        protect(Report(findings=[Finding('Critical','Vocabulary',path.name,'Integrity unreadable')],completed=True),self.folder)
        audit(self.folder,quick=True)
        with self.assertRaises(UserMessageError):save_csv(words(),path,sep=';',index=False)
        audit(self.folder)
        save_csv(words(),path,sep=';',index=False)

    def test_person_json_write_is_validated_before_replacing_original(self):
        from app.conjugation.persons import default_configuration
        path=self.folder/'Spanish_con_persons.json'
        original=default_configuration('Spanish').to_json().encode('utf-8')
        save_bytes(path,original)
        with self.assertRaises(ValueError):save_bytes(path,b'{"version":999}')
        self.assertEqual(path.read_bytes(),original)

    def test_new_invalid_history_and_dates_are_rejected_but_old_values_survive(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        for column,value in (('Repetition','S?F'),('Next repetition','invalid-date')):
            frame=words();frame[column]=value;before=path.read_bytes()
            with self.assertRaises(UserMessageError):save_csv(frame,path,sep=';',index=False)
            self.assertEqual(path.read_bytes(),before)
            frame.to_csv(path,sep=';',index=False)
            frame['Description']='updated'
            save_csv(frame,path,sep=';',index=False)
            self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False)[column].iloc[0],value)
            if column=='Repetition':
                frame[column]=value+'SF'
                save_csv(frame,path,sep=';',index=False)
                self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False)[column].iloc[0],value+'SF')
            words().to_csv(path,sep=';',index=False)

    def test_damaged_existing_header_is_protected_without_prior_audit(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        for content in ('ID;ID\n1;2\n','"unterminated header'):
            path.write_text(content,encoding='utf-8');before=path.read_bytes()
            with self.assertRaises(UserMessageError):save_csv(words(),path,sep=';',index=False)
            self.assertEqual(path.read_bytes(),before)

    def test_cancel_while_waiting_for_writer_releases_worker(self):
        from threading import Thread
        from app.shared.storage import destination_lock
        stop=Event();entered=Event();results=[]
        def progress(*_):entered.set()
        with destination_lock(self.folder/'Czech_Spanish_voc.csv'):
            worker=Thread(target=lambda:results.append(audit(self.folder,cancelled=stop,progress=progress)))
            worker.start();self.assertTrue(entered.wait(2))
            stop.set();worker.join(1)
            self.assertFalse(worker.is_alive())
        self.assertFalse(results[0].completed)

    def test_unknown_tag_is_reported_and_new_invalid_reference_is_not_saved(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        catalog=self.folder/'Czech_Spanish_tags.csv'
        pd.DataFrame([('1','known','','')],columns=['ID','Czech','Spanish','Note']).to_csv(catalog,sep=';',index=False)
        frame=words();frame['Tags']='999';before=path.read_bytes()
        with self.assertRaises(UserMessageError):save_csv(frame,path,sep=';',index=False)
        self.assertEqual(path.read_bytes(),before)
        frame.to_csv(path,sep=';',index=False)
        self.assertTrue(any(f.code=='Integrity reference' for f in audit(self.folder).findings))

    def test_quick_check_defers_unusually_large_configuration(self):
        path=self.folder/'Spanish_con_persons.json';path.write_text(' '*70000,encoding='utf-8')
        self.assertTrue(any(f.code=='Integrity deferred' for f in audit(self.folder,quick=True).findings))

    def test_invalid_optional_filter_warns_but_cannot_be_newly_introduced(self):
        path=self.folder/'settings.csv';frame=sample_preferences()
        frame.loc[len(frame)]=['Saved grammar category filters','JSON','invalid-json']
        original=path.read_bytes()
        with self.assertRaises(UserMessageError):save_csv(frame,path,sep=';',index=False)
        self.assertEqual(path.read_bytes(),original)
        frame.to_csv(path,sep=';',index=False)
        report=audit(self.folder)
        self.assertTrue(any(f.module=='Settings' and f.code=='Integrity values' and f.severity=='Warning' for f in report.findings))
        frame.loc[frame.Name.eq('Learn batch'),'Value']='20'
        save_csv(frame,path,sep=';',index=False)
        self.assertEqual(pd.read_csv(path,sep=';').set_index('Name').at['Saved grammar category filters','Value'],'invalid-json')

    def test_diagnostic_export_never_contains_setting_values_or_paths(self):
        settings=sample_preferences();settings.loc[settings.Name.eq('11Labs token'),'Value']='secret-token-123'
        settings.to_csv(self.folder/'settings.csv',sep=';',index=False)
        payload=audit(self.folder).export()
        self.assertNotIn('secret-token-123',payload)
        self.assertNotIn(str(self.folder),payload)
        self.assertNotIn('synthetic-test-value',payload)

    def test_quick_check_is_bounded_and_full_check_performance_is_reported(self):
        path=self.folder/'Czech_Spanish_voc.csv'
        words(10000).to_csv(path,sep=';',index=False)
        start=perf_counter();quick=audit(self.folder,quick=True);quick_time=perf_counter()-start
        start=perf_counter();full=audit(self.folder);full_time=perf_counter()-start
        self.assertLess(quick.records,1000)
        self.assertGreaterEqual(full.records,10000)
        self.assertLess(quick_time,1)
        self.assertLess(full_time,10)
        self.assertTrue(quick.completed and full.completed)
        # Measure the actual write-boundary cost against the same atomic writer.
        frame=words(1000)
        save_csv(frame,path,sep=';',index=False)
        before,after=[],[]
        for _ in range(5):
            with patch('app.shared.integrity.validate_write'):
                start=perf_counter();save_csv(frame,path,sep=';',index=False);before.append(perf_counter()-start)
            start=perf_counter();save_csv(frame,path,sep=';',index=False);after.append(perf_counter()-start)
        baseline,validated=median(before),median(after)
        print(f'PERF integrity 10000 rows: quick {quick_time*1000:.2f} ms; full {full_time*1000:.2f} ms; atomic save 1000 rows: baseline {baseline*1000:.2f} ms / validated {validated*1000:.2f} ms')


class IntegrityUITests(TestCase):
    def test_clean_vocabulary_is_selectable_and_last_audit_date_is_not_displayed(self):
        from app.preferences.integrity import IntegrityPanel
        self.root.app_context.last_integrity_audit='PRIVATE-OLD-DATE'
        report=Report(completed=True,finished='PRIVATE-NEW-DATE',modules=['Vocabulary','Settings'])
        panel=IntegrityPanel(self.root,self.folder,lambda key:key,report=report)
        self.assertIn('Vocabulary',panel.area.cget('values'))
        panel.area.set('Vocabulary');panel.show_page(0)
        self.assertIn('Integrity no findings',panel.results.get('1.0','end'))
        self.assertNotIn('PRIVATE-',panel.status.cget('text'))
        panel.destroy()

    def setUp(self):
        import customtkinter as cst
        from app.core.context import AppContext
        self.directory=TemporaryDirectory();self.folder=Path(self.directory.name)
        sample_preferences().to_csv(self.folder/'settings.csv',sep=';',index=False)
        self.root=cst.CTk();self.root.geometry('1080x760')
        AppContext(files_dir=self.folder).bind(self.root)
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for widget in tuple(self.root.winfo_children()):widget.destroy()
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy();self.directory.cleanup()
        self.assertEqual(self.errors,[])

    def test_async_results_and_cancel_keep_tk_callbacks_on_main_thread(self):
        from app.preferences.integrity import open_integrity,IntegrityPanel
        dialog=open_integrity(self.root,self.folder,lambda value:value)
        panel=next(w for w in dialog.winfo_children() if isinstance(w,IntegrityPanel))
        panel.start()
        deadline=perf_counter()+5
        while panel.report is None and perf_counter()<deadline:self.root.update()
        self.assertIsNotNone(panel.report)
        self.assertTrue(panel.report.completed)
        self.assertEqual(panel.run.cget('state'),'normal')
        self.assertIn('Integrity summary',panel.status.cget('text'))
        panel.start();panel.stop();task=panel.task;dialog.destroy();self.root.update()
        self.assertTrue(task.closed)

    def test_pagination_and_export_do_not_overwrite_user_data(self):
        from app.preferences.integrity import open_integrity,IntegrityPanel
        report=Report(findings=[Finding('Warning','Grammar','Spanish_gra.csv','Integrity date',i) for i in range(120)],completed=True)
        dialog=open_integrity(self.root,self.folder,lambda value:value,report)
        panel=next(w for w in dialog.winfo_children() if isinstance(w,IntegrityPanel))
        self.assertEqual(panel.results.get('1.0','end').count('Spanish_gra.csv'),50)
        panel.show_page(99);self.assertEqual(panel.results.get('1.0','end').count('Spanish_gra.csv'),20)
        path=self.folder/'settings.csv';before=path.read_bytes()
        with patch('app.preferences.integrity.filedialog.asksaveasfilename',return_value=str(path)),patch('app.ui.messagebox.showerror') as error:
            panel.export_report();error.assert_called_once()
        self.assertEqual(path.read_bytes(),before)
        dialog.destroy()

    def test_startup_check_runs_once_and_failed_refresh_keeps_existing_screen(self):
        from app.main import main_proc
        from app.shared.integrity import audit as real_audit
        import customtkinter as cst
        with patch('app.shared.integrity.audit',wraps=real_audit) as check,patch('app.main._try_bkp'),\
                patch('app.main._load_vocab_stats',return_value={}),patch('app.main._build_menu'),patch('app.main._build_main_window'):
            main_proc(self.root);main_proc(self.root)
        check.assert_called_once_with(self.folder,quick=True)
        screen=cst.CTkFrame(self.root);screen.pack()
        with patch('app.main._try_bkp'),patch('app.main._load_vocab_stats',side_effect=ValueError('synthetic')):
            main_proc(self.root)
        self.assertTrue(screen.winfo_exists())

    def test_corrupt_settings_have_recovery_ui_and_are_never_reset(self):
        from app.main import main_proc
        path=self.folder/'settings.csv';path.write_text('broken',encoding='utf-8')
        main_proc(self.root)
        self.assertEqual(path.read_text(encoding='utf-8'),'broken')
        self.assertTrue(self.root.winfo_children())
        self.assertTrue(any(f.severity=='Critical' for f in self.root.app_context.startup_integrity.findings))

    def test_report_export_is_asynchronous_and_contains_only_diagnostics(self):
        from app.preferences.integrity import open_integrity,IntegrityPanel
        report=Report(findings=[Finding('Warning','Grammar','Spanish_gra.csv','Integrity date',2)],completed=True)
        dialog=open_integrity(self.root,self.folder,lambda value:value,report)
        panel=next(w for w in dialog.winfo_children() if isinstance(w,IntegrityPanel))
        with TemporaryDirectory() as exported:
            path=Path(exported)/'report.json'
            with patch('app.preferences.integrity.filedialog.asksaveasfilename',return_value=str(path)):
                panel.export_report()
            deadline=perf_counter()+5
            while not panel.task.closed and perf_counter()<deadline:self.root.update()
            self.assertTrue(panel.task.closed)
            document=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(document['version'],1)
            self.assertEqual(document['findings'][0]['row'],2)
            self.assertIn('description',document['findings'][0])
            self.assertEqual(panel.run.cget('state'),'normal')
        dialog.destroy()

    def test_settings_include_a_separate_integrity_tab(self):
        from app.preferences.dialog import PreferencesDialog
        from app.preferences.integrity import IntegrityPanel
        with patch('app.ui.surfaces.PanelSurface.paint'):
            dialog=PreferencesDialog(self.root,lambda value:value,self.folder/'settings.csv')
            self.assertIsInstance(dialog.integrity_panel,IntegrityPanel)
            dialog.tabs.set('Data integrity');self.root.update()
            self.assertTrue(dialog.integrity_panel.winfo_exists())
            dialog.destroy()

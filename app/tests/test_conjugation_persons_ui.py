"""Dynamic editors/training, person controls, locale layout and worker statistics."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import get_ident
from time import perf_counter
from unittest import TestCase
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.preferences.courses import StudyCourse, COURSE_FIELD, encode_courses
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import load_preferences, save_preferences
from app.repositories.conjugation_persons import load_configuration, save_configuration, configuration_path
from app.conjugation.persons import Person, default_configuration
from app.conjugation.history import HISTORY_COLUMN, decode_history
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_conjugation_model import verbs


LOCALES=('en','cs','sk','de','es','fr')


class ConjugationPersonsUiTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.files=Path(self.folder.name)
        self.settings=self.files/'settings.csv';settings=sample_preferences()
        settings.loc[len(settings)]=['Random repeat batch - Conjugation','Int','10']
        settings.to_csv(self.settings,sep=';',index=False)
        self.courses=(StudyCourse('es',conjugation_enabled=True),StudyCourse('en',conjugation_enabled=True))
        saved=save_preferences(load_preferences(self.settings),{COURSE_FIELD:encode_courses('cs',self.courses)},self.settings)
        self.root=cst.CTk();self.root.geometry('1280x850')
        self.context=AppContext(files_dir=self.files,preferences=RuntimePreferences.from_frame(saved))
        self.context.bind(self.root);self.context.on_home=Mock()
        self.path=self.context.conjugation_path('Spanish');verbs().to_csv(self.path,sep=';',index=False)
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for child in tuple(self.root.winfo_children()):child.destroy()
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy();self.folder.cleanup();self.assertEqual(self.errors,[])

    def people(self,count=10):
        config,revision=load_configuration(self.files,'es',self.path)
        extra=tuple(Person.create('vos · variante regional '+str(i)) for i in range(count-len(config.persons)))
        config=replace(config,persons=(*config.persons,*extra),practice_person_ids=tuple(p.id for p in (*config.persons,*extra)))
        save_configuration(self.files,config,revision)
        frame=verbs()
        for person in config.persons:frame[person.id]=person.id
        frame.to_csv(self.path,sep=';',index=False)
        return config

    def test_person_dialog_renames_reorders_deactivates_and_saves_selection_without_changing_csv(self):
        from app.conjugation.persons_dialog import PersonsDialog
        self.people();before=self.path.read_bytes()
        dialog=PersonsDialog(self.root,'es',files=self.files,source='cs',translate=self.context.translate)
        dialog.present();self.root.update();old=dialog.rows[0]['person'].id
        dialog.rows[0]['label'].set('yo / primera persona');dialog.move(0,1)
        self.assertEqual(dialog.rows[1]['person'].id,old)
        dialog.rows[1]['enabled'].set(False);dialog.rows[2]['practice'].set(False)
        dialog.add();new_id=dialog.rows[-1]['person'].id;dialog.rows[-1]['label'].set('otra persona')
        dialog.rows[-1]['practice'].set(True)
        self.assertTrue(dialog.save());self.assertEqual(self.path.read_bytes(),before)
        saved,_=load_configuration(self.files,'es',self.path)
        self.assertEqual(saved.persons[1].id,old);self.assertEqual(saved.persons[1].label,'yo / primera persona')
        self.assertFalse(saved.persons[1].enabled);self.assertNotIn(old,saved.practice_person_ids)
        self.assertIn(new_id,saved.practice_person_ids)

    def test_person_validation_and_failed_save_leave_dialog_open_and_cancel_keeps_original_config(self):
        from app.conjugation.persons_dialog import PersonsDialog
        path=configuration_path(self.files,'es');before=path.read_bytes()
        dialog=PersonsDialog(self.root,'es',files=self.files,source='cs',translate=self.context.translate)
        dialog.add();self.assertFalse(dialog.save());self.assertTrue(dialog.winfo_exists())
        dialog.rows[-1]['label'].set('vos')
        with patch('app.conjugation.persons_dialog.save_configuration',side_effect=PermissionError('synthetic lock')):
            self.assertFalse(dialog.save())
        self.assertEqual(path.read_bytes(),before)
        with patch('app.conjugation.persons_dialog.messagebox.askyesnocancel',return_value=None):dialog.close()
        self.assertTrue(dialog.winfo_exists())
        with patch('app.conjugation.persons_dialog.messagebox.askyesnocancel',return_value=False):dialog.close()
        self.assertEqual(path.read_bytes(),before)

    def test_person_dialog_controls_fit_all_locales_at_minimum_width(self):
        from app.conjugation.persons_dialog import PersonsDialog
        self.people()
        for locale in LOCALES:
            with self.subTest(locale=locale):
                self.context.preferences=replace(self.context.preferences,app_language=locale)
                dialog=PersonsDialog(self.root,'es',files=self.files,source='cs',translate=self.context.translate)
                dialog.geometry('740x560');dialog.present();self.root.update()
                self.assertEqual(len(dialog.rows),10)
                for row in dialog.rows:
                    self.assertGreater(row['entry'].winfo_width(),90)
                    card=row['entry'].master
                    for widget in card.winfo_children():
                        self.assertLessEqual(widget.winfo_x()+widget.winfo_width(),card.winfo_width()+2)
                dialog.destroy()

    def test_dynamic_editor_fits_all_locales_and_keeps_inactive_fields_on_save(self):
        from app.conjugation.editor import Edit_conjugation
        config=self.people(13)
        config=replace(config,persons=tuple(replace(p,enabled=False) if p.id=='s2' else p for p in config.persons),
                       practice_person_ids=tuple(key for key in config.practice_person_ids if key!='s2'))
        revision=load_configuration(self.files,'es',self.path)[1];save_configuration(self.files,config,revision)
        before=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                self.context.preferences=replace(self.context.preferences,app_language=locale)
                editor=Edit_conjugation(self.root,'Spanish',context=self.context);self.root.update()
                self.assertEqual(len(editor.tables.fields),16);self.assertNotIn('s2',editor.tables.fields)
                self.assertGreater(editor.view.sheet.winfo_width(),800)
                editor.view.sheet.set_cell_data(0,editor.tables.fields.index('Description')+1,'edited '+locale)
                self.assertTrue(editor.save(close=False))
                for button in editor.view.tools.buttons.values():
                    self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                editor.lifecycle.close();editor.view.root.destroy()
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        for key in ('ID','R','LR','Custom','s2'):self.assertEqual(saved[key].tolist(),before[key].tolist())

    def test_editor_cancel_save_failure_and_new_verb_keep_screen_and_stable_identity(self):
        from app.conjugation.editor import Edit_conjugation
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        editor.view.sheet.set_cell_data(0,1,'enseñar cambiado')
        with patch('app.ui.messagebox.askyesnocancel',return_value=None):editor.back()
        self.assertFalse(editor.lifecycle.closed)
        before=self.path.read_bytes()
        with patch.object(editor.document,'save',side_effect=PermissionError('synthetic lock')), \
                patch('app.ui.messagebox.showerror') as error:
            self.assertFalse(editor.save());error.assert_called_once()
        self.assertEqual(self.path.read_bytes(),before);self.assertFalse(editor.lifecycle.closed)
        editor.add();row=editor.view.sheet.get_total_rows()-1
        editor.view.sheet.set_cell_data(row,1,'ir')
        editor.view.sheet.set_cell_data(row,editor.tables.fields.index('s1')+1,'voy')
        self.assertTrue(editor.save(close=False));identifier=editor.document.frame.ID.iloc[-1];self.assertNotEqual(identifier,'001')
        self.assertEqual(editor.document.frame.ID.tolist(),['001',identifier])
        self.assertEqual(editor.document.verb('001')['R'],'S?FSS')

    def test_training_uses_more_than_six_fields_and_one_shared_normalization_for_feedback(self):
        from app.conjugation.practise import Conjugation
        config=self.people(10)
        frame=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False);frame['s1']='enseño';frame.to_csv(self.path,sep=';',index=False)
        controller=Conjugation(self.root,'es',context=self.context);self.root.update()
        self.assertEqual(len(controller.view.entries),10)
        answers={person.id:person.id for person in config.persons};answers['s1']=' ENSENO ';answers['s2']='wrong'
        for key,value in answers.items():controller.view.variables[key].set(value)
        controller.confirm();self.root.update()
        from app.ui import learning_layout as ui
        self.assertEqual(controller.view.entries['s1'].cget('fg_color'),ui.SURFACE)
        self.assertEqual(controller.view.entries['s2'].cget('fg_color'),ui.ERROR)
        self.assertEqual(decode_history(controller.session.selection.iloc[0][HISTORY_COLUMN])['s1'],'S')
        self.assertEqual(controller.session.selection.iloc[0].R,'S?FSSF')
        controller.confirm()
        self.assertTrue(controller.lifecycle.closed)
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.iloc[0].R,'S?FSSF')
        self.assertEqual(decode_history(saved.iloc[0][HISTORY_COLUMN])['s2'],'F')

    def test_stats_person_panel_is_retained_unknown_is_not_zero_and_labels_fit_all_locales(self):
        from app.statistics.conjugation_persons_panel import ConjugationPersonsPanel
        from app.statistics.conjugation import PersonStatistics
        items=(PersonStatistics('s1','yo / una etiqueta de persona bastante larga',True,12,3),
               PersonStatistics('s2','tú',False,0,0))
        for locale in LOCALES:
            self.context.preferences=replace(self.context.preferences,app_language=locale)
            self.root.geometry('600x850')
            panel=ConjugationPersonsPanel(self.root,self.context.translate);panel.pack(fill='x')
            panel.set_data(items);self.root.update()
            self.assertIn('—',panel.labels[1].cget('text'))
            for label in (panel.title,panel.description,*panel.labels):
                self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2,label.cget('text'))
                self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2,label.cget('text'))
            widgets=tuple(panel.body.winfo_children());start=perf_counter()
            for _ in range(1000):panel.set_data(items)
            self.assertEqual(tuple(panel.body.winfo_children()),widgets)
            if locale=='en':print(f'PERF conjugation persons: 1000 unchanged updates {(perf_counter()-start)*1000:.2f} ms; retained widgets')
            panel.destroy()

    def test_disabled_home_settings_about_and_direct_entry_points_hide_conjugation(self):
        from app.main import _build_main_window
        from app.conjugation.editor import Edit_conjugation
        from app.conjugation.practise import Conjugation
        from app.preferences.dialog import PreferencesDialog
        from app.about.shortcuts import shortcut_sections
        self.context.preferences=replace(self.context.preferences,
            courses=tuple(replace(c,conjugation_enabled=False) for c in self.courses))
        for entry in (Edit_conjugation,Conjugation):
            with patch('app.repositories.conjugation_persons.load_configuration',side_effect=AssertionError('disabled read')):
                self.assertIsNone(entry(self.root,'es',context=self.context))
        rows=pd.DataFrame({'ID':[1]});item=dict(rep_words=rows,lrn_words=rows,rep_count=1,lrn_count=1,all_count=1,gra_count=1,con_count=1)
        home=_build_main_window(self.root,dict.fromkeys(self.context.preferences.learning_languages,item),self.context)
        def labels(widget):
            for child in widget.winfo_children():
                if isinstance(child,cst.CTkLabel):yield child.cget('text')
                yield from labels(child)
        self.assertNotIn(self.context.translate('Conjugation'),tuple(labels(home)))
        for title,_ in shortcut_sections(conjugation_enabled=False):self.assertNotIn(title,('Conjugation','Conjugation editors'))
        save_preferences(load_preferences(self.settings),{COURSE_FIELD:encode_courses('cs',self.context.preferences.courses)},self.settings)
        dialog=PreferencesDialog(self.root,self.context.translate,self.settings)
        self.assertNotIn('Random repeat batch - Conjugation',dialog.fields)
        self.assertEqual(dialog.course_editor.rows[0]['conjugation'].get(),'0');dialog.destroy()

    def test_real_statistics_worker_collects_person_results_and_switching_language_clears_them(self):
        from app.statistics.viewer import Stats
        from app.statistics.conjugation import person_statistics
        frame=verbs();frame[HISTORY_COLUMN]='{"version":1,"results":{"s1":"SSF"}}';frame.to_csv(self.path,sep=';',index=False)
        main_thread=get_ident();threads=[];messages=[]
        def calculate(*args):threads.append(get_ident());return person_statistics(*args)
        with patch('app.statistics.conjugation.person_statistics',side_effect=calculate), \
                patch('app.ui.messagebox.showerror',side_effect=lambda *args,**kwargs:messages.append(kwargs)):
            window=Stats(self.root,context=self.context,language='Spanish',section='Conjugation')
            def ready():
                deadline=perf_counter()+30
                while not window.ready and not messages and perf_counter()<deadline:self.root.update()
                self.assertEqual(messages,[]);self.assertTrue(window.ready)
            try:
                ready();panel=window.controller.conjugation_persons
                self.assertIn('67%',panel.labels[0].cget('text'))
                self.assertGreater(panel.grid_info()['row'],window.controller.conjugation_table.grid_info()['row'])
                window.controller.lang_var.set('English');window.load(window.controller.load);ready()
                self.assertEqual(len(panel._snapshot[0]),5)
                self.assertTrue(all(p.successes+p.failures==0 for p in panel._snapshot[0]))
                self.assertTrue(all(thread!=main_thread for thread in threads));self.assertEqual(len(threads),2)
            finally:window.destroy()

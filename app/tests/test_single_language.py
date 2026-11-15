"""One active course, reversible preferences and byte-for-byte inactive data safety."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic,sleep
from unittest import TestCase
from unittest.mock import Mock,patch
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences,with_defaults,validate_preferences,PreferenceError
from app.repositories.preferences import load_preferences,save_preferences
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.shared.translations import LANGUAGES
from app.statistics.data import prepare_statistics


class SingleLanguageDataTests(TestCase):
    def test_legacy_defaults_two_languages_and_disabling_preserves_second_values(self):
        frame=with_defaults(sample_preferences())
        original=frame.copy(deep=True)
        config=RuntimePreferences.from_frame(frame)
        self.assertEqual(config.learning_languages,('Spanish','English'))
        updated=validate_preferences(frame,{'Enable second learning language':'0'})
        one=RuntimePreferences.from_frame(updated)
        self.assertEqual(one.learning_languages,('Spanish',))
        self.assertEqual(one.second_language,'English')
        self.assertEqual(one.context_probabilities,config.context_probabilities)
        pd.testing.assert_frame_equal(frame,original)
        restored=RuntimePreferences.from_frame(validate_preferences(updated,{'Enable second learning language':'1'}))
        self.assertEqual(restored,config)

    def test_first_course_required_and_only_active_languages_must_differ(self):
        frame=with_defaults(sample_preferences())
        with self.assertRaises(PreferenceError):validate_preferences(frame,{'First learning language':''})
        with self.assertRaises(PreferenceError):validate_preferences(frame,{'Enable second learning language':'invalid'})
        single=validate_preferences(frame,{'Enable second learning language':'0','First learning language':'English'})
        self.assertEqual(RuntimePreferences.from_frame(single).learning_languages,('English',))
        with self.assertRaises(PreferenceError):validate_preferences(single,{'Enable second learning language':'1'})
        with self.assertRaises(PreferenceError):validate_preferences(single,{'Learned by':'English'})

    def test_save_reload_toggle_never_deletes_or_changes_inactive_files(self):
        from app.main import Load_setting
        with TemporaryDirectory() as folder:
            root=Path(folder);path=root/'settings.csv'
            sample_preferences().to_csv(path,sep=';',index=False)
            inactive={
                'Czech_English_voc.csv':b'ID;Repetition\n',
                'Czech_English_synonyms.csv':b'ID 1;ID 2;Date\n',
                'English_gra.csv':b'question_id;R\n1;SF\n',
                'English_gra_records.csv':b'best_streak\n8\n',
                'Czech_English_con.csv':b'ID;R;LR\n1;SF;\n',
                'Czech_English_tags.csv':b'ID;Czech;English;Note\n1;A;B;\n',
                'Czech_English_gra_ex.csv':b'category;rules\nA;Rule\n',
                'Czech_French_voc.csv':b'ID;Repetition\n'}
            for name,data in inactive.items():(root/name).write_bytes(data)
            audio=root/'audio'/'Czech_English';audio.mkdir(parents=True)
            (audio/'1.wav').write_bytes(b'synthetic audio')
            context=AppContext(files_dir=root)
            for enabled in ('0','1','0','1'):
                save_preferences(load_preferences(path),{'Enable second learning language':enabled},path)
                Load_setting(context)
                self.assertEqual(len(context.preferences.learning_languages),1 if enabled=='0' else 2)
                for name,data in inactive.items():self.assertEqual((root/name).read_bytes(),data)
                self.assertEqual((audio/'1.wav').read_bytes(),b'synthetic audio')
            self.assertFalse((root/'Czech__voc.csv').exists())

    def test_disabled_second_course_is_not_created(self):
        from app.main import Load_setting
        with TemporaryDirectory() as folder:
            root=Path(folder);path=root/'settings.csv'
            frame=with_defaults(sample_preferences())
            frame.loc[frame.Name=='Enable second learning language','Value']='0'
            frame.to_csv(path,sep=';',index=False)
            Load_setting(AppContext(files_dir=root))
            self.assertTrue((root/'Czech_Spanish_voc.csv').exists())
            self.assertFalse((root/'Czech_English_voc.csv').exists())

    def test_main_reads_and_renders_only_the_active_course(self):
        from app import main
        context=AppContext(preferences=replace(RuntimePreferences.from_frame(sample_preferences()),second_language_enabled=False))
        app=Mock()
        with patch.object(main,'Load_setting'),patch.object(main,'_try_bkp'),patch.object(main.s,'Clear_frames'),\
             patch.object(main,'_build_menu'),patch.object(main,'_load_vocab_stats',return_value={}) as load,\
             patch.object(main,'build_home') as build:
            main.main_proc(app,context)
        load.assert_called_once_with('Spanish',context)
        self.assertEqual(build.call_args.args[2],('Spanish',))


class SingleLanguageUiTests(TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.root=cst.CTk();self.root.geometry('1400x900');self.root.update()
        self.context=AppContext(files_dir=Path(self.folder.name),preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root);self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.after_cancel(job)
        self.root.destroy();self.folder.cleanup()
        self.assertEqual(self.errors,[])

    def test_toggle_disables_second_language_parameters_and_keeps_values_all_locales(self):
        from app.preferences.dialog import PreferencesDialog
        path=Path(self.folder.name)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
        before=path.read_bytes()
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            dialog=PreferencesDialog(self.root,self.context.translate,path);dialog.deiconify();self.root.update()
            names=['Second learning language']+[name for name in dialog.fields if '2.lang' in name]
            original={name:dialog.variables[name].get() for name in names}
            for enabled,state in (('0','disabled'),('1','normal')):
                dialog.variables['Enable second learning language'].set(enabled)
                self.root.update()
                for name in names:
                    self.assertEqual(dialog.fields[name].cget('state'),state)
                    self.assertEqual(dialog.variables[name].get(),original[name])
                self.assertEqual(dialog.fields['First learning language'].cget('state'),'normal')
                label=dialog.field_labels['Enable second learning language']
                self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
            dialog.destroy()
        self.assertEqual(path.read_bytes(),before)

    def test_statistics_single_language_and_reactivation_read_existing_data(self):
        from app.statistics.viewer import Stats
        root=Path(self.folder.name)
        english=course().assign(Tags='').drop(columns='Enabled')
        english.to_csv(root/'Czech_English_voc.csv',sep=';',index=False)
        english.rename(columns={'English':'Spanish'}).drop(columns='Phonetic').to_csv(root/'Czech_Spanish_voc.csv',sep=';',index=False)
        originals={p.name:p.read_bytes() for p in root.glob('*.csv')}
        for enabled,requested,expected in ((False,'English','Spanish'),(True,'English','English')):
            self.context.preferences=replace(self.context.preferences,second_language_enabled=enabled)
            with patch('app.statistics.viewer.Generate_chart'),patch('app.statistics.viewer.prepare_statistics',wraps=prepare_statistics) as prepare:
                window=Stats(self.root,context=self.context,language=requested)
                deadline=monotonic()+20
                while not window.ready and monotonic()<deadline:self.root.update();sleep(.005)
                self.assertTrue(window.ready)
                controller=window.controller
                self.assertEqual(controller.lang_var.get(),expected)
                self.assertEqual(controller.language_switch.winfo_manager()!='',enabled)
                self.assertEqual(prepare.call_args.args[2],expected)
                self.assertEqual(int(controller.tot_res_voc_lbl.cget('text')),len(english))
                window.destroy()
        self.assertEqual({p.name:p.read_bytes() for p in root.glob('*.csv')},originals)

    def test_home_has_one_wider_course_and_practises_with_first_language_parameters(self):
        from app.main import _build_main_window
        self.context.preferences=replace(self.context.preferences,second_language_enabled=False)
        rows=pd.DataFrame({'ID':[1]})
        data=dict(rep_words=rows,lrn_words=rows,rep_count=1,lrn_count=1,all_count=1,gra_count=0,con_count=0)
        body=_build_main_window(self.root,{'Spanish':data},self.context);self.root.update()
        cards=[widget for widget in body.winfo_children() if isinstance(widget,cst.CTkFrame)]
        self.assertEqual(len(cards),1)
        self.assertEqual(float(cards[0].place_info()['relwidth']),.44)
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        buttons=[widget for widget in descendants(cards[0]) if isinstance(widget,cst.CTkButton)]
        repeat=next(button for button in buttons if button.cget('text')==self.context.translate('Repeat'))
        with patch('app.vocabulary.practise.Rep') as practise:
            repeat.invoke()
            self.assertEqual(practise.call_args.args[2:],('Spanish',1))

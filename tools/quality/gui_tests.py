"""Small interaction journeys complementing the existing, larger GUI suite."""
from pathlib import Path
import os
import tempfile
import time
import unittest
from unittest.mock import patch,Mock


class Journeys(unittest.TestCase):
    def setUp(self):
        import customtkinter as cst
        from app.core.context import AppContext
        from app.preferences.data import RuntimePreferences
        from app.tests.test_preferences_data import sample_preferences
        self.directory=tempfile.TemporaryDirectory();self.files=Path(self.directory.name)
        self.settings=sample_preferences();self.settings.to_csv(self.files/'settings.csv',sep=';',index=False)
        self.context=AppContext(files_dir=self.files,preferences=RuntimePreferences.from_frame(self.settings))
        self.root=None;self.errors=[];self.quality_metrics={}
        if self._testMethodName!='test_00_real_entrypoint_ready_and_shutdown':
            self.root=cst.CTk();self.root.geometry('1400x900');self.context.bind(self.root)
            self.root.report_callback_exception=lambda *error:self.errors.append(error)
            self.root.update()

    def tearDown(self):
        if self.root is not None and self.root.winfo_exists():
            for widget in tuple(self.root.winfo_children()):widget.destroy()
            for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
            self.root.destroy()
        self.directory.cleanup()
        self.assertEqual(self.errors,[])

    def test_00_real_entrypoint_ready_and_shutdown(self):
        import customtkinter as cst
        import start
        original=cst.CTk.__init__;ready=[];errors=[];destroyed=[]
        build=start.main.main_proc
        began=time.perf_counter()
        def init(root,*args,**kwargs):
            original(root,*args,**kwargs)
            root.report_callback_exception=lambda *error:errors.append(error)
            root.bind('<Destroy>',lambda event:destroyed.append(True) if event.widget is root else None,add='+')
            root.after(20000,root.destroy)
        def main(root,context):
            build(root,context)
            def loaded():
                try:
                    root.update_idletasks()
                    self.assertTrue(root.winfo_ismapped())
                    self.assertTrue(root.winfo_children())
                    self.assertEqual(root.app_context.files_dir,self.files)
                    ready.append((time.perf_counter()-began)*1000)
                    if os.environ.get('QUALITY_PROCESS_STARTED'):
                        self.quality_metrics['startup_process_to_ready_ms']=(time.perf_counter()-float(os.environ['QUALITY_PROCESS_STARTED']))*1000
                    try:
                        import psutil
                        self.quality_metrics['startup_process_rss_mb']=psutil.Process().memory_info().rss/1024**2
                    except ImportError:pass
                except Exception as error:errors.append(error)
                finally:
                    for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
                    root.after(50,lambda:root.tk.call(root.protocol('WM_DELETE_WINDOW')))
            root.after_idle(loaded)
        with patch.object(cst.CTk,'__init__',init),patch('start.AppContext',return_value=self.context),patch('start.main.main_proc',side_effect=main):
            start.run()
        self.assertEqual(errors,[]);self.assertEqual(len(ready),1)
        self.assertEqual(destroyed,[True])
        self.quality_metrics['startup_ready_ms']=ready[0]
        self.assertTrue((self.files/'Czech_Spanish_voc.csv').exists())

    def test_settings_click_validation_save_and_language_reload(self):
        from app.preferences.dialog import PreferencesDialog
        from app.main import Load_setting
        from app.shared.translations import translate
        dialog=PreferencesDialog(self.root,self.context.translate,self.files/'settings.csv')
        dialog.present();self.root.update()
        original=(self.files/'settings.csv').read_bytes()
        field=dialog.fields['Learn batch'];field.delete(0,'end');field.insert(0,'0')
        dialog.header.buttons['save'].invoke();self.root.update()
        self.assertFalse(dialog.saved);self.assertTrue(dialog.error.cget('text'))
        self.assertEqual((self.files/'settings.csv').read_bytes(),original)
        field.delete(0,'end');field.insert(0,'15')
        dialog.variables['App language'].set(dialog.translate('Czech'))
        dialog.header.buttons['save'].invoke();self.assertTrue(dialog.saved)
        Load_setting(self.context)
        self.assertEqual(self.context.preferences.learn_batch,15)
        self.assertEqual(self.context.translate('Setting'),translate('Setting','Czech'))

    def test_grammar_editor_input_save_reload_and_category_statistics(self):
        import pandas as pd
        from app.tests.test_grammar_editor import questions
        from app.grammar.editor import GrammarEditor
        from app.statistics.data import training_statistics
        path=self.files/'English_gra.csv';questions().to_csv(path,sep=';',index=False)
        with patch('app.grammar.editor.messagebox.showinfo'):
            editor=GrammarEditor(self.root,'English',path,Mock());self.root.update()
            editor.view.category_filter.set('Tenses');editor.filter();self.root.update()
            self.assertEqual(editor.view.tree.get_children(),('002',))
            field=editor.view.fields['anchor'];field.delete('1.0','end');field.insert('1.0','Quality audit sentence')
            self.assertTrue(editor.save(close=False))
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertIn('Quality audit sentence',saved.anchor.tolist())
            self.assertEqual(saved.R.tolist(),['SF','SS'])
            self.assertEqual(training_statistics(path,'grammar')['summary'][0],2)

    def test_conjugation_spreadsheet_paste_save_and_isolated_backup_restore(self):
        from app.tests.test_conjugation_model import verbs
        from app.conjugation.editor import Edit_conjugation
        from app.services.backup import backup_files
        from app.shared.atomic_bytes import save_bytes
        from app.repositories.conjugation import load_source
        from app.conjugation.persons import default_configuration
        path=self.files/'Czech_Spanish_con.csv';verbs().to_csv(path,sep=';',index=False)
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        column=editor.tables.fields.index('s1')+1
        editor.view.sheet.set_cell_data(0,column,'auditado')
        self.assertTrue(editor.save(close=False))
        original=path.read_bytes();snapshot=dict(backup_files(self.files))
        self.assertEqual(snapshot[path.name],original)
        # There is no application restore UI. Verify only a byte restore through
        # its atomic writer in an isolated directory; report that scope explicitly.
        restored=self.files/'restored';restored.mkdir()
        target=restored/path.name;save_bytes(target,snapshot[path.name])
        result=load_source(target,'Spanish','Czech',default_configuration('es'))
        self.assertEqual(result.s1.tolist(),['auditado'])
        self.assertEqual(target.read_bytes(),original)

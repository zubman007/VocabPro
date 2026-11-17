"""Actual clipboard parsing, category editing, record layout and statistics launch."""
from dataclasses import replace
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import pandas as pd
from app.tests import test_conjugation_persons_ui as fixtures
from app.tests.test_conjugation_model import verbs
from app.conjugation.editor import Edit_conjugation
from app.conjugation.categories import catalog_path, category_names, ensure_catalog
from app.repositories.practice_records import update_records


class ConjugationSpreadsheetUiTests(TestCase):
    def setUp(self):
        fixtures.ConjugationPersonsUiTests.setUp(self)
        def unexpected_error(*args,**kwargs):raise AssertionError(kwargs)
        error=patch('app.ui.messagebox.showerror',side_effect=unexpected_error)
        error.start();self.addCleanup(error.stop)
    tearDown=fixtures.ConjugationPersonsUiTests.tearDown

    def test_excel_tsv_paste_expands_rows_supports_undo_and_preserves_old_ids_history(self):
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        before=self.path.read_bytes();editor.add()
        data='ir\tjít\tImperativo\tfree text\tvoy\tvas\tva\tvamos\tvais\tvan\nser\tbýt\tPresente\tfree text\tsoy\teres\tes\tsomos\tsois\tson'
        with patch.object(editor.view.sheet.MT,'clipboard_get',return_value=data):editor.view.sheet.paste()
        rows=editor.view.sheet.get_sheet_data()
        self.assertEqual([row[1] for row in rows],['enseñar','ir','ser'])
        self.assertEqual(rows[0][0],'001');self.assertEqual(rows[1][0],'')
        editor.view.sheet.undo();self.assertNotIn('ir',[row[1] for row in editor.view.sheet.get_sheet_data()])
        editor.view.sheet.redo();self.assertEqual(editor.view.sheet.get_sheet_data()[2][1],'ser')
        self.assertEqual(self.path.read_bytes(),before)
        self.assertTrue(editor.save(close=False))
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.ID.iloc[0],'001');self.assertEqual(saved.R.tolist(),['S?FSS','',''])
        self.assertEqual(saved.s1.tolist(),['enseño','voy','soy'])
        self.assertEqual(len(set(saved.ID)),3);self.assertTrue(catalog_path(self.path).exists())
        # A fresh course must accept its first paste without Add row/selection,
        # including languages with a different number of person columns.
        editor.lifecycle.close();editor.view.root.destroy()
        english=Edit_conjugation(self.root,'en',context=self.context);self.root.update()
        self.assertTrue(english.document.frame.empty)
        with patch.object(english.view.sheet.MT,'clipboard_get',return_value='go\tjít\tPresent\tdesc\tgo\tgo\tgoes\tgo\tgo'):
            english.view.sheet.paste()
        self.assertTrue(english.save(close=False))
        self.assertEqual(english.document.frame.English.tolist(),['go'])
        self.assertEqual(english.document.frame.R.tolist(),[''])

    def test_category_sheet_rename_and_protected_used_category_deletion(self):
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        editor.view.tabs.set(self.context.translate('Categories'));editor.add()
        with patch.object(editor.view.category_sheet.MT,'clipboard_get',return_value='Pasado\tA category note'):
            editor.view.category_sheet.paste()
        editor.view.sheet.set_cell_data(0,3,'Pasado')
        self.assertTrue(editor.save(close=False));identifier=editor.document.frame.at[0,'Category']
        row=editor.tables.catalog.index[editor.tables.catalog.ID.eq(identifier)][0]
        editor.view.category_sheet.set_cell_data(row,1,'Pretérito')
        self.assertTrue(editor.save(close=False));self.assertEqual(editor.document.frame.at[0,'Category'],identifier)
        self.assertEqual(category_names(editor.document.frame,editor.tables.catalog).tolist(),['Pretérito'])
        before=self.path.read_bytes();editor.view.category_sheet.delete_rows([row])
        with patch('app.ui.messagebox.showerror') as error:
            self.assertFalse(editor.save(close=False));error.assert_called_once()
        self.assertEqual(self.path.read_bytes(),before)

    def test_filter_edit_and_delete_leave_unseen_records_and_their_histories_untouched(self):
        frame=pd.concat([verbs().assign(Spanish='ir'),verbs().assign(ID='002',Spanish='ser',R='FFFF'),
                         verbs().assign(ID='003',Spanish='hablar',R='SSSS')],ignore_index=True)
        frame.to_csv(self.path,sep=';',index=False)
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        editor.view.query.insert(0,'hablar');editor.filter()
        self.assertEqual(editor.visible_ids,{'003'})
        editor.view.sheet.set_cell_data(0,editor.tables.fields.index('s1')+1,'hablo')
        self.assertTrue(editor.save(close=False))
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.ID.tolist(),['001','002','003']);self.assertEqual(saved.R.tolist(),frame.R.tolist())
        self.assertEqual(saved.s1.tolist(),['enseño','enseño','hablo'])
        editor.view.sheet.select_row(0)
        with patch('app.ui.messagebox.askyesno',return_value=True):editor.delete()
        self.assertTrue(editor.save(close=False));self.assertEqual(editor.document.frame.ID.tolist(),['001','002'])

    def test_extra_pasted_column_is_reported_and_never_truncated_into_saved_data(self):
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update();before=self.path.read_bytes()
        editor.add();data='\t'.join(['verb','translation','category','description',*['form']*6,'unexpected'])
        with patch.object(editor.view.sheet.MT,'clipboard_get',return_value=data):editor.view.sheet.paste()
        with patch('app.ui.messagebox.showerror') as error:
            self.assertFalse(editor.save(close=False));error.assert_called_once()
        self.assertEqual(self.path.read_bytes(),before)

    def test_ctrl_s_from_sheet_stops_after_one_save_even_if_validation_fails(self):
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        editor.view.sheet.MT.focus_force();self.root.update()
        with patch.object(editor,'save',return_value=False) as save:
            editor.view.sheet.MT.event_generate('<Control-s>');self.root.update()
            save.assert_called_once()

    def test_persons_button_refreshes_added_reordered_and_disabled_columns_without_losing_drafts(self):
        from app.conjugation.persons_dialog import PersonsDialog
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        before=self.path.read_bytes();added=[]
        editor.view.sheet.set_cell_data(0,4,'draft description')
        def add_person(owner,language,**kwargs):
            dialog=PersonsDialog(owner,language,**kwargs)
            dialog.rows[0]['label'].set('yo / primera persona');dialog.move(0,1)
            dialog.add();dialog.rows[-1]['label'].set('vos');added.append(dialog.rows[-1]['person'].id)
            return dialog.save()
        with patch('app.conjugation.editor.open_persons',side_effect=add_person):
            editor.view.tools.buttons['persons'].invoke()
        self.assertEqual(editor.tables.fields[4:6],('s2','s1'))
        self.assertIn('yo / primera persona',editor.view.sheet.headers())
        self.assertEqual(editor.view.sheet.get_sheet_data()[0][5:7],['enseñas','enseño'])
        self.assertEqual(editor.document.frame.at[0,'Description'],'draft description')
        self.assertEqual(len(editor.view.sheet.headers()),len(editor.tables.fields)+1)
        editor.view.sheet.set_cell_data(0,editor.tables.fields.index(added[0])+1,'enseñás')
        def deactivate(owner,language,**kwargs):
            dialog=PersonsDialog(owner,language,**kwargs)
            next(row for row in dialog.rows if row['person'].id=='s2')['enabled'].set(False)
            return dialog.save()
        with patch('app.conjugation.editor.open_persons',side_effect=deactivate):
            self.assertTrue(editor.edit_persons())
        self.assertNotIn('s2',editor.tables.fields)
        self.assertEqual(editor.document.frame.at[0,'s2'],'enseñas')
        self.assertEqual(editor.document.frame.at[0,added[0]],'enseñás')
        self.assertEqual(self.path.read_bytes(),before)
        self.assertTrue(editor.save(close=False))
        saved=pd.read_csv(self.path,sep=';',dtype=str,keep_default_na=False)
        self.assertEqual(saved.at[0,'R'],'S?FSS');self.assertEqual(saved.at[0,'s2'],'enseñas')
        self.assertEqual(saved.at[0,added[0]],'enseñás')

    def test_cancelled_persons_dialog_keeps_drafts_and_invalid_rows_do_not_open_it(self):
        editor=Edit_conjugation(self.root,'es',context=self.context);self.root.update()
        before=self.path.read_bytes();headers=list(editor.view.sheet.headers())
        editor.view.sheet.set_cell_data(0,4,'pending')
        with patch('app.conjugation.editor.open_persons',return_value=False) as dialog:
            self.assertFalse(editor.edit_persons());dialog.assert_called_once()
        self.assertEqual(editor.document.frame.at[0,'Description'],'pending')
        self.assertEqual(list(editor.view.sheet.headers()),headers)
        editor.add()
        with patch('app.conjugation.editor.open_persons') as dialog,patch('app.ui.messagebox.showerror'):
            editor.view.sheet.set_cell_data(1,2,'incomplete row')
            self.assertFalse(editor.edit_persons());dialog.assert_not_called()
        self.assertEqual(editor.view.sheet.get_sheet_data()[1][2],'incomplete row')
        self.assertEqual(self.path.read_bytes(),before)

    def test_record_card_highlights_either_record_and_reflows_without_overlap(self):
        from app.conjugation.practise import Conjugation
        frame=pd.concat([verbs().assign(ID=str(i)) for i in range(3)],ignore_index=True)
        frame.to_csv(self.path,sep=';',index=False)
        with update_records(self.path,3,1):pass
        controller=Conjugation(self.root,'es',context=self.context);self.root.update()
        panel=controller.view.records_panel
        self.assertEqual(panel.grid_info()['row'],0);self.assertFalse(panel.new_record)
        for expected in (False,True):
            controller.view.variables['s1'].set('enseño');controller.view.variables['s2'].set('enseñas')
            controller.confirm();self.root.update();self.assertEqual(panel.new_record,expected)
        self.assertEqual(panel.cget('fg_color'),'#f1dfad')
        self.root.geometry('900x800');self.root.update()
        self.assertEqual(panel.grid_info()['row'],2)
        self.assertLessEqual(panel.report._label.winfo_reqwidth(),panel.report.winfo_width()+2)
        self.assertGreaterEqual(controller.view.entries['s1'].winfo_rooty(),panel.winfo_rooty()+panel.winfo_height())
        self.context.preferences=replace(self.context.preferences,show_personal_records=False)
        controller._refresh_records();self.root.geometry('1000x800');self.root.update()
        self.assertFalse(panel.winfo_ismapped());self.assertTrue(controller.view.count.winfo_ismapped())

    def test_new_category_statistics_repeat_only_selected_category_and_keep_return_route(self):
        from app.statistics.viewer import Stats,_practise_conjugation_category
        from app.conjugation.practise import Conjugation
        frame=pd.concat([verbs().assign(ID=str(i),Description='Presente, type' if i<2 else 'Pasado, type') for i in range(3)],ignore_index=True)
        frame.to_csv(self.path,sep=';',index=False);ensure_catalog(self.path,frame)
        errors=[];opened=[]
        def launch(*args,**kwargs):
            controller=Conjugation(*args,**kwargs);opened.append(controller);return controller
        with patch('app.ui.messagebox.showerror',side_effect=lambda *a,**k:errors.append(k)):
            window=Stats(self.root,context=self.context,language='Spanish',section='Conjugation')
            deadline=perf_counter()+30
            while not window.ready and not errors and perf_counter()<deadline:self.root.update()
            self.assertEqual(errors,[]);self.assertTrue(window.ready)
            panel=window.controller.conjugation_categories_panel
            self.assertEqual({item.name:item.questions for item in panel.items},{'Presente':2,'Pasado':1})
            self.assertGreater(panel.grid_info()['row'],window.controller.conjugation_persons.grid_info()['row'])
            with patch('app.conjugation.practise.Conjugation',side_effect=launch):_practise_conjugation_category(window,'Presente')
            self.assertEqual(errors,[]);self.assertEqual(len(opened),1)
            self.assertEqual(set(opened[0].session.selection.ID),{'0','1'})
            self.assertIsNot(opened[0].on_back,self.context.go_home);opened[0].lifecycle.close()

    def test_record_card_labels_fit_all_locales_and_unchanged_state_is_retained(self):
        from types import SimpleNamespace
        from app.conjugation.records_card import ConjugationRecordsCard
        from app.repositories.practice_records import PracticeRecords
        state=SimpleNamespace(correct=12,streak=3,best_streak=7)
        for locale in ('en','cs','sk','de','es','fr'):
            self.context.preferences=replace(self.context.preferences,app_language=locale)
            self.root.geometry('560x800')
            panel=ConjugationRecordsCard(self.root,self.context.translate);panel.pack(fill='x')
            panel.set_state(state,PracticeRecords(6,10),True);self.root.update()
            self.assertTrue(panel.new_record)
            for label in (panel.heading,panel.report):
                self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2)
            with patch.object(panel,'configure') as configure:
                for _ in range(1000):panel.set_state(state,PracticeRecords(6,10),True)
                configure.assert_not_called()
            panel.destroy()

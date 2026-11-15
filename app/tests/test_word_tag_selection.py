"""Catalog-only multiple tag selection and vocabulary save safety."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.tests.test_tag_catalog import catalog
from app.repositories.tags import save_catalog
from app.shared.storage import file_revision, FileChangedError
from app.vocabulary.tags_data import validate_word_tags, UnknownTagError
from app.vocabulary.save_workflow import save_course
from app.vocabulary.editor_tag_picker import WordTagsDialog


class WordTagDataTests(TestCase):
    def test_multiple_selection_canonical_names_duplicates_and_empty_tags(self):
        frame=pd.DataFrame({'ID':[12,15],'Tags':[' zvířata, NADÁVKY, Zvířata ', '']})
        result=validate_word_tags(frame,catalog(),'Czech')
        self.assertEqual(result.Tags.tolist(),['Zvířata, Nadávky',''])
        self.assertEqual(frame.Tags.iloc[0],' zvířata, NADÁVKY, Zvířata ')

    def test_unknown_tag_rejects_whole_batch_and_identifies_word(self):
        frame=pd.DataFrame({'ID':[12,15],'Tags':['Zvířata','invented']})
        with self.assertRaises(UnknownTagError) as raised:
            validate_word_tags(frame,catalog(),'Czech')
        self.assertEqual(raised.exception.word_id,15)
        self.assertEqual(raised.exception.tag,'invented')
        self.assertEqual(frame.Tags.tolist(),['Zvířata','invented'])

    def test_empty_catalog_allows_only_empty_assignments(self):
        frame=pd.DataFrame({'ID':[1],'Tags':['']})
        self.assertEqual(validate_word_tags(frame,catalog().iloc[:0],'Czech').Tags.tolist(),[''])
        frame['Tags']='Zvířata'
        with self.assertRaises(UnknownTagError):validate_word_tags(frame,catalog().iloc[:0],'Czech')

    def test_workflow_rejects_imported_unknown_tag_before_enrichment_or_write(self):
        with TemporaryDirectory() as directory:
            context=AppContext(files_dir=Path(directory),preferences=RuntimePreferences.from_frame(sample_preferences()))
            path=context.vocabulary_path('English');source=course().assign(Tags='')
            source.to_csv(path,sep=';',index=False)
            save_catalog(context.tags_path('English'),catalog(),'Czech','English',None)
            before=path.read_bytes();edited=source.copy();edited['Tags']='unknown'
            with patch('app.vocabulary.save_workflow.enrich_attributes') as enrich:
                with self.assertRaises(UnknownTagError):
                    save_course(edited,path,'English',context.audio_folder('English'),file_revision(path),
                                Event(),lambda *args:None,context=context)
                enrich.assert_not_called()
            self.assertEqual(path.read_bytes(),before)
            self.assertFalse(context.audio_folder('English').exists())

    def test_workflow_canonicalizes_tags_and_rejects_catalog_changed_during_save(self):
        with TemporaryDirectory() as directory:
            context=AppContext(files_dir=Path(directory),preferences=RuntimePreferences.from_frame(sample_preferences()))
            path=context.vocabulary_path('English');source=course().assign(Tags='')
            source.to_csv(path,sep=';',index=False)
            tag_path=context.tags_path('English')
            save_catalog(tag_path,catalog(),'Czech','English',None)
            edited=source.copy();edited['Tags']='zvířata, NADÁVKY'
            def enrich(frame,*args,**kwargs):return frame
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=enrich):
                save_course(edited,path,'English',context.audio_folder('English'),file_revision(path),
                            Event(),lambda *args:None,context=context)
            self.assertEqual(pd.read_csv(path,sep=';',keep_default_na=False).Tags.tolist(),['1, 3'])
            before=path.read_bytes()
            def change_catalog(frame,*args,**kwargs):
                updated=catalog();updated.loc[0,'Czech']='Nový název'
                save_catalog(tag_path,updated,'Czech','English',file_revision(tag_path))
                return frame
            with patch('app.vocabulary.save_workflow.enrich_attributes',side_effect=change_catalog):
                with self.assertRaises(FileChangedError):
                    save_course(edited,path,'English',context.audio_folder('English'),file_revision(path),
                                Event(),lambda *args:None,context=context)
            self.assertEqual(path.read_bytes(),before)


class WordTagUiTests(TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory()
        self.root=cst.CTk();self.root.geometry('1280x900')
        self.context=AppContext(files_dir=Path(self.directory.name),
            preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)
        from dataclasses import replace
        self.context.preferences=replace(self.context.preferences,tag_display_language='Student language')
        save_catalog(self.context.tags_path('English'),catalog(),'Czech','English',None)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy();self.directory.cleanup()

    def test_editor_tag_shortcuts_select_apply_manage_and_cleanup(self):
        from app.vocabulary.editor import EditorController
        from app.vocabulary.editor_tags import TagsDialog
        path=self.context.vocabulary_path('English')
        course().assign(Tags='').to_csv(path,sep=';',index=False)
        original=path.read_bytes()
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update();self.root.focus_force();self.root.update()
        self.root.event_generate('<Control-t>');self.root.update()
        self.assertFalse(any(isinstance(widget,WordTagsDialog) for widget in self.root.winfo_children()))
        controller.edit_tbl.select_cell(0,1)
        controller.edit_tbl.MT.focus_set();self.root.update()
        controller.edit_tbl.MT.event_generate('<Control-t>');self.root.update()
        picker=next(widget for widget in self.root.winfo_children() if isinstance(widget,WordTagsDialog))
        picker.present(modal=True);picker.focus_force();self.root.update()
        picker.event_generate('<Control-f>');self.root.update()
        self.assertIs(picker.focus_get(),picker.search.query._entry)
        picker.checkboxes[0].toggle()
        picker.search.query.event_generate('<Control-Return>');self.root.update()
        self.assertFalse(picker.winfo_exists())
        self.assertEqual(controller.main_df.Tags.iloc[0],'Zvířata')
        self.assertEqual(path.read_bytes(),original)
        self.root.focus_force();self.root.update()
        self.root.event_generate('<Control-Shift-T>');self.root.update()
        self.assertTrue(controller._tags_dialog.winfo_exists())
        self.assertIsInstance(controller._tags_dialog,TagsDialog)
        controller._tags_dialog.destroy()
        controller.edit_frm.destroy();self.root.update()
        self.assertEqual(self.root.bind('<Control-t>'),'')
        self.assertEqual(self.root.bind('<Control-Shift-T>'),'')

    def test_tag_shortcuts_respect_disabled_setting_saving_and_modal_dialogs(self):
        from dataclasses import replace
        from app.vocabulary.editor import EditorController
        course().assign(Tags='').to_csv(self.context.vocabulary_path('English'),sep=';',index=False)
        self.context.preferences=replace(self.context.preferences,tags_enabled=False)
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update()
        self.assertFalse(any('Ctrl+T' in item or 'Ctrl+Shift+T' in item
                             for item in controller.edit_frm._shortcut_hint.items))
        with patch.object(controller,'Open_word_tags') as word_tags,patch.object(controller,'Open_tags') as manage:
            controller.Tag_shortcut();controller.Tag_shortcut(manage=True)
            self.context.preferences=replace(self.context.preferences,tags_enabled=True)
            controller._saving=True
            controller.Tag_shortcut();controller.Tag_shortcut(manage=True)
            controller._saving=False
            dialog=cst.CTkToplevel(self.root);self.root.update();dialog.grab_set()
            controller.Tag_shortcut();controller.Tag_shortcut(manage=True)
            dialog.destroy()
            word_tags.assert_not_called();manage.assert_not_called()

    def test_multi_selection_survives_search_and_cancel_does_not_apply(self):
        values=[]
        dialog=WordTagsDialog(self.root,'English',1,'word','Zvířata',values.append,context=self.context)
        self.root.update()
        dialog.query.set('Insults')
        self.assertEqual(len(dialog.checkboxes),1)
        dialog.checkboxes[0].toggle()
        dialog.query.set('')
        self.assertEqual(len(dialog.selected),2)
        dialog.apply()
        self.assertEqual(values,['Zvířata, Nadávky'])
        dialog=WordTagsDialog(self.root,'English',1,'word',values[0],values.append,context=self.context)
        dialog.clear();dialog.destroy()
        self.assertEqual(values,['Zvířata, Nadávky'])

    def test_selection_rejects_deleted_catalog_tag_on_apply(self):
        values=[]
        dialog=WordTagsDialog(self.root,'English',1,'word','Zvířata',values.append,context=self.context)
        self.root.update()
        path=self.context.tags_path('English')
        save_catalog(path,catalog().iloc[1:],'Czech','English',file_revision(path))
        with patch('app.vocabulary.editor_tag_picker.messagebox.showerror') as errors:
            dialog.apply()
            errors.assert_called_once()
        self.assertEqual(values,[])
        self.assertTrue(dialog.winfo_exists())

    def test_editor_footer_and_picker_fit_all_languages(self):
        from dataclasses import replace
        from app.shared.translations import LANGUAGES
        from app.vocabulary.editor import EditorController
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            course().assign(Tags='').to_csv(self.context.vocabulary_path('English'),sep=';',index=False)
            controller=EditorController(self.root,'English',context=self.context)
            self.root.update()
            footer=controller.edit_frm._manage_tags_button.master.master
            for button in footer.buttons.values():
                self.assertGreaterEqual(button.winfo_rootx(),footer.winfo_rootx())
                self.assertLessEqual(button.winfo_rootx()+button.winfo_width(),footer.winfo_rootx()+footer.winfo_width())
                self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width())
                self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height())
            dialog=WordTagsDialog(self.root,'English',1,'test','',lambda value:None,context=self.context)
            dialog.present();self.root.update()
            self.assertTrue(dialog.checkboxes)
            dialog.destroy()

    def test_editor_footer_assignment_works_with_filtered_rows_and_is_deferred(self):
        from app.vocabulary.editor import EditorController
        path=self.context.vocabulary_path('English')
        original=pd.concat([course().assign(Tags=''),course().assign(ID=7,English='second',Tags='')],ignore_index=True)
        original.to_csv(path,sep=';',index=False);before=path.read_bytes()
        controller=EditorController(self.root,'English',context=self.context);self.root.update()
        self.assertFalse(hasattr(controller.filt_frm,'tags_button'))
        self.assertEqual(controller.edit_frm._word_tags_button.cget('state'),'disabled')
        self.assertEqual(controller.edit_frm._manage_tags_button.master.master.cget('fg_color'),'#d7dfca')
        controller.filt_col_var.set(controller.translate('English'))
        controller.filt_entry_var.set('second');controller.Filter()
        controller.edit_tbl.select_cell(0,1);controller._update_status()
        self.assertEqual(controller.edit_frm._word_tags_button.cget('state'),'normal')
        controller.Open_word_tags();self.root.update()
        dialog=next(widget for widget in self.root.winfo_children() if isinstance(widget,WordTagsDialog))
        for checkbox in dialog.checkboxes:checkbox.toggle()
        dialog.apply()
        self.assertEqual(controller.main_df.set_index('ID').loc[7,'Tags'],'Zvířata, Nadávky')
        self.assertEqual(controller.main_df.set_index('ID').loc[1,'Tags'],'')
        self.assertEqual(controller.edit_tbl.get_cell_data(0,controller.headers.index('Tags')),'Zvířata, Nadávky')
        self.assertEqual(path.read_bytes(),before)
        controller.edit_tbl.set_cell_data(0,controller.headers.index('Tags'),'unknown')
        with patch('app.vocabulary.editor.messagebox.showerror') as errors:
            controller.Save(self.root,None)
            errors.assert_called_once()
        self.assertFalse(controller._saving)
        self.assertEqual(path.read_bytes(),before)

    def test_double_click_tag_cell_opens_picker_without_adding_a_word(self):
        from types import SimpleNamespace
        from app.vocabulary.editor import EditorController
        course().assign(Tags='').to_csv(self.context.vocabulary_path('English'),sep=';',index=False)
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update()
        column=controller.headers.index('Tags')
        controller.edit_tbl.see(0,column);self.root.update()
        table=controller.edit_tbl.MT
        event=SimpleNamespace(widget=table,
            x=(table.col_positions[column]+table.col_positions[column+1])/2-table.canvasx(0),
            y=(table.row_positions[0]+table.row_positions[1])/2-table.canvasy(0))
        self.assertEqual(controller._add_row_below_table(event),'break')
        self.assertEqual(controller.edit_tbl.get_total_rows(),1)
        dialog=next(widget for widget in self.root.winfo_children() if isinstance(widget,WordTagsDialog))
        self.assertEqual(dialog.word_id,1)
        dialog.destroy()

    def test_excel_paste_multiple_rows_and_filtered_paste_keep_word_ids(self):
        from app.vocabulary.editor import EditorController
        path=self.context.vocabulary_path('English')
        source=pd.concat([course().assign(Tags=''),course().assign(ID=7,English='second',Tags='')],ignore_index=True)
        source.to_csv(path,sep=';',index=False)
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update()
        column=controller.headers.index('Tags')
        controller.edit_tbl.select_cell(0,column)
        self.root.clipboard_clear()
        self.root.clipboard_append('Zvířata, Nadávky\nNadávky\n')
        controller.edit_tbl.paste()
        self.assertEqual(controller.main_df.Tags.tolist(),['Zvířata, Nadávky','Nadávky'])
        self.assertEqual(controller.main_df.ID.tolist(),[1,7])
        self.assertEqual(controller.main_df.Repetition.tolist(),source.Repetition.tolist())
        controller.filt_col_var.set(controller.translate('English'))
        controller.filt_entry_var.set('second');controller.Filter()
        controller.edit_tbl.select_cell(0,column)
        self.root.clipboard_clear();self.root.clipboard_append('Zvířata')
        controller.edit_tbl.paste()
        self.assertEqual(controller.main_df.set_index('ID').Tags.to_dict(),{1:'Zvířata, Nadávky',7:'Zvířata'})

    def test_excel_paste_unknown_tag_blocks_save_and_preserves_original_csv(self):
        from app.vocabulary.editor import EditorController
        path=self.context.vocabulary_path('English')
        course().assign(Tags='').to_csv(path,sep=';',index=False)
        original=path.read_bytes()
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update()
        controller.edit_tbl.select_cell(0,controller.headers.index('Tags'))
        self.root.clipboard_clear();self.root.clipboard_append('Zvířata, invented')
        with patch('app.vocabulary.editor.messagebox.showerror') as errors, \
             patch('app.vocabulary.editor.save_course') as save:
            controller.edit_tbl.paste()
            errors.assert_called_once()
            self.assertIn('invented',errors.call_args.kwargs['message'])
            save.assert_not_called()
        self.assertEqual(controller.main_df.Tags.tolist(),[''])
        self.assertEqual(path.read_bytes(),original)
        self.assertFalse(controller._saving)

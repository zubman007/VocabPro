"""Tag catalog contracts and GUI workflows, using only temporary course data."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import customtkinter as cst
import pandas as pd

from app.repositories.tags import load_catalog, save_catalog, validate_catalog, TagValidationError
from app.shared.storage import FileChangedError
from app.tests.test_preferences_data import sample_preferences
from app.preferences.data import RuntimePreferences
from app.core.context import AppContext
from app.vocabulary.editor_tags import TagsDialog


def catalog():
    return pd.DataFrame([['1','Zvířata','Animals',''],['3','Nadávky','Insults','']],
                        columns=['ID','Czech','English','Note'])


class TagCatalogTests(TestCase):
    def test_missing_catalog_does_not_create_a_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'Czech_English_tags.csv'
            frame, revision = load_catalog(path,'Czech','English')
            self.assertIsNone(revision)
            self.assertTrue(frame.empty)
            self.assertFalse(path.exists())

    def test_roundtrip_unicode_extra_columns_optional_translation_and_backup(self):
        from app.repositories.courses import backup_files
        with TemporaryDirectory() as directory:
            path = Path(directory)/'Czech_English_tags.csv'
            original = catalog().assign(Custom=['a; b','é'])
            original.loc[1,'English']=''
            save_catalog(path,original,'Czech','English',None)
            loaded, revision = load_catalog(path,'Czech','English')
            pd.testing.assert_frame_equal(loaded,original)
            self.assertIsNotNone(revision)
            self.assertEqual([name for name,_ in backup_files(Path(directory))],[path.name])
            save_catalog(path,original.iloc[:0],'Czech','English',revision)
            self.assertEqual(list(backup_files(Path(directory))),[])

    def test_invalid_batch_keeps_original_bytes(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'tags.csv'
            save_catalog(path,catalog(),'Czech','English',None)
            before=path.read_bytes()
            _,revision=load_catalog(path,'Czech','English')
            for column,value in [('ID','1'),('ID','1.5'),('ID','0'),('Czech',' zvířata '),
                                 ('Czech',''),('English','two, labels'),('Czech','two\nlabels')]:
                frame=catalog();frame.loc[1,column]=value
                with self.subTest(column=column,value=value), self.assertRaises(TagValidationError) as raised:
                    save_catalog(path,frame,'Czech','English',revision)
                self.assertEqual(raised.exception.row,2)
                self.assertEqual(path.read_bytes(),before)

    def test_stale_save_and_creation_race_do_not_overwrite(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'tags.csv'
            save_catalog(path,catalog(),'Czech','English',None)
            original,revision=load_catalog(path,'Czech','English')
            updated=original.copy();updated.loc[0,'Note']='external update'
            save_catalog(path,updated,'Czech','English',revision)
            before=path.read_bytes()
            for expected in (None,revision):
                with self.assertRaises(FileChangedError):
                    save_catalog(path,original,'Czech','English',expected)
                self.assertEqual(path.read_bytes(),before)

    def test_write_failure_retains_original_and_cleans_temporary_files(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'tags.csv'
            save_catalog(path,catalog(),'Czech','English',None)
            original,revision=load_catalog(path,'Czech','English')
            before=path.read_bytes()
            with patch('app.shared.storage.os.replace',side_effect=PermissionError('locked')):
                with self.assertRaises(PermissionError):
                    save_catalog(path,original,'Czech','English',revision)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(list(Path(directory).glob('*.tmp')),[])
            save_catalog(path,original,'Czech','English',revision)

    def test_bom_load_and_malformed_rows(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'tags.csv'
            path.write_text('ID;Czech;English;Note\n1;Zvířata;Animals;\n',encoding='utf-8-sig')
            frame,_=load_catalog(path,'Czech','English')
            self.assertEqual(frame.Czech.tolist(),['Zvířata'])
            for invalid in ('ID;Czech;English;Note\n1;Short\n','ID;Czech;English;Note;Note\n',
                            'ID;Czech;English;Note\n1;"unterminated'):
                path.write_text(invalid,encoding='utf-8')
                with self.assertRaises(ValueError):load_catalog(path,'Czech','English')

    def test_supplied_catalogs_contain_all_91_labels_and_translations(self):
        from app.paths import FILES_DIR
        for language in ('Spanish','English'):
            frame,_=load_catalog(FILES_DIR/f'Czech_{language}_tags.csv','Czech',language)
            self.assertGreater(len(frame),0)
            self.assertTrue(frame.ID.is_unique)
            self.assertTrue(frame.Czech.str.len().gt(0).all())


class TagCatalogUiTests(TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory()
        self.root=cst.CTk()
        self.root.geometry('1200x800')
        self.context=AppContext(files_dir=Path(self.directory.name),
            preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)

    def tearDown(self):
        for job in self.root.tk.call('after','info'):
            self.root.tk.call('after','cancel',job)
        self.root.destroy()
        self.directory.cleanup()

    def test_table_add_edit_delete_save_keeps_ids_and_vocabulary_unchanged(self):
        path=self.context.tags_path('English')
        save_catalog(path,catalog(),'Czech','English',None)
        vocabulary=self.context.vocabulary_path('English')
        vocabulary.write_text('ID;Tags\n12;Nadávky\n',encoding='utf-8')
        before=vocabulary.read_bytes()
        dialog=TagsDialog(self.root,'English',context=self.context)
        self.root.update()
        dialog.add_tag()
        self.assertEqual(str(dialog.table.get_cell_data(2,0)),'4')
        dialog.table.set_cell_data(2,1,'Cestování')
        dialog.table.set_cell_data(2,2,'Travel')
        dialog.table.select_cell(0,1)
        dialog.delete_tags()
        self.assertEqual([row[0] for row in dialog.table.get_sheet_data()],['3','4'])
        dialog.save()
        loaded,_=load_catalog(path,'Czech','English')
        self.assertEqual(loaded.ID.tolist(),['3','4'])
        self.assertEqual(loaded.Czech.tolist(),['Nadávky','Cestování'])
        self.assertEqual(vocabulary.read_bytes(),before)

    def test_cancel_close_and_validation_failure_do_not_create_catalog(self):
        dialog=TagsDialog(self.root,'English',context=self.context)
        self.root.update()
        dialog.add_tag()
        with patch('app.vocabulary.editor_tags.messagebox.showerror') as errors:
            dialog.save()
            errors.assert_called_once()
        self.assertTrue(dialog.winfo_exists())
        with patch('app.vocabulary.editor_tags.messagebox.askyesnocancel',return_value=None):
            dialog.close()
        self.assertTrue(dialog.winfo_exists())
        with patch('app.vocabulary.editor_tags.messagebox.askyesnocancel',return_value=False):
            dialog.close()
        self.assertFalse(self.context.tags_path('English').exists())

    def test_heading_and_buttons_fit_in_all_ui_languages(self):
        from dataclasses import replace
        from app.shared.translations import LANGUAGES
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            dialog=TagsDialog(self.root,'English',context=self.context)
            dialog.present()
            self.root.update()
            for widget in self._buttons(dialog):
                label=widget._text_label
                self.assertLessEqual(label.winfo_reqwidth(),widget.winfo_width())
                self.assertLessEqual(label.winfo_reqheight(),widget.winfo_height())
            dialog.destroy()

    def test_vocabulary_editor_button_opens_current_catalog_once(self):
        from app.tests.test_editor_save import course
        from app.vocabulary.editor import EditorController
        path=self.context.vocabulary_path('English')
        course().to_csv(path,sep=';',index=False)
        controller=EditorController(self.root,'English',context=self.context)
        self.root.update()
        controller.edit_frm._manage_tags_button.invoke()
        self.root.update()
        dialog=controller._tags_dialog
        self.assertEqual(dialog.path,self.context.tags_path('English'))
        self.assertTrue(dialog.winfo_exists())
        controller.Open_tags()
        self.assertIs(controller._tags_dialog,dialog)
        self.assertFalse(dialog.path.exists())
        dialog.close()
        self.assertFalse(dialog.path.exists())

    def _buttons(self,owner):
        for widget in owner.winfo_children():
            if isinstance(widget,cst.CTkButton):yield widget
            yield from self._buttons(widget)

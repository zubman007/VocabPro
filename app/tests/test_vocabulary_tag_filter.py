"""Set-based tag quantifiers and checkbox filter integration, without data writes."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import customtkinter as cst
import pandas as pd

from app.core.context import AppContext
from app.preferences.data import RuntimePreferences
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_editor_save import course
from app.tests.test_tag_catalog import catalog
from app.repositories.tags import save_catalog
from app.vocabulary.tags_data import filter_by_tags
from app.vocabulary.editor import EditorController
from app.vocabulary.editor_tag_picker import WordTagsDialog
from app.shared.translations import LANGUAGES


def tagged_frame():
    return pd.DataFrame({'ID':[1,2,3,4,5],
        'Tags':['Zvířata, Nadávky','Zvířata, Nadávky, Cestování','Zvířata','Cestování','']})


class TagFilterDataTests(TestCase):
    def test_all_none_and_exact_are_whole_set_operations(self):
        frame=tagged_frame();before=frame.copy(deep=True)
        for mode,expected in [('all',[1,2]),('none',[4,5]),('exact',[1])]:
            self.assertEqual(filter_by_tags(frame,['Zvířata','Nadávky'],mode).ID.tolist(),expected)
        pd.testing.assert_frame_equal(frame,before)

    def test_order_duplicates_case_and_substrings(self):
        frame=tagged_frame()
        frame.loc[0,'Tags']='NADÁVKY, zvířata, Zvířata'
        self.assertEqual(filter_by_tags(frame,'Zvířata, nadávky, Zvířata','exact').ID.tolist(),[1])
        self.assertEqual(filter_by_tags(frame,'Zvíře','all').ID.tolist(),[])

    def test_empty_selection_and_legacy_empty_frames(self):
        frame=tagged_frame()
        for mode in ('all','none'):
            self.assertEqual(filter_by_tags(frame,[],mode).ID.tolist(),[1,2,3,4,5])
        self.assertEqual(filter_by_tags(frame,[],'exact').ID.tolist(),[5])
        self.assertTrue(filter_by_tags(frame.iloc[:0],[],'exact').empty)
        self.assertEqual(filter_by_tags(pd.DataFrame({'ID':[1]}),[],'exact').ID.tolist(),[1])
        with self.assertRaises(ValueError):filter_by_tags(frame,[],'unsupported')


class TagFilterUiTests(TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory();self.root=cst.CTk();self.root.geometry('1280x900')
        self.context=AppContext(files_dir=Path(self.directory.name),
            preferences=RuntimePreferences.from_frame(sample_preferences()))
        self.context.bind(self.root)
        self.context.preferences=replace(self.context.preferences,tag_display_language='Student language')
        save_catalog(self.context.tags_path('English'),catalog(),'Czech','English',None)
        rows=[course().assign(ID=row.ID,English=f'word{row.ID}',Tags=row.Tags)
              for row in tagged_frame().itertuples(index=False)]
        self.source=pd.concat(rows,ignore_index=True)
        self.path=self.context.vocabulary_path('English')
        self.source.to_csv(self.path,sep=';',index=False)
        self.before=self.path.read_bytes()

    def tearDown(self):
        for job in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',job)
        self.root.destroy();self.directory.cleanup()

    def test_checkbox_selection_modes_restore_text_filter_and_keep_hidden_edits(self):
        controller=EditorController(self.root,'English',context=self.context);self.root.update()
        controller.filt_entry_var.set('old text query')
        controller.filt_col_var.set(controller.translate('Tags'));self.root.update()
        panel=controller.filt_frm
        self.assertTrue(panel.tag_mode)
        self.assertFalse(panel.query.winfo_ismapped())
        panel.tag_button.invoke();self.root.update()
        dialog=next(widget for widget in self.root.winfo_children() if isinstance(widget,WordTagsDialog))
        for checkbox in dialog.checkboxes:checkbox.toggle()
        dialog.apply()
        self.assertEqual(panel.tag_selection,'Zvířata, Nadávky')
        self.assertTrue(controller.filt_flag)
        self.assertEqual(controller.filt_df.ID.tolist(),[1,2])
        for label,mode in panel.tag_operators.items():
            controller.sign_var.set(label);controller.Filter()
            expected={'all':[1,2],'none':[4,5],'exact':[1]}[mode]
            self.assertEqual(controller.filt_df.ID.tolist(),expected)
        column=controller.headers.index('Description')
        controller.edit_tbl.set_cell_data(0,column,'edited through exact tag filter')
        controller.filt_col_var.set(controller.translate('English'));self.root.update()
        self.assertFalse(panel.tag_mode)
        self.assertTrue(panel.query.winfo_ismapped())
        self.assertEqual(controller.filt_entry_var.get(),'old text query')
        controller.filt_entry_var.set('word3');controller.Filter()
        self.assertEqual(controller.filt_df.ID.tolist(),[3])
        self.assertEqual(controller.main_df.set_index('ID').loc[1,'Description'],'edited through exact tag filter')
        self.assertEqual(self.path.read_bytes(),self.before)

    def test_cancel_keeps_selection_and_empty_exact_matches_untagged(self):
        controller=EditorController(self.root,'English',context=self.context);self.root.update()
        controller.filt_col_var.set(controller.translate('Tags'))
        controller.filt_frm.set_tag_selection('Zvířata')
        controller.Open_tag_filter();self.root.update()
        dialog=next(widget for widget in self.root.winfo_children() if isinstance(widget,WordTagsDialog))
        dialog.clear();dialog.destroy()
        self.assertEqual(controller.filt_frm.tag_selection,'Zvířata')
        controller.filt_frm.set_tag_selection('')
        exact=next(label for label,mode in controller.filt_frm.tag_operators.items() if mode=='exact')
        controller.sign_var.set(exact);controller.Filter()
        self.assertEqual(controller.filt_df.ID.tolist(),[5])
        self.assertEqual(self.path.read_bytes(),self.before)

    def test_filter_controls_are_localized_and_fit_all_languages(self):
        for language in LANGUAGES:
            self.context.preferences=replace(self.context.preferences,app_language=language)
            controller=EditorController(self.root,'English',context=self.context);self.root.update()
            self.assertEqual(controller.filt_col_var.get(),controller.translate('English'))
            self.assertEqual(controller.filt_frm.column.get(),controller.translate('English'))
            controller.filt_col_var.set(controller.translate('Tags'));self.root.update()
            panel=controller.filt_frm
            self.assertEqual(len(panel.operator.cget('values')),3)
            for label in panel.tag_operators:
                controller.sign_var.set(label);self.root.update()
                self.assertLessEqual(panel.operator._text_label.winfo_reqwidth(),panel.operator._text_label.winfo_width())
            self.assertGreater(panel.tag_button.winfo_width(),100)
            self.assertIsNone(panel.apply)
            for widget in (panel.column,panel.operator,panel.tag_button,panel.reset):
                self.assertGreaterEqual(widget.winfo_rootx(),panel.winfo_rootx())
                self.assertLessEqual(widget.winfo_rootx()+widget.winfo_width(),panel.winfo_rootx()+panel.winfo_width())

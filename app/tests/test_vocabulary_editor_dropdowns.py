"""Real Tk regression test: dropdown creation must never replace cell values."""
import unittest
from unittest.mock import patch
import tkinter as tk
import pandas as pd
from app import main
from dataclasses import replace
from app.core.context import get_context
from app.vocabulary import editor
import customtkinter as cst


class VocabularyDropdownTests(unittest.TestCase):
    def test_open_filter_refresh_and_add_preserve_existing_values(self):
        # Synthetic values differ from every dropdown's first/default item.
        source=pd.DataFrame({'ID':[1,2],'Spanish':['uno','dos'],'Czech':['jedna','dva'],
            'Audio':['Own','No audio'],'Description':['-','-'],'Example':['-','-'],
            'Part of Speech':['Noun','Verb'],'Enabled':['False','True'],
            'Created':['2026-01-01','2026-01-01'],'Repetition':['S','F'],
            'Next repetition':['2026-11-12 10:00:00','2026-11-12 10:00:00']})
        context=get_context()
        original_preferences=context.preferences
        root=None
        try:
            try:
                root=cst.CTk()
                root.withdraw()
            except tk.TclError as error:
                self.skipTest(f'Tk display unavailable: {error}')
            context.preferences=replace(context.preferences,learned_by='Czech')
            with patch('app.vocabulary.editor.pd.read_csv',return_value=source.copy()), \
                 patch('app.vocabulary.editor.next_word_id',return_value=3), \
                 patch('app.shared.settings.T',side_effect=lambda value:value):
                controller=editor.Edit(root,'Spanish')
                root.update_idletasks()
                self.assertEqual(controller.filt_col_var.get(),'Spanish')
                self.assertEqual(controller.filt_frm.column.get(),'Spanish')
                def assert_values():
                    rows=pd.DataFrame(controller.edit_tbl.get_sheet_data(),columns=controller.headers)
                    pd.testing.assert_frame_equal(rows[['ID','Audio','Part of Speech']].reset_index(drop=True),
                        source[['ID','Audio','Part of Speech']].reset_index(drop=True))
                    self.assertNotIn('Enabled',rows.columns)
                assert_values()
                controller.filt_col_var.set('Spanish')
                controller.filt_entry_var.set('uno')
                controller.Filter()
                self.assertEqual(controller.edit_tbl.get_cell_data(0,controller.headers.index('Part of Speech')),'Noun')
                controller.Refresh()
                assert_values()
                controller.New_row(None)
                existing=pd.DataFrame(controller.edit_tbl.get_sheet_data(),columns=controller.headers).iloc[:2]
                self.assertEqual(existing['Part of Speech'].tolist(),['Noun','Verb'])
                self.assertEqual(existing['Audio'].tolist(),['Own','No audio'])
        finally:
            context.preferences=original_preferences
            if root is not None:
                for timer in root.tk.call("after", "info"):
                    root.tk.call("after", "cancel", timer)
                root.destroy()

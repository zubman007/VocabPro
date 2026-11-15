"""Shared shortcut appearance and complete wrapping across languages and widths."""
import tkinter as tk
import unittest
import customtkinter as cst
from app.ui.components.shortcut_hint import ShortcutHint
from app.about.shortcuts import shortcut_sections
from app.shared.translations import translate


class ShortcutHintLayoutTests(unittest.TestCase):
    def test_all_items_fit_and_remain_present_across_languages_and_widths(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        errors=[];root.report_callback_exception=lambda *error:errors.append(error)
        root.geometry('1400x950');root.update()
        holder=cst.CTkFrame(root,width=1200,height=700)
        holder.pack();holder.pack_propagate(False)
        try:
            for language in ('cs','de','en','es','fr','sk'):
                for width in (240,650,1100):
                    holder.configure(width=width)
                    for section in ('Vocabulary','Repeat','Grammar','Conjugation','Grammar editors','Setting','Word tags','Manage tags'):
                        hint=ShortcutHint(holder,section,lambda key:translate(key,language),False)
                        hint.pack(fill='x');root.update()
                        for item in hint.items:self.assertIn(item,hint.cget('text'))
                        if section=='Repeat':
                            enter=next(item for item in hint.items if item.startswith(translate('Enter',language)+' '))
                            self.assertLessEqual(hint.hint_font.measure(enter),hint.cget('wraplength'))
                        self.assertLessEqual(hint._label.winfo_reqwidth(),hint.winfo_width())
                        self.assertLessEqual(hint._label.winfo_reqheight(),hint.winfo_height())
                        self.assertLessEqual(hint.winfo_height(),holder.winfo_height())
                        hint.destroy()
            self.assertFalse(errors)
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

    def test_theory_and_category_filter_have_distinct_descriptions(self):
        grammar=dict(dict(shortcut_sections())['Grammar'])
        self.assertEqual(grammar['Ctrl+T'],'Show question theory')
        self.assertEqual(grammar['Ctrl+F'],'Filter question categories')
        self.assertNotEqual(grammar['Ctrl+T'],grammar['Ctrl+F'])

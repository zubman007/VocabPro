"""Actual Tk geometry, text contrast and narrow dialogs across supported languages."""
from pathlib import Path
import tempfile
from time import monotonic
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst
import pandas as pd
from app.home.layout import build_home
from app.grammar.editor import GrammarEditor
from app.grammar.editor_theory import GrammarTheoryEditor
from app.grammar.category_filter import CategoryFilterDialog
from app.shared.translations import translate
from app.tests.test_grammar_editor import questions
from app.tests.test_grammar_editor_theory import source

LANGUAGES = ('cs','en','de','es','fr','sk')


def rectangle(widget):
    return widget.winfo_rootx(),widget.winfo_rooty(),widget.winfo_width(),widget.winfo_height()


class DesignMatrixTests(unittest.TestCase):
    def setUp(self):
        try:self.root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        self.root.geometry('1400x850');self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *error:self.errors.append(error)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def assert_inside(self,child,parent,tolerance=3):
        x,y,w,h=rectangle(child);px,py,pw,ph=rectangle(parent)
        self.assertGreaterEqual(x,px-tolerance)
        self.assertGreaterEqual(y,py-tolerance)
        self.assertLessEqual(x+w,px+pw+tolerance)
        self.assertLessEqual(y+h,py+ph+tolerance)

    def test_home_cards_and_actions_fit_two_sizes_and_six_languages(self):
        data=dict(all_count=12345,rep_count=1234,lrn_count=5678,gra_count=700,con_count=300,
            rep_words=pd.DataFrame({'ID':[1]}),lrn_words=pd.DataFrame({'ID':[2]}))
        callbacks={key:Mock() for key in ('practice','learn','edit','grammar','edit_grammar','conjugation')}
        callbacks['available']=lambda language,kind:language=='Spanish' or kind=='grammar'
        for size in ('1400x850','1700x950'):
            self.root.geometry(size);self.root.update()
            for language in LANGUAGES:
                with self.subTest(size=size,language=language),patch('app.shared.settings.T',side_effect=lambda key:translate(key,language)):
                    body=build_home(self.root,{'Spanish':data,'English':data},('Spanish','English'),callbacks)
                    self.root.update_idletasks()
                    cards=[w for w in body.winfo_children() if isinstance(w,cst.CTkFrame)]
                    self.assertEqual(len(cards),2)
                    for card in cards:
                        self.assert_inside(card,body)
                        sections=[w for w in card.winfo_children() if isinstance(w,cst.CTkFrame)]
                        for section in sections:
                            self.assert_inside(section,card)
                            actions=next(w for w in section.winfo_children() if isinstance(w,cst.CTkFrame))
                            buttons=[w for w in actions.winfo_children() if isinstance(w,cst.CTkButton)]
                            for button in buttons:
                                self.assert_inside(button,actions)
                                self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                            for first,second in zip(buttons,buttons[1:]):
                                self.assertLessEqual(first.winfo_rootx()+first.winfo_width(),second.winfo_rootx())
                    body.destroy()

    def test_both_editors_keep_panes_separate_and_readable_in_six_languages(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'English_gra.csv';questions().to_csv(path,sep=';',index=False)
            theory=path.with_name('Czech_English_gra_ex.csv');source().to_csv(theory,sep=';',index=False)
            for language in LANGUAGES:
                for editor_type,filename in ((GrammarEditor,path),(GrammarTheoryEditor,theory)):
                    with self.subTest(language=language,editor=editor_type.__name__),patch('app.shared.settings.T',side_effect=lambda key:translate(key,language)):
                        editor=editor_type(self.root,'English',filename,Mock())
                        self.root.update_idletasks()
                        self.assert_inside(editor.view.tree,editor.view.body)
                        self.assert_inside(editor.view.fields['category'],editor.view.body)
                        tree=editor.view.tree
                        self.assertLess(tree.winfo_rootx()+tree.winfo_width(),editor.view.fields['category'].winfo_rootx())
                        combo=editor.view.category_filter
                        self.assertEqual(combo.cget('dropdown_text_color'),'#244743')
                        self.assertNotEqual(combo.cget('dropdown_text_color'),combo.cget('dropdown_fg_color'))
                        self.assert_inside(editor.view.tabs,editor.view.header)
                        editor.view.root.destroy()

    def test_category_filter_keeps_actions_inside_its_minimum_window(self):
        options=[(str(i),'A fairly long category name '+str(i),i+1) for i in range(35)]
        with patch('app.shared.settings.T',side_effect=lambda key:translate(key,'de')):
            dialog=CategoryFilterDialog(self.root,options,{'0'},Mock())
            dialog.geometry('480x450')
            deadline=monotonic()+5
            def wait_for_mapping():
                if dialog.query.winfo_ismapped() and dialog.apply_button.winfo_ismapped():
                    self.root.after(80,self.root.quit)
                elif monotonic()>deadline:self.root.quit()
                else:self.root.after(25,wait_for_mapping)
            self.root.after(25,wait_for_mapping);self.root.mainloop()
            self.assertTrue(dialog.query.winfo_ismapped())
            self.assert_inside(dialog.query,dialog)
            self.assert_inside(dialog.apply_button,dialog)
            self.assert_inside(dialog.count,dialog)
            self.assertLess(dialog.query.winfo_width(),dialog.winfo_width())
            dialog.destroy()

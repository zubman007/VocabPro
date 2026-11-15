"""Real dialogs and practice feedback, with temporary course files only."""
from app.core.context import get_context
from app.tests.context_helpers import patch_context,patch_preferences
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import tkinter as tk
import unittest
import customtkinter as cst
import pandas as pd
from time import monotonic,sleep
from app import main
from app.repositories import synonyms as sy
from app.vocabulary.editor_synonyms import SynonymsDialog
from app.vocabulary.practise import PracticeController


class SynonymsUiTests(unittest.TestCase):
    def test_linked_synonyms_first_with_numeric_id_order_in_both_groups(self):
        words=pd.concat([self.words.iloc[[0]]]*6,ignore_index=True)
        words['ID']=[20,3,100,11,2,1]
        words.to_csv(self.course,sep=';',index=False)
        sy.replace_links(self.course,1,[100,11],None)
        before=self.course.read_bytes()
        relations_before=sy.relation_path(self.course).read_bytes()
        dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
        dialog.deiconify();self.root.update()
        def ids():
            return [int(check.cget('text').rsplit('ID ',1)[1]) for check in dialog._row_checkboxes]
        self.assertEqual(ids(),[11,100,2,3,20])
        dialog.query.set('angry');self.root.update()
        self.assertEqual(ids(),[11,100,2,3,20])
        dialog.destroy()
        self.assertEqual(self.course.read_bytes(),before)
        self.assertEqual(sy.relation_path(self.course).read_bytes(),relations_before)

    def test_synonym_candidates_use_numeric_ids_more_rows_and_available_width(self):
        words=pd.concat([self.words.iloc[[0]]]*210,ignore_index=True)
        words['ID']=list(reversed(range(1,211)))
        words['Spanish']='Tal como estaba previsto'
        words['Czech']='Tak, jak bylo předpokládáno'
        words.to_csv(self.course,sep=';',index=False)
        before=self.course.read_bytes()
        dialog=SynonymsDialog(self.root,self.course,210,'Spanish','Czech')
        dialog.deiconify();self.root.update()
        checks=dialog._row_checkboxes
        self.assertEqual(len(checks),200)
        self.assertEqual([int(check.cget('text').rsplit('ID ',1)[1]) for check in checks],list(range(1,201)))
        first=checks[0]._text_label
        self.assertLess(first.winfo_reqheight(),30)
        wide=int(first.cget('wraplength'))
        dialog.geometry('650x480');self.root.update()
        self.assertLess(int(first.cget('wraplength')),wide)
        self.assertLessEqual(first.winfo_reqwidth(),checks[0].winfo_width()-25)
        dialog.query.set('not a word');self.root.update()
        self.assertEqual(dialog.list._parent_canvas.yview()[0],0)
        dialog.destroy();self.assertEqual(self.course.read_bytes(),before)

    def test_editor_synonyms_button_follows_cell_row_and_empty_selection(self):
        from app.vocabulary.editor import EditorController
        before=self.course.read_bytes()
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish');self.root.update()
            button=editor.edit_frm._synonyms_button
            editor.edit_tbl.deselect('all');self.root.update()
            self.assertEqual(button.cget('state'),'disabled')
            editor.edit_tbl.select_cell(0,editor.headers.index('Spanish'));self.root.update()
            self.assertEqual(button.cget('state'),'normal')
            editor.edit_tbl.deselect('all');self.root.update()
            self.assertEqual(button.cget('state'),'disabled')
            editor.edit_tbl.select_row(1);self.root.update()
            self.assertEqual(button.cget('state'),'normal')
            editor.edit_tbl.select_column(0);self.root.update()
            self.assertEqual(button.cget('state'),'disabled')
            editor.edit_tbl.select_cell(0,1)
            editor.filt_col_var.set('Spanish');editor.filt_entry_var.set('no such word');editor.Filter();self.root.update()
            self.assertEqual(button.cget('state'),'disabled')
            self.assertEqual(self.course.read_bytes(),before)

    def test_synonym_search_placeholder_and_query_sync(self):
        dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
        entry=dialog.search_entry
        self.assertEqual(entry.cget('placeholder_text'),'Search word or translation')
        self.assertEqual(entry.get(),'')
        self.assertTrue(entry._placeholder_text_active)
        entry.insert(0,'annoyed');entry.read_value();self.root.update()
        self.assertEqual(dialog.query.get(),'annoyed')
        checks=[w for w in dialog.list.winfo_children() if isinstance(w,cst.CTkCheckBox)]
        self.assertEqual(len(checks),1)
        self.assertIn('enfadado',checks[0].cget('text'))
        dialog.query.set('enfadado');self.root.update()
        self.assertEqual(entry.get(),'enfadado')
        dialog.query.set('');entry._entry_focus_out();self.root.update()
        self.assertTrue(entry._placeholder_text_active)
        self.assertEqual(entry.get(),'')
        dialog.destroy()

    def test_synonym_dialog_background_and_actions_fit_in_six_languages(self):
        from app.shared.translations import translate
        for locale in ('cs','en','de','es','fr','sk'):
            with self.subTest(locale=locale),patch('app.shared.settings.T',side_effect=lambda key:translate(key,locale)):
                dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
                dialog.geometry('650x480')
                dialog.deiconify()
                self.root.update()
                self.assertTrue(hasattr(dialog,'_backdrop'))
                self.assertEqual(dialog.heading_label.master.cget('fg_color'),'#d7dfca')
                self.assertFalse(hasattr(dialog,'save_hint'))
                buttons=[]
                def collect(widget):
                    for child in widget.winfo_children():
                        if isinstance(child,cst.CTkButton):buttons.append(child)
                        elif isinstance(child,cst.CTkFrame):collect(child)
                collect(dialog)
                self.assertEqual(len(buttons),2)
                for button in buttons:
                    self.assertIs(button.master,dialog)
                    self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                    self.assertLessEqual(button.winfo_rootx()+button.winfo_width(),dialog.winfo_rootx()+dialog.winfo_width())
                dialog.destroy()

    def test_sidebar_synonyms_have_no_separate_card_and_count_is_one_line(self):
        from types import SimpleNamespace
        from app.vocabulary.practise_layout import PracticeSidebar
        panel=PracticeSidebar(self.root,lambda:None)
        panel.pack(fill='both',expand=True)
        previous=SimpleNamespace(id=1,word='word',tr='translation')
        current=SimpleNamespace(id=5)
        panel.update_session(previous,current,1,6,'other — translation\nanother — meaning')
        self.root.update()
        self.assertEqual(panel.count.cget('text'),'1 / 6')
        self.assertEqual(panel.count.cget('font')[1],24)
        self.assertEqual(panel.synonyms.cget('fg_color'),'transparent')
        self.assertEqual(panel.synonym_title.cget('text'),'Synonyms')
        self.assertLess(panel.synonyms.winfo_rooty(),panel.review.winfo_rooty())
        self.assertEqual(panel.synonyms.grid_info()['padx'],panel.word.grid_info()['padx'])
        panel.update_session(previous,current,1,6,'')
        self.root.update()
        self.assertFalse(panel.synonyms.winfo_ismapped())
        self.assertFalse(panel.synonym_title.winfo_ismapped())

    def test_editor_ctrl_h_opens_synonyms_for_selected_word(self):
        from app.vocabulary.editor import EditorController
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish')
            editor.edit_tbl.select_cell(1,editor.headers.index('Spanish'))
            from app.ui.components.module_header import ModuleHeader
            self.assertIsInstance(editor.head_frm,ModuleHeader)
            self.assertEqual(editor.save_btn.cget('text'),'Save')
            self.assertEqual(editor.headers[editor.headers.index('Part of Speech'):],
                ['Part of Speech','Tags','Tag count','Has synonyms','Synonym count','Description','Example','Repetition','Next repetition'])
            self.root.focus_force();self.root.update()
            self.assertLess(editor.headers.index('Has synonyms'),editor.headers.index('Repetition'))
            self.assertLess(editor.headers.index('Synonym count'),editor.headers.index('Repetition'))
            self.assertIs(editor.edit_frm._row_count.master.master,editor.edit_frm)
            hint=editor.edit_frm._shortcut_hint
            self.assertLessEqual(abs(hint._label.winfo_rootx()-editor.edit_frm._row_count._label.winfo_rootx()),3)
            self.root.event_generate('<Control-h>');self.root.update()
            dialog=next(child for child in self.root.winfo_children() if isinstance(child,SynonymsDialog))
            self.assertEqual(dialog.word_id,5)
            dialog.destroy();editor.edit_frm.destroy()
            self.assertTrue(editor.bindings.closed)

    def test_back_without_answers_or_vocabulary_edits_does_not_prompt(self):
        from app.vocabulary.editor import EditorController
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch.object(get_context(),'on_home') as home:
            editor=EditorController(self.root,'Spanish')
            with patch('app.vocabulary.editor.messagebox.askyesnocancel') as ask:
                editor.Cancel(self.root);ask.assert_not_called()
            home.assert_called_once()
        self.words.Repetition=''
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch.object(get_context(),'on_home') as home,patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            with patch('app.vocabulary.practise.messagebox.askyesnocancel') as ask:
                controller.Back();ask.assert_not_called()
            home.assert_called_once()

    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);(self.base/'files').mkdir()
        self.course=self.base/'files'/'Czech_Spanish_voc.csv'
        self.words=pd.DataFrame({'ID':[1,5],'Spanish':['enojado','enfadado'],'Czech':['angry','annoyed'],
            'Audio':['No audio']*2,'Description':['-']*2,'Example':['-']*2,'Part of Speech':['Adjective']*2,
            'Created':['2026-01-01']*2,'Repetition':['S']*2,'Next repetition':['2026-01-01 10:00:00']*2})
        self.words.to_csv(self.course,sep=';',index=False)
        try:self.root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        self.root.geometry('1400x900');self.root.update()
        self.translation=patch('app.shared.settings.T',side_effect=lambda key:key);self.translation.start()
        self.errors=[];self.root.report_callback_exception=lambda *error:self.errors.append(error)

    def tearDown(self):
        self.translation.stop()
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.assertEqual(self.errors,[])

    def test_select_save_reopen_remove_and_cancel(self):
        original=self.course.read_bytes()
        dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
        check=next(child for child in dialog.list.winfo_children() if isinstance(child,cst.CTkCheckBox))
        check.toggle()
        self.assertFalse(sy.relation_path(self.course).exists())
        self.assertTrue(dialog.save())
        frame,_=sy.load(self.course,self.words);self.assertEqual(sy.linked_ids(frame,5),{1})
        dialog=SynonymsDialog(self.root,self.course,5,'Spanish','Czech')
        self.assertEqual(dialog.selected,{1})
        dialog.selected.clear();dialog.destroy()
        frame,_=sy.load(self.course,self.words);self.assertEqual(sy.linked_ids(frame,5),{1})
        dialog=SynonymsDialog(self.root,self.course,5,'Spanish','Czech')
        dialog.selected.clear();self.assertTrue(dialog.save())
        frame,_=sy.load(self.course,self.words);self.assertTrue(frame.empty)
        self.assertEqual(self.course.read_bytes(),original)

    def test_practice_feedback_and_synonyms_window_preserve_course(self):
        sy.replace_links(self.course,1,[5],None)
        original=self.course.read_bytes()
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            self.root.update()
            self.assertTrue(controller.synonym_text(controller.w_new.id))
            controller.Show_synonyms()
            self.assertEqual(controller.current_synonym_label.cget('text'),controller.synonym_text(controller.w_new.id))
            controller.Conf_resp('incorrect','')
            self.root.update()
            self.assertTrue(controller.synonym_label.winfo_ismapped())
            self.assertTrue(controller.synonym_label.cget('text'))
            self.assertNotIn('Synonyms:',controller.synonym_label.cget('text'))
            self.assertEqual(self.course.read_bytes(),original)

    def test_unsort_button_state_and_filtered_original_order(self):
        from app.vocabulary.editor import EditorController
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish')
            button=editor.edit_frm._sort_button
            self.assertIn('↕',button.cget('text'))
            self.assertEqual(button.cget('state'),'disabled')
            editor.edit_tbl.select_cell(0,editor.headers.index('ID'));self.root.update()
            self.assertEqual(button.cget('state'),'normal')
            editor.edit_tbl.deselect('all');self.root.update()
            self.assertEqual(button.cget('state'),'disabled')
            editor.filt_col_var.set('Spanish');editor.filt_entry_var.set('en');editor.Filter()
            editor.edit_tbl.select_column(editor.headers.index('ID'));editor.Sort(True)
            self.assertEqual(editor.filt_df.ID.tolist(),[5,1])
            self.assertEqual(button.cget('state'),'normal')
            editor.edit_tbl.deselect('all');self.root.update()
            self.assertEqual(button.cget('state'),'normal')
            button.invoke()
            self.assertEqual(editor.filt_df.ID.tolist(),[1,5])
            self.assertEqual(editor.filt_entry_var.get(),'en')
            self.assertIn('↕',button.cget('text'))
            self.assertEqual(button.cget('state'),'disabled')
            editor.Sort(True);editor.Refresh()
            self.assertIn('↕',button.cget('text'))

    def test_filter_searches_word_or_translation_and_scrolls_to_first_result(self):
        words=pd.concat([self.words]*30,ignore_index=True)
        words['ID']=range(1,len(words)+1)
        words.to_csv(self.course,sep=';',index=False)
        dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
        dialog.deiconify();self.root.update()
        dialog.list._parent_canvas.yview_moveto(1)
        self.root.update()
        self.assertGreater(dialog.list._parent_canvas.yview()[0],0)
        for query in ('enfadado','annoyed'):
            dialog.query.set(query);self.root.update()
            checks=[child for child in dialog.list.winfo_children() if isinstance(child,cst.CTkCheckBox)]
            self.assertEqual(len(checks),30)
            self.assertAlmostEqual(dialog.list._parent_canvas.yview()[0],0,places=3)
            self.assertIn('enfadado',checks[0].cget('text'))
            self.assertLess(checks[0].winfo_rooty(),dialog.list._parent_canvas.winfo_rooty()+60)
            dialog.list._parent_canvas.yview_moveto(1)
        dialog.query.set('60');self.root.update()
        self.assertFalse(any(isinstance(child,cst.CTkCheckBox) for child in dialog.list.winfo_children()))
        dialog.destroy()

    def test_fast_close_then_open_has_no_delayed_focus_error(self):
        for _ in range(3):
            dialog=SynonymsDialog(self.root,self.course,1,'Spanish','Czech')
            dialog.focus_set();self.root.update()
            other=SynonymsDialog(self.root,self.course,5,'Spanish','Czech')
            dialog.destroy();other.destroy()
            deadline=monotonic()+.3
            while monotonic()<deadline:self.root.update();sleep(.01)

    def test_synonym_setting_inline_previous_word_and_numpad(self):
        sy.replace_links(self.course,1,[5],None)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch_preferences(show_synonyms=False),patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            self.root.update()
            self.assertTrue(controller.synonym_button.winfo_ismapped())
            self.assertIn('Ctrl+H',controller.sidebar.shortcuts.cget('text'))
            self.assertFalse(controller.current_synonyms._parent_frame.winfo_ismapped())
            self.root.focus_force();self.root.update()
            self.root.event_generate('<Control-h>');self.root.update()
            self.assertTrue(controller.current_synonyms.winfo_ismapped())
            controller.w_old.id=5;controller.w_new.id=1
            controller.sidebar.update_session(controller.w_old,controller.w_new,0,2,controller.synonym_text(5))
            self.root.update()
            self.assertIn('enojado',controller.sidebar.synonym_list.value)
            options=['one','two','three','four']
            controller._show_question(3,options,0);self.root.update();self.root.focus_force();self.root.update()
            with patch.object(controller,'Conf_resp') as answer:
                for index in range(4):
                    answer.reset_mock()
                    self.root.event_generate('<KeyPress>',keysym=str(index+1),state=0x8)
                    self.root.update();answer.assert_called_once()
                    self.assertEqual(answer.call_args.args[0],options[index])
            with patch_preferences(show_synonyms=True):
                controller._show_question(3,options,0);self.root.update()
                self.assertTrue(controller.current_synonyms.winfo_ismapped())
                self.assertFalse(controller.synonym_button.winfo_ismapped())

    def test_editor_computed_columns_filter_and_update_after_synonym_changes(self):
        from app.vocabulary.editor import EditorController
        sy.replace_links(self.course,1,[5],None)
        original=self.course.read_bytes()
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish')
            editor.Refresh()
            self.assertEqual(editor.main_df['Synonym count'].tolist(),[1,1])
            editor.filt_col_var.set('Has synonyms');editor.filt_entry_var.set('1');editor.Filter()
            self.assertEqual(editor.edit_tbl.get_total_rows(),2)
            editor.filt_col_var.set('Synonym count');editor.filt_entry_var.set('1');editor.sign_var.set('=');editor.Filter()
            self.assertEqual(editor.edit_tbl.get_total_rows(),2)
            _,revision=sy.load(self.course,self.words)
            sy.replace_links(self.course,1,[],revision);editor._synonyms_changed()
            self.assertEqual(editor.edit_tbl.get_total_rows(),0)
            editor.filt_col_var.set('Has synonyms');editor.filt_entry_var.set('0');editor.Filter()
            self.assertEqual(editor.edit_tbl.get_total_rows(),2)
            self.assertEqual(editor.main_df['Synonym count'].tolist(),[0,0])
            self.assertEqual(self.course.read_bytes(),original)

    def test_compact_long_synonym_list_scrolls_without_losing_text_and_no_auto_shortcut_hint(self):
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch_preferences(show_synonyms=True),patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            self.root.update()
            self.assertNotIn('Ctrl+H',controller.sidebar.shortcuts.cget('text'))
            self.assertEqual(controller.skip_btn.cget('text'),'Next')
            self.assertEqual(controller.skip_btn.grid_info()['column'],1)
            self.assertEqual(controller.confirm_btn.grid_info()['column'],0)
            self.assertLessEqual(abs(controller.skip_btn.winfo_width()-controller.confirm_btn.winfo_width()),2)
            for button in (controller.skip_btn,controller.confirm_btn):
                self.assertEqual(button.cget('height'),54)
                self.assertEqual(button.grid_info()['sticky'],'ew')
            with patch.object(controller,'synonym_text',return_value='one — short translation'):controller.Show_synonyms()
            self.root.update()
            short_height=controller.current_synonyms.cget('height')
            self.assertLessEqual(short_height,40)
            self.assertFalse(controller.current_synonyms._scrollbar.winfo_ismapped())
            self.assertFalse(controller._synonyms_hscroll.winfo_ismapped())
            edit=controller.edit_current_synonyms
            panel=controller.current_synonyms._parent_frame
            self.assertLessEqual(edit.winfo_rooty()+edit.winfo_height(),panel.winfo_rooty()+panel.winfo_height())
            self.assertLessEqual(edit._text_label.winfo_reqheight(),edit.winfo_height())
            self.assertLessEqual(controller.current_synonyms._parent_frame.winfo_height(),100*controller.current_synonyms._get_widget_scaling())
            self.assertEqual(controller.current_synonym_label.cget('wraplength'),0)
            self.assertEqual(len(controller.current_synonym_label.cget('text').splitlines()),1)
            text='\n'.join(f'word {i} '+('long translation '*12) for i in range(30))
            with patch.object(controller,'synonym_text',return_value=text):controller.Show_synonyms()
            self.root.update()
            self.assertLessEqual(controller.current_synonyms.cget('height'),110)
            self.assertGreaterEqual(controller.current_synonyms.cget('height'),28)
            self.assertGreater(controller.current_synonyms.cget('height'),short_height)
            self.assertIn('word 29',controller.current_synonym_label.cget('text'))
            self.assertEqual(len(controller.current_synonym_label.cget('text').splitlines()),30)
            self.assertNotIn('Synonyms:',controller.current_synonym_label.cget('text'))
            canvas=controller.current_synonyms._parent_canvas
            self.assertLess(canvas.yview()[1],1)
            canvas.yview_moveto(1);self.root.update()
            self.assertGreater(canvas.yview()[0],0)
            self.assertTrue(controller._synonyms_hscroll.winfo_ismapped(),(
                canvas.winfo_width(),controller.current_synonyms.winfo_reqwidth(),
                controller.current_synonym_label.winfo_reqwidth(),controller.current_synonym_label._label.winfo_reqwidth(),
                controller.current_synonyms._parent_frame.winfo_width(),self.root.winfo_width()))
            canvas.xview_moveto(1);self.root.update()
            self.assertGreater(canvas.xview()[0],0)

    def test_editor_sort_keeps_ids_associated_with_edits_and_does_not_write_csv(self):
        from app.vocabulary.editor import EditorController
        original=self.course.read_bytes()
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish')
            editor.filt_col_var.set('ID');editor.Sort(True)
            self.assertEqual(editor.filt_df.ID.tolist(),[5,1])
            editor.edit_tbl.set_cell_data(0,editor.headers.index('Spanish'),'changed')
            editor.Sync_changes(1,'')
            self.assertEqual(editor.main_df.set_index('ID').loc[5,'Spanish'],'changed')
            editor.Sort(False)
            self.assertEqual(editor.filt_df.ID.tolist(),[1,5])
            self.assertEqual(self.course.read_bytes(),original)

    def test_review_can_edit_synonyms_and_back_supports_cancel_save_and_discard(self):
        sy.replace_links(self.course,1,[5],None)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            controller.w_old.id=5;controller.w_old.word='enfadado';controller.w_new.id=1
            controller.Review_w(None);self.root.update()
            review=controller._review_dialog
            self.assertIn('Synonyms',[child.cget('text') for child in review.detail_body.winfo_children()])
            controller.Edit_review_synonyms();self.root.update()
            dialog=next(child for child in self.root.winfo_children() if isinstance(child,SynonymsDialog))
            self.assertEqual(dialog.word_id,5)
            dialog.selected.clear();self.assertTrue(dialog.save())
            self.assertEqual(controller.synonym_text(5),'')
            controller._has_answers=True
            with patch('app.vocabulary.practise.messagebox.askyesnocancel',return_value=None):controller.Back()
            self.assertTrue(controller.rep_frm.winfo_exists())
            with patch('app.vocabulary.practise.messagebox.askyesnocancel',return_value=True),patch.object(controller,'Save_rep') as save:
                controller.Back();save.assert_called_once()
            with patch('app.vocabulary.practise.messagebox.askyesnocancel',return_value=False),patch.object(get_context(),'on_home') as home:
                controller.Back();home.assert_called_once_with()

    def test_review_description_and_example_edits_stay_in_session_until_saved(self):
        from app.repositories.vocabulary import save_practice
        original=self.course.read_bytes()
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            controller.w_old.id=5;controller.w_old.word='enfadado';controller.w_new.id=1
            controller.w_old.desc='old description'
            controller.Review_w(None)
            dialog=controller.Edit_review_attribute('Description')
            dialog.editor.delete('1.0','end');dialog.editor.insert('1.0','cancelled')
            dialog.destroy()
            self.assertEqual(controller.w_old.desc,'old description')
            controller.Review_w(None)
            for column,value in [('Description','New description\nsecond line; detail'),('Example','A new example.')]:
                dialog=controller.Edit_review_attribute(column)
                dialog.editor.delete('1.0','end');dialog.editor.insert('1.0',value)
                dialog.save_edit();self.root.update()
                self.assertEqual(controller.session.data.at[5,column],value)
                self.assertEqual(self.course.read_bytes(),original)
            remaining,completed=controller.session.frames()
            save_practice(self.course,remaining,completed,controller.headers)
            saved=pd.read_csv(self.course,sep=';',dtype=str,keep_default_na=False).set_index('ID')
            self.assertEqual(saved.loc['5','Description'],'New description\nsecond line; detail')
            self.assertEqual(saved.loc['5','Example'],'A new example.')

    def test_current_synonyms_editor_updates_marker_and_current_panel(self):
        sy.replace_links(self.course,1,[5],None)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch_preferences(show_synonyms=False),patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            controller.w_new.id=1;controller._mark_synonyms();self.root.update()
            self.assertTrue(controller.synonym_dot.place_info())
            controller.Show_synonyms();self.root.update()
            dialog=controller.Edit_current_synonyms()
            self.assertEqual(dialog.word_id,1)
            dialog.selected.clear();self.assertTrue(dialog.save());self.root.update()
            self.assertFalse(controller.synonym_dot.place_info())
            self.assertIn('No synonyms linked.',controller.current_synonym_label.cget('text'))

    def test_active_synonym_editor_does_not_reveal_translation_answer_or_allow_navigation(self):
        sy.replace_links(self.course,1,[5],None)
        duplicate=self.words.iloc[:1].copy();duplicate.ID=9;duplicate.Spanish='Enojado'
        pd.concat([self.words,duplicate],ignore_index=True).to_csv(self.course,sep=';',index=False)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,self.words,'Spanish',1)
            controller.w_new.id=1;controller.w_new.word='enojado';controller.w_new.tr='angry'
            for mode,options,expected in [(1,None,'angry'),(3,['a','b','c','d'],'enojado')]:
                controller._show_question(mode,options,0);self.root.update()
                dialog=controller.Edit_current_synonyms()
                self.assertIn(expected,dialog.heading_label.cget('text'))
                if mode==1:self.assertNotIn('enojado',dialog.heading_label.cget('text'))
                else:
                    self.assertFalse(dialog.show_translation)
                    self.assertNotIn('annoyed',' '.join(child.cget('text') for child in dialog.list.winfo_children()))
                self.assertFalse(dialog.allow_navigation)
                self.assertIn(9,dialog.hidden_ids)
                self.assertFalse(any(isinstance(child,cst.CTkButton) for child in dialog.list.winfo_children()))
                self.assertNotIn('enojado',' '.join(child.cget('text') for child in dialog.list.winfo_children()))
                dialog.navigate(5);self.assertEqual(dialog.word_id,1)
                dialog.destroy()

    def test_skip_preserves_previous_word_and_error_return_preserves_layout(self):
        third=self.words.iloc[:1].copy();third.ID=9;third.Spanish='tercero'
        words=pd.concat([self.words,third],ignore_index=True);words.to_csv(self.course,sep=';',index=False)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0,0]),patch_preferences(audio_probabilities=[0,0]), \
             patch_preferences(show_synonyms=False),patch.object(PracticeController,'Play_audio'),patch.object(PracticeController,'Auto_audio'):
            controller=PracticeController(self.root,words,'Spanish',1)
            controller.w_new.id=1;controller.w_new.word='enojado';controller.w_new.tr='angry'
            controller.w_old.id=5;controller.w_old.word='enfadado';controller.w_old.tr='annoyed'
            controller.session.skip(5)
            with patch.object(controller.session,'pick',return_value=controller.session.data.loc[9]):controller.Skip_resp()
            self.assertEqual(controller.w_old.id,5)
            self.assertEqual(controller.w_old.word,'enfadado')
            self.assertNotIn('enojado',controller.sidebar.word.cget('text'))
            self.assertEqual(controller.session.history(1),'S')
            self.root.update();original=controller.action_frm.grid_info().copy()
            controller.Conf_resp('incorrect','');self.root.update()
            controller.Show_w_next(None);self.root.update()
            restored=controller.action_frm.grid_info()
            for key in ('padx','pady','sticky','column'):self.assertEqual(restored[key],original[key])
            self.assertGreater(controller.synonym_button.winfo_rootx(),controller.rep_frm.winfo_rootx()+10)

    def test_sort_uses_selected_cell_or_header_and_keeps_filter_and_edits(self):
        from app.vocabulary.editor import EditorController
        third=self.words.iloc[:1].copy();third.ID=12;third.Spanish='alfa'
        words=pd.concat([self.words,third],ignore_index=True)
        words['Spanish']=['zeta','beta','alfa']
        words.to_csv(self.course,sep=';',index=False)
        original=self.course.read_bytes()
        sy.replace_links(self.course,1,[5,12],None)
        with patch_context(root_dir=self.base),patch_preferences(learned_by='Czech'):
            editor=EditorController(self.root,'Spanish')
            editor.filt_col_var.set('ID')
            editor.edit_tbl.select_cell(0,editor.headers.index('Spanish'))
            editor.Sort(False)
            self.assertEqual(editor.filt_df.ID.tolist(),[12,5,1])
            self.assertEqual(editor._sort_spec,('Spanish',False))
            editor.edit_tbl.select_column(editor.headers.index('ID'))
            editor.Sort(False)
            self.assertEqual(editor.filt_df.ID.tolist(),[1,5,12])
            editor.edit_tbl.MT.extra_table_rc_menu_funcs['Sort']['command']()
            self.assertEqual(editor.filt_df.ID.tolist(),[12,5,1])
            editor.edit_tbl.MT.extra_header_rc_menu_funcs['Sort']['command']()
            self.assertEqual(editor.filt_df.ID.tolist(),[1,5,12])
            editor.filt_col_var.set('Has synonyms');editor.filt_entry_var.set('1');editor.Filter()
            self.assertEqual(editor.filt_df.ID.tolist(),[1,5,12])
            editor.filt_col_var.set('Synonym count');editor.filt_entry_var.set('1');editor.sign_var.set('=');editor.Filter()
            self.assertEqual(set(editor.filt_df.ID),{5,12})
            editor.edit_tbl.select_cell(0,editor.headers.index('ID'));editor.Sort(True)
            self.assertEqual(editor.filt_df.ID.tolist(),[12,5])
            editor.edit_tbl.set_cell_data(0,editor.headers.index('Spanish'),'changed')
            editor.Sync_changes(1,'')
            self.assertEqual(editor.main_df.set_index('ID').loc[12,'Spanish'],'changed')
            self.assertEqual(len(editor.main_df),3)
            editor.filt_entry_var.set('2');editor.Filter()
            self.assertEqual(editor.filt_df.ID.tolist(),[1])
            editor.Refresh()
            self.assertEqual(editor.edit_tbl.get_total_rows(),3)
            self.assertEqual(self.course.read_bytes(),original)

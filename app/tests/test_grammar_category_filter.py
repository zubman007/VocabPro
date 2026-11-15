"""Multi-select filtering, round lifecycle and cancellation, with no CSV writes."""
from unittest.mock import Mock, patch
import tkinter as tk
import unittest
import customtkinter as cst
from app.grammar.category_filter import category_options, CategoryFilterDialog
from app.grammar.practise import GrammarController


def questions():
    return [dict(id=str(index),category=category,prompt='Choose',anchor='Sentence',
        options=['yes','no','x','y'],correct_answer='yes',explanation='Reason')
        for index,category in enumerate(('Articles','Tenses','Articles',''))]


class FilterTests(unittest.TestCase):
    def test_weighted_rounds_stay_filtered_and_keep_unsaved_progress_after_switch(self):
        from copy import deepcopy
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x850');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            values=questions()
            for item in values:
                item.update(repetition='SS',last_review='2026-01-01')
            before=deepcopy(values)
            with patch('app.shared.settings.T',side_effect=lambda text:text), \
                 patch('app.grammar.practise.play_effect'), \
                 patch('app.grammar.practise.save_answers') as save:
                controller=GrammarController(root,values,'unused.csv',Mock(),learned_by='Czech',
                                             initial_categories=['Articles'])
                answered=controller.session.current['id']
                controller.choose(controller.session.options.index('no'))
                self.assertEqual(len(controller.pending_answers),1)
                self.assertTrue(controller.apply_filter({'tenses'}))
                self.assertEqual(controller.session.current['category'],'Tenses')
                self.assertTrue(controller.apply_filter({'articles'}))
                current_round=[controller.session.current,*controller.session.remaining]
                self.assertEqual({item['category'] for item in current_round},{'Articles'})
                self.assertEqual(len(current_round),2)
                updated=next(item for item in current_round if item['id']==answered)
                self.assertEqual(updated['repetition'],'SSF')
                self.assertEqual(updated['last_review'],controller.pending_answers[0][3])
                self.assertEqual(len(controller.pending_answers),1)
                self.assertEqual(values,before)
                save.assert_not_called()
                controller.view.root.destroy()
                self.assertEqual(errors,[])
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

    def test_search_resets_scroll_without_changing_selected_categories(self):
        root=cst.CTk();root.geometry('900x800');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            options=[(str(i),f'Topic {i:02}',10) for i in range(60)]
            dialog=CategoryFilterDialog(root,options,{'59'},Mock())
            dialog.deiconify();root.update()
            canvas=dialog.body._parent_canvas
            canvas.yview_moveto(1);root.update()
            self.assertGreater(canvas.yview()[0],0)
            dialog.search_text.set('Topic 00');root.update()
            self.assertEqual(canvas.yview()[0],0)
            self.assertTrue(dialog.checkboxes['0'].winfo_ismapped())
            self.assertFalse(dialog.checkboxes['59'].winfo_ismapped())
            self.assertTrue(dialog.variables['59'].get())
            dialog.search_text.set('does not exist');root.update()
            self.assertTrue(all(not item.winfo_ismapped() for item in dialog.checkboxes.values()))
            dialog.search_text.set('');root.update()
            self.assertEqual(canvas.yview()[0],0)
            self.assertTrue(dialog.checkboxes['0'].winfo_ismapped())
            self.assertEqual(dialog.description.cget('fg_color'),'transparent')
            self.assertEqual(dialog.count.cget('fg_color'),'transparent')
            self.assertTrue(hasattr(dialog.apply_button,'_surface'))
            self.assertEqual(errors,[])
            dialog.destroy()
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

    def test_categories_count_missing_and_normalized_names(self):
        values=questions()+[dict(category=' ARTICLES ')]
        self.assertEqual(category_options(values),[('', '',1),('articles','Articles',3),('tenses','Tenses',1)])

    def test_filtered_round_restart_clear_and_dialog_cancel(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.geometry('1400x850');root.update()
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            with patch('app.shared.settings.T',side_effect=lambda text:text), \
                 patch('app.grammar.practise.save_answers') as save:
                controller=GrammarController(root,questions(),'unused.csv',Mock(),learned_by='Czech')
                self.assertTrue(controller.apply_filter({'articles','tenses'}))
                self.assertEqual(len(controller.session.questions),3)
                self.assertNotEqual(controller.view.filter_status.winfo_manager(),'')
                self.assertTrue(controller.apply_filter({'articles'}))
                self.assertTrue(all(q['category']=='Articles' for q in controller.session.questions))
                session=controller.session
                self.assertFalse(controller.apply_filter(set()))
                self.assertTrue(controller.apply_filter({'articles'}))
                self.assertIs(controller.session,session)
                controller.open_filter()
                dialog=controller._filter_window
                dialog._select_all(False)
                self.assertEqual(dialog.apply_button.cget('state'),'disabled')
                dialog.variables['tenses'].set(True);dialog._refresh()
                self.assertEqual(dialog.apply_button.cget('state'),'normal')
                dialog.destroy()
                self.assertIs(controller.session,session)
                controller.restart()
                self.assertEqual(len(controller.session.questions),2)
                controller.apply_filter({key for key,_,_ in controller.categories})
                self.assertEqual(len(controller.session.questions),4)
                self.assertEqual(controller.view.filter_status.winfo_manager(),'')
                controller.open_filter();dialog=controller._filter_window
                dialog._select_all(False);dialog.variables['tenses'].set(True);dialog._refresh();dialog._apply()
                self.assertEqual(controller.session.current['category'],'Tenses')
                self.assertFalse(dialog.winfo_exists())
                controller.next_question()
                self.assertIsNone(controller.session.current)
                controller.restart()
                self.assertEqual(controller.session.current['category'],'Tenses')
                controller.open_filter();dialog=controller._filter_window
                controller.view.root.destroy()
                self.assertFalse(dialog.winfo_exists())
                save.assert_not_called()
                self.assertEqual(errors,[])
        finally:
            for timer in root.tk.call('after','info'):root.tk.call('after','cancel',timer)
            root.destroy()

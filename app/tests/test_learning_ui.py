"""Real Tk checks for learning transitions, shared styling and safe cleanup."""
from app.tests.context_helpers import patch_preferences
import tkinter as tk
import unittest
from unittest.mock import patch, Mock
import customtkinter as cst
import pandas as pd
from app import main
from app.grammar import practise as grammar
from app.conjugation import practise as conjugation
from app.vocabulary import practise as practice
from app.ui.learning_review import ReviewDialog
from app.ui.widgets import VerticalScrolledFrame_class
from app.statistics.components import summary_cards, SuccessRing
from app.ui.sections import SectionTabs
from app.ui.surfaces import surface
from app.statistics.background import StatisticsBackdrop
from app.statistics.window import StatisticsWindow
from app.ui import learning_layout as ui
from app.ui import surfaces as ui_surfaces


class LearningUiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = cst.CTk()
            self.root.geometry('1400x850')
            self.root.update()
            self.callback_errors = []
            self.root.report_callback_exception = lambda *error: self.callback_errors.append(error)
        except tk.TclError as error:
            self.skipTest(str(error))
        self.translation = patch('app.shared.settings.T', side_effect=lambda text: text)
        self.translation.start()

    def tearDown(self):
        self.translation.stop()
        for timer in self.root.tk.call('after', 'info'):
            self.root.tk.call('after', 'cancel', timer)
        self.root.destroy()
        self.assertEqual(self.callback_errors, [])

    def test_practice_modes_and_answer_card_keep_their_shared_palette(self):
        frame = pd.DataFrame({'ID': [1, 2, 3, 4], 'Spanish': ['uno', 'dos', 'tres', 'cuatro'],
            'Czech': ['one', 'two', 'three', 'four'], 'Repetition': ['S'] * 4,
            'Audio': ['Own'] * 4, 'Enabled': ['True'] * 4, 'Description': ['description'] * 4,
            'Example': ['example'] * 4, 'Part of Speech': ['Noun'] * 4,
            'Next repetition': ['2026-11-12 10:00:00'] * 4})
        with patch_preferences(learned_by='Czech'), \
             patch_preferences(context_probabilities=[0, 0]), \
             patch_preferences(audio_probabilities=[0, 0]), \
             patch('app.vocabulary.practise.read_words', return_value=frame), \
             patch.object(practice.PracticeController, 'Play_audio'):
            controller = practice.Rep(self.root, frame, 'Spanish', 1)
            self.root.update()
            from app.ui.components.module_header import ModuleHeader
            self.assertIsInstance(controller.header,ModuleHeader)
            self.assertTrue(controller.header.logo_label.winfo_ismapped())
            self.assertEqual(controller.header.buttons['save'].cget('text'),'Save')
            self.assertEqual(controller.header.title_label.cget('text_color'),'#fffcf5')
            self.assertEqual(controller.resp_entry.cget('fg_color'), ui.SURFACE)
            original=controller.w_new.tr
            # Match the main-window minimum enforced by start.py. Narrow text
            # cards are covered independently by test_shared_controls.
            for size in ('1600x850','1700x950','1900x1000'):
                self.root.geometry(size);self.root.update()
                for text in ('trysknout (voda, krev) / vyrašit (rostliny) / objevit se, vzniknout',
                        'Eine sehr lange Beschreibung mit mehreren Bedeutungen und zusätzlichen Erklärungen. '*3,
                        'palabra'*30,'first line\nsecond line\nthird line\nfourth line'):
                    with self.subTest(size=size,text=text[:30]):
                        controller.w_new.tr=text
                        controller._show_question(1,None,0);self.root.update()
                        label=controller.transl_lbl;card=controller.lbl_frm
                        self.assertEqual(label.cget('text'),text)
                        self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                        self.assertLessEqual(label._label.winfo_reqheight(),label.winfo_height()+2)
                        self.assertGreaterEqual(label.winfo_rootx(),card.winfo_rootx()+20)
                        self.assertLessEqual(label.winfo_rootx()+label.winfo_width(),card.winfo_rootx()+card.winfo_width()-20)
            self.root.geometry('1400x850');self.root.update()
            controller.w_new.tr='short'
            controller._show_question(1,None,0);self.root.update()
            self.assertEqual(controller.transl_lbl.cget('font')[1],42)
            self.assertEqual(controller.lbl_frm.cget('height'),260)
            label=controller.transl_lbl;card=controller.lbl_frm
            self.assertLess(abs(label.winfo_rooty()+label.winfo_height()/2-
                card.winfo_rooty()-card.winfo_height()/2),4)
            controller.w_new.tr=original
            controller._show_question(2, None, 0)
            self.root.update()
            self.assertTrue(controller.type_2_frm.winfo_ismapped())
            self.assertEqual(controller.type_2_frm.cget('fg_color'),'transparent')
            self.assertGreaterEqual(controller.type_2_frm.grid_info()['padx'],controller.lbl_frm.cget('corner_radius'))
            self.assertGreaterEqual(controller.type_2_frm.grid_info()['pady'],controller.lbl_frm.cget('corner_radius'))
            controller._show_question(3, ['one', 'two', 'three', 'four'], 0)
            self.root.update()
            self.assertTrue(controller.opc_frm.winfo_ismapped())
            controller.Conf_resp('deliberately incorrect', '')
            self.root.update()
            self.assertEqual(controller.show_w_frm.cget('fg_color'), ui.ERROR)
            self.assertEqual(controller.w_lbl.cget('bg_color'), ui.ERROR)
            controller.Show_w_next(None)
            self.root.update()
            self.assertTrue(controller.action_frm.winfo_ismapped())
            external = self.root.bind('<Return>', lambda event: None, add='+')
            own_trace = controller._response_trace
            controller.rep_frm.destroy()
            self.assertTrue(controller.bindings.closed)
            self.assertIsNone(controller._response_trace)
            self.assertFalse(any(token == own_trace for modes, token in controller.resp_var.trace_info()))
            self.assertIn(external, self.root.bind('<Return>'))

    def test_grammar_scoring_works_without_audio_device(self):
        question = dict(id='1', prompt='Choose', anchor='sentence', options=['yes', 'no', 'x', 'y'],
                        correct_answer='yes', explanation='Reason', count_trailing_s=0)
        with patch.object(grammar, 'Load_questions_from_csv', return_value=[question]), \
             patch.object(grammar, 'save_answers') as save, \
             patch('app.shared.audio_effects.pygame.mixer.get_init', return_value=None):
            controller = grammar.Grammar_training(self.root, 'Spanish')
            chosen = next(i for i, button in enumerate(controller.view.options) if button.cget('text').endswith(' · yes'))
            controller.choose(chosen)
            self.assertEqual(controller.session.correct, 1)
            save.assert_not_called()
            self.assertEqual(len(controller.pending_answers),1)
            controller.next_question()
            controller.restart()
            self.assertEqual(controller.session.current['id'], '1')

    def test_review_can_close_before_its_delayed_presentation(self):
        dialog = ReviewDialog(self.root, 'Review', 'word', 'translation', ['description'])
        timer = dialog._present_id
        dialog.destroy()
        self.assertNotIn(timer, self.root.tk.call('after', 'info'))

    def test_preferences_dialog_stays_open_after_failed_write_then_saves(self):
        from pathlib import Path
        import tempfile
        from app.preferences.dialog import PreferencesDialog
        from app.repositories.preferences import load_preferences
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'settings.csv'
            pd.DataFrame([['Learn batch','Int','10']],
                         columns=['Name','Type','Value']).to_csv(path,sep=';',index=False)
            before = path.read_bytes()
            dialog = PreferencesDialog(self.root, lambda value: value, path)
            self.root.after(350, self.root.quit)
            self.root.mainloop()
            dialog.variables['Learn batch'].set('12')
            with patch('app.repositories.preferences.commit_document',side_effect=PermissionError('Locked file')):
                dialog.save()
            self.assertTrue(dialog.winfo_exists())
            self.assertFalse(dialog.saved)
            self.assertEqual(dialog.error.cget('text'),'Locked file')
            self.assertEqual(path.read_bytes(),before)
            dialog.save()
            self.assertTrue(dialog.saved)
            self.assertFalse(dialog.winfo_exists())
            self.assertEqual(load_preferences(path).iloc[0].Value,'12')

    def test_review_buttons_invoke_callbacks_without_file_operations(self):
        from app.vocabulary.practise_review import open_review
        from app.vocabulary.practise_data import Word
        from app.vocabulary.practise_session import PracticeSession
        source = pd.DataFrame({'ID': [1, 2], 'Audio': ['Own', 'Own'],
            'Description': ['first', 'second'], 'Example': ['example', 'other']})
        original = source.copy(deep=True)
        session = PracticeSession(source.copy(), {}, 0)
        word = Word(1, 'word', '[word]', 'first', 'example', 'translation', 'Noun')
        audio = Mock()
        controller = practice.PracticeController.__new__(practice.PracticeController)
        controller.session, controller.w_old, controller.audio = session, word, audio
        with patch.object(controller, 'Review_w_end') as close, \
             patch.object(controller, 'Play_btn_ability'), \
             patch.object(practice, 'save_practice') as save, \
             patch('pathlib.Path.unlink') as unlink:
            dialog = open_review(self.root, word, controller.Del_audio, controller.Del_desc,
                                 controller.Del_sentence_example)
            dialog.geometry('700x600')
            self.root.after(350, self.root.quit)
            self.root.mainloop()
            buttons = [child for frame in dialog.winfo_children()
                       if isinstance(frame, cst.CTkFrame) for child in frame.winfo_children()
                       if isinstance(child, cst.CTkButton)]
            self.assertEqual(len(buttons), 3)
            self.assertEqual([button.grid_info()['row'] for button in buttons], [0, 0, 0])
            for button in buttons:
                button.invoke()
            audio.delete.assert_called_once_with(1)
            self.assertEqual(close.call_count, 3)
            self.assertEqual(session.data.loc[1, ['Audio', 'Description', 'Example']].tolist(),
                             ['No audio', 'No found', 'No found'])
            self.assertEqual(session.data.loc[2, ['Audio', 'Description', 'Example']].tolist(),
                             ['Own', 'second', 'other'])
            save.assert_not_called()
            unlink.assert_not_called()
            pd.testing.assert_frame_equal(source, original)
            dialog.destroy()

    def test_skip_shortcut_ignores_review_and_feedback_windows(self):
        body = cst.CTkFrame(self.root)
        body.pack()
        self.root.update()
        controller = practice.PracticeController.__new__(practice.PracticeController)
        controller.app, controller.action_frm = self.root, body
        with patch.object(controller, 'Skip_resp') as skip:
            self.assertEqual(controller.Skip_shortcut(), 'break')
            skip.assert_called_once_with()
            skip.reset_mock()
            dialog = cst.CTkToplevel(self.root)
            controller.Skip_shortcut()
            skip.assert_not_called()
            dialog.destroy()
            body.pack_forget()
            controller.Skip_shortcut()
            skip.assert_not_called()

    def test_long_review_fields_scroll_without_expanding_the_dialog(self):
        value = 'Long description and example. ' * 200
        dialog = ReviewDialog(self.root, 'Previous word', 'word ' * 100, value,
                              [('Phonetic', '[word]'), ('Description', value), ('Example', value)],
                              [('Delete audio', lambda: None)] * 3)
        dialog.geometry('700x600')
        self.root.after(350, self.root.quit)
        self.root.mainloop()
        body = dialog.detail_body
        self.assertLess(body._parent_frame.winfo_height(), dialog.winfo_height())
        self.assertGreater(body.winfo_height(), body._parent_canvas.winfo_height())
        body._parent_canvas.yview_moveto(1)
        self.root.update()
        self.assertGreater(body._parent_canvas.yview()[0], 0)
        self.assertEqual(sum(label.cget('text') == value for label in body.winfo_children()), 3)
        dialog.destroy()

    def test_conjugation_feedback_preserves_scoring_and_separates_header_rows(self):
        frame = pd.DataFrame({'ID': [1, 2], 'Spanish': ['hablar', 'mirar'],
            'Czech': ['speak', 'look'], 'Description': ['present', 'present'],
            'R': ['', ''], 'LR': ['', ''],
            **{key: ['form', 'form'] for key, _ in conjugation.PERSONS_MAP['Spanish']}})
        with patch_preferences(learned_by='Czech'), \
             patch_preferences(conjugation_batch=2), \
             patch.object(conjugation, 'exists', return_value=True), \
             patch.object(conjugation, 'load_source', return_value=frame), \
             patch.object(conjugation, 'play_effect', return_value=False):
            controller = conjugation.Conjugation(self.root, 'Spanish')
            self.root.update()
            self.assertNotEqual(controller.view.description.grid_info()['row'], controller.view.count.grid_info()['row'])
            controller.confirm()
            selected_id = controller.session.current.id
            selection = controller.session.selection
            self.assertEqual(selection.loc[selection.ID == selected_id, 'R'].iloc[0], 'F')
            self.assertEqual(controller.view.entries['s1'].cget('fg_color'), ui.ERROR)
            controller.confirm()
            self.assertEqual(controller.session.completed, 1)
            self.assertEqual(selection.loc[selection.ID == selected_id, 'R'].iloc[0], 'F')

    def test_scroll_frame_does_not_remove_other_mousewheel_callbacks(self):
        other_id = self.root.bind('<MouseWheel>', lambda event: None, add='+')
        frame = VerticalScrolledFrame_class(self.root)
        own_id = frame._wheel_binding
        frame.destroy()
        binding = self.root.bind('<MouseWheel>')
        self.assertIn(other_id, binding)
        self.assertNotIn(own_id, binding)

    def test_success_ring_handles_no_data_and_all_success_without_extra_figures(self):
        container, cards = summary_cards(self.root, ['Vocabulary', 'Conjugation', 'Grammar'])
        ring = SuccessRing(cards[0])
        ring.grid(row=0, column=0)
        self.root.update()
        ring.configure(text='0.00%', attempts=0)
        self.assertEqual(len(ring.canvas.find_all()), 3)
        ring.configure(text='100.00%', attempts=10)
        self.assertEqual(len(ring.canvas.find_all()), 3)
        self.assertEqual(ring.canvas.type(ring.canvas.find_all()[0]), 'image')
        ring.configure(text='-')
        self.assertEqual(len(ring.canvas.find_all()), 3)

    def test_previous_word_omits_empty_synonyms(self):
        from app.vocabulary.practise_review import open_review
        word = Mock(word='word', tr='translation', phon='', PoS='Noun', desc='', sen='')
        dialog = open_review(self.root, word, Mock(), Mock(), Mock(), synonyms='')
        labels = [widget.cget('text') for widget in dialog.detail_body.winfo_children()
                  if isinstance(widget, cst.CTkLabel)]
        self.assertNotIn('Synonyms', labels)
        self.assertNotIn('No synonyms linked.', labels)
        dialog.destroy()

    def test_ring_image_antialiases_edges_at_multiple_scales(self):
        from app.statistics.components import ring_image
        for scale in (1, 1.25, 2):
            image = ring_image(112*scale, 13*scale, '#d4dcc6', '#416d58', 88.35)
            self.assertEqual(image.size, (round(125*scale+4),)*2)
            self.assertGreater(len(image.getcolors(image.width*image.height)), 20)

    def test_section_tabs_keep_current_tab_after_fast_changes(self):
        tabs = SectionTabs(self.root)
        tabs.enable_transparent_panels()
        tabs.pack(fill='both', expand=True)
        for title in ('Overview', 'Guide', 'Keyboard shortcuts'):
            tabs.add(title)
        tabs.set('Guide')
        tabs.set('Keyboard shortcuts')
        tabs._grid_forget_all_tabs(exclude_name='Overview')
        self.root.update()
        self.assertEqual(tabs.get(), 'Keyboard shortcuts')
        self.assertEqual(tabs.tab('Keyboard shortcuts').winfo_manager(), 'grid')
        tabs.tab('Overview').destroy()
        tabs._draw()
        tabs.destroy()
        tabs._grid_forget_all_tabs(exclude_name='Overview')

    def test_rounded_corners_follow_position_changes_and_background_switches(self):
        host = cst.CTkFrame(self.root)
        host.pack(fill='both', expand=True)
        backdrop = ui.background(host, 'practice_warm_v4.png')
        panel = cst.CTkFrame(host, width=250, height=130, corner_radius=24, fg_color=ui.TEAL)
        panel.place(x=30, y=40)
        layer = surface(panel, backdrop)
        def settle():
            self.root.after(120, self.root.quit)
            self.root.mainloop()
        settle()
        first_photo = layer._photo
        self.assertIsNotNone(first_photo)
        self.assertEqual(layer._image.getpixel((0, 0)), backdrop._surface.region(panel).convert('RGB').getpixel((0, 0)))
        panel.place_configure(x=160, y=100)
        settle()
        self.assertIsNot(layer._photo, first_photo)
        self.assertEqual(layer._image.getpixel((0, 0)), backdrop._surface.region(panel).convert('RGB').getpixel((0, 0)))
        backdrop.switch_asset('practice_answer_v3.png')
        settle()
        self.assertEqual(layer._image.getpixel((0, 0)), backdrop._surface.region(panel).convert('RGB').getpixel((0, 0)))

    def test_surface_reuses_unchanged_render_and_releases_images_on_destroy(self):
        host = cst.CTkFrame(self.root)
        host.pack(fill='both', expand=True)
        backdrop = ui.background(host, 'practice_warm_v4.png')
        panel = cst.CTkFrame(host, width=250, height=130, corner_radius=24)
        panel.place(x=20, y=20)
        layer = surface(panel, backdrop, 'practice_answer_v3.png')
        self.root.update()
        layer.paint()
        photo = layer._photo
        layer.paint()
        self.assertIs(layer._photo, photo)
        panel.destroy()
        self.assertTrue(layer._dead)
        self.assertIsNone(layer._photo)
        self.assertIsNone(layer._image)
        self.assertIsNone(layer.source)


    def test_statistics_backdrop_scrolls_cached_tiles_using_only_viewport_image_memory(self):
        host = cst.CTkFrame(self.root)
        host.pack(fill='both', expand=True)
        backdrop = ui.background(host, 'statistics_warm_v2.png')
        scroller = VerticalScrolledFrame_class(host)
        scroller.pack(fill='both', expand=True)
        tk.Frame(scroller.interior, width=900, height=6000).grid(row=0, column=0)
        background = StatisticsBackdrop(scroller, backdrop)
        card = cst.CTkFrame(scroller.interior, width=800, height=200, corner_radius=24)
        card.place(x=20, y=4800)
        panel = background.add_panel(card)
        self.root.update()
        def settle():
            self.root.after(120, self.root.quit)
            self.root.mainloop()
        settle()
        photo = background._photo
        self.assertIsNotNone(photo)
        self.assertEqual(photo.height(), scroller.canvas.winfo_height())
        self.assertGreater(scroller.interior.winfo_height(), photo.height()*4)
        panel_photo = panel._photo
        with patch('app.ui.surfaces.ImageTk.PhotoImage', wraps=ui_surfaces.ImageTk.PhotoImage) as images:
            for position in (.2, .5, .8, 1):
                scroller.canvas.yview_moveto(position)
                panel.request()
                settle()
            images.assert_not_called()
        self.assertIs(panel._photo, panel_photo)
        self.assertGreater(scroller.canvas.yview()[0], 0)
        self.assertIs(background._photo, photo)
        self.assertLessEqual(abs(background.layer.winfo_rooty()-scroller.interior.winfo_rooty()), 1)
        self.assertIsNone(background._pending)
        self.root.geometry('1150x720')
        self.root.update()
        settle()
        self.assertEqual(background._photo.height(), scroller.canvas.winfo_height())
        self.assertEqual(background._photo.width(), scroller.canvas.winfo_width())
        scroller.destroy()
        self.assertTrue(background._dead)
        self.assertIsNone(background._photo)

    def test_statistics_loading_cover_remains_until_builder_and_layout_finish(self):
        window = StatisticsWindow(self.root)
        calls = []
        def build():
            self.assertIsNotNone(window.cover)
            self.assertFalse(window.ready)
            cst.CTkLabel(window.content, text='Prepared statistics').pack()
            calls.append(True)
        window.load(build)
        self.assertEqual(calls, [])
        self.root.after(350, self.root.quit)
        self.root.mainloop()
        self.assertEqual(calls, [True])
        self.assertTrue(window.ready)
        self.assertIsNone(window.cover)
        window.destroy()

    def test_closing_loading_statistics_cancels_deferred_builder(self):
        window = StatisticsWindow(self.root)
        calls = []
        window.load(lambda: calls.append(True))
        window.destroy()
        self.root.after(120, self.root.quit)
        self.root.mainloop()
        self.assertEqual(calls, [])
        self.assertEqual(window._jobs, set())


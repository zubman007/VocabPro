"""Recent-session feedback and compact sidebar geometry on synthetic lessons."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import customtkinter as cst

from app.core.context import AppContext
from app.grammar.practise import GrammarController
from app.grammar.session import GrammarSession
from app.shared.translations import LANGUAGES
from app.tests.test_grammar_selection import question


class RecentResultsTests(unittest.TestCase):
    def test_recent_window_is_bounded_chronological_and_scores_each_answer_once(self):
        state=GrammarSession([question(i) for i in range(17)])
        expected=[]
        for index in range(17):
            state.advance()
            correct=index%3!=0
            state.answer(state.options.index('yes' if correct else 'no'))
            expected.append(correct)
            self.assertIsNone(state.answer(0))
            self.assertFalse(state.reveal())
            self.assertEqual(list(state.recent_results),expected[-10:])
        self.assertEqual(state.correct,sum(expected))
        self.assertEqual(state.incorrect,len(expected)-sum(expected))
        self.assertEqual(len(state.recent_results),10)

    def test_reveal_is_failure_skip_is_not_and_new_round_resets_recent_results(self):
        state=GrammarSession([question(1),question(2),question(3)])
        state.advance();state.reveal();state.reveal()
        state.advance();state.advance()
        self.assertEqual(list(state.recent_results),[False])
        self.assertEqual(state.progress,{})
        state.answer(state.options.index('yes'))
        self.assertEqual(list(state.recent_results),[False,True])
        state.restart()
        self.assertEqual(list(state.recent_results),[])
        self.assertEqual(len(state.progress),1)


class SessionInsightUiTests(unittest.TestCase):
    def setUp(self):
        self.directory=TemporaryDirectory()
        self.root=cst.CTk()
        self.root.geometry('1400x850')
        self.root.update()
        self.errors=[]
        self.root.report_callback_exception=lambda *error:self.errors.append(error)
        self.context=AppContext(files_dir=Path(self.directory.name),on_home=Mock())
        self.context.bind(self.root)
        self.effects=patch('app.grammar.practise.play_effect')
        self.effects.start()

    def tearDown(self):
        self.effects.stop()
        for token in self.root.tk.call('after','info'):
            self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.directory.cleanup()
        self.assertEqual(self.errors,[])

    def lesson(self):
        return GrammarController(self.root,[question(i,category='Presente de Subjuntivo') for i in range(20)],
                                 Path(self.directory.name)/'English_gra.csv',Mock(),context=self.context)

    def settle(self):
        self.root.update()
        self.root.after(50,self.root.quit)
        self.root.mainloop()

    def test_feedback_caption_colors_and_reset_match_current_session(self):
        controller=self.lesson();self.settle()
        self.assertFalse(controller.view.recent.winfo_ismapped())
        with patch('app.grammar.practise.save_answers') as save:
            for answer in ('yes','no'):
                controller.choose(controller.session.options.index(answer))
                controller.next_question()
            controller.reveal();self.settle()
            self.assertEqual(controller.view.recent_caption.cget('text'),
                             self.context.translate('Last {count} answers: {accuracy}%').format(count=3,accuracy=33))
            self.assertEqual([slot.cget('fg_color') for slot in controller.view.recent_markers],
                             ['#567b63','#b87960','#b87960']+['#c6ceb8']*7)
            self.assertEqual(len(controller.pending_answers),2)
            controller.next_question();controller.next_question();self.settle()
            self.assertEqual(len(controller.session.recent_results),3)
            controller.restart();self.settle()
            self.assertFalse(controller.view.recent.winfo_ismapped())
            self.assertTrue(all(slot.cget('fg_color')=='#c6ceb8' for slot in controller.view.recent_markers))
            save.assert_not_called()

    def test_recent_caption_and_full_sidebar_fit_in_every_language(self):
        for language in LANGUAGES:
            with self.subTest(language=language):
                self.context.preferences=replace(self.context.preferences,app_language=language,grammar_batch=12)
                controller=self.lesson()
                for _ in range(12):
                    controller.choose(controller.session.options.index('yes'))
                    controller.next_question()
                self.settle()
                view=controller.view
                self.assertIn('100',view.recent_caption.cget('text'))
                self.assertIn('10',view.recent_caption.cget('text'))
                self.assertLessEqual(view.recent_caption._label.winfo_reqwidth(),view.recent_caption.winfo_width()+1)
                self.assertLessEqual(view.recent.winfo_height()/view.recent._get_widget_scaling(),42)
                canvas=view.session_panel._parent_canvas
                self.assertFalse(view.session_panel._scrollbar.winfo_ismapped(),
                    (language,view.session_compact,canvas.yview(),view.session_panel.winfo_reqheight(),canvas.winfo_height()))
                self.assertEqual(view.shortcuts.hint_font.cget('size'),12)
                self.assertGreaterEqual(view.shortcuts.winfo_rootx(),view.session_frame.winfo_rootx())
                self.assertLessEqual(view.shortcuts.winfo_rooty()+view.shortcuts.winfo_height(),
                                     canvas.winfo_rooty()+canvas.winfo_height()+2)
                controller.view.root.destroy()

    def test_short_window_compacts_gaps_and_restores_spacing_on_growth(self):
        controller=self.lesson()
        controller.choose(controller.session.options.index('no'))
        self.root.geometry('1400x650');self.settle()
        self.assertTrue(controller.view.session_compact)
        self.assertEqual(controller.view.shortcuts.hint_font.cget('size'),12)
        self.root.geometry('1400x1000');self.settle()
        self.assertFalse(controller.view.session_compact)
        self.assertFalse(controller.view.session_panel._scrollbar.winfo_ismapped())
        self.assertEqual(controller.view.shortcuts._last_geometry_manager_call['kwargs']['pady'],(6,12))

    def test_long_category_keeps_real_overflow_scrollable_and_cleans_resize_jobs(self):
        controller=self.lesson()
        controller.view.mode.configure(text='An unusually long category name '*16+'\nQuestion ID: 999999')
        self.root.geometry('1400x650');self.settle()
        panel=controller.view.session_panel
        self.assertTrue(panel._scrollbar.winfo_ismapped())
        panel._parent_canvas.yview_moveto(1);self.settle()
        self.assertGreater(panel._parent_canvas.yview()[0],0)
        controller.view.root.destroy();self.settle()
        self.assertTrue(controller.lifecycle.closed)

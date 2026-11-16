"""Grammar screen controller; round state and rendering are separate modules."""
from app.shared.messages import error_text
from app.core.context import get_context
from pathlib import Path
from app.ui import messagebox
from app.shared.audio_effects import play_effect
from app.repositories.grammar import Load_questions_from_csv, save_answers
from app.repositories.grammar_records import load_record, update_record
from datetime import datetime
from app.grammar.layout import build as build_layout, reset_option
from app.grammar.session import GrammarSession
from app.grammar.category_filter import category_options
from app.repositories.grammar_theory import load_theory
from app.grammar.theory_data import category_key
import logging
import csv
from app.core.screen_controller import ScreenController
from app.ui.answer_keys import answer_index, ANSWER_SEQUENCES, has_answer_modifier
from app.ui import learning_layout as ui
from app.shared import settings as s


class GrammarController:
    def __init__(self, app, questions, path, on_back, learned_by=None, initial_categories=None, remember_filter=None, *, context=None):
        self.context=get_context(app,context)
        self.translate=self.context.translate
        self.app, self.path, self.on_back = app, Path(path), on_back
        self.record_at_start=load_record(self.path)
        self.record_candidate=self.record_at_start
        self.remember_filter = remember_filter
        self.pending_answers=[]
        if learned_by is None:
            learned_by = self.context.preferences.learned_by
        theory_path = self.path.with_name(f'{learned_by}_{self.path.stem}_ex.csv')
        try:
            self.theory = load_theory(theory_path)
        except (OSError, UnicodeError, ValueError, csv.Error) as error:
            logging.getLogger(__name__).warning('Grammar theory could not be loaded')
            messagebox.showerror(parent=app,title=self.translate('Error'),message=error_text(error, self.translate))
            self.theory = {}
        self._theory_window = None
        self._filter_window = None
        self._review_window = None
        self.all_questions = tuple(questions)
        self.question_progress = {}
        self.categories = category_options(self.all_questions)
        available = {key for key, _, _ in self.categories}
        self.selected_categories = available if initial_categories is None else available & {
            category_key(value) for value in initial_categories}
        if initial_categories is not None and not self.selected_categories:
            raise ValueError('No questions match the selected category.')
        self.session = GrammarSession([question for question in self.all_questions
            if category_key(question.get('category', '')) in self.selected_categories], progress=self.question_progress)
        s.Clear_frames(app)
        self.view = build_layout(app, self.choose, self.reveal, self.next_question,
                                 self.back, self.exit_app, self.show_theory, self.open_filter,
                                 self.save)
        self.lifecycle = ScreenController(app,self.view.root,{
            '<Return>': self.continue_if_revealed,
            '<space>': self.reveal_or_next,
            '<Escape>': self.back,
            '<Control-s>': self.save, '<Control-S>': self.save,
            '<Alt-Right>': self.next_shortcut,
            '<Control-z>': self.review_previous, '<Control-Z>': self.review_previous,
            '<Control-t>': self.theory_shortcut, '<Control-T>': self.theory_shortcut,
            '<Control-f>': self.filter_shortcut, '<Control-F>': self.filter_shortcut,
        },context=self.context,on_window_close=self.exit_app)
        self.bindings=self.lifecycle.bindings
        self.bindings.bind('<KeyPress>', self.answer_key)
        for index in range(4):
            self.bindings.bind(str(index+1), lambda event, choice=index: self.answer_shortcut(choice, event))
        for sequence in ANSWER_SEQUENCES:
            if sequence not in ('<KeyPress-1>','<KeyPress-2>','<KeyPress-3>','<KeyPress-4>'):
                self.bindings.bind(sequence,self.answer_key)
        self.lifecycle.add_cleanup(self._close_dialogs)
        self._refresh_filter_status()
        self.next_question()
        self.lifecycle.after_idle(self._focus_lesson)

    def _close_dialogs(self):
        self._close_filter()
        if self._theory_window is not None and self._theory_window.winfo_exists():self._theory_window.destroy()

    def _focus_lesson(self):
        if self.bindings.closed:return
        focus = self.app.focus_get()
        if focus is None or focus.winfo_toplevel() is self.app:
            self.view.root.focus_set()

    def open_filter(self):
        if self.bindings.closed:
            return
        if self._filter_window is not None and self._filter_window.winfo_exists():
            self._filter_window.lift()
            return
        from app.grammar.category_filter import CategoryFilterDialog
        self._filter_window = CategoryFilterDialog(self.app, self.categories, self.selected_categories, self.apply_filter)

    def apply_filter(self, selected):
        selected = set(selected) & {key for key, _, _ in self.categories}
        if not selected or self.bindings.closed:
            return False
        if selected == self.selected_categories:
            self._remember_filter()
            return True
        self.selected_categories = selected
        self.session = GrammarSession([question for question in self.all_questions
            if category_key(question.get('category', '')) in selected], progress=self.question_progress)
        self.view.next.configure(command=self.next_question)
        self._refresh_filter_status()
        self.next_question()
        self._remember_filter()
        return True

    def _remember_filter(self):
        if self.remember_filter is not None:
            try:
                self.remember_filter(self.selected_categories)
            except (OSError, ValueError):
                parent = self._filter_window if self._filter_window is not None and self._filter_window.winfo_exists() else self.app
                messagebox.showerror(parent=parent, title=self.translate('Question categories'),
                    message=self.translate('Category filter applied but could not be remembered.'))

    def _refresh_filter_status(self):
        if len(self.selected_categories) == len(self.categories):
            self.view.filter_status.grid_remove()
        else:
            self.view.filter_status.configure(text=f"{self.translate('Filtered categories')}: "
                f'{len(self.selected_categories)}/{len(self.categories)}')
            self.view.filter_status.grid()

    def _close_filter(self):
        if self._filter_window is not None and self._filter_window.winfo_exists():
            self._filter_window.destroy()
        if self._review_window is not None and self._review_window.winfo_exists():
            self._review_window.destroy()

    def _shortcuts_allowed(self):
        if self.bindings.closed:return False
        if any(window is not None and window.winfo_exists() for window in
               (self._filter_window,self._review_window,self._theory_window)):
            return False
        focus = self.app.focus_get()
        return self.app.grab_current() is None and (focus is None or focus.winfo_toplevel() is self.app)

    def answer_shortcut(self, index, event=None):
        if self._shortcuts_allowed() and not (event and has_answer_modifier(event)):
            self.choose(index)
        return 'break'

    def answer_key(self, event):
        index = answer_index(event)
        if index is not None:return self.answer_shortcut(index, event)

    def next_shortcut(self, event=None):
        if self._shortcuts_allowed() and self.session.current is not None:
            self.next_question()
        return 'break'

    def theory_shortcut(self, event=None):
        if self._shortcuts_allowed():self.show_theory()
        return 'break'

    def filter_shortcut(self, event=None):
        if self._shortcuts_allowed():self.open_filter()
        return 'break'

    def review_previous(self, event=None):
        if not self._shortcuts_allowed() or self.session.previous is None:
            return 'break'
        from app.ui.learning_review import ReviewDialog
        question = self.session.previous
        self._review_window = ReviewDialog(self.app, 'Previous question', question['anchor'], question['prompt'],
            [('Category', question.get('category','')), ('Correct answer', question['correct_answer']),
             ('Explanation', question['explanation'])], actions=[('Close', lambda: self._review_window.destroy())], subtitle_caption='Question instruction',
            background_file='grammar_background_v1.png')
        return 'break'

    def next_question(self):
        if self.bindings.closed:
            return
        question = self.session.advance()
        self._refresh_theory()
        if question is None:
            self._show_finish()
            return
        view = self.view
        view.prompt.configure(text=question['prompt'])
        view.anchor.configure(text=question['anchor'])
        view.mode.configure(text=f"{self.translate('Question ID')}: {question['id']}" if question['id'] else '')
        if question.get('category'):
            view.mode.configure(text=f"{question.get('category')}\n{view.mode.cget('text')}")
        view.result.configure(text='')
        view.result.grid_remove()
        view.question._parent_canvas.yview_moveto(0)
        for index, (button, option) in enumerate(zip(view.options, self.session.options), 1):
            reset_option(button, f'{index} · {option}')
        self._refresh_score()

    def choose(self, index):
        if self.bindings.closed or not self.session.can_answer:
            return
        correct = self.session.is_correct(index)
        answered_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.pending_answers.append((self.session.current['id'],'S' if correct else 'F',
            self.session.current.copy(),answered_at))
        self.session.answer(index, when=answered_at)
        play_effect('success.FLAC' if correct else 'wrong.wav')
        self.view.options[index].configure(fg_color=ui.SUCCESS if correct else ui.ERROR)
        if not correct:
            self._highlight_correct()
        self._show_feedback()

    def reveal(self):
        if self.bindings.closed or not self.session.reveal():
            return
        self._highlight_correct()
        self._show_feedback()

    def continue_if_revealed(self, event=None):
        if self._shortcuts_allowed() and self.session.revealed:
            self.next_question()

    def reveal_or_next(self, event=None):
        if not self._shortcuts_allowed():
            return
        if self.session.revealed:
            self.next_question()
        else:
            self.reveal()

    def restart(self):
        if self.bindings.closed:
            return
        self.session.restart()
        self.view.next.configure(command=self.next_question)
        self.next_question()

    def back(self, event=None):
        if not self._can_leave():return 'break'
        self.lifecycle.finish(self.on_back)

    def save(self,event=None, *, close=True):
        if self.lifecycle.closed:return False
        if not self.pending_answers:
            if close:self.back()
            return True
        try:
            with update_record(self.path,self.record_candidate):
                save_answers(self.path,self.pending_answers)
        except (OSError,ValueError) as error:
            messagebox.showerror(parent=self.app,title=self.translate('Error'),message=error_text(error, self.translate))
            return False
        self.pending_answers.clear()
        play_effect('saved')
        if close:self.back()
        return True

    def _can_leave(self):
        return self.lifecycle.can_leave(bool(self.pending_answers),lambda:self.save(close=False),
            message='Save this practice session before going back?')

    def exit_app(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def _refresh_theory(self):
        question=self.session.current
        category=question.get('category','') if question else ''
        self.view.theory.configure(state='normal' if category_key(category) in self.theory else 'disabled')

    def show_theory(self):
        if self.bindings.closed:
            return
        question = self.session.current
        theory = self.theory.get(category_key(question.get('category'))) if question else None
        if theory is None:
            return
        if self._theory_window is not None and self._theory_window.winfo_exists():
            self._theory_window.destroy()
        from app.grammar.theory_window import TheoryWindow
        self._theory_window = TheoryWindow(self.app, theory)

    def _refresh_score(self):
        state = self.session
        self.record_candidate=max(self.record_candidate,state.best_streak)
        record_text=self.translate('New record: {count}') if self.record_candidate>self.record_at_start else self.translate('All-time best streak: {count}')
        self.view.counter.configure(text=f'{state.correct + state.incorrect} / {len(state.questions)}')
        self.view.score.configure(text=f"{self.translate('Correct answers')}: {state.correct}\n{self.translate('Incorrect answers')}: {state.incorrect}\n"
                                       f"{self.translate('Streak')}: {state.streak}\n{self.translate('Best streak')}: {state.best_streak}\n"
                                       +record_text.format(count=self.record_candidate),
                                  text_color='#815632' if self.record_candidate>self.record_at_start else ui.MUTED)
        recent=tuple(state.recent_results)
        if recent:
            self.view.recent_caption.configure(text=self.translate('Last {count} answers: {accuracy}%').format(
                count=len(recent),accuracy=round(100*sum(recent)/len(recent))))
            self.view.recent.grid()
        else:
            self.view.recent.grid_remove()
        for index,marker in enumerate(self.view.recent_markers):
            color=('#567b63' if recent[index] else '#b87960') if index<len(recent) else '#c6ceb8'
            if marker.cget('fg_color')!=color:marker.configure(fg_color=color)

    def _highlight_correct(self):
        for button, option in zip(self.view.options, self.session.options):
            if option == self.session.current['correct_answer']:
                button.configure(fg_color=ui.SUCCESS)
                break

    def _show_feedback(self):
        for button in self.view.options:
            button.configure(state='disabled', text_color_disabled='black')
        self.view.result.configure(text=self.session.current['explanation'].replace('\\n', '\n'))
        self.view.result.grid()
        self.view.result.update_idletasks()
        self.view.question._parent_canvas.yview_moveto(
            max(0, self.view.result.winfo_y()-12) / max(1, self.view.question.winfo_height()))
        self._refresh_score()

    def _show_finish(self):
        self.view.prompt.configure(text=self.translate('Done'))
        self.view.anchor.configure(text=self.translate('You have completed the whole grammar round.'))
        self.view.mode.configure(text='')
        for button in self.view.options:
            button.configure(text='', state='disabled')
        self.view.result.configure(text=self.translate('Press Next for a new round.'))
        self.view.result.grid()
        self.view.next.configure(command=self.restart)
        self.view.question._parent_canvas.yview_moveto(0)


def Grammar_training(app_input,lang_input,categories=None,*,context=None,on_back=None):
    """Keep the menu entry point; each call creates an independent lesson."""
    context=get_context(app_input,context)
    config=context.preferences
    if not config.grammar_enabled(lang_input):return
    path=context.grammar_path(lang_input)
    try:questions = Load_questions_from_csv(path)
    except (OSError,ValueError,csv.Error) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error, context.translate))
        return
    explicit_categories = categories is not None
    remember = None
    if config.remember_grammar_categories and config.learned_by:
        from app.repositories.grammar_filters import load_filter, save_filter
        available = {key for key, _, _ in category_options(questions)}
        filter_path = context.files_dir/'settings.csv'
        learned_by = config.learned_by
        remember = lambda selected: save_filter(filter_path, learned_by, lang_input, selected, available)
        if categories is None:
            categories = load_filter(filter_path, config.learned_by, lang_input, available)
    if config.learned_by:
        from app.repositories.grammar_theory import ensure_theory_categories
        try:
            ensure_theory_categories(path.with_name(f'{config.learned_by}_{lang_input}_gra_ex.csv'),
                [question.get('category', '') for question in questions])
        except OSError:
            logging.getLogger(__name__).warning('Missing theory categories could not be created')
    try:
        controller = GrammarController(app_input, questions, path, on_back if on_back is not None else context.go_home, config.learned_by,
            initial_categories=categories, remember_filter=remember,context=context)
    except (OSError,ValueError) as error:
        messagebox.showerror(parent=app_input,title=context.translate('Error'),message=error_text(error, context.translate))
        return
    if remember is not None and explicit_categories:
        controller._remember_filter()
    return controller

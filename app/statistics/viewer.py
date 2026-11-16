from app.shared.messages import error_text
from app.statistics.table import StatisticsTable
from app.statistics.difficult_words import DifficultWordsPanel
from app.statistics.grammar_categories import GrammarCategoriesPanel
from app.statistics.vocabulary_tags import VocabularyTagsPanel
from app.statistics.components import summary_cards, style_summary_cards, SuccessRing, arrange_success_ring, summary_metrics
from app.statistics.charts import Generate_chart, _release_chart
from app.statistics.background import StatisticsBackdrop
from app.statistics.window import StatisticsWindow
from app.statistics.data import prepare_statistics
from app.shared.background_task import BackgroundTask
from app.statistics.tabs import StatisticsTabs
from app.ui.surfaces import surface
from app.ui.learning_layout import background
from app.ui.theme import SECTION_SURFACE as SURFACE, PAGE, FONT, TEXT, style_statistics
from app.shared import config as s
from app.ui.helpers import Clear_tops, Grid_ratio
from app.ui.widgets import VerticalScrolledFrame_class
import customtkinter as cst
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.ui.brand import set_window_icon
import pywinstyles
from app.core.context import get_context

def Stats(app, *, context=None, language=None, section='Vocabulary'):
    """Open one statistics window; all mutable state belongs to its controller."""
    context = get_context(app, context)
    Clear_tops(app)
    window = StatisticsWindow(app)
    window.app_context = context
    languages = context.preferences.learning_languages
    window.initial_language = language if language in languages else languages[0]
    window.initial_section = section if section in ('Vocabulary', 'Grammar', 'Conjugation') else 'Vocabulary'
    window.minsize(min(1400, window.winfo_screenwidth()), min(800, max(400, window.winfo_screenheight()-80)))
    window.title(s.app_name + ' - ' + context.translate('Statistics Viewer'))
    set_window_icon(window)
    pywinstyles.apply_style(window, 'dark')
    controller = StatisticsController(window)
    window.controller = controller
    window.begin(controller.build)
    return window


def _build_statistics(window):
    """Stateless compatibility helper for embedded UI checks."""
    controller = StatisticsController(window)
    window.controller = controller
    return controller.build()


class StatisticsController:
    def __init__(self, window):
        self.window = window
        self.context = get_context(window)
        self.translate = self.context.translate
        self.task = None
        self.closed = False

    def build(self):
        window = self.window
        context = get_context(window)
        config = context.preferences
        content = window.content
        backdrop = background(window, 'statistics_warm_v2.png')
        backdrop.lower()
        content.configure(fg_color='transparent')
        surface(content, backdrop)
        holder_frm = tk.Frame(content, bg=PAGE, highlightthickness=0, bd=0)
        vs_frm = VerticalScrolledFrame_class(holder_frm)
        body_frm = vs_frm.interior
        vs_frm.canvas.configure(background=PAGE)
        ttk.Style().configure('Stats.TFrame', background=PAGE)
        summary_frm, cards = summary_cards(body_frm, [self.translate('Vocabulary'), self.translate('Conjugation'), self.translate('Grammar')])
        tabs = StatisticsTabs(body_frm, self.translate, lambda: vs_frm.canvas.yview_moveto(0))
        tabs.grid(row=1, column=0, columnspan=2, sticky='ew', padx=0, pady=(4, 12))
        window.statistics_tabs = tabs
        vocabulary_body = tabs.panels['Vocabulary']
        conjugation_body = tabs.panels['Conjugation']
        grammar_body = tabs.panels['Grammar']
        vocab_card, con_card, gra_card = cards
        window.summary_cards = cards
        from app.ui.components.module_header import ModuleHeader
        window.header = head_frm = ModuleHeader(content, self.translate('Statistics') + ' - ' + s.app_name, translate=self.translate, actions=[('close', window.destroy)])
        self.lang_var = tk.StringVar(value=getattr(window, 'initial_language', config.first_language))
        window._statistics_language = self.lang_var
        vocabulary_values, rate_lbl = summary_metrics(vocab_card, [
            self.translate('Number of words in vocabulary') + ': ',
            self.translate('Total Attempts (vocabulary): '),
            self.translate('Successful Attempts (vocabulary): '),
            self.translate('Failed Attempts (vocabulary): '),
            self.translate('Success Rate (vocabulary): ')])
        (self.tot_res_voc_lbl, self.tot_res_lbl, self.succ_res_lbl,
         self.fail_res_lbl, self.rate_res_lbl) = vocabulary_values
        conjugation_values, rate_con_lbl = summary_metrics(con_card, [
            self.translate('Number of verbs') + ' :',
            self.translate('Total Attempts (conjugation): '),
            self.translate('Successful Attempts (conjugation): '),
            self.translate('Failed Attempts (conjugation): '),
            self.translate('Success Rate (conjugation): ')], first_row=6)
        (self.tot_verbs_res_con_lbl, self.tot_res_con_lbl, self.succ_res_con_lbl,
         self.fail_res_con_lbl, self.rate_res_con_lbl) = conjugation_values
        grammar_values, rate_gra_lbl = summary_metrics(gra_card, [
            self.translate('Number of questions') + ' :',
            self.translate('Total answers (grammar): '),
            self.translate('Successful answers (grammar): '),
            self.translate('Failed answers (grammar): '),
            self.translate('Success Rate (grammar): ')], first_row=12)
        (self.tot_verbs_res_gra_lbl, self.tot_res_gra_lbl, self.succ_res_gra_lbl,
         self.fail_res_gra_lbl, self.rate_res_gra_lbl) = grammar_values
        self.tot_sheet = StatisticsTable(vocabulary_body, self.translate)
        self.difficult_words_panel = DifficultWordsPanel(vocabulary_body, self.translate)
        self.difficult_words_panel.grid(row=5, column=0, columnspan=2, sticky='ew', padx=20, pady=12)
        self.vocabulary_tags_panel=VocabularyTagsPanel(vocabulary_body,self.translate,lambda tag:_practise_tag(window,tag))
        self.vocabulary_tags_panel.grid(row=4,column=0,columnspan=2,sticky='ew',padx=20,pady=12)
        self.grammar_categories_panel = GrammarCategoriesPanel(grammar_body, self.translate, lambda category: _practise_category(window, category))
        self.grammar_categories_panel.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=12)
        sheet_lbl = self.tot_sheet.title_label
        self.chart_rep_frm = cst.CTkFrame(vocabulary_body)
        self.chart_cr_frm = cst.CTkFrame(vocabulary_body)
        self.chart_PoS_frm = cst.CTkFrame(vocabulary_body)
        self.chart_con_frm = cst.CTkFrame(conjugation_body)
        self.conjugation_progress = cst.CTkLabel(conjugation_body, text='', font=(FONT, 17), text_color=TEXT,
                                               justify='left', anchor='w', wraplength=850)
        self.conjugation_progress.grid(row=2, column=0, columnspan=2, sticky='ew', padx=24, pady=12)
        self.conjugation_table = StatisticsTable(conjugation_body, self.translate)
        self.conjugation_table.title_label.configure(text=self.translate('Difficult conjugation rounds'))
        self.conjugation_table.grid(row=3, column=0, columnspan=2, sticky='ew', padx=20, pady=12)
        self.chart_voc_trail_frm = cst.CTkFrame(vocabulary_body)
        conjugation_empty = cst.CTkLabel(conjugation_body, text=self.translate('No conjugation statistics available.'), font=(FONT, 20), text_color=TEXT)
        window.conjugation_empty = conjugation_empty
        style_statistics(sheet_lbl)
        Grid_ratio(vs_frm.interior, [], [1, 1])
        Grid_ratio(content, [1, 15], [1])
        Grid_ratio(vs_frm.interior, [], [1, 1])
        Grid_ratio(self.chart_rep_frm, [1], [1])
        Grid_ratio(self.chart_cr_frm, [1], [1])
        Grid_ratio(self.chart_PoS_frm, [1], [1])
        Grid_ratio(self.chart_con_frm, [1], [1])
        Grid_ratio(self.chart_voc_trail_frm, [1], [1])
        vs_frm.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.TRUE)
        holder_frm.grid(row=1, column=0, sticky='NWES')
        head_frm.grid_standard()
        self.tot_sheet.grid(row=6, column=0, columnspan=2, padx=20, pady=(8, 20), sticky='ew')
        style_summary_cards(cards)
        for ring, caption in ((self.rate_res_lbl, rate_lbl), (self.rate_res_con_lbl, rate_con_lbl), (self.rate_res_gra_lbl, rate_gra_lbl)):
            arrange_success_ring(ring, caption)
        self.window.configure(fg_color=PAGE)
        content.grid_rowconfigure(0, weight=0)
        languages = {self.translate(language): language for language in config.learning_languages}

        def select_language(label):
            self.lang_var.set(languages[label])
            window.load(self.load)
        switch = cst.CTkSegmentedButton(head_frm, values=list(languages), command=select_language, font=(FONT, 17), height=32, fg_color='#ded1b4', selected_color='#b5c3a4', selected_hover_color='#a3b48f', unselected_color='#ded1b4', unselected_hover_color='#cdbb98', text_color=TEXT, corner_radius=10)
        switch.set(self.translate(self.lang_var.get()))
        tabs.select(getattr(window, 'initial_section', 'Vocabulary'))
        self.language_switch=switch
        if len(languages)>1:head_frm.set_detail(switch, sticky='w')
        self.window._statistics_backdrop = StatisticsBackdrop(vs_frm, backdrop)
        canvas_background = self.window._statistics_backdrop
        header_surface = head_frm.attach_background(backdrop)
        switch_surface = canvas_background.add_panel(switch, header_surface)
        for button in switch.winfo_children():
            if isinstance(button, cst.CTkButton):
                canvas_background.add_panel(button, switch_surface)
        summary_frm.configure(fg_color='transparent')
        summary_surface = canvas_background.add_panel(summary_frm)
        for card in cards:
            canvas_background.add_panel(card.master, summary_surface)
        tabs_surface = canvas_background.add_panel(tabs)
        navigation_surface = canvas_background.add_panel(tabs.navigation, tabs_surface)
        for button in tabs.navigation.winfo_children():
            if isinstance(button, cst.CTkButton):
                canvas_background.add_panel(button, navigation_surface)
        for panel in tabs.panels.values():
            canvas_background.add_panel(panel, tabs_surface)
        for panel in (self.tot_sheet, self.difficult_words_panel, self.vocabulary_tags_panel, self.grammar_categories_panel, self.chart_rep_frm, self.chart_cr_frm, self.chart_PoS_frm, self.chart_con_frm, self.chart_voc_trail_frm):
            canvas_background.add_panel(panel)
        sheet_lbl.configure(bg_color=SURFACE, fg_color='transparent', corner_radius=0)
        canvas_background.add_panel(self.conjugation_table)
        content.update_idletasks()
        return self.load()

    def load(self):
        if self.closed:
            return False
        language = self.lang_var.get()
        config = self.context.preferences
        files = self.context.files_dir
        def calculate(cancelled, progress):
            return prepare_statistics(files, config.learned_by, language, s.stat_horizon,
                s.days_gap_map, s.default_wait, s.PoS_types, s.PoS_ideal)
        self.task = BackgroundTask(self.window, calculate, self._prepared, self.window.fail).start()
        return False

    def _prepared(self, prepared):
        try:
            self._apply_data(prepared)
        except Exception as error:
            if not self.closed:
                self.window.fail(error)

    def close(self):
        self.closed = True
        if self.task is not None:
            self.task.close()
            self.task = None
        self.df = None
        self.window.controller = None
        self.window = None

    def _apply_data(self, prepared):
        if self.closed:
            return
        data, conjugation, grammar = prepared
        charts = []
        self.df = data['table']
        from app.repositories.tags import decode_tags
        self.df=decode_tags(self.df,self.context.tags_path(self.lang_var.get()),self.context.preferences.learned_by,
            self.lang_var.get(),target=self.context.preferences.tag_display_language=='Learning language')
        if not self.context.preferences.tags_enabled:self.df=self.df.drop(columns=['Tags'],errors='ignore')
        self.difficult_words_panel.set_items(*data['difficult'])
        from app.repositories.tags import load_catalog
        from app.statistics.vocabulary_tags import TagStatistics
        catalog,_=load_catalog(self.context.tags_path(self.lang_var.get()),self.context.preferences.learned_by,self.lang_var.get())
        counts={item.name:item for item in data.get('tags',[])}
        column=self.lang_var.get() if self.context.preferences.tag_display_language=='Learning language' else self.context.preferences.learned_by
        items=[]
        for _,row in catalog.iterrows():
            item=counts.get(row.ID) or counts.get(row[self.context.preferences.learned_by])
            items.append(TagStatistics(row[column] or row[self.context.preferences.learned_by],item.words if item else 0,
                item.successes if item else 0,item.failures if item else 0,row.ID))
        self.vocabulary_tags_panel.set_items(items or data.get('tags',[]))
        if not self.context.preferences.tags_enabled:self.vocabulary_tags_panel.grid_remove()
        _show_summary(data['summary'], self.tot_res_voc_lbl, self.tot_res_lbl, self.succ_res_lbl, self.fail_res_lbl, self.rate_res_lbl)
        self.tot_sheet.set_data(self.df)
        for values, frame, title, row in ((data['forecast'], self.chart_rep_frm, 'Number of words to review next days', 0), (data['growth'], self.chart_cr_frm, 'Growth of the vocabulary', 1), (data['pos'], self.chart_PoS_frm, 'Vocabulary by Part of Speech', 2), (data['trailing'], self.chart_voc_trail_frm, 'Vocabulary trailing successes', 3)):
            charts.append((values, frame, title, row))
        available = conjugation is not None
        _set_conjugation_available(self.window, available)
        if available:
            from app.statistics.conjugation import progress_table
            progress = conjugation.get('progress')
            if progress is not None:
                lines = [f'{self.translate(key)}: {progress[field]}' for key, field in (
                    ('Practised conjugation rounds', 'practised'), ('Unpractised conjugation rounds', 'unpractised'),
                    ('Forms in practised rounds', 'covered_forms'))]
                lines.append(self.translate('Conjugation statistics explanation'))
                self.conjugation_progress.configure(text='\n'.join(lines))
                self.conjugation_table.set_data(progress_table(progress))
            charts.append((conjugation['trailing'], self.chart_con_frm, 'Conjugation trailing successes', 0))
            if conjugation['trailing'].empty:
                self.window.conjugation_empty.grid(row=1, column=0, columnspan=2, padx=24, pady=32)
            else:
                self.window.conjugation_empty.grid_remove()
            _show_summary(conjugation['summary'], self.tot_verbs_res_con_lbl, self.tot_res_con_lbl, self.succ_res_con_lbl, self.fail_res_con_lbl, self.rate_res_con_lbl)
        else:
            _release_chart(self.chart_con_frm)
            self.chart_con_frm.grid_remove()
            self.window.conjugation_empty.grid_remove()
        if grammar is not None:
            self.grammar_categories_panel.set_items(grammar['categories'], summary=grammar['summary'],best_streak=grammar.get('best_streak',0))
            _show_summary(grammar['summary'], self.tot_verbs_res_gra_lbl, self.tot_res_gra_lbl, self.succ_res_gra_lbl, self.fail_res_gra_lbl, self.rate_res_gra_lbl)
        else:
            self.grammar_categories_panel.set_items([])
            for label in (self.tot_verbs_res_gra_lbl, self.tot_res_gra_lbl, self.succ_res_gra_lbl, self.fail_res_gra_lbl, self.rate_res_gra_lbl):
                label.configure(text='-')
        self._render_charts(iter(charts))

    def _render_charts(self, charts):
        if self.closed:
            return
        try:
            chart = next(charts)
        except StopIteration:
            self.window.complete()
            return
        try:
            Generate_chart(*chart)
        except Exception as error:
            self.window.fail(error)
            return
        # Keep the cover until every graph is prepared, yielding between figures.
        self.window._later(1, lambda: self._render_charts(charts))



def _show_summary(summary, count_label, total_label, success_label, failure_label, ring):
    from app.shared.localization_format import percent
    count, successes, failures = summary
    attempts = successes + failures
    count_label.configure(text=count)
    total_label.configure(text=attempts)
    success_label.configure(text=successes)
    failure_label.configure(text=failures)
    ring.configure(text=percent(successes / attempts if attempts else 0,
        get_context(ring).preferences.app_language, places=2), attempts=attempts)

def _set_conjugation_available(window, available):
    window.statistics_tabs.set_conjugation_available(available)
    vocabulary, conjugation, grammar = [card.master for card in window.summary_cards]
    container = vocabulary.master
    for column in range(3):container.grid_columnconfigure(column,weight=0,uniform='',minsize=0)
    visible=[vocabulary,grammar]+([conjugation] if available else [])
    if not available:conjugation.grid_remove()
    for column,card in enumerate(visible):
        container.grid_columnconfigure(column,weight=1,uniform='summary')
        card.grid(row=0,column=column,sticky='nsew',padx=6)

def _practice_return(window, section):
    """Retain navigation values, not widgets belonging to the closed statistics window."""
    app, context = window.master, get_context(window)
    language = window._statistics_language.get()
    def reopen():
        context.go_home()
        return Stats(app, context=context, language=language, section=section)
    return reopen


def _practise_category(window, category):
    if not window.winfo_exists() or getattr(window, '_opening_practice', False) or getattr(window, '_building', False):
        return
    window._opening_practice = True
    try:
        from app.grammar.practise import Grammar_training
        controller = Grammar_training(window.master,window._statistics_language.get(),categories=[category],
            context=get_context(window),on_back=_practice_return(window, 'Grammar'))
    except Exception as error:
        messagebox.showerror(parent=window, title=get_context(window).translate('Statistics'), message=error_text(error, get_context(window).translate))
    else:
        if controller is not None:window.destroy()
    finally:
        window._opening_practice = False


def _practise_tag(window,tag_id):
    if not window.winfo_exists() or getattr(window, '_opening_practice', False) or getattr(window, '_building', False):
        return
    window._opening_practice = True
    context=get_context(window)
    try:
        from app.repositories.tag_lessons import tag_lesson
        from app.vocabulary.practise import Rep
        language=window._statistics_language.get()
        frame=tag_lesson(context.vocabulary_path(language),context.tags_path(language),
                         context.preferences.learned_by,language,tag_id)
        if frame.empty:return
        controller = Rep(window.master,frame,language,1 if language==context.preferences.first_language else 2,
            context=context,on_back=_practice_return(window, 'Vocabulary'))
        if controller is not None:window.destroy()
    except (OSError,ValueError) as error:
        messagebox.showerror(parent=window,title=context.translate('Tags'),message=error_text(error, context.translate))
    finally:
        window._opening_practice = False

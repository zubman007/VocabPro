"""Screen controller with per-instance state; menu entry point preserved."""
from app.vocabulary.practise_session import PracticeSession, ChoicePool
from app.ui import learning_layout as ui
from app.vocabulary.practise_layout import style_practice
from app.vocabulary.practise_audio import PracticeAudio
from app.shared.audio_effects import play_effect
from app.vocabulary.practise_review import open_review
from app.vocabulary.practise_data import Word, answers_match, shuffle_letters as Shuffle_w
from app.repositories.vocabulary import save_practice,read_words
from app.shared import settings as s
from app.core.context import get_context
from app.shared.diagnostics import report_error
from app.shared.learning_data import Set_datatypes
import customtkinter as cst
from tkinter import *
from tkinter import messagebox
from functools import partial
import pygame
import random
from app.core.screen_controller import ScreenController
from app.ui.components.module_header import ModuleHeader
from app.ui.answer_keys import answer_index, ANSWER_SEQUENCES, has_answer_modifier
from app.repositories import synonyms
from app.repositories.tags import load_catalog
from app.vocabulary.tags_data import translated_tags

class PracticeController:
    """Owns one screen, its widgets and editing/learning state."""

    def __init__(self, app_input, repeat_df_input, lang, lang_ord_desc, *, context=None, on_back=None):
        self.context=get_context(app_input,context)
        self.on_back = on_back if on_back is not None else self.context.go_home
        self.translate=self.context.translate
        self.learned_by = self.context.preferences.learned_by
        self.lang_desc, self.mistake, self.app, self.lang_ord = (lang, 0, app_input, lang_ord_desc)
        batch = repeat_df_input.copy()
        Set_datatypes(batch,self.lang_desc,self.learned_by)
        self.session = PracticeSession(batch, s.days_gap_map, s.default_wait)
        self._initial_session_data=self.session.data.copy(deep=True)
        self._has_answers=False
        self._synonyms_fit_id=None
        self.session_size = len(batch)
        if not self.session:
            return
        file_path = self.context.vocabulary_path(self.lang_desc)
        self.synonym_words = read_words(file_path)
        self._tag_values={int(identifier):value for identifier,value in
            self.synonym_words[['ID','Tags']].itertuples(index=False,name=None)} if 'Tags' in self.synonym_words else {}
        self._tag_translations={}
        if any(str(value).strip() for value in self._tag_values.values()):
            try:
                catalog,_=load_catalog(self.context.tags_path(lang),self.learned_by,lang)
                self._tag_translations={name.casefold():target for name,target in
                    catalog[[self.learned_by,lang]].itertuples(index=False,name=None)}
            except (OSError,ValueError) as error:
                report_error(error,operation='load practice tag labels')
                message=self.translate(str(error))
                if hasattr(error,'row'):message=message.format(row=error.row)
                messagebox.showerror(parent=self.app,title=self.translate('Tags'),message=message)
        translations = self.synonym_words[self.learned_by]
        self.choice_pool = ChoicePool(translations)
        self.synonym_relations, _ = synonyms.load(file_path, self.synonym_words)
        self.audio = PracticeAudio(self.learned_by,self.lang_desc,folder=self.context.audio_folder(self.lang_desc))
        type_2 = self.context.preferences.context_probabilities[self.lang_ord - 1]
        type_3 = self.context.preferences.audio_probabilities[self.lang_ord - 1]
        self.test_weights = ((100 - type_2 - type_3) / 100, type_2 / 100, type_3 / 100)
        s.Clear_frames(self.app)
        self.rep_frm = cst.CTkFrame(self.app)
        self.lifecycle=ScreenController(self.app,self.rep_frm,context=self.context,on_window_close=self.Exit)
        self.bindings=self.lifecycle.bindings
        self.lifecycle.add_cleanup(self._dispose)
        self.bindings.bind('<KeyPress>',self.Answer_key)
        for sequence in ANSWER_SEQUENCES:
            if 'KeyPress-KP_' in sequence:self.bindings.bind(sequence,self.Answer_key)
        self.rep_frm.pack(side=BOTTOM, fill=BOTH, expand=TRUE)
        self.rep_frm._backdrop = ui.background(self.rep_frm, 'practice_warm_v4.png')
        self.header=head_frm=ModuleHeader(self.rep_frm,self.translate('Repeat')+' '+self.translate(self.lang_desc),translate=self.translate,
            actions=[('save',partial(self.Save_rep,'')),('listen',partial(self.Play_audio,'None','old','')),
                ('close',self.Back),('exit',self.Exit)])
        self.action_frm = cst.CTkFrame(self.rep_frm, bg_color=s.clr_bg_trans, fg_color=s.clr_bg_trans)
        self.lbl_frm = cst.CTkFrame(self.action_frm, bg_color=s.clr_bg_trans, fg_color=s.clr_repeat_bg)
        self.opc_frm = cst.CTkFrame(self.action_frm, bg_color=s.clr_bg_trans, fg_color=s.clr_bg_letters)
        self.letters_frm = cst.CTkFrame(self.action_frm, bg_color=s.clr_bg_trans, fg_color=s.clr_bg_letters)
        self.show_w_frm = cst.CTkFrame(self.rep_frm, bg_color=s.clr_bg_trans, fg_color='#eb3d49', corner_radius=40, border_width=3)
        self.type_2_frm = cst.CTkFrame(self.lbl_frm, bg_color=s.clr_repeat_bg, fg_color=s.clr_repeat_bg)
        self.play_btn=head_frm.buttons['listen']
        self.play_btn.configure(state='disabled')
        self.headers = ['ID', self.lang_desc, 'Phonetic', self.learned_by, 'Audio', 'Description', 'Example', 'Part of Speech', 'Created', 'Repetition', 'Next repetition']
        if self.lang_desc == 'Spanish':
            self.headers = [i for i in self.headers if i != 'Phonetic']
        self.w_old, self.w_new, self.resp_var = (Word('', '', '', '', '', '', ''), Word('', '', '', '', '', '', ''), StringVar(master=self.app))
        self.resp_entry = cst.CTkEntry(self.action_frm, width=800, textvariable=self.resp_var, **s.entry_set_01)
        self.transl_lbl = cst.CTkLabel(self.lbl_frm, text='', **s.lbl_set_11)
        self.desc_lbl = cst.CTkLabel(self.type_2_frm, text='', wraplength=1200, **s.lbl_set_12)
        self.sentence_lbl = cst.CTkLabel(self.type_2_frm, text='', wraplength=1200, **s.lbl_set_12)
        self.letters_lbl = cst.CTkLabel(self.letters_frm, text='', **s.lbl_set_05)
        self.play_type_3_btn = cst.CTkButton(self.lbl_frm, command=partial(self.Play_audio, 'None', 'new', ''), text=self.translate('Audio'), width=120, height=120, **s.btn_set_6)
        self.op1_btn = cst.CTkButton(self.opc_frm, command=partial(self.Play_audio, 'None', 'new', ''), height=60, **s.btn_set_7)
        self.op2_btn = cst.CTkButton(self.opc_frm, command=partial(self.Play_audio, 'None', 'new', ''), height=60, **s.btn_set_7)
        self.op3_btn = cst.CTkButton(self.opc_frm, command=partial(self.Play_audio, 'None', 'new', ''), height=60, **s.btn_set_7)
        self.op4_btn = cst.CTkButton(self.opc_frm, command=partial(self.Play_audio, 'None', 'new', ''), height=60, **s.btn_set_7)
        self.skip_btn = cst.CTkButton(self.action_frm, command=self.Skip_resp, text=self.translate('Next'), width=300, height=80, **s.btn_set_1)
        self.confirm_btn = cst.CTkButton(self.action_frm, command=partial(self.Conf_resp, '', ''), text=self.translate('OK'), width=300, height=80, **s.btn_set_1)
        self.w_lbl = cst.CTkLabel(self.show_w_frm, text='', **s.lbl_set_19)
        self.transl_lrn_lbl = cst.CTkLabel(self.show_w_frm, text='', **s.lbl_set_03)
        self.pho_lrn_lbl = cst.CTkLabel(self.show_w_frm, text='', **s.lbl_set_20)
        self.PoS_lrn_lbl = cst.CTkLabel(self.show_w_frm, text='', **s.lbl_set_20)
        self.desc_lrn_lbl = cst.CTkLabel(self.show_w_frm, text='', wraplength=1200, **s.lbl_set_13)
        self.sentence_lrn_lbl = cst.CTkLabel(self.show_w_frm, text='', wraplength=1200, **s.lbl_set_18)
        show_w_next_btn = cst.CTkButton(self.show_w_frm, command=partial(self.Show_w_next, ''), text=self.translate('OK'), width=300, height=80, **s.btn_set_1)
        self.bindings.bind('<Return>', partial(self.Conf_resp, ''))
        self.bindings.bind('<Control-p>', partial(self.Play_audio, 'None', 'old'))
        self.bindings.bind('<Control-P>', partial(self.Play_audio, 'None', 'old'))
        self.bindings.bind('<Control-s>', self.Save_rep)
        self.bindings.bind('<Control-S>', self.Save_rep)
        self.bindings.bind('<Control-r>', self.Review_w)
        self.bindings.bind('<Control-R>', self.Review_w)
        self.bindings.bind('<KeyRelease-Control_L>', self.Review_w_end)
        self.bindings.bind('<Alt-Right>', self.Skip_shortcut)
        self.bindings.bind('<Escape>',lambda event:self.Back())
        self.bindings.bind('<Control-h>',self.Synonym_shortcut)
        self.bindings.bind('<Control-H>',self.Synonym_shortcut)
        self._response_trace = self.lifecycle.trace(self.resp_var,'write',self.Resp_change)
        self.lbl_frm.grid(row=0, column=0, sticky='NWES', padx=10, pady=10, columnspan=2, rowspan=2)
        self.desc_lbl.grid(row=0)
        self.sentence_lbl.grid(row=1)
        self.resp_entry.grid(row=2, column=0, padx=12, pady=10, sticky='ew', columnspan=2)
        self.letters_frm.grid(row=3, column=0, sticky='WE', padx=0, pady=10, columnspan=2)
        self.letters_lbl.grid(row=0, sticky='NWES', padx=0, pady=10, columnspan=2)
        self.skip_btn.grid(row=4, column=1, padx=5, pady=5)
        self.confirm_btn.grid(row=4, column=0, padx=5, pady=5)
        self.w_lbl.grid(row=0, padx=5, pady=5)
        self.transl_lrn_lbl.grid(row=1, padx=5, pady=5)
        show_w_next_btn.grid(row=6, padx=5, pady=5)
        head_frm.grid_standard(columnspan=2)
        self.action_frm.grid(row=1, sticky='NWES')
        self.play_type_3_btn.grid(row=0, padx=5, pady=5, columnspan=2, rowspan=2)
        self.op1_btn.grid(row=0, column=0, padx=5, pady=5)
        self.op2_btn.grid(row=0, column=1, padx=5, pady=5)
        self.op3_btn.grid(row=1, column=0, padx=5, pady=5)
        self.op4_btn.grid(row=1, column=1, padx=5, pady=5)
        s.Grid_ratio(self.letters_frm, [1], [1])
        s.Grid_ratio(self.lbl_frm, [1, 1], [1])
        s.Grid_ratio(self.rep_frm, [1, 15], [1])
        s.Grid_ratio(self.action_frm, [4, 5, 1, 1, 3], [1, 1])
        s.Grid_ratio(self.show_w_frm, [1, 1, 1, 1, 1, 1], [1])
        s.Grid_ratio(self.type_2_frm, [1, 1], [1])
        s.Grid_ratio(self.opc_frm, [1, 1], [1, 1])
        self.sidebar = style_practice(self.rep_frm, head_frm, self.action_frm, self.lbl_frm, self.letters_frm, self.opc_frm, self.show_w_frm, self.type_2_frm, prompt=self.transl_lbl, response=self.resp_entry, word=self.w_lbl, translation=self.transl_lrn_lbl, continue_button=show_w_next_btn, skip_button=self.skip_btn, review=partial(self.Review_w, None))
        self.lbl_frm.grid_configure(rowspan=1)
        self.current_tags_label=cst.CTkLabel(self.lbl_frm,text='',font=(ui.FONT,13),text_color='#c6dacb',
            fg_color='transparent',anchor='w',justify='left',width=0,wraplength=800)
        from app.ui.surfaces import surface
        self.lbl_frm._prompt_footer=self.current_tags_label
        self.current_tags_label.bind('<Configure>',lambda event:self.lbl_frm._fit_prompt(),add='+')
        self.answer_tags_label=cst.CTkLabel(self.show_w_frm,text='',font=(ui.FONT,16),
            text_color='#567b63',wraplength=800,justify='left')
        self.hint_button = cst.CTkButton(self.letters_frm, text=self.translate('Show hint'),
            command=self.Show_hint, height=36)
        ui.button(self.hint_button, secondary=True)
        from app.ui.surfaces import surface
        surface(self.hint_button, self.letters_frm._surface)
        self.synonym_button = cst.CTkButton(self.action_frm, text=self.translate('Synonyms'), command=self.Show_synonyms,
            fg_color='#48665a', hover_color='#355e59', height=38,width=160)
        self.synonym_dot=cst.CTkLabel(self.synonym_button,text='●',text_color='#80d591',
            fg_color='#48665a',font=(ui.FONT,16),width=16,height=20)
        self.synonym_dot.bind('<Button-1>',lambda event:self.Show_synonyms())
        self.current_synonyms = cst.CTkScrollableFrame(self.action_frm, fg_color='#d7dfca',corner_radius=6,height=28)
        self.current_synonyms._parent_frame.grid_propagate(False)
        from app.ui.surfaces import surface
        surface(self.current_synonyms._parent_frame,self.action_frm._surface)
        self.current_synonyms.grid_columnconfigure(0,weight=1)
        self.current_synonym_label = cst.CTkLabel(self.current_synonyms,text='',text_color=ui.TEXT,
            font=(ui.FONT,14),wraplength=0,justify='left',anchor='w')
        self.current_synonym_label.grid(sticky='ew',padx=10,pady=2)
        self.edit_current_synonyms=cst.CTkButton(self.current_synonyms._parent_frame,text=self.translate('Edit synonyms'),
            command=self.Edit_current_synonyms,fg_color='#48665a',hover_color='#355e59',
            width=110,height=24,font=(ui.FONT,13))
        self.edit_current_synonyms.grid(row=1,column=2,sticky='ne',padx=6,pady=6)
        from app.ui.module_style import tool_button
        tool_button(self.synonym_button)
        tool_button(self.edit_current_synonyms)
        self.synonym_dot.configure(fg_color=self.synonym_button.cget('fg_color'))
        self._synonyms_hscroll=cst.CTkScrollbar(self.current_synonyms._parent_frame,orientation='horizontal',
            command=self.current_synonyms._parent_canvas.xview,height=12,width=40)
        self.current_synonyms._parent_canvas.configure(xscrollcommand=self._synonyms_hscroll.set)
        self.current_synonyms._parent_canvas.bind('<Configure>',self._resize_current_synonyms,add='+')
        self.current_synonym_label.bind('<Configure>',self._resize_current_synonyms,add='+')
        show_w_next_btn.grid_configure(row=99)
        self.New_repeat(1)

    def tag_text(self, word_id):
        if not self.context.preferences.tags_enabled:return ''
        if word_id in ('',None):return ''
        return translated_tags(getattr(self,'_tag_values',{}).get(int(word_id),''),
                               getattr(self,'_tag_translations',{}) if self.context.preferences.tag_display_language=='Learning language' else {})

    def synonym_text(self, word_id):
        if word_id in ('', None):return ''
        return synonyms.describe(self.synonym_relations, self.synonym_words, word_id, self.lang_desc, self.learned_by)

    def Show_synonyms(self):
        self.synonym_button.grid_remove()
        value=self.synonym_text(self.w_new.id)
        count=len(value.splitlines())
        self.current_synonym_label.configure(text=value or self.translate('No synonyms linked.'),
            font=(ui.FONT,13 if count>5 else 14))
        self.current_synonyms.grid(row=5,column=0,columnspan=2,sticky='ew',pady=(0,6))
        self._resize_current_synonyms()
        self.current_synonyms._parent_canvas.yview_moveto(0)
        self.current_synonyms._parent_canvas.xview_moveto(0)

    def _resize_current_synonyms(self,event=None):
        if self._synonyms_fit_id is None:
            self._synonyms_fit_id=self.lifecycle.after_idle(self._fit_current_synonyms)

    def _fit_current_synonyms(self):
        self._synonyms_fit_id=None
        if getattr(self,'_sizing_synonyms',False):return
        self._sizing_synonyms=True
        try:
            self.current_synonyms.grid_rowconfigure(0,weight=0)
            self.current_synonyms.grid_columnconfigure(0,weight=1)
            scale=self.current_synonyms._get_widget_scaling()
            canvas=self.current_synonyms._parent_canvas
            needed=self.current_synonym_label._label.winfo_reqwidth()+round(20*scale)
            desired=max(canvas.winfo_width(),needed)
            if float(canvas.itemcget(self.current_synonyms._create_window_id,'width'))!=desired:
                canvas.itemconfigure(self.current_synonyms._create_window_id,width=desired)
            horizontal=needed>canvas.winfo_width()+1
            required=int(self.current_synonym_label.winfo_reqheight()/scale)+4
            height=max(40,min(110,required))
            outer_height=max(height,self.edit_current_synonyms.cget('height'))+12+(16 if horizontal else 0)
            if self.current_synonyms._parent_frame.cget('height')!=outer_height:
                self.current_synonyms._parent_frame.configure(height=outer_height)
            if self.current_synonyms.cget('height')!=height:self.current_synonyms.configure(height=height)
            # CTk's scrollbar defaults to height 200 and otherwise forces the
            # entire scroll-frame row to that height, regardless of canvas size.
            if self.current_synonyms._scrollbar.cget('height')!=height:
                self.current_synonyms._scrollbar.configure(height=height)
            # CTkScrollableFrame.configure rebuilds its grid: apply visibility last.
            if required>110:
                if self.current_synonyms._scrollbar.winfo_manager()!='grid':
                    self.current_synonyms._scrollbar.grid(row=1,column=1,sticky='ns',pady=6)
            elif self.current_synonyms._scrollbar.winfo_manager()=='grid':self.current_synonyms._scrollbar.grid_remove()
            if horizontal:
                if self._synonyms_hscroll.winfo_manager()!='grid':
                    self._synonyms_hscroll.grid(row=2,column=0,columnspan=2,sticky='ew',padx=6,pady=(0,4))
            elif self._synonyms_hscroll.winfo_manager()=='grid':self._synonyms_hscroll.grid_remove()
            bounds=canvas.bbox('all')
            if bounds and tuple(map(float,canvas.cget('scrollregion').split()))!=bounds:
                canvas.configure(scrollregion=bounds)
        finally:self._sizing_synonyms=False

    def Synonym_shortcut(self,event=None):
        if not self.context.preferences.show_synonyms and self.action_frm.winfo_ismapped() and not any(
                isinstance(widget,cst.CTkToplevel) for widget in self.app.winfo_children()):
            self.Show_synonyms()
        return 'break'

    def Answer_key(self,event):
        index = answer_index(event)
        if index is not None and self.opc_frm.winfo_ismapped():
            options = getattr(self,'_answer_options',None)
            if options and index<len(options):return self.Choice_shortcut(options[index],event)

    def Exit(self):
        if self._can_leave():self.lifecycle.finish(self.app.destroy)

    def Back(self):
        if self._can_leave():self.lifecycle.finish(self._return_home)

    def _can_leave(self):
        fields=['Description','Example','Audio']
        dirty=self._has_answers or not self.session.data[fields].equals(self._initial_session_data[fields])
        return self.lifecycle.can_leave(dirty,lambda:self.Save_rep('',close=False),
            message='Save this practice session before going back?')

    def _return_home(self):
        self.rep_frm.destroy()
        self.on_back()

    def _dispose(self, event=None):
        self._synonyms_fit_id=None
        self._response_trace=None
        dialog=getattr(self,'_review_dialog',None)
        if dialog is not None and dialog.winfo_exists():dialog.destroy()

    def Review_w(self, event):
        if any((isinstance(widget, cst.CTkToplevel) for widget in self.app.winfo_children())):
            return
        if self.w_old.id in ('', self.w_new.id):
            return
        self.Auto_audio('None', 'old')
        try:
            self._review_dialog=open_review(self.app, self.w_old, self.Del_audio, self.Del_desc, self.Del_sentence_example,
                        self.synonym_text(self.w_old.id),self.Edit_review_synonyms,
                        lambda:self.Edit_review_attribute('Description'),lambda:self.Edit_review_attribute('Example'),
                        tags=self.tag_text(self.w_old.id),on_tags=self.Edit_review_tags if self.context.preferences.tags_enabled else None)
        except (OSError, TclError) as error:
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=self.translate(str(error)))

    def Edit_review_tags(self):
        from app.vocabulary.editor_tag_picker import WordTagsDialog
        identifier=int(self.w_old.id)
        if getattr(self,'_review_dialog',None) is not None:self._review_dialog.destroy()
        def apply(value):
            self._tag_values[identifier]=value
            self.session.set_attribute(identifier,'Tags',value)
            self._has_answers=True
            self.sidebar.update_session(self.w_old,self.w_new,len(self.session.completed),self.session_size,
                self.synonym_text(self.w_old.id),tags=self.tag_text(identifier))
            self.lifecycle.after_idle(lambda:self.Review_w(None))
        WordTagsDialog(self.app,self.lang_desc,identifier,self.w_old.word,
            self._tag_values.get(identifier,''),apply,context=self.context)

    def Edit_review_attribute(self,column):
        from app.vocabulary.practise_review_editor import edit_attribute
        attribute='desc' if column=='Description' else 'sen'
        word_id=int(self.w_old.id)
        value=getattr(self.w_old,attribute)
        self._review_dialog.destroy()
        def save(text):
            self.session.set_attribute(word_id,column,text)
            setattr(self.w_old,attribute,text)
            if int(self.w_new.id)==word_id:
                setattr(self.w_new,attribute,text)
                self._show_answer_details()
            self.Review_w(None)
        return edit_attribute(self.app,'Edit description' if column=='Description' else 'Edit example',
            self.w_old.word,value,save)

    def Edit_current_synonyms(self):
        from app.vocabulary.editor_synonyms import SynonymsDialog
        course=self.context.vocabulary_path(self.lang_desc)
        heading=self.w_new.word if getattr(self,'_audio_question',False) else self.w_new.tr
        return SynonymsDialog(self.app,course,self.w_new.id,self.lang_desc,self.learned_by,
            on_changed=self._reload_synonyms,heading=heading,allow_navigation=False,
            show_translation=not getattr(self,'_audio_question',False))

    def _mark_synonyms(self):
        if self.synonym_text(self.w_new.id):self.synonym_dot.place(x=10,rely=.5,anchor='w')
        else:self.synonym_dot.place_forget()

    def Edit_review_synonyms(self):
        from app.vocabulary.editor_synonyms import SynonymsDialog
        course=self.context.vocabulary_path(self.lang_desc)
        self._review_dialog.destroy()
        SynonymsDialog(self.app,course,self.w_old.id,self.lang_desc,self.learned_by,on_changed=self._reload_synonyms)

    def _reload_synonyms(self):
        course=self.context.vocabulary_path(self.lang_desc)
        self.synonym_words=read_words(course)
        self.synonym_relations,_=synonyms.load(course,self.synonym_words)
        self._mark_synonyms()
        self.sidebar.update_session(self.w_old,self.w_new,len(self.session.completed),self.session_size,
            self.synonym_text(self.w_old.id),tags=self.tag_text(self.w_old.id))
        if self.context.preferences.show_synonyms or self.current_synonyms._parent_frame.winfo_ismapped():self.Show_synonyms()

    def Review_w_end(self, event):
        s.Clear_tops(self.app)
        if self.w_old.id == self.w_new.id:
            self.Auto_audio('None', 'old')

    def Del_desc(self):
        self.session.set_attribute(int(self.w_old.id), 'Description', 'No found')
        self.w_old.desc = 'No found'
        self.Review_w_end('')

    def Del_sentence_example(self):
        self.session.set_attribute(int(self.w_old.id), 'Example', 'No found')
        self.w_old.sen = 'No found'
        self.Review_w_end('')

    def Del_audio(self):
        try:
            self.audio.delete(self.w_old.id)
            self.session.set_attribute(int(self.w_old.id), 'Audio', 'No audio')
        except (OSError, pygame.error) as error:
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=self.translate(str(error)))
        self.Play_btn_ability()
        self.Review_w_end('')

    def Save_rep(self,event,*,close=True):
        if self.lifecycle.closed:return False
        try:
            file_voc = self.context.vocabulary_path(self.lang_desc)
            remaining, completed = self.session.frames()
            save_practice(file_voc, remaining, completed, self.headers, original=self._initial_session_data,maximum_tags=self.context.preferences.maximum_tags)
        except Exception as error:
            report_error(error, operation='vocabulary screen')
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=self.translate(str(error)))
            return False
        else:
            self._has_answers=False
            self._initial_session_data=self.session.data.copy(deep=True)
            play_effect('saved')
            if close:self.lifecycle.finish(self._return_home)
            return True

    def Conf_resp(self, option, event):
        word_id = int(self.w_new.id)
        if word_id not in self.session.positions:
            return
        self._has_answers=True
        self.mistake = 0
        self.bindings.unbind('<Return>')
        self.bindings.bind('<Return>', partial(self.Conf_resp, ''))
        correct = answers_match(self.w_new.word, self.resp_var.get()) if option == '' else option == self.w_new.tr
        if correct:
            self.session.succeed(word_id)
            self.New_repeat(1)
            return
        self.mistake = 1
        self.w_old.copy(self.w_new)
        self.session.fail(word_id)
        self.Play_btn_ability()
        self.sidebar.update_session(self.w_old, self.w_new, len(self.session.completed), self.session_size,
                                    self.synonym_text(self.w_old.id),tags=self.tag_text(self.w_old.id))
        self.Auto_audio('wrong.wav', 'new')
        self.action_frm.grid_forget()
        self._answer_color(ui.ERROR)
        self.show_w_frm.grid(row=1, sticky='nsew', padx=(28, 12), pady=(8, 28))
        self.bindings.unbind('<Return>')
        self.bindings.bind('<Return>', self.Show_w_next)

    def Show_w_next(self, event):
        self.show_w_frm.grid_forget()
        self.action_frm.grid_configure(row=1, column=0, sticky='NWES',padx=(28,12),pady=(8,28))
        self.bindings.unbind('<Return>')
        self.bindings.bind('<Return>', partial(self.Conf_resp, ''))
        self.New_repeat(1)

    def Skip_resp(self):
        self.session.skip(int(self.w_new.id))
        self.New_repeat(0,update_previous=False)

    def Skip_shortcut(self, event=None):
        if self.action_frm.winfo_ismapped() and (not any((isinstance(widget, cst.CTkToplevel) for widget in self.app.winfo_children()))):
            self.Skip_resp()
        return 'break'

    def Choice_shortcut(self, option, event=None):
        if self.action_frm.winfo_ismapped() and self.opc_frm.winfo_ismapped() and not any(
                isinstance(widget, cst.CTkToplevel) for widget in self.app.winfo_children()):
            if not (event and has_answer_modifier(event)):
                self.Conf_resp(option, event)
        return 'break'

    def Auto_audio(self, default, version):
        if self.context.preferences.autoplay_pronunciation:
            self.Play_audio(default, version, '')
        elif default not in ('None', None, ''):
            play_effect(default)

    def Play_audio(self, default, version, event):
        try:
            word = self.w_old if version == 'old' else self.w_new
            self.audio.play(word.id, default)
        except (OSError, pygame.error) as error:
            messagebox.showerror(parent=self.app, title=self.translate('Error'), message=self.translate('Something got wrong.') + ' ' + str(error))

    def Resp_change(self, *args):
        if self.w_new.word.lower().strip() == self.resp_var.get().lower().strip():
            self.Conf_resp('', '')

    def New_repeat(self, play, update_previous=True):
        if not self.session:
            self.Save_rep('')
            return
        if update_previous:self.w_old.copy(self.w_new)
        row = self.session.pick()
        self.rep_frm._backdrop.switch_asset('practice_warm_v4.png')
        self.w_new.copy(Word(row['ID'], row[self.lang_desc], row.get('Phonetic', ''), row['Description'], row['Example'], row[self.learned_by], row['Part of Speech']))
        self.letters_lbl.configure(text=Shuffle_w(self.w_new.word))
        self.w_lbl.configure(text=self.w_new.word)
        chosen_type = random.choices((1, 2, 3), weights=self.test_weights, k=1)[0]
        options = self.choice_pool.options(self.w_new.tr) if chosen_type == 3 and self.audio.available(self.w_new.id) else None
        self._show_question(chosen_type, options, play)
        self.resp_var.set('')
        self._show_answer_details()
        if self.session.introduce(int(self.w_new.id)):
            self.w_old.copy(self.w_new)
            self.Auto_audio('success.FLAC', 'new')
            self.action_frm.grid_forget()
            self._answer_color(ui.SUCCESS)
            self.show_w_frm.grid(row=1, column=0, sticky='nsew', padx=(28, 12), pady=(8, 28))
            self.bindings.unbind('<Return>')
            self.bindings.bind('<Return>', self.Show_w_next)
        self.Play_btn_ability()
        self.sidebar.update_session(self.w_old, self.w_new, len(self.session.completed), self.session_size,
                                    self.synonym_text(self.w_old.id),tags=self.tag_text(self.w_old.id))

    def _show_question(self, chosen_type, options, play):
        tags=self.tag_text(self.w_new.id) if self.context.preferences.show_practice_tags else ''
        self.current_tags_label.configure(text=tags)
        if tags:
            self.current_tags_label.grid(row=2,column=0,columnspan=2,sticky='ew',padx=32,pady=(0,12))
        else:self.current_tags_label.grid_remove()
        self._audio_question=chosen_type==3 and options is not None
        self._mark_synonyms()
        self._answer_options = options
        self.current_synonyms.grid_forget()
        self.synonym_button.grid_remove()
        if self.context.preferences.show_synonyms:self.Show_synonyms()
        else:self.synonym_button.grid(row=5,column=0,columnspan=2,pady=(0,10),sticky='w')
        mode = 'Practice in context' if chosen_type == 2 and self.w_new.desc not in ('-', '', 'No found') and (self.w_new.sen not in ('-', '', 'No found')) else 'Listen and choose' if chosen_type == 3 and options is not None else 'Translate the word'
        self.lbl_frm._mode_label.configure(text=self.translate(mode))
        if chosen_type == 2 and self.w_new.desc not in ['-', '', 'No found'] and (self.w_new.sen not in ['-', '', 'No found']):
            if play == 1:
                self.Auto_audio('success.FLAC', 'old')
            self.desc_lbl.configure(text=self.w_new.desc)
            sentence = self.w_new.sen
            if self.w_new.word:
                sentence = sentence.replace(self.w_new.word[0].lower() + self.w_new.word[1:], '______').replace(self.w_new.word[0].upper() + self.w_new.word[1:], '______')
            self.sentence_lbl.configure(text=sentence)
            self.type_2_frm.grid(row=0, column=0, padx=24, pady=24, columnspan=2, rowspan=2, sticky='NWES')
            self.letters_frm.grid(row=3, column=0, sticky='WE', padx=0, pady=10, columnspan=2)
            self.resp_entry.grid(row=2, column=0, padx=12, pady=10, sticky='ew', columnspan=2)
            self.resp_entry.focus()
            for k in [self.transl_lbl, self.play_type_3_btn, self.opc_frm]:
                k.grid_forget()
            for k in range(1, 5):
                self.bindings.unbind(str(k))
            self.bindings.bind('<KeyRelease-Control_L>', self.Review_w_end)
        elif chosen_type == 3 and options is not None:
            for k in [self.transl_lbl, self.type_2_frm, self.letters_frm, self.resp_entry]:
                k.grid_forget()
            for idx, i in enumerate([self.op1_btn, self.op2_btn, self.op3_btn, self.op4_btn]):
                i.configure(text=str(idx + 1) + '- ' + options[idx], command=partial(self.Conf_resp, options[idx], ''),
                    anchor='w', border_spacing=10)
                self.bindings.bind(str(idx + 1), partial(self.Choice_shortcut, options[idx]))
            self.bindings.bind('<KeyRelease-Control_L>', self.Review_w_end)
            self.bindings.unbind('<Return>')
            self.bindings.bind('<Return>', partial(self.Play_audio, 'None', 'new'))
            self.opc_frm.grid(row=3, column=0, sticky='WE', padx=0, pady=10, columnspan=2)
            self.play_type_3_btn.grid(row=0, padx=5, pady=5, columnspan=2, rowspan=2)
            self.Auto_audio('None', 'new')
            self.app.focus_set()
        else:
            if self.mistake == 0 and play == 1:
                self.Auto_audio('success.FLAC', 'old')
            self.transl_lbl.configure(text=self.w_new.tr)
            self.transl_lbl.grid(row=0,padx=32,pady=24,columnspan=2,rowspan=2,sticky='ew')
            self.lbl_frm._fit_prompt()
            self.letters_frm.grid(row=3, sticky='WE', padx=0, pady=10, columnspan=2)
            self.resp_entry.grid(row=2, padx=12, pady=10, sticky='ew', columnspan=2)
            self.resp_entry.focus()
            for k in [self.opc_frm, self.type_2_frm, self.play_type_3_btn]:
                k.grid_forget()
            for k in range(1, 5):
                self.bindings.unbind(str(k))
            self.bindings.bind('<KeyRelease-Control_L>', self.Review_w_end)

        self.lbl_frm._fit_prompt()
        self._reset_letter_hint()

    def _reset_letter_hint(self):
        """Each new question requires its own reveal; audio choices need no letters."""
        self.letters_lbl.grid_remove()
        self.hint_button.grid_remove()
        mode = self.context.preferences.letter_hints
        if self._audio_question or mode == 'Disabled':
            self.letters_frm.grid_remove()
        elif mode == 'Automatic':
            self.letters_lbl.grid()
        else:
            self.hint_button.grid(row=0, column=0, sticky='ew', padx=16, pady=8)

    def Show_hint(self):
        if self.lifecycle.closed or self._audio_question or self.context.preferences.letter_hints != 'On request':
            return
        self.hint_button.grid_remove()
        self.letters_lbl.grid()

    def _show_answer_details(self):
        for label in (self.pho_lrn_lbl, self.desc_lrn_lbl, self.sentence_lrn_lbl, self.PoS_lrn_lbl):
            label.grid_forget()
        self.transl_lrn_lbl.configure(text=self.w_new.tr)
        self.desc_lrn_lbl.configure(text=self.w_new.desc)
        self.sentence_lrn_lbl.configure(text=self.w_new.sen)
        self.pho_lrn_lbl.configure(text=self.w_new.phon)
        self.PoS_lrn_lbl.configure(text=self.translate(self.w_new.PoS))
        pos = 2
        if self.w_new.phon not in ['', '-', '[]']:
            self.pho_lrn_lbl.grid(row=pos, padx=5, pady=2)
            pos += 1
        if self.w_new.desc not in ['', '-', 'No found']:
            self.desc_lrn_lbl.grid(row=pos, padx=5, pady=2)
            pos += 1
        if self.w_new.sen not in ['', '-', 'No found']:
            self.sentence_lrn_lbl.grid(row=pos, padx=32, pady=8)
            pos += 1
        if self.w_new.PoS not in ['', '-', 'No found']:
            self.PoS_lrn_lbl.grid(row=pos, padx=32, pady=8)
            pos += 1
        self.answer_tags_label.grid_remove()
        tags=self.tag_text(self.w_new.id)
        self.answer_tags_label.configure(text=tags)
        if tags:
            self.answer_tags_label.grid(row=pos,padx=32,pady=4,sticky='ew')
            pos+=1
        if not hasattr(self, 'synonym_label'):
            self.synonym_label = cst.CTkLabel(self.show_w_frm, text='', text_color=ui.TEXT,
                font=(ui.FONT,18), wraplength=800, justify='left')
        self.synonym_label.grid_forget()
        value = self.synonym_text(self.w_new.id)
        if value:
            lines = value.splitlines()
            preview = '\n'.join(line[:140] for line in lines[:3])
            if len(lines)>3:preview += '\n…'
            self.synonym_label.configure(text=preview)
            self.synonym_label.grid(row=pos, padx=32, pady=8, sticky='ew')
        s.Grid_ratio(self.show_w_frm, [1] + [0] * 5 + [1], [1])

    def Play_btn_ability(self):
        self.play_btn.configure(state='normal' if self.audio.available(self.w_old.id) else 'disabled')

    def _answer_color(self, color):
        self.rep_frm._backdrop.switch_asset('practice_answer_v3.png')
        self.show_w_frm.configure(fg_color=color)
        self.show_w_frm.configure(border_color='#c78d77' if color == ui.ERROR else '#318b87')
        self.show_w_frm._status_label.configure(text=self.translate('Review the answer' if color == ui.ERROR else 'A new word'))
        for widget in self.show_w_frm.winfo_children():
            widget.configure(bg_color=color)

def Rep(app_input, repeat_df_input, lang, lang_ord_desc, *, context=None, on_back=None):
    if repeat_df_input.empty:
        return None
    return PracticeController(app_input,repeat_df_input,lang,lang_ord_desc,context=context,on_back=on_back)

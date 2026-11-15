"""Real geometry and repeated-update costs of shared learning controls."""
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
from app.ui.module_style import tool_button,choice_button,QUESTION
from app.ui.components.synonym_summary import SynonymSummary
from app.shared.translations import translate


class SharedControlsTests(TestCase):
    def test_question_prompt_fits_narrow_cards_and_restores_short_text_size(self):
        from app.ui.fitted_text import fit_question_prompt
        self.root.geometry('1400x1100');self.root.update()
        card=cst.CTkFrame(self.root,width=320,height=260)
        card.pack(anchor='nw');card.grid_propagate(False)
        card.grid_columnconfigure(0,weight=1);card.grid_rowconfigure(0,weight=1)
        label=cst.CTkLabel(card,text='',width=0,height=0)
        label.grid(row=0,column=0,sticky='ew',padx=32,pady=(60,24))
        for width in (320,600,1000):
            card.configure(width=width);self.root.update()
            for text in ('dlouhý překlad / další význam / doplňující vysvětlení '*4,'word'*50,'one\ntwo\nthree\nfour\nfive'):
                with self.subTest(width=width,text=text[:20]):
                    label.configure(text=text);fit_question_prompt(label,card);self.root.update()
                    self.assertEqual(label.cget('text'),text)
                    self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                    self.assertLessEqual(label.winfo_rooty()+label.winfo_height(),card.winfo_rooty()+card.winfo_height())
                    self.assertGreaterEqual(label.cget('font')[1],22)
            label.configure(text='short');fit_question_prompt(label,card);self.root.update()
            self.assertEqual(label.cget('font')[1],42)
            self.assertEqual(card.cget('height'),260)

    def test_popup_action_groups_stay_equal_and_centered_when_resized(self):
        from app.ui.module_style import dialog_button,dialog_actions
        for width in (650,900):
            self.root.geometry(f'{width}x700')
            for count in (1,2,3,4,6):
                with self.subTest(width=width,count=count):
                    parent=cst.CTkFrame(self.root);parent.pack(fill='x')
                    buttons=[dialog_button(cst.CTkButton(parent,text=f'Action {i}')) for i in range(count)]
                    dialog_actions(parent,buttons);self.root.update()
                    self.assertLessEqual(max(b.winfo_width() for b in buttons)-min(b.winfo_width() for b in buttons),2)
                    for offset in range(0,count,3):
                        group=buttons[offset:offset+3]
                        left=group[0].winfo_rootx()
                        right=group[-1].winfo_rootx()+group[-1].winfo_width()
                        self.assertLessEqual(abs((left+right)/2-parent.winfo_rootx()-parent.winfo_width()/2),2)
                        for first,second in zip(group,group[1:]):
                            self.assertLess(first.winfo_rootx()+first.winfo_width(),second.winfo_rootx())
                    parent.destroy()

    def test_dialog_action_sizes_and_long_translations_fit(self):
        from app.ui.module_style import dialog_button,header_button
        from app.ui.learning_review import ReviewDialog
        from unittest.mock import Mock
        for locale in ('cs','en','de','es','fr','sk'):
            with self.subTest(locale=locale),patch('app.shared.settings.T',side_effect=lambda key:translate(key,locale)):
                dialog=ReviewDialog(self.root,'Previous word','word','translation',[],
                    [('Close',Mock()),('Save edit',Mock()),('Delete example sentence',Mock())])
                dialog.geometry('650x550');dialog.deiconify();self.root.update()
                buttons=[]
                for frame in dialog.winfo_children():
                    if isinstance(frame,cst.CTkFrame):
                        buttons.extend(w for w in frame.winfo_children() if isinstance(w,cst.CTkButton))
                self.assertEqual(len(buttons),3)
                self.assertLessEqual(max(b.winfo_width() for b in buttons)-min(b.winfo_width() for b in buttons),2)
                self.assertLessEqual(max(b.winfo_height() for b in buttons)-min(b.winfo_height() for b in buttons),2)
                for button in buttons:
                    self.assertGreaterEqual(button.cget('font')[1],12)
                    self.assertLessEqual(button.cget('font')[1],16)
                    self.assertGreaterEqual(button.cget('width'),140)
                    self.assertGreaterEqual(button.cget('height'),44)
                    self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                    self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height()-8)
                dialog.destroy()
                first=header_button(cst.CTkButton(self.root,text=translate('Close',locale),width=90))
                second=header_button(cst.CTkButton(self.root,text=translate('Close',locale),width=300))
                self.assertEqual(first.cget('width'),second.cget('width'))
                first.destroy();second.destroy()

    def test_about_and_preferences_header_actions_share_training_style_in_all_languages(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from app.about.dialog import AboutDialog
        from app.preferences.dialog import PreferencesDialog
        from app.ui.components.module_header import ModuleHeader
        from app.tests.test_preferences_data import sample_preferences
        from app.about.shortcuts import shortcut_sections
        for section,items in shortcut_sections():
            if section in ('Repeat','Vocabulary','Grammar','Conjugation','Grammar editors'):
                self.assertIn(('Esc','Close'),items)
        with TemporaryDirectory() as folder:
            path=Path(folder)/'settings.csv'
            sample_preferences().to_csv(path,sep=';',index=False)
            before=path.read_bytes()
            for locale in ('cs','en','de','es','fr','sk'):
                tr=lambda key:translate(key,locale)
                for kind in ('about','preferences'):
                    with self.subTest(locale=locale,dialog=kind):
                        dialog=(AboutDialog(self.root,tr,'VocabPro','Czech',('Spanish','English'))
                            if kind=='about' else PreferencesDialog(self.root,tr,path))
                        dialog.deiconify();self.root.update()
                        header=next(w for w in dialog.winfo_children() if isinstance(w,ModuleHeader))
                        buttons=[]
                        def collect(parent):
                            for child in parent.winfo_children():
                                if isinstance(child,cst.CTkButton):buttons.append(child)
                                elif isinstance(child,cst.CTkFrame):collect(child)
                        collect(header)
                        self.assertIn(tr('Close'),[button.cget('text') for button in buttons])
                        for button in buttons:
                            self.assertEqual(button.cget('fg_color'),'#fffcf5')
                            self.assertEqual(button.cget('text_color'),'#244743')
                            self.assertEqual(button.cget('font')[1],18)
                            self.assertEqual(button.cget('height'),44)
                            self.assertEqual(button.cget('corner_radius'),14)
                            self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                        dialog.destroy()
            self.assertEqual(path.read_bytes(),before)

    def setUp(self):
        self.root=cst.CTk();self.root.geometry('650x700');self.root.update()
        self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)

    def tearDown(self):
        for token in self.root.tk.call('after','info'):self.root.tk.call('after','cancel',token)
        self.root.destroy()
        self.assertFalse(self.errors)

    def test_long_translated_tool_captions_fit_narrow_and_wide_panels(self):
        holder=cst.CTkFrame(self.root,width=220,height=600)
        holder.pack();holder.pack_propagate(False)
        for locale in ('cs','en','de','es','fr','sk'):
            for width in (180,300):
                holder.configure(width=width)
                for caption in ('Previous category theory','Delete selected words','Add question','Sort descending'):
                    with self.subTest(locale=locale,width=width,caption=caption):
                        button=tool_button(cst.CTkButton(holder,text=translate(caption,locale)))
                        button.pack(fill='x',padx=8);self.root.update()
                        self.assertLessEqual(button._text_label.winfo_reqwidth(),button.winfo_width()-8)
                        self.assertLessEqual(button._text_label.winfo_reqheight(),button.winfo_height()-8)
                        self.assertGreaterEqual(button.cget('height'),36)
                        button.destroy()

    def test_answer_choices_keep_readable_contrast_and_restore_after_feedback(self):
        from app.grammar.layout import reset_option
        button=cst.CTkButton(self.root,text='1 · Answer')
        choice_button(button)
        expected={key:button.cget(key) for key in ('fg_color','text_color','hover_color','font')}
        button.configure(fg_color='#f3ddd5',state='disabled')
        reset_option(button,'2 · Another answer')
        self.assertEqual(button.cget('state'),'normal')
        self.assertEqual(expected,{key:button.cget(key) for key in expected})
        def luminance(color):
            rgb=[int(color[index:index+2],16)/255 for index in (1,3,5)]
            linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
            return sum(value*weight for value,weight in zip(linear,(.2126,.7152,.0722)))
        for style in (choice_button,tool_button):
            style(button)
            light,dark=sorted((luminance(button.cget('fg_color')),luminance(button.cget('text_color'))),reverse=True)
            self.assertGreaterEqual((light+.05)/(dark+.05),4.5)

    def test_synonym_words_are_bold_and_translations_smaller_with_rows_reused(self):
        summary=SynonymSummary(self.root);summary.pack(fill='x')
        summary.set_text('palabra — slovo\notra — další')
        self.root.update()
        word,translation=summary.rows[0]
        self.assertEqual(word.cget('text'),'palabra')
        self.assertEqual(translation.cget('text'),'slovo')
        self.assertEqual(word.cget('font')[2],'bold')
        self.assertLess(translation.cget('font')[1],word.cget('font')[1])
        before=tuple(summary.winfo_children())
        begin=perf_counter()
        for _ in range(10000):summary.set_text('palabra — slovo\notra — další')
        elapsed=perf_counter()-begin
        self.assertEqual(tuple(summary.winfo_children()),before)
        self.assertLess(elapsed,1)
        print(f'PERF 10000 unchanged synonym summaries: {elapsed*1000:.2f} ms')
        summary.set_text('one — '+('long translation '*30));self.root.update()
        self.assertFalse(summary.rows[1][0].winfo_ismapped())
        self.assertLessEqual(translation._label.winfo_reqwidth(),summary.winfo_width())
        summary.set_text('');self.root.update()
        self.assertTrue(all(not label.winfo_ismapped() for pair in summary.rows for label in pair))

    def test_conjugation_uses_grammar_question_surface(self):
        from app.conjugation.layout import build
        view=build(self.root,[('s1','Yo')],lambda:None,lambda:None,lambda:None,lambda:None,lambda:None)
        self.assertEqual(view.card.cget('fg_color'),QUESTION)
        self.assertEqual(view.card.cget('corner_radius'),24)
        self.assertEqual(view.card.cget('border_width'),1)

    def test_surface_lifecycle_callback_accepts_a_call_without_event_payload(self):
        import re
        from app.ui.surfaces import surface
        from app.tests.ui_helpers import solid_surface
        panel=cst.CTkFrame(self.root)
        panel.pack(fill='both',expand=True)
        layer=surface(panel,solid_surface(self.root,'#d7dfca'))
        self.root.update()
        callbacks=re.findall(r'\[([^\s\]]*<lambda>)',panel._canvas.bind('<Configure>'))
        self.assertTrue(callbacks)
        self.root.tk.call(callbacks[-1])
        self.root.update()
        self.assertFalse(layer._dead)
        panel.destroy()
        self.root.update()
        self.assertTrue(layer._dead)

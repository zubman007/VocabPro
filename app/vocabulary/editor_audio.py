"""Styled recording dialog; microphone work never touches Tk widgets."""
from app.shared.messages import error_text
from app.ui.theme import FONT, PAGE, SURFACE, TEXT
from pathlib import Path
import queue
import threading
import time
from app.ui import messagebox
import customtkinter as cst
import pygame
from app.shared import settings as s
from app.vocabulary.editor_recording import record_wave
from app.ui.surfaces import surface


class AudioRecorderPlayer:
    def __init__(self,top,lbl_1,lbl_2,lbl_3,id,idx,tbl,df,audio_folder,language):
        self.app,self.edit_tbl,self.df=top,tbl,df
        self.audio_folder,self.language=Path(audio_folder),language
        self.id,self.idx=id,idx
        self.recording=False
        self.a_thread=None
        self.stop_event=threading.Event()
        self.results=queue.Queue()
        self.closing=False
        self._poll_id=None
        self._show_id=None
        top.withdraw()
        top.title(s.T("Audio Recorder"))
        top.geometry('740x600')
        top.minsize(680,550)
        top.configure(fg_color=PAGE)
        backdrop=top.make_background('editor_warm_v1.png')
        top.grid_columnconfigure(0,weight=1)
        top.protocol('WM_DELETE_WINDOW',self.Cancel_rec)
        top.bind('<Escape>',lambda event:self.Cancel_rec())
        heading=cst.CTkFrame(top,fg_color='#355e59',corner_radius=24)
        heading.grid(row=0,column=0,sticky="ew",padx=24,pady=(24,16))
        cst.CTkLabel(heading,text=s.T('Record audio'),font=(FONT,30,'bold'),
                     text_color=SURFACE).pack(anchor='w',padx=22,pady=16)
        surface(heading,backdrop)
        card=cst.CTkScrollableFrame(top,fg_color='#ded4bf',corner_radius=24)
        card.grid(row=1,column=0,sticky="nsew",padx=24,pady=4)
        top.grid_rowconfigure(1,weight=1)
        surface(card._parent_frame,backdrop)
        cst.CTkLabel(card,text=s.T(language),font=(FONT,16),text_color="#8a7253").pack(anchor="w",padx=22,pady=(18,4))
        self.lbl_1_lbl=cst.CTkLabel(card,text=lbl_1,font=(FONT,32,"bold"),text_color=TEXT,wraplength=620)
        self.lbl_1_lbl.pack(anchor="w",padx=22,pady=(0,8))
        self.lbl_2_lbl=cst.CTkLabel(card,text=lbl_2,font=(FONT,21),text_color="#496e68",wraplength=620)
        self.lbl_2_lbl.pack(anchor="w",padx=22,pady=4)
        self.lbl_3_lbl=cst.CTkLabel(card,text=lbl_3,font=(FONT,18),text_color="#7d7467",wraplength=620)
        self.lbl_3_lbl.pack(anchor="w",padx=22,pady=(0,18))
        self.status=cst.CTkLabel(top,text=s.T("Ready to record"),font=(FONT,19),text_color="#5b7c70")
        self.status.grid(row=2,column=0,sticky="w",padx=30,pady=20)
        self.status.configure(fg_color='#ded4bf',corner_radius=12,padx=12,pady=8)
        surface(self.status,backdrop)
        actions=cst.CTkFrame(top,fg_color="transparent")
        actions.grid(row=3,column=0,sticky="ew",padx=24,pady=4)
        actions.grid_columnconfigure((0,1,2),weight=1)
        self.start_btn=cst.CTkButton(actions,text=s.T("Start Recording"),command=self.Start_rec,fg_color="#a96349",hover_color="#8c513b",height=46,font=(FONT,18))
        self.stop_btn=cst.CTkButton(actions,text=s.T("Stop Recording"),command=self.Stop_rec,fg_color="#af5d5d",hover_color="#924949",height=46,font=(FONT,18),state="disabled")
        self.play_btn=cst.CTkButton(actions,text=s.T("Play Recording"),command=self.Play_rec,fg_color="#3e827b",hover_color="#315f5b",height=46,font=(FONT,18))
        for column,widget in enumerate((self.start_btn,self.stop_btn,self.play_btn)):
            widget.grid(row=0,column=column,sticky="ew",padx=5)
        top.grid_rowconfigure(4,weight=0)
        footer=cst.CTkFrame(top,fg_color="transparent")
        footer.grid(row=5,column=0,sticky="ew",padx=28,pady=(8,16))
        self.cancel,self.next_btn=top.add_actions(footer,
            [('Close',self.Cancel_rec),('Next word',self.Next)],s.T)
        for frame in (actions,footer):
            layer=surface(frame,backdrop)
            for button in frame.winfo_children():
                button.configure(corner_radius=14)
                surface(button,layer)
        card.bind('<Configure>',lambda event: [label.configure(wraplength=max(180,event.width/card._get_widget_scaling()-55),justify='left')
            for label in (self.lbl_1_lbl,self.lbl_2_lbl,self.lbl_3_lbl)],add='+')
        self._set_paths()
        self._show_id=top.after(250,self._present)
        if top.lifecycle_owner is not None:top.lifecycle_owner.own_dialog(top,self._dispose)

    def _dispose(self):
        """Stop recording/polling when its owning editor disappears."""
        self.closing=True
        self.stop_event.set()
        for timer in (self._show_id,self._poll_id):
            if timer is not None:self.app.after_cancel(timer)
        self._show_id=self._poll_id=None
        self.app.destroy()

    def _present(self):
        self._show_id=None
        self.app.present(modal=True)

    def _set_paths(self):
        self.path_wav=self.audio_folder/f'{self.id}.wav'
        self.path_mp3=self.audio_folder/f'{self.id}.mp3'
        self.play_btn.configure(state="normal" if self.path_wav.exists() or self.path_mp3.exists() else "disabled")

    def Start_rec(self):
        if self.a_thread is not None and self.a_thread.is_alive():
            return
        self.stop_event.clear()
        self.recording=True
        self.started=time.monotonic()
        self.start_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
        self.play_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        pygame.mixer.quit()
        self.a_thread=threading.Thread(target=self.Record_audio,daemon=True)
        self.a_thread.start()
        self._poll()

    def Record_audio(self):
        try:
            record_wave(self.path_wav,self.stop_event)
            self.results.put((True,None))
        except Exception as error:
            self.results.put((False,str(error)))

    def Stop_rec(self):
        self.recording=False
        self.stop_event.set()
        self.stop_btn.configure(state="disabled")
        self.status.configure(text=s.T("Saving recording"),text_color="#8a7253")

    def _poll(self):
        self._poll_id=None
        try:
            success,error=self.results.get_nowait()
        except queue.Empty:
            if self.recording:
                seconds=int(time.monotonic()-self.started)
                self.status.configure(text=f"● {s.T('Recording')}  {seconds//60:02d}:{seconds%60:02d}",text_color="#a14343")
            self._poll_id=self.app.after(60,self._poll)
            return
        self.recording=False
        if success:
            try:
                self.path_mp3.unlink(missing_ok=True)
            except OSError:
                pass
            self.edit_tbl.set_cell_data(r=int(self.idx),c=list(self.df.columns).index('Audio'),value='Own',redraw=True)
            self.status.configure(text=s.T("Recording saved"),text_color="#3e827b")
        else:
            self.status.configure(text=s.T("Recording failed"),text_color="#a14343")
            if not self.closing:
                messagebox.showerror(parent=self.app,title=s.T("Audio Recorder"),message=error_text(error, s.T))
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        if self.closing:
            self._close()
            return
        self.start_btn.configure(state="normal")
        self.next_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._set_paths()

    def Cancel_rec(self):
        if self.a_thread is not None and (self.a_thread.is_alive() or self._poll_id is not None):
            self.closing=True
            self.Stop_rec()
        else:
            self._close()

    def _close(self):
        for timer in (self._show_id,self._poll_id):
            if timer is not None:
                self.app.after_cancel(timer)
        self.app.destroy()
        self.edit_tbl.see(int(self.idx),0)

    def Next(self):
        if self.recording or (self.a_thread is not None and self.a_thread.is_alive()):
            return
        next_index=self.idx+1
        if next_index>=self.edit_tbl.get_total_rows():
            self.Cancel_rec()
            return
        self.idx=next_index
        self.id=self.edit_tbl.get_cell_data(self.idx,0)
        if self.id in ('',None):
            self.Cancel_rec()
            return
        self.lbl_1_lbl.configure(text=self.edit_tbl.get_cell_data(self.idx,1))
        self.lbl_2_lbl.configure(text=self.edit_tbl.get_cell_data(self.idx,2))
        self.lbl_3_lbl.configure(text='' if self.language=='Spanish' else self.edit_tbl.get_cell_data(self.idx,3))
        self.status.configure(text=s.T("Ready to record"),text_color="#5b7c70")
        self._set_paths()

    def Play_rec(self):
        path=self.path_wav if self.path_wav.exists() else self.path_mp3
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
        except (pygame.error,OSError) as error:
            messagebox.showerror(parent=self.app,title=s.T("Audio Recorder"),message=error_text(error, s.T))

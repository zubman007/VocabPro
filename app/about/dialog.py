"""Branded About, guide and keyboard reference, separate from the main menu."""
from app.ui.theme import FONT, PAGE, SECTION_SURFACE as SURFACE
import customtkinter as cst
import pywinstyles
from app.ui.theme import TEXT, SECTION_CONTROL as TEAL, RADIUS
from app.ui.sections import SectionTabs
from app.ui.components.module_header import ModuleHeader
from app.ui.components.app_dialog import AppDialog
from app.ui.surfaces import surface

AboutTabs = SectionTabs


class AboutDialog(AppDialog):
    def __init__(self, parent, translate, app_name, learned_by, languages):
        super().__init__(parent)
        self.withdraw()
        self.owner=parent
        self._show_after=None
        self.title(app_name+" · "+translate("About the application"))
        self.geometry("1030x720")
        self.minsize(900,620)
        self.configure(fg_color=PAGE)
        backdrop=self.make_background('sections_warm_v1.png')
        pywinstyles.apply_style(self,"dark")
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.header=hero=ModuleHeader(self,translate('About the application'),
            app_name+'  ·  '+translate('Your vocabulary. Your pace.'),translate=translate,
            actions=[('close',self.destroy)])
        hero.grid_standard()
        hero.attach_background(backdrop)
        panel=cst.CTkFrame(self, fg_color='transparent', corner_radius=24)
        panel.grid(row=1,column=0,sticky="nsew",padx=22,pady=(12,4))
        panel.grid_rowconfigure(0,weight=1)
        panel.grid_columnconfigure(0,weight=1)
        panel_surface=surface(panel, backdrop)
        tabs=SectionTabs(panel)
        tabs.enable_transparent_panels()
        self.tabs=tabs
        tabs.grid(row=0,column=0,sticky="nsew")
        tabs_surface=surface(tabs, panel_surface)
        selector_surface=surface(tabs._segmented_button, tabs_surface)
        overview=tabs.add(translate("Overview"))
        overview.configure(fg_color='transparent',corner_radius=0)
        overview_surface=surface(overview, tabs_surface)
        guide=tabs.add(translate("Guide"))
        shortcuts=tabs.add(translate("Keyboard shortcuts"))
        guide_surface=surface(guide, tabs_surface)
        shortcuts_surface=surface(shortcuts, tabs_surface)
        # The segmented buttons are created by add(), not by SectionTabs().
        for button in tabs._segmented_button.winfo_children():
            if isinstance(button,cst.CTkButton):
                surface(button, selector_surface)
        overview.grid_columnconfigure((0,1,2),weight=1,uniform="features")
        cards=[("Vocabulary","Guide courses"), ("Repeat","Guide practice"),
               ("Statistics","Guide progress")]
        for column,(title,detail) in enumerate(cards):
            card=cst.CTkFrame(overview,fg_color=SURFACE,corner_radius=RADIUS)
            surface(card, overview_surface)
            card.grid(row=0,column=column,sticky="nsew",padx=8,pady=(22,18))
            cst.CTkLabel(card,text=translate(title),font=(FONT,24,"bold"),text_color=TEAL).pack(anchor="w",padx=18,pady=(20,12))
            description=cst.CTkLabel(card,text=translate(detail),font=(FONT,18),text_color=TEXT,
                         wraplength=260,justify="left",anchor="nw")
            description.pack(fill="both",expand=True,padx=18,pady=(0,22))
            card.bind('<Configure>',lambda event,label=description,panel=card:
                      label.configure(wraplength=max(120,event.width/panel._get_widget_scaling()-40)),add='+')
        info=cst.CTkFrame(overview,fg_color=SURFACE,corner_radius=RADIUS)
        surface(info, overview_surface)
        info.grid(row=1,column=0,columnspan=3,sticky="ew",padx=18,pady=8)
        cst.CTkLabel(info,text=translate("Learned by")+": "+translate(learned_by),text_color=TEXT,font=(FONT,18)).pack(anchor="w",pady=4)
        cst.CTkLabel(info,text=" · ".join(translate(language) for language in languages),text_color="#80684f",font=(FONT,23,"bold")).pack(anchor="w",pady=4)
        for label in info.winfo_children():
            label.pack_configure(padx=16, pady=8)
        body=cst.CTkScrollableFrame(guide,fg_color=SURFACE,corner_radius=RADIUS)
        body.pack(fill="both",expand=True,padx=16,pady=12)
        surface(body._parent_frame, guide_surface)
        guide_labels=[]
        for title,text in (("Vocabulary","Guide editor details"),("Repeat","Guide repeat details"),
                           ("Grammar","Guide grammar details"),("Conjugation","Guide conjugation details"),
                           ("Statistics","Guide statistics details"),("Backups","Guide storage details"),
                           ("API services","Guide services details")):
            cst.CTkLabel(body,text=translate(title),font=(FONT,22,"bold"),text_color=TEAL).pack(anchor="w",padx=12,pady=(14,5))
            label=cst.CTkLabel(body,text=translate(text),font=(FONT,18),text_color=TEXT,wraplength=850,justify="left")
            label.pack(anchor="w",padx=12,pady=(0,10))
            guide_labels.append(label)
        body.bind('<Configure>',lambda event: [label.configure(wraplength=max(200,event.width/body._get_widget_scaling()-40))
                                               for label in guide_labels],add='+')
        shortcut_card=cst.CTkScrollableFrame(shortcuts,fg_color=SURFACE,corner_radius=RADIUS)
        shortcut_card.pack(fill="both",expand=True,padx=16,pady=12)
        surface(shortcut_card._parent_frame, shortcuts_surface)
        shortcuts=cst.CTkFrame(shortcut_card,fg_color=SURFACE,corner_radius=0)
        shortcuts.pack(fill="both",expand=True,padx=16,pady=12)
        shortcuts.grid_columnconfigure(1,weight=1)
        row=0
        from app.core.context import get_context
        from app.about.shortcuts import shortcut_sections
        preferences=get_context(parent).preferences
        for title,items in shortcut_sections(preferences.show_synonyms,preferences.tags_enabled):
            cst.CTkLabel(shortcuts,text=translate(title),font=(FONT,21,"bold"),text_color=TEAL).grid(row=row,column=0,columnspan=2,sticky="w",padx=8,pady=(10,6))
            row+=1
            for key,label in items:
                cst.CTkLabel(shortcuts,text=translate(key),fg_color="#cdb78f",corner_radius=8,width=105,height=30,
                    text_color=TEXT,font=(FONT,16,"bold")).grid(row=row,column=0,padx=(8,16),pady=3)
                cst.CTkLabel(shortcuts,text=translate(label),text_color=TEXT,font=(FONT,18),
                             wraplength=600,justify='left').grid(row=row,column=1,sticky="w",padx=(0,12),pady=3)
                row+=1
        self.withdraw()
        self._show_after=self.after(250,self.present)

    def present(self):
        self._show_after=None
        super().present()

    def destroy(self):
        if getattr(self,"_show_after",None) is not None:
            self.after_cancel(self._show_after)
            self._show_after=None
        super().destroy()


def open_about(parent,translate,app_name,learned_by,languages):
    for window in parent.winfo_children():
        if isinstance(window,AboutDialog):
            window.lift()
            return window
    return AboutDialog(parent,translate,app_name,learned_by,languages)

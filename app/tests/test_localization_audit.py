"""UI text coverage, complete shortcut reference and lossless localized enums."""
import ast
from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
import customtkinter as cst
import pandas as pd
from app.paths import ROOT_DIR
from app.about.shortcuts import shortcut_sections
from app.shared.translations import translate,get_catalog,LANGUAGES
from app.vocabulary.editor_localization import ENUMS,display_frame,canonical_rows
from app.preferences.dialog import PreferencesDialog
from app.repositories.preferences import load_preferences
from app.tests.test_preferences_data import sample_preferences


class LocalizationAuditTests(unittest.TestCase):
    def test_custom_keyboard_bindings_are_all_listed_in_about(self):
        import re
        documented={key for _,items in shortcut_sections(False) for key,_ in items}
        aliases={'<Return>':'Enter','<space>':'Space','<Escape>':'Esc','<Alt-Right>':'Alt+→'}
        missing=[]
        for path in (ROOT_DIR/'app').rglob('*.py'):
            if 'tests' in path.parts:continue
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
                if not isinstance(node,ast.Constant) or not isinstance(node.value,str):continue
                match=re.fullmatch(r'<Control-(Shift-)?([a-zA-Z]|Return)>',node.value)
                if match:
                    suffix='Enter' if match.group(2)=='Return' else match.group(2).upper()
                    key='Ctrl+'+('Shift+' if match.group(1) else '')+suffix
                else:key=aliases.get(node.value)
                if key and key not in documented:missing.append((path.name,node.lineno,key))
        self.assertEqual(missing,[])

    def test_shortcut_descriptions_and_enum_values_exist_in_every_language(self):
        messages=set()
        for section,items in shortcut_sections(False):
            messages.add(section);messages.update(label for _,label in items)
        messages.add('Space')
        for values in ENUMS.values():messages.update(values)
        for language in LANGUAGES:
            self.assertFalse(messages-set(get_catalog(language)),language)
        self.assertNotIn(('Ctrl+H','Show synonyms'),dict(shortcut_sections(True))['Repeat'])
        self.assertIn(('Ctrl+H','Show synonyms'),dict(shortcut_sections(False))['Repeat'])
        groups=dict(shortcut_sections(False))
        self.assertIn(('Ctrl+S','Save'),groups['Setting'])
        self.assertIn(('Ctrl+S','Save'),groups['Grammar editors'])
        self.assertIn(('Enter','Apply filter'),groups['Vocabulary'])
        self.assertIn(('Ctrl+H','Show synonyms'),groups['Vocabulary'])
        self.assertIn(('Ctrl+V','Paste'),groups['Tables and text fields'])
        self.assertIn(('Ctrl+Shift+Z','Redo'),groups['Tables and text fields'])
        self.assertIn(('Ctrl+T','Word tags'),groups['Vocabulary'])
        self.assertIn(('Ctrl+Shift+T','Manage tags'),groups['Vocabulary'])
        self.assertIn(('Ctrl+F','Search tags'),groups['Word tags'])
        self.assertIn(('Ctrl+Enter','Apply'),groups['Word tags'])
        disabled=dict(shortcut_sections(False,False))
        self.assertNotIn('Word tags',disabled)
        self.assertNotIn('Manage tags',disabled)
        self.assertNotIn(('Ctrl+T','Word tags'),disabled['Vocabulary'])
        self.assertNotIn(('Ctrl+Shift+T','Manage tags'),disabled['Vocabulary'])

    def test_display_values_roundtrip_to_original_storage_values_in_all_languages(self):
        rows=max(map(len,ENUMS.values()))
        frame=pd.DataFrame({column:[values[i%len(values)] for i in range(rows)] for column,values in ENUMS.items()})
        frame.insert(0,'ID',range(1,rows+1));original=frame.copy(deep=True)
        for language in LANGUAGES:
            tr=lambda value:translate(value,language)
            shown=display_frame(frame,tr)
            restored=pd.DataFrame(canonical_rows(shown.values.tolist(),list(frame.columns),tr),columns=frame.columns)
            pd.testing.assert_frame_equal(restored,original)
            pd.testing.assert_frame_equal(frame,original)

    def test_no_raw_english_widget_text_and_shared_ui_titles_are_in_catalog(self):
        catalog=get_catalog('English');missing=[]
        for path in (ROOT_DIR/'app').rglob('*.py'):
            if 'tests' in path.parts:continue
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
                if not isinstance(node,ast.Call):continue
                for option in node.keywords:
                    value=option.value
                    call_name = getattr(node.func,'attr',getattr(node.func,'id',''))
                    is_sink = option.arg in ('text','placeholder_text') or call_name in ('showerror','showwarning','showinfo','askyesno','askyesnocancel')
                    if is_sink and option.arg in ('text','title','message','placeholder_text') and isinstance(value,ast.Constant) and isinstance(value.value,str):
                        if any(char.isalpha() for char in value.value):missing.append((path.name,node.lineno,value.value))
                name=getattr(node.func,'id','')
                if name in ('action','shell','ReviewDialog') and len(node.args)>1 and isinstance(node.args[1],ast.Constant):
                    title=node.args[1].value
                    if isinstance(title,str) and title and title not in catalog:missing.append((path.name,node.lineno,title))
        self.assertEqual(missing,[])

    def test_localized_language_options_save_canonical_settings(self):
        try:root=cst.CTk()
        except tk.TclError as error:self.skipTest(str(error))
        root.withdraw()
        try:
            with TemporaryDirectory() as folder:
                path=Path(folder)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
                dialog=PreferencesDialog(root,lambda key:translate(key,'Czech'),path)
                self.assertEqual(dialog.variables['App language'].get(),translate('English','Czech'))
                dialog.save()
                self.assertTrue(dialog.saved)
                saved=load_preferences(path).set_index('Name')
                self.assertEqual(saved.loc['App language','Value'],'English')
                self.assertEqual(saved.loc['First learning language','Value'],'Spanish')
        finally:
            for token in root.tk.call('after','info'):root.tk.call('after','cancel',token)
            root.destroy()

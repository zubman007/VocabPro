"""Explicit offline self-check, restricted to marked disposable fixtures."""
import json
import importlib
import os
from pathlib import Path
from time import perf_counter, sleep
import traceback


def require(condition, message):
    if not condition:raise RuntimeError(message)


def check(destination):
    from app.paths import FILES_DIR, ROOT_DIR, COMPILED
    from app.version import __version__
    output=Path(destination).resolve()
    if (not (FILES_DIR/'RELEASE_TEST_ONLY').is_file()
            or not output.is_relative_to(FILES_DIR.parent)):
        return 2
    report={'version':__version__,'compiled':COMPILED,'passed':False,'steps':[]}
    root=None;started=perf_counter();errors=[]
    try:
        import platform
        platform.uname()
        import socket
        def no_network(*args,**kwargs):
            raise RuntimeError('Network access is disabled during release verification.')
        socket.socket.connect=no_network
        socket.socket.connect_ex=no_network
        for module in ('pyaudio','pygame','requests','matplotlib','tksheet'):
            importlib.import_module(module)
        import customtkinter as cst
        from PIL import Image
        from app.core.context import AppContext
        from app import main
        from app.services import mail_credentials
        from app.shared.integrity import audit
        from app.shared.translations import get_catalog, LANGUAGES
        from app.ui import messagebox
        def dialog_error(*args,**kwargs):
            raise RuntimeError(str(kwargs.get('message','Unexpected dialog in release probe')))
        messagebox.showerror=dialog_error
        messagebox.showwarning=dialog_error
        messagebox.showinfo=lambda *args,**kwargs:None
        # A release probe never opens the user's vault or sends a backup.
        mail_credentials.load_credentials=lambda:None
        main._try_bkp=lambda *args:None
        report['steps'].append('runtime imports')
        require(Image.open(ROOT_DIR/'images/vocabpro_logo_v2.png').size[0]>0,'Brand image is unavailable.')
        for language in LANGUAGES:require(get_catalog(language),'Translation catalog is empty: '+language)
        report['steps'].append('images and translations')
        root=cst.CTk();root.geometry('1400x900')
        root.report_callback_exception=lambda *args:errors.append(''.join(traceback.format_exception(*args)))
        context=AppContext(on_home=lambda:None);context.bind(root)
        main.main_proc(root,context);root.update()
        require(root.winfo_ismapped() and root.winfo_children(),'Home window did not render.')
        report['ready_ms']=(perf_counter()-started)*1000
        if os.environ.get('VOCABPRO_PROBE_STARTED'):
            report['process_to_ready_ms']=(perf_counter()-float(os.environ['VOCABPRO_PROBE_STARTED']))*1000
        report['steps'].append('home ready')
        result=audit(FILES_DIR)
        require(result.completed and not [f for f in result.findings if f.severity=='Critical'],'Synthetic fixture integrity failed.')
        report['steps'].append('fixture integrity')
        from app.vocabulary.editor import EditorController
        editor=EditorController(root,'English',context=context);root.update()
        require(len(editor.main_df)>0,'Vocabulary editor did not load its fixture.')
        report['steps'].append('vocabulary editor')
        from app.grammar.editor import GrammarEditor
        editor=GrammarEditor(root,'English',context.grammar_path('English'),lambda:None,context=context)
        root.update();require(editor.view.tree.get_children(),'Grammar editor did not load its fixture.')
        report['steps'].append('grammar editor')
        from app.conjugation.editor import Edit_conjugation
        editor=Edit_conjugation(root,'Spanish',context=context);root.update()
        require(editor is not None,'Conjugation editor did not open.')
        column=editor.tables.fields.index('s1')+1
        editor.view.sheet.set_cell_data(0,column,'release-check')
        require(editor.save(close=False),'Conjugation editor failed to save.')
        import pandas as pd
        require(pd.read_csv(context.conjugation_path('Spanish'),sep=';').s1.iloc[0]=='release-check','Saved form did not survive reload.')
        report['steps'].append('conjugation spreadsheet save/reload')
        from app.statistics.data import training_statistics
        require(training_statistics(context.grammar_path('English'),'grammar')['summary'][0]>0,'Grammar statistics are incorrect.')
        from app.statistics.viewer import Stats
        window=Stats(root,context=context,language='English')
        deadline=perf_counter()+30
        while window.winfo_exists() and not window.ready and perf_counter()<deadline:
            root.update();sleep(.02)
        require(window.winfo_exists() and window.ready,'Statistics did not finish rendering.')
        window.destroy();report['steps'].append('statistics window and calculations')
        require(not errors,'Tk callback errors: '+str(errors))
        report['passed']=True
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        report['callback_errors']=errors
        if root is not None:
            for child in tuple(root.winfo_children()):child.destroy()
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()
        report['elapsed_ms']=(perf_counter()-started)*1000
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['passed'] else 1

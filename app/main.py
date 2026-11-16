"""Application composition: contexts, navigation and home-screen entry points."""
from app.shared.messages import error_text
import os
import sys
from dataclasses import replace
from pathlib import Path
from functools import partial
from tkinter import messagebox
from app.core.context import get_context
from app.home.layout import build_home, build_navigation
from app.home.data import course_overview
from app.repositories.courses import ensure_course
from app.services.backup import backup_due, send_backup
from app.preferences.data import RuntimePreferences
from app.repositories.preferences import load_preferences
from app.shared import settings as s
from app.shared.translations import translate
from app.shared.languages import legacy_name


def main_proc(app,context=None):
    context=get_context(app,context)
    context.bind(app)
    context.on_home=lambda:main_proc(app,context)
    Load_setting(context)
    _try_bkp(app,context)
    config=context.preferences
    languages=config.learning_languages
    stats={language:_load_vocab_stats(language,context) for language in languages}
    s.Clear_frames(app)
    _build_menu(app,context)
    _build_main_window(app,stats,context)


def Exit(app):
    app.destroy()
    sys.exit()


def Load_setting(context=None):
    context=get_context(context=context)
    frame=load_preferences(context.files_dir/'settings.csv')
    config=RuntimePreferences.from_frame(frame)
    for language in config.learning_languages:
        ensure_course(context.files_dir,config.learned_by,language)
    # Publish one immutable snapshot only after preparation succeeds.
    context.preferences=config
    context.preferences_frame=frame
    from app.shared.audio_effects import configure
    configure(config.sounds_enabled,config.sound_volume)
    return config


def Back_up(app,context=None):
    context=get_context(app,context)
    config=context.preferences
    if not backup_due(config.backup_mail,config.backup_period,config.next_backup):return
    from app.services.backup_background import BackupCoordinator
    from app.repositories.preferences import record_success
    files,recipient,period,expected_next,language=(context.files_dir,config.backup_mail,
        config.backup_period,config.next_backup,config.app_language)
    if not hasattr(app,'_backup_coordinator'):
        def sent(key):
            folder,mail,days,previous=key
            try:next_date=record_success(Path(folder)/'settings.csv',mail,days,previous)
            except Exception:
                messagebox.showerror(parent=app,title=context.translate('Backups'),
                    message=context.translate('Backup sent but its next date could not be saved.'))
            else:
                current=context.preferences
                if next_date is not None and (str(context.files_dir),current.backup_mail,
                        current.backup_period,current.next_backup)==key:
                    context.preferences=replace(current,next_backup=next_date)
        def failed(error):
            messagebox.showerror(parent=app,title=context.translate('Backups'),
                message=context.translate("The backup mail should have been sent but it wasn't.")+'\n'+error_text(error, context.translate))
        app._backup_coordinator=BackupCoordinator(app,sent,failed)
    sender=partial(send_backup,files,recipient,
        os.environ.get('VOC_SMTP_USER',''),os.environ.get('VOC_SMTP_PASSWORD',''),
        lambda text:translate(text,language),s.app_name)
    app._backup_coordinator.request((str(files),recipient,period,expected_next),sender)


def About_app(app,context=None):
    from app.about.dialog import open_about
    context=get_context(app,context)
    config=context.preferences
    return open_about(app,context.translate,s.app_name,config.learned_by,
        config.learning_languages)


def _build_menu(app,context):
    def preferences():
        from app.preferences.dialog import open_preferences
        return open_preferences(app,context=context)
    def statistics():
        from app.statistics.viewer import Stats
        return Stats(app,context=context)
    return build_navigation(app,dict(about=partial(About_app,app,context),refresh=context.go_home,
        settings=preferences,stats=statistics,exit=partial(Exit,app)))


def _try_bkp(app,context):
    try:Back_up(app,context)
    except Exception as error:
        messagebox.showerror(parent=app,title=context.translate('Error'),
            message=context.translate("The backup mail should have been sent but it wasn't.")+'\n'+error_text(error, context.translate))


def _load_vocab_stats(language,context):
    config=context.preferences
    return course_overview(context.files_dir,config.learned_by,language,config.learn_batch,config.repeat_batch)


def _build_main_window(app,stats,context):
    config=context.preferences
    languages=config.learning_languages
    selected = next((legacy_name(pair.target) for pair in config.language_pairs
                     if pair == context.selected_course), languages[0])
    def practice(language,kind):
        from app.vocabulary.practise import Rep
        return Rep(app,stats[language][kind],language,languages.index(language)+1,context=context)
    def edit(language):
        from app.vocabulary.editor import Edit
        return Edit(app,language,context=context)
    def conjugation(language):
        from app.conjugation.practise import Conjugation
        return Conjugation(app,language,context=context)
    def grammar(language):
        from app.grammar.practise import Grammar_training
        return Grammar_training(app,language,context=context)
    def edit_grammar(language):
        from app.grammar.editor import Edit_grammar
        return Edit_grammar(app,language,context=context)
    return build_home(app,stats,languages,dict(practice=lambda language:practice(language,'rep_words'),
        learn=lambda language:practice(language,'lrn_words'),edit=edit,conjugation=conjugation,
        grammar=grammar,edit_grammar=edit_grammar,refresh=context.go_home,
        available=lambda language,kind:(context.conjugation_path(language) if kind=='conjugation'
            else context.grammar_path(language)).exists()), initial_language=selected,
        on_select=lambda language: setattr(context, 'selected_course', context.language_pair(language)))

"""Compose question/theory navigation without coupling their implementations."""
from importlib import import_module


def open_editor(app, language, *, theory=False, context=None):
    module_name, entry = ('editor_theory', 'Edit_grammar_theory') if theory else ('editor', 'Edit_grammar')
    module = import_module('app.grammar.' + module_name)
    return getattr(module, entry)(app, language, context=context)

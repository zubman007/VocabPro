"""Scoped application dependencies for tests; never load user preferences."""
from contextlib import contextmanager, ExitStack
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from app.core.context import get_context


@contextmanager
def patch_preferences(**values):
    context=get_context()
    with patch.object(context,'preferences',replace(context.preferences,**values)):
        yield context


@contextmanager
def patch_context(*,root_dir=None,files_dir=None):
    context=get_context()
    with ExitStack() as stack:
        if root_dir is not None:
            stack.enter_context(patch.object(context,'root_dir',Path(root_dir)))
            stack.enter_context(patch.object(context,'files_dir',Path(root_dir)/'files'))
        if files_dir is not None:
            stack.enter_context(patch.object(context,'files_dir',Path(files_dir)))
        yield context

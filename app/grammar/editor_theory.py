"""Category-theory editor, sharing selection and unsaved-change handling with questions."""
from app.core.context import get_context
from app.grammar.editor import GrammarEditor
from app.grammar.editor_theory_data import GrammarTheoryDocument


class GrammarTheoryEditor(GrammarEditor):
    document_type = GrammarTheoryDocument
    theory_mode = True
    title_key = 'Edit grammar theory'
    add_key = 'Add theory'
    delete_key = 'Delete theory'
    apply_prompt = 'Apply changes to the current theory?'
    delete_prompt = 'Delete theory for this category?'
    count_key = 'Number of categories'

    def refresh(self, preferred=None):
        super().refresh(preferred)
        choices = sorted(self.document.suggestions | (set(self.document.frame.category) - {''}), key=str.casefold)
        self.view.fields['category'].configure(values=choices or [''])


def Edit_grammar_theory(app,language,*,context=None):
    context=get_context(app,context)
    if not context.preferences.grammar_enabled(language):return
    return GrammarTheoryEditor(app,language,context.theory_path(language),context.go_home,context=context)

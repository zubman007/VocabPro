"""Previous-word review; session changes remain in controller callbacks."""
from app.ui.learning_review import ReviewDialog
from app.shared import settings as s


def open_review(app, word, on_audio, on_description, on_example, synonyms='', on_synonyms=None,
                on_edit_description=None,on_edit_example=None,*,tags='',on_tags=None):
    actions=[('Delete audio',on_audio),('Delete word description',on_description),('Delete example sentence',on_example)]
    if on_synonyms is not None:actions.append(('Edit synonyms',on_synonyms))
    if on_edit_description is not None:actions.append(('Edit description',on_edit_description))
    if on_edit_example is not None:actions.append(('Edit example',on_edit_example))
    if on_tags is not None:actions.append(('Edit tags',on_tags))
    return ReviewDialog(app, 'Review of the previous word', word.word, word.tr,
                        [('Phonetic', word.phon), ('Part of Speech', s.T(word.PoS)),
                         ('Description', word.desc), ('Example', word.sen), ('Tags', tags), ('Synonyms', synonyms.strip())],actions)

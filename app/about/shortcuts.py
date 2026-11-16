"""User-facing shortcut reference, including contextual and native editing keys."""


def shortcut_sections(show_synonyms=True, tags_enabled=True, grammar_enabled=True, conjugation_enabled=True):
    vocabulary=[('Ctrl+S','Save'),('Ctrl+R','Record audio'),('Ctrl+P','Play audio (ctrl+p)'),('Ctrl+H','Show synonyms')]
    if tags_enabled:
        vocabulary.extend([('Ctrl+T','Word tags'),('Ctrl+Shift+T','Manage tags')])
    vocabulary.extend([('Enter','Apply filter'),('Esc','Close')])
    repeat=[('1–4','Choose answer (options only)'),('Enter','Confirm answer or play audio'),
        ('Ctrl+S','Save'),('Ctrl+R','Review of the previous word'),('Ctrl+P','Listen'),('Alt+→','Next'),('Esc','Close')]
    if not show_synonyms:repeat.append(('Ctrl+H','Show synonyms'))
    sections = [
        ('Vocabulary',vocabulary),
        ('Repeat',repeat),
        ('Grammar',[('1–4','Choose answer (options only)'),('Enter','Next after feedback'),('Ctrl+S','Save'),('Space','Reveal or next question'),
            ('Alt+→','Next question'),('Ctrl+Z','Previous question'),('Ctrl+T','Show question theory'),('Ctrl+F','Filter question categories'),('Esc','Close')]),
        ('Conjugation',[('Enter','OK'),('Ctrl+S','Save'),('Ctrl+R','Review of the previous verb'),('Esc','Close')]),
        ('Grammar editors',[('Ctrl+S','Save'),('Enter','Apply filter'),('Esc','Close')]),
        ('Conjugation editors',[('Ctrl+S','Save'),('Esc','Close')]),
        ('Setting',[('Ctrl+S','Save'),('Esc','Close')]),
        *([('Word tags',[('Ctrl+F','Search tags'),('Ctrl+Enter','Apply'),('Esc','Close')]),
           ('Manage tags',[('Ctrl+S','Save'),('Esc','Close')])] if tags_enabled else []),
        ('Tables and text fields',[('Ctrl+C','Copy'),('Ctrl+X','Cut'),('Ctrl+V','Paste'),('Ctrl+A','Select all'),('Ctrl+Z','Undo'),('Ctrl+Shift+Z','Redo')]),
        ('Dialogs',[('Esc','Close')]),
    ]
    return [section for section in sections
            if (grammar_enabled or section[0] not in ('Grammar','Grammar editors'))
            and (conjugation_enabled or section[0] not in ('Conjugation','Conjugation editors'))]



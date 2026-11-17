from dataclasses import replace
from pathlib import Path
from PIL import ImageGrab
from app.tests.safety import isolated_services
from app.tests.test_learning_module_alignment import LearningAlignmentUiTests
from app.conjugation.editor import Edit_conjugation
from app.grammar.editor import Edit_grammar

output = Path(r'C:\Users\zubso\AppData\Local\Temp\vocabpro-unify-zqmfti6e')
with isolated_services():
    case = LearningAlignmentUiTests()
    case.setUp()
    try:
        def capture(name, size='1280x850'):
            root = case.root
            root.geometry(size+'+40+40'); root.lift(); root.focus_force()
            root.after(500, root.quit); root.mainloop()
            box = (root.winfo_rootx(), root.winfo_rooty(), root.winfo_rootx()+root.winfo_width(), root.winfo_rooty()+root.winfo_height())
            ImageGrab.grab(bbox=box).save(output/(name+'.png'))
        lesson = case.lesson(); capture('conjugation-session'); lesson.lifecycle.close()
        editor = Edit_conjugation(case.root, 'es', context=case.context); capture('conjugation-editor'); editor.lifecycle.close()
        editor = Edit_grammar(case.root, 'Spanish', context=case.context); capture('grammar-editor'); editor.lifecycle.close()
        case.context.preferences = replace(case.context.preferences, app_language='de')
        lesson = case.lesson(); capture('conjugation-session-de', '1000x800'); lesson.lifecycle.close()
        print('Four synthetic UI previews saved to', output)
    finally:
        case.tearDown(); case.doCleanups()

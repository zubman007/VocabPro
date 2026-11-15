"""End-to-end temporary courses, randomized histories and interrupted writes."""
import random
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from app.grammar.editor_data import GrammarDocument
from app.repositories.grammar import Load_questions_from_csv, save_answers
from app.repositories.grammar_theory import load_theory
from app.repositories.grammar_theory import ensure_theory_categories
from app.statistics.data import training_statistics
from app.services.backup import backup_files
from app.shared.storage import save_csv, FileChangedError
from app.statistics.cache import StatisticsCache
from app.grammar.session import GrammarSession


def course():
    return pd.DataFrame([dict(question_id=str(index), category='Topic '+str(index % 3),
        prompt='Choose', anchor=f'Sentence {index}; with a newline\nsecond line',
        option_1='Correct', option_2='Wrong A', option_3='Wrong B', option_4='Wrong C',
        explanation='A reason', R='S'*index+'F', LR='', custom='007') for index in range(1, 9)])


class WorkflowTests(unittest.TestCase):
    def test_editor_practice_theory_statistics_and_backup_agree(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'English_gra.csv'
            course().to_csv(path,sep=';',index=False)
            original=Load_questions_from_csv(path)
            editor=GrammarDocument(path)
            editor.delete('2');editor.save()
            before=path.read_bytes()
            with self.assertRaises(FileChangedError):
                save_answers(path,[('2','F',original[1],'2026-11-13 12:00:00')])
            self.assertEqual(path.read_bytes(),before)
            current=Load_questions_from_csv(path)[1]
            save_answers(path,[(current['id'],'S',current,'2026-11-13 12:00:00')])
            frame=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(frame.question_id.tolist(),[str(i) for i in range(1,8)])
            self.assertEqual(frame.loc[1,'R'],'SSSFS')
            self.assertEqual(frame.custom.tolist(),['007']*7)
            theory=root/'Czech_English_gra_ex.csv'
            self.assertEqual(ensure_theory_categories(theory,frame.category),3)
            self.assertEqual(load_theory(theory),{})
            statistics=training_statistics(path,'grammar')
            self.assertEqual(statistics['summary'],(7,int(frame.R.str.count('S').sum()),7))
            self.assertEqual(sum(item.questions for item in statistics['categories']),7)
            (root/'empty.csv').write_text('ID;value\n',encoding='utf-8')
            (root/'settings.csv').write_text('Name;Value\nAPI key;fake\n',encoding='utf-8')
            backed_up=dict(backup_files(root))
            self.assertEqual(set(backed_up),{'English_gra.csv','Czech_English_gra_ex.csv'})
            self.assertEqual(backed_up[path.name],path.read_bytes())

    def test_fsync_failure_never_publishes_partial_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';path.write_bytes(b'original')
            with patch('app.shared.storage.os.fsync',side_effect=OSError('Disk flush failed')):
                with self.assertRaises(OSError):save_csv(course(),path,index=False,sep=';')
            self.assertEqual(path.read_bytes(),b'original')
            self.assertEqual(list(path.parent.iterdir()),[path])

    def test_continuously_changing_input_is_never_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'data.csv';path.write_text('a',encoding='utf-8')
            cache=StatisticsCache();calls=[]
            def calculate(source):
                value=source.read_text();calls.append(value)
                source.write_text(value+'x',encoding='utf-8')
                return value
            with self.assertRaises(OSError):cache.get(path,'test',(),calculate)
            self.assertEqual(len(calls),2)
            self.assertFalse(cache._entries)

    def test_randomized_round_never_scores_the_same_question_twice(self):
        generator=random.Random(781)
        questions=[dict(id=str(i),options=['yes','no','x','y'],correct_answer='yes') for i in range(80)]
        session=GrammarSession(questions)
        rounds=0
        while session.advance() is not None:
            rounds+=1
            if generator.choice([True,False]):
                session.answer(generator.randrange(4))
            else:session.reveal()
            before=(session.correct,session.incorrect,session.streak)
            for _ in range(5):session.answer(generator.randrange(4));session.reveal()
            self.assertEqual((session.correct,session.incorrect,session.streak),before)
        self.assertEqual(rounds,80)
        self.assertEqual(session.correct+session.incorrect,80)

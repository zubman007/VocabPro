"""Cross-module edge cases, randomized edits, restarts and repeated persistence."""
from pathlib import Path
import random
import tempfile
import unittest
import pandas as pd
from app.grammar.editor_data import GrammarDocument, QuestionValidationError
from app.grammar.editor_theory_data import GrammarTheoryDocument
from app.repositories.grammar_theory import ensure_theory_categories
from app.repositories.grammar_theory import load_theory
from app.repositories.preferences import load_preferences, save_preferences
from app.services.backup import backup_files
from app.repositories.vocabulary import save_practice
from app.statistics.data import training_statistics
from app.tests.test_preferences_data import sample_preferences
from app.tests.test_grammar_editor import questions
from app.tests.test_editor_save import course


class ExtendedScenarioTests(unittest.TestCase):
    def test_random_correct_answer_changes_keep_unicode_history_and_unknown_fields(self):
        generator=random.Random(435)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar.csv';questions().to_csv(path,sep=';',index=False)
            for _ in range(40):
                document=GrammarDocument(path)
                values=document.question('001')
                answers=['caf\u00e9','ni\u00f1o','\u0159eka','NA']
                for index,value in enumerate(answers,1):values[f'option_{index}']=value
                selected=generator.randrange(4)
                document.update('001',values,selected);document.save()
                result=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
                self.assertEqual(result.loc[0,'option_1'],answers[selected])
                self.assertEqual(result.loc[0,'R'],'SF')
                self.assertEqual(result.loc[0,'custom'],'007;keep')

    def test_invalid_hidden_question_reports_id_without_partial_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar.csv';questions().to_csv(path,sep=';',index=False)
            original=path.read_bytes();document=GrammarDocument(path)
            document.frame.loc[1,'option_4']=document.frame.loc[1,'option_1']
            with self.assertRaises(QuestionValidationError) as raised:document.save()
            self.assertEqual(raised.exception.identifier,'002')
            self.assertEqual(path.read_bytes(),original)

    def test_placeholder_can_be_completed_then_becomes_available_and_backed_up(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'Czech_English_gra_ex.csv'
            ensure_theory_categories(path,['Articles','Tenses'])
            self.assertFalse(load_theory(path))
            document=GrammarTheoryDocument(path)
            values=document.question('1');values.update(title='Articles',rules='Rule; with newline\nMore',examples='A | B')
            document.update('1',values);document.save()
            self.assertEqual(set(load_theory(path)),{'articles'})
            self.assertEqual(dict(backup_files(directory))[path.name],path.read_bytes())
            self.assertEqual(ensure_theory_categories(path,['ARTICLES','Tenses']),0)

    def test_repeated_preference_updates_never_reset_unrelated_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.csv';sample_preferences().to_csv(path,sep=';',index=False)
            initial=load_preferences(path).set_index('Name').Value.to_dict()
            # Saving a legacy settings file adds the documented defaults once.
            # Still compare the entire mapping so unrelated values cannot reset.
            expected=dict(initial,**{'Letter hints':'On request','Enable tags':'1',
                'Show tags during practice':'1','Tag display language':'Learning language',
                'Maximum tags per word':'10','Enable second learning language':'1',
                'Track personal records':'1','Show personal records':'1','Remember conjugation categories':'1',
                'Random repeat batch - Grammar':'10','Random repeat batch - Conjugation':'10'})
            for number in (1,20,1000,2,9999,10):
                frame=load_preferences(path)
                save_preferences(frame,{'Learn batch':str(number)},path)
                saved=load_preferences(path).set_index('Name').Value.to_dict()
                self.assertEqual(saved['Learn batch'],str(number))
                self.assertEqual({key:value for key,value in saved.items() if key!='Learn batch'},
                                 {key:value for key,value in expected.items() if key!='Learn batch'})

    def test_practice_repeated_save_is_idempotent_and_preserves_custom_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'course.csv';source=course();source.to_csv(path,sep=';',index=False)
            completed=source.copy();completed.loc[0,'Repetition']='SFSS'
            remaining=source.iloc[:0].copy()
            save_practice(path,remaining,completed,list(source.columns))
            first=path.read_bytes()
            for _ in range(5):save_practice(path,remaining,completed,list(source.columns))
            self.assertEqual(path.read_bytes(),first)
            saved=pd.read_csv(path,sep=';',dtype=str,keep_default_na=False)
            self.assertEqual(saved.loc[0,'Custom'],'007;keep')
            self.assertEqual(saved.loc[0,'Repetition'],'SFSS')

    def test_cache_after_atomic_grammar_save_reflects_the_new_category_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'grammar.csv';questions().to_csv(path,sep=';',index=False)
            first=training_statistics(path,'grammar')
            document=GrammarDocument(path)
            values=document.question('002');values['category']='Articles'
            document.update('002',values);document.save()
            second=training_statistics(path,'grammar')
            self.assertEqual(len(first['categories']),2)
            self.assertEqual(len(second['categories']),1)
            self.assertEqual(second['categories'][0].questions,2)

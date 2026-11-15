"""Grammar editor document: stable IDs, preserved history and atomic conflict checks."""
from pathlib import Path
import pandas as pd
from app.repositories.csv_store import read_document,commit_document

FIELDS = ('category', 'prompt', 'anchor', 'option_1', 'option_2', 'option_3', 'option_4', 'explanation')
COLUMNS = ('question_id', *FIELDS, 'R', 'LR')


class QuestionValidationError(ValueError):
    def __init__(self, identifier, message):
        self.identifier = str(identifier)
        super().__init__(message)


def validate_question(values):
    if any(not str(values.get(key, '')).strip() for key in FIELDS if key != 'explanation'):
        raise ValueError('Fill in the category, question, sentence and all four answers.')
    answers = [' '.join(str(values[key]).split()).casefold() for key in FIELDS if key.startswith('option_')]
    if len(set(answers)) != 4:
        raise ValueError('The four answer options must be different.')


class GrammarDocument:
    fields = FIELDS
    id_column = 'question_id'
    summary_column = 'anchor'
    def __init__(self, path):
        self.path = Path(path)
        self.frame,self.revision=read_document(path,message='The grammar file changed. Reopen the editor before saving.')
        if 'Category' in self.frame and 'category' not in self.frame:
            self.frame.rename(columns={'Category': 'category'}, inplace=True)
            self._category_name = 'Category'
        else:
            self._category_name = 'category'
        for column in COLUMNS:
            if column not in self.frame:
                if column in ('category', 'explanation', 'R', 'LR'):
                    self.frame[column] = ''
                else:
                    raise ValueError('Missing required grammar columns.')
        if self.frame.question_id.eq('').any() or self.frame.question_id.duplicated().any():
            raise ValueError('Question IDs must be filled and unique.')
        self.dirty = False

    def question(self, identifier):
        return self.frame.loc[self.frame.question_id.eq(str(identifier))].iloc[0].to_dict()

    def update(self, identifier, values, correct_index=0):
        values = {key: str(values.get(key, '')).strip() for key in FIELDS}
        validate_question(values)
        if correct_index not in range(4):
            raise ValueError('Choose the correct answer.')
        answers = [values[f'option_{i}'] for i in range(1, 5)]
        correct = answers.pop(correct_index)
        for index, answer in enumerate([correct, *answers], 1):
            values[f'option_{index}'] = answer
        mask = self.frame.question_id.eq(str(identifier))
        if not mask.any():
            raise ValueError('Question not found.')
        for key, value in values.items():
            self.frame.loc[mask, key] = value
        self.dirty = True

    def add(self):
        numeric = pd.to_numeric(self.frame.question_id, errors='coerce').dropna()
        identifier = str(int(numeric.max())+1 if len(numeric) else 1)
        while identifier in set(self.frame.question_id):
            identifier = str(int(identifier)+1)
        row = dict.fromkeys(self.frame.columns, '')
        row['question_id'] = identifier
        self.frame = pd.concat([self.frame, pd.DataFrame([row])], ignore_index=True)
        self.dirty = True
        return identifier

    def delete(self, identifier):
        self.frame = self.frame.loc[self.frame.question_id.ne(str(identifier))].reset_index(drop=True)
        self.frame['question_id'] = [str(index+1) for index in range(len(self.frame))]
        self.dirty = True

    def save(self):
        for values in self.frame.to_dict('records'):
            try:
                validate_question(values)
            except ValueError as error:
                raise QuestionValidationError(values['question_id'], str(error)) from error
        result = self.frame.rename(columns={'category': self._category_name})
        self.revision=commit_document(self.path,result,self.revision)
        self.dirty = False

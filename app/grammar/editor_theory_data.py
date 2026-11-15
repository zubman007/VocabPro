"""Theory documents preserve extra CSV columns and never alter grammar questions."""
from pathlib import Path
import pandas as pd
from app.repositories.csv_store import read_document,commit_document
from app.grammar.theory_data import category_key
from app.repositories.grammar_theory import THEORY_FIELDS,question_categories_for_theory

FIELDS = THEORY_FIELDS


class GrammarTheoryDocument:
    fields = FIELDS
    id_column = '_editor_id'
    summary_column = 'title'

    def __init__(self, path):
        self.path = Path(path)
        self.frame,self.revision=read_document(path,optional=True,columns=FIELDS,
            message='The theory file changed. Reopen the editor before saving.')
        if self.id_column in self.frame:
            raise ValueError('Reserved editor column in theory CSV.')
        for field in FIELDS:
            if field not in self.frame:
                self.frame[field] = ''
        self.frame[self.id_column] = [str(i+1) for i in range(len(self.frame))]
        self.dirty = False
        self.suggestions = set(self.frame.category) - {''}
        self.suggestions.update(question_categories_for_theory(self.path))
        known = set(self.frame.category.map(category_key))
        for category in sorted(self.suggestions, key=str.casefold):
            if category_key(category) not in known:
                identifier = self.add()
                self.frame.loc[self.frame[self.id_column].eq(identifier), 'category'] = category
                known.add(category_key(category))

    def question(self, identifier):
        return self.frame.loc[self.frame[self.id_column].eq(str(identifier))].iloc[0].to_dict()

    def update(self, identifier, values, correct_index=0):
        values = {key: str(values.get(key, '')).strip() for key in FIELDS}
        self._validate(values, identifier)
        mask = self.frame[self.id_column].eq(str(identifier))
        if not mask.any():
            raise ValueError('Theory not found.')
        for key, value in values.items():
            self.frame.loc[mask, key] = value
        self.dirty = True

    def _validate(self, values, identifier):
        placeholder = values['category'] and not any(values[field] for field in FIELDS[1:])
        if not placeholder and (not values['category'] or not values['title'] or not any(values[field] for field in FIELDS[3:])):
            raise ValueError('Fill in the category, title and at least one theory section.')
        others = self.frame.loc[self.frame[self.id_column].ne(str(identifier)), 'category']
        if category_key(values['category']) in set(others.map(category_key)):
            raise ValueError('Theory for this category already exists.')

    def add(self):
        ids = self.frame[self.id_column].astype(int)
        identifier = str(int(ids.max())+1 if len(ids) else 1)
        row = dict.fromkeys(self.frame.columns, '')
        row[self.id_column] = identifier
        self.frame = pd.concat([self.frame, pd.DataFrame([row])], ignore_index=True)
        self.dirty = True
        return identifier

    def delete(self, identifier):
        self.frame = self.frame.loc[self.frame[self.id_column].ne(str(identifier))].reset_index(drop=True)
        self.dirty = True

    def save(self):
        for values in self.frame.to_dict('records'):
            self._validate(values, values[self.id_column])
        self.revision=commit_document(self.path,self.frame.drop(columns=self.id_column),self.revision,
            message='The theory file changed. Reopen the editor before saving.')
        self.dirty = False

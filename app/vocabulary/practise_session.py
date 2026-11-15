"""In-memory practice state: direct ID access, no per-answer DataFrame joins."""
import random
from app.vocabulary.practise_data import next_repetition


class PracticeSession:
    def __init__(self, frame, days_gap_map, default_wait):
        if frame['ID'].isna().any() or frame['ID'].duplicated().any():
            raise ValueError('Practice requires unique word IDs')
        self.data=frame.set_index('ID',drop=False)
        self.remaining=self.data['ID'].tolist()
        self.ordered=bool(frame.attrs.get('ordered_lesson',False))
        self.order={identifier:index for index,identifier in enumerate(self.remaining)}
        self.positions={word_id:index for index,word_id in enumerate(self.remaining)}
        self.completed=[]
        self.days_gap_map=days_gap_map
        self.default_wait=default_wait

    def __bool__(self):
        return bool(self.remaining)

    def pick(self):
        return self.data.loc[min(self.remaining,key=self.order.get) if self.ordered else random.choice(self.remaining)]

    def history(self,word_id):
        return str(self.data.at[word_id,'Repetition'])

    def introduce(self,word_id):
        if self.history(word_id):
            return False
        self.data.at[word_id,'Repetition']='S'
        return True

    def succeed(self,word_id,now=None):
        if word_id not in self.positions:
            return False
        history=self.history(word_id)
        self.data.at[word_id,'Repetition']=history+'S'
        if history.count('S')<4:
            return False
        self.data.at[word_id,'Next repetition']=next_repetition(
            history+'S',self.days_gap_map,self.default_wait,now)
        self.skip(word_id)
        return True

    def fail(self,word_id):
        if word_id in self.positions:
            self.data.at[word_id,'Repetition']=self.history(word_id)+'F'

    def skip(self,word_id):
        position=self.positions.pop(word_id,None)
        if position is None:
            return
        last=self.remaining.pop()
        if position<len(self.remaining):
            self.remaining[position]=last
            self.positions[last]=position
        self.completed.append(word_id)

    def set_attribute(self,word_id,column,value):
        if word_id in self.data.index:
            self.data.at[word_id,column]=value

    def frames(self):
        # Materialize independent tables only at the persistence boundary.
        remaining=self.data.loc[self.remaining].reset_index(drop=True).copy()
        completed=self.data.loc[self.completed].reset_index(drop=True).copy()
        return remaining,completed


class ChoicePool:
    def __init__(self,translations):
        self.translations=tuple(translations)
        self._cache={}

    def _candidates(self,correct):
        if correct not in self._cache:
            if len(self._cache)>=64:
                self._cache.pop(next(iter(self._cache)))
            # Keep row weighting but bound memory to the current lesson.
            self._cache[correct]=tuple(value for value in self.translations if value!=correct)
        return self._cache[correct]
    def options(self,correct):
        candidates=self._candidates(correct)
        if len(candidates)<3:
            return None
        options=random.sample(candidates,3)+[correct]
        random.shuffle(options)
        return options

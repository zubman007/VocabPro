"""Read-only synonym indicators; these columns never belong to vocabulary CSVs."""
from app.repositories import synonyms
from app.repositories.vocabulary import read_words
import pandas as pd

from app.vocabulary.synonyms import COLUMNS


class SynonymCounts:
    """One editor-owned derived index, invalidated by the relations file signature."""
    def __init__(self):
        self.signature = None
        self.counts = {}

    def get(self, course, frame):
        path = synonyms.relation_path(course)
        info = path.stat() if path.exists() else None
        signature = (str(path.resolve()), (info.st_mtime_ns, info.st_ctime_ns, info.st_size) if info else None)
        if signature != self.signature:
            # Read all valid links independently of pending editor deletions.
            words = read_words(course)
            relations, _ = synonyms.load(course, words)
            counts = {}
            for first, second in relations[['ID 1','ID 2']].itertuples(index=False,name=None):
                for identifier in (int(first),int(second)):
                    counts[identifier] = counts.get(identifier,0)+1
            self.counts, self.signature = counts, signature
        return self.counts


def add_columns(frame, course, cache=None):
    result=frame.copy()
    from app.vocabulary.tags_data import tag_count
    result['Tag count']=result.get('Tags',pd.Series('',index=result.index)).map(tag_count)
    if cache is not None:
        counts = cache.get(course, frame)
    else:
        relations,_=synonyms.load(course,result)
        counts={}
        for first,second in relations[['ID 1','ID 2']].itertuples(index=False,name=None):
            for word_id in (int(first),int(second)):counts[word_id]=counts.get(word_id,0)+1
    result['Synonym count']=result.ID.map(counts).fillna(0).astype(int)
    result['Has synonyms']=result['Synonym count'].map(lambda count:'●' if count else '—')
    return result

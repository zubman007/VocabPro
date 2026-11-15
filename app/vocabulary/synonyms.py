"""Undirected, course-local vocabulary links; never alternative answer rules."""

COLUMNS = ('Has synonyms','Synonym count')


def linked_ids(frame, word_id):
    word_id = int(word_id)
    return {int(b if int(a) == word_id else a) for a,b in frame[['ID 1','ID 2']].itertuples(index=False,name=None)
            if word_id in (int(a), int(b))}


def describe(frame, words, word_id, language, learned_by):
    ids = linked_ids(frame, word_id)
    if not ids:return ''
    matches = words.loc[words.ID.astype(int).isin(ids)]
    return '\n'.join(f"{' '.join(str(source).split())} — {' '.join(str(target).split())}"
                     for source,target in matches[[language,learned_by]].itertuples(index=False,name=None))



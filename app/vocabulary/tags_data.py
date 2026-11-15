"""Pure normalization and catalog membership rules for multiple word tags."""
from unicodedata import normalize
import pandas as pd


class UnknownTagError(ValueError):
    MESSAGE = 'Unknown tag "{tag}" for word ID {word_id}. Choose tags from the catalog.'

    def __init__(self, tag, word_id):
        self.tag, self.word_id = tag, word_id
        super().__init__(self.MESSAGE)


def normalize_tags(value):
    """Comma-separated labels, preserving spelling and order of the first occurrence."""
    if value is None or pd.isna(value):
        return ''
    tags = {}
    for item in str(value).split(','):
        tag = normalize('NFC', item.strip())
        if tag:
            tags.setdefault(tag.casefold(), tag)
    return ', '.join(tags.values())


def validate_word_tags(frame, catalog, learned_by):
    """Canonicalize catalog names; reject the whole batch if any tag is unknown."""
    result = frame.copy()
    if 'Tags' not in result:
        return result
    allowed = {name.casefold():name for name in catalog[learned_by]}
    for column in catalog.columns:
        if column not in ('ID','Note',learned_by):
            for source,target in zip(catalog[learned_by],catalog[column]):
                if target:allowed.setdefault(target.casefold(),source)
    tags = []
    for identifier, value in result[['ID','Tags']].itertuples(index=False, name=None):
        normalized=normalize_tags(value)
        labels = normalized.split(', ') if normalized else []
        for label in labels:
            if label.casefold() not in allowed:
                raise UnknownTagError(label, identifier)
        tags.append(', '.join(allowed[label.casefold()] for label in labels))
    result['Tags'] = tags
    return result


def translated_tags(value, translations):
    """Present target-language labels, falling back to the assigned name if missing."""
    labels={}
    normalized=normalize_tags(value)
    for name in normalized.split(', ') if normalized else ():
        label=translations.get(name.casefold()) or name
        labels.setdefault(label.casefold(),label)
    return ' · '.join(labels.values())


def filter_by_tags(frame, selected, mode):
    """Match whole tag sets: all selected, none selected, or exact equality."""
    if mode not in ('all','none','exact'):
        raise ValueError('Invalid tag filter mode')
    normalized=normalize_tags(selected if isinstance(selected,str) else ', '.join(selected))
    wanted=set(normalized.casefold().split(', ')) if normalized else set()
    def matches(value):
        normalized=normalize_tags(value)
        present=set(normalized.casefold().split(', ')) if normalized else set()
        if mode=='all':return wanted <= present
        if mode=='none':return wanted.isdisjoint(present)
        return wanted==present
    values=frame['Tags'] if 'Tags' in frame else pd.Series('',index=frame.index)
    mask=values.map(matches).astype(bool)
    return frame.loc[mask].copy().reset_index(drop=True)

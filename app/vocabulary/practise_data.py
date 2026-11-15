"""Vocabulary practice values, answer rules, hints and scheduling; no CSV I/O."""
from datetime import datetime, timedelta
from functools import lru_cache
import random
import re
import string
import unicodedata

class Word:
    def __init__(self, id, w, ph, desc, sen, tr, PoS):
        self.id = id
        self.word = w
        self.phon = ph
        self.desc = desc
        self.sen = sen
        self.tr = tr
        self.PoS = PoS
    def copy(self, next):
        self.__dict__.update(next.__dict__)


@lru_cache(maxsize=512)
def _answer_variants(value):
    normalized = unicodedata.normalize('NFD', value)
    plain = ''.join(char for char in normalized if not unicodedata.combining(char))
    cleaned = re.sub(r'[^\w\s/]', '', plain)
    return frozenset(item.strip() for item in cleaned.lower().split('/') if item.strip())


def answers_match(expected, response):
    return not _answer_variants(expected).isdisjoint(_answer_variants(response))


def shuffle_letters(word):
    word = ' '.join(w.capitalize() for w in word.split())
    word = word.replace(' ','_')
    combined_list = list(word+''.join(random.choices(string.ascii_letters,k=3)).lower())
    random.shuffle(combined_list)
    letters = ''.join(combined_list)
    if len(word) > 17: spaces = ' ' * 1
    else: spaces = ' ' * 4
    letters = spaces.join(letters)
    return letters

def next_repetition(rep, days_gap_map, default_wait, now=None):
    count, index, num_last_succ = 0, 0, 0
    while index < len(rep) and count < 4:
        if rep[index] == 'S': count += 1
        index += 1
    rep_cleared = rep[index:]
    for char in reversed(rep_cleared):
        if char == 'S': num_last_succ += 1
        else: break
    next_rep = (now or datetime.now()) + timedelta(days=days_gap_map.get(num_last_succ, default_wait))
    return next_rep.strftime("%Y-%m-%d %H:%M:%S")


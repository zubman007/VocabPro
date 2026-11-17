"""Saved verb-category IDs, isolated by source/target pair from grammar filters."""
from app.repositories import grammar_filters

FILTER_SETTING = 'Saved conjugation category filters'


def load_filter(path, learned_by, language, available):
    return grammar_filters.load_filter(path, learned_by, language, available,
                                      setting=FILTER_SETTING, normalize=str.strip)


def save_filter(path, learned_by, language, selected, available):
    return grammar_filters.save_filter(path, learned_by, language, selected, available,
                                      setting=FILTER_SETTING, normalize=str.strip)

"""Deterministic UI formats; never change CSV values or process-wide locale."""
from app.shared.translations import LANGUAGE_CODES


def language_code(language):
    return LANGUAGE_CODES.get(language, language if language in LANGUAGE_CODES.values() else 'en')


def number(value, language='English', places=0):
    text = f'{value:.{places}f}'
    return text if language_code(language) == 'en' else text.replace('.', ',')


def percent(fraction, language='English', places=0):
    separator = '' if language_code(language) == 'en' else '\N{NO-BREAK SPACE}'
    return number(fraction * 100, language, places) + separator + '%'


def date_pattern(language='English'):
    code = language_code(language)
    if code in ('cs', 'sk', 'de'):
        return '%d.%m.%Y'
    return '%d/%m/%Y' if code in ('es', 'fr') else '%Y-%m-%d'


def date_text(value, language='English'):
    return value.strftime(date_pattern(language))

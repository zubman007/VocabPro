"""Only newly observed person outcomes; never infer them from round histories."""
import json
from app.conjugation.persons import unique_object, valid_person_id
from app.shared.messages import UserMessageError

HISTORY_COLUMN = 'Person history'


def decode_history(value):
    if not value:return {}
    try:
        data = json.loads(value, object_pairs_hook=unique_object)
        if (not isinstance(data, dict) or set(data) != {'version', 'results'}
                or type(data['version']) is not int or data['version'] != 1 or not isinstance(data['results'], dict)
                or any(not valid_person_id(key) or not isinstance(history, str) or set(history)-set('SF')
                       for key, history in data['results'].items())):
            raise ValueError
        return data['results']
    except (ValueError, TypeError, KeyError):
        raise UserMessageError('Invalid conjugation person history.') from None


def record_person_results(frame, identifier, results):
    if HISTORY_COLUMN not in frame:frame[HISTORY_COLUMN] = ''
    mask = frame.ID.eq(identifier)
    if not mask.any():raise UserMessageError('Verb not found.')
    index = frame.index[mask][0]
    histories = decode_history(frame.at[index, HISTORY_COLUMN])
    for key, correct in results.items():histories[key] = histories.get(key, '')+('S' if correct else 'F')
    frame.at[index, HISTORY_COLUMN] = json.dumps(dict(version=1, results=histories), separators=(',', ':'))

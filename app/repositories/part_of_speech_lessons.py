"""Read-only vocabulary selection by canonical part of speech."""
import pandas as pd
from app.repositories.vocabulary import read_words


def part_of_speech_lesson(course, part_of_speech):
    frame = read_words(course)
    result = frame.loc[frame['Part of Speech'].eq(part_of_speech)].copy()
    dates = pd.to_datetime(result['Next repetition'], format='ISO8601', errors='coerce', utc=True)
    result = result.loc[dates.sort_values(kind='stable', na_position='first').index].reset_index(drop=True)
    result.attrs['ordered_lesson'] = True
    return result

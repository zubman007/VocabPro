"""Append after the highest remaining ID; never renumber existing words."""


def next_word_id(course, frame):
    return int(frame.ID.max())+1 if len(frame) else 1

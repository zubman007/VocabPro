"""Shared number-row and Windows numpad answer decoding."""
import sys


def has_answer_modifier(event):
    # Tk on Windows uses Mod1 (0x8) for Num Lock, and 0x20000 for Alt.
    mask = 0x4 | (0x20000 if sys.platform == 'win32' else 0x8)
    return bool(getattr(event,'state',0) & mask)


def answer_index(event):
    if has_answer_modifier(event):return None
    key = getattr(event,'keysym','')
    names = {'plus':0,'ecaron':1,'scaron':2,'ccaron':3,
             'KP_End':0,'KP_Down':1,'KP_Next':2,'KP_Left':3}
    if key in names:return names[key]
    if key in ('1','2','3','4','KP_1','KP_2','KP_3','KP_4'):return int(key[-1])-1
    code = getattr(event,'keycode',0)
    if 97 <= code <= 100:return code-97
    if 49 <= code <= 52:return code-49
    return {'+':0,'ě':1,'š':2,'č':3}.get(getattr(event,'char',''))


ANSWER_SEQUENCES = tuple(f'<KeyPress-{name}>' for name in
    ('1','2','3','4','KP_1','KP_2','KP_3','KP_4','KP_End','KP_Down','KP_Next','KP_Left',
     'plus','ecaron','scaron','ccaron'))

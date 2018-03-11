from random import randint
from random import choice as rchoice

blanks = (
    '\u180e\u200b\u200c\u200d\u2060\u2061\u2062\u2063\u2064'
    '\u2068\u2069\u206a\u206b\u206c\u206d\u206e\u206f\ufeff'
)

def insert_blanks(s, min_chars=32, max_chars=128):
    for _ in range(1, randint(min_chars, max_chars)):
        i = randint(0, len(s))
        s = s[:i] + rchoice(blanks) + s[i:]
    return s

def message_text(m):
    return getattr(m.media, 'caption', None) or m.message or ''

def message_author(message):
    return getattr(message.fwd_from, 'from_id', None) or message.from_id
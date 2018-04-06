import re
import random
from random import randint
from collections import Counter

from telethon import events

from __main__ import client


def density_repeat(s):
    chars, weights = zip(*Counter(s).items())
    return ''.join(
        random.choices(chars, weights=weights, k=len(s) + randint(1, 10))
    )


@client.on(events.NewMessage(outgoing=False, pattern=re.compile(r'^(?i)(?:[^@]|^)(aw)(oo+)(\W*)$')))
def awoo(event):
    suffix = event.pattern_match.group(1)
    prefix = event.pattern_match.group(2)
    punctuation = event.pattern_match.group(3)
    if not punctuation:
        punctuation = '!' * randint(1, 6)
    else:
        punctuation = density_repeat(punctuation)

    if suffix.islower() and prefix.islower():
        prefix += 'o' * randint(1, 10)
    elif suffix.isupper() and prefix.isupper():
        prefix += 'O' * randint(1, 10)
    else:
        match = re.match('^(o+|O+)(o+|O+)$', prefix)
        if match:
            prefix = (
                match.group(1) + match.group(1)[0] * randint(1, 10)
                + match.group(2) + match.group(2)[0] * randint(1, 10)
            )
        else:
            prefix = density_repeat(prefix)

    event.reply(suffix + prefix + punctuation)
    raise events.StopPropagation

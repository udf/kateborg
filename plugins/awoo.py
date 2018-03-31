import re
from random import randint

from telethon import events

from __main__ import client


@client.on(events.NewMessage(outgoing=False, pattern=re.compile(r'(?:[^@]|^)(awoo+)')))
def awoo(event):
    event.reply(event.pattern_match.group(1).strip() + 'o' * randint(1, 10) + '!' * randint(1, 4))
    raise events.StopPropagation

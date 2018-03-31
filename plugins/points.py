# global karma point system for users
import re
from collections import namedtuple

from garry import events

from kiritostore import Kiritostore
from __main__ import client, my_id
from asuna import get_target, insert_blanks, get_entity_cached
from plugins.nicknames import get_name

import logging
logger = logging.getLogger("Kiritoborg@{}".format(__name__))

POINT_STORE = Kiritostore('points.json', int)
IGNORED_USERS = [548127565]
ADMINS = [my_id]

Pattern = namedtuple('Pattern', ['re', 'to_int'])
PATTERNS = (
    Pattern(re.compile('^([+-]\d+)$'), lambda m: int(m.group(1))),
    Pattern(re.compile('(?i)^(correct|good bot)$'), lambda m: 1),
    Pattern(re.compile('(?i)^(incorrect|bad bot)$'), lambda m: -1),
)


@client.on(events.NewMessage)
def on_message(event):
    if event.forward or event.message.from_id in IGNORED_USERS:
        return

    points = None
    for pattern in PATTERNS:
        match = pattern.re.match(event.raw_text)
        if match:
            points = pattern.to_int(match)
            break
    if points is None:
        return
    if abs(points) > 1 and event.message.from_id not in ADMINS:
        return
    if get_entity_cached(event.message.from_id).bot:
        return

    who = get_target(event)
    if not who or who == event.message.from_id:
        return

    # give points to the person
    POINT_STORE[who] += points
    message = '{} now has {} point{}'.format(
        get_name(who),
        POINT_STORE[who],
        '' if POINT_STORE[who] == 1 else 's'
    )
    logger.info(message)
    event.respond(
        '```' + insert_blanks(message) + '```',
        parse_mode='md'
    )
    raise events.StopPropagation

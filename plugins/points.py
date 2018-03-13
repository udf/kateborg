# global karma point system for users
import re

from telethon import events

from katestore import Katestore
from kateborg import client, my_id
from kateutil import get_target, insert_blanks
from plugins.nicknames import get_name

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))

POINT_STORE = Katestore('points.json', int)
IGNORED_USERS = [548127565]
ADMINS = [my_id]
RE_ADMIN = re.compile('^([+-]\d+)$')
RE_NORNAL = re.compile('^([+-]1)$')

@client.on(events.NewMessage)
def on_message(event):
    if event.forward or event.message.from_id in IGNORED_USERS:
        return

    pattern = RE_ADMIN if event.message.from_id in ADMINS else RE_NORNAL
    points = pattern.match(event.raw_text)
    if not points:
        return
    points = int(points.group(1))

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
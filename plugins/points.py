# global karma point system for users
import re

from telethon import events
from telethon.utils import get_peer_id, get_display_name

from katestore import Katestore
from kateborg import client, me
from kateutil import message_author, insert_blanks

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))
logger.info('Initializing...')

POINT_STORE = Katestore('points.json', int)
IGNORED_USERS = [548127565]
ADMINS = [get_peer_id(me)]
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

    # figure out who we're giving points to
    who = None
    who_name = None
    if event.is_reply:
        who = message_author(event.reply_message)
        who_name = get_display_name(client.get_entity(who))
    elif event.is_private:
        who_peer = event.chat if event.out else me
        who_name = get_display_name(who_peer)
        who = get_peer_id(who_peer)
    if not who or who == event.message.from_id:
        return
    if not who_name:
        who_name = 'ERROR:{}'.format(who)

    # give points to the person
    POINT_STORE[who] += points
    message = '{} now has {} point{}'.format(
        who_name,
        POINT_STORE[who],
        '' if POINT_STORE[who] == 1 else 's'
    )
    logger.info(message)
    event.respond(
        '```' + insert_blanks(message) + '```',
        parse_mode='md'
    )

logger.info('successfully loaded!')
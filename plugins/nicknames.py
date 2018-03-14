# nickname system and name caching
import re

from telethon import events

from katestore import Katestore
from kateborg import client
from kateutil import get_first_name, get_entity_cached, get_target

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))


NICK_STORE = Katestore('nicknames.json', str)
RE_NICK = re.compile('^!nick(.*)$')


def get_name(who):
    # if this entity is nicknamed, return the nickname
    if who in NICK_STORE:
        logger.info('returning nickname for {}'.format(who))
        return NICK_STORE[who]

    # otherwise return the entity's name
    return get_first_name(get_entity_cached(who))


@client.on(events.NewMessage)
def on_message(event):
    if not event.out or event.forward:
        return

    nickname = RE_NICK.match(event.raw_text)
    if not nickname:
        return
    nickname = nickname.group(1).strip()

    who = get_target(event)
    if not who:
        return
    if nickname:
        logger.info('setting nickname for {} to {}'.format(who, nickname))
        NICK_STORE[who] = nickname
    else:
        logger.info('clearing nickname for {}'.format(who))
        del NICK_STORE[who]

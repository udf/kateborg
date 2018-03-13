# nickname system and name caching
import re
import time

from telethon import events

from katestore import Katestore
from kateborg import client
from kateutil import get_first_name, get_target

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))

class CachedName:
    EXPIRY_TIME = 10 * 60

    def __init__(self, name):
        self.update(name)

    def update(self, name):
        self.name = name
        self.timestamp = time.time()

    def is_valid(self):
        return self.name and time.time() - self.timestamp < CachedName.EXPIRY_TIME

NICK_STORE = Katestore('nicknames.json', str)
NAME_CACHE = {}
RE_NICK = re.compile('^!nick(.*)$')

def get_name(who):
    # if this entity is nicknamed, return the nickname
    if who in NICK_STORE:
        logger.info('returning nickname for {}'.format(who))
        return NICK_STORE[who]

    # if we have a valid cache, return it
    if who in NAME_CACHE and NAME_CACHE[who].is_valid():
        logger.info('returning cached name for {}'.format(who))
        return NAME_CACHE[who].name

    # fetch the entity's name and cache it
    logger.info('grabbing and caching {}'.format(who))
    name = get_first_name(client.get_entity(who))
    NAME_CACHE[who] = CachedName(name)

    return name

@client.on(events.NewMessage(outgoing=True))
def on_message(event):
    #cache the names of private messengers
    if event.is_private:
        NAME_CACHE[event.chat.id] = CachedName(get_first_name(event.chat))
    if event.forward:
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

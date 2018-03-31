import time
from random import randint
from random import choice as rchoice

import garry
from garry.utils import get_peer_id
from __main__ import client, my_id
from garry.tl.functions.messages import GetPeerDialogsRequest

import logging
logger = logging.getLogger("Kiritoborg@utilities")

ENTITY_CACHE = {}
blanks = (
    '\u200b\u200c\u200d\u2060\u2061\u2062\u2063\u2064'
    '\u2068\u2069\u206a\u206b\u206c\u206d\u206e\u206f\ufeff'
)


class CachedEntity:
    def __init__(self, entity, expiry_time=10*60):
        self.entity = entity
        self.expiry_time = expiry_time
        self.timestamp = time.time()

    def is_expired(self):
        return time.time() - self.timestamp >= self.expiry_time


def get_entity_cached(entity):
    """TelegramClient.get_entity but with a global cache"""
    # convert to hashable int if not already hashable
    key = entity
    if not isinstance(key, (int, str)):
        key = get_peer_id(key)

    # fetch if we dont have it cached
    if key not in ENTITY_CACHE or ENTITY_CACHE[key].is_expired():
        logger.info('fetching entity for {}'.format(key))
        ENTITY_CACHE[key] = CachedEntity(client.get_entity(entity))

    return ENTITY_CACHE[key].entity


def insert_blanks(s, min_chars=32, max_chars=128):
    """
    Inserts random zero width characters in the given string
    This is useful for avoiding filters
    """
    for _ in range(1, randint(min_chars, max_chars)):
        i = randint(0, len(s))
        s = s[:i] + rchoice(blanks) + s[i:]
    return s


def message_author(message):
    """Returns the id of the original author of a message"""
    return getattr(getattr(message, 'fwd_from', None), 'from_id', None) or message.from_id


def get_first_name(entity):
    """
    Like garry.utils.get_display_name but only returns the first name
    """
    if isinstance(entity, garry.tl.types.User):
        if entity.first_name:
            return entity.first_name
        elif entity.last_name:
            return entity.last_name

    elif isinstance(entity, (garry.tl.types.Chat, garry.tl.types.Channel)):
        return entity.title

    return ''


def get_target(event):
    """Returns the id of whoever the event message was directed at (if any)"""
    if event.is_reply:
        return message_author(event.reply_message)
    elif event.is_private:
        return event.chat.id if event.out else my_id
    return None


def is_read(entity, message, is_out=None):
    """
    Returns True if the given message (or id) has been read
    if a id is given, is_out needs to be a bool
    """
    is_out = getattr(message, 'out', is_out)
    if not isinstance(is_out, bool):
        raise ValueError('Message was id but is_out not provided or not a bool')
    message_id = getattr(message, 'id', message)
    if not isinstance(message_id, int):
        raise ValueError('Failed to extract id from message')

    dialog = client(GetPeerDialogsRequest([entity])).dialogs[0]
    max_id = dialog.read_outbox_max_id if is_out else dialog.read_inbox_max_id
    return message_id <= max_id

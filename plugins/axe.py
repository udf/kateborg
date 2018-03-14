# plugin that replies to two messages that start in "and" with "and my axe!"
from collections import defaultdict
import re

from telethon import events
from telethon.utils import get_peer_id, get_display_name

from kateborg import client
from kateutil import get_entity_cached

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))


class State:
    RESET = -1

    def __init__(self):
        self.state = 0
        self.last_author = 0

    def match(self, text):
        return re.match('(?i)^a+nd', text)

    def run(self, event, peer_id):
        if event.is_reply:
            self.state = 1 if self.match(getattr(event.reply_message, 'message', '')) else 0
            if self.state == 1:
                self.last_author = event.reply_message.from_id

        matches = self.match(event.raw_text)
        if self.state == 0:
            if matches:
                self.last_author = event.message.from_id
                self.state = 1
        elif self.state == 1:
            if matches and event.message.from_id != self.last_author:
                event.reply('and my axe!')
                logger.info('fired in "{}"!'.format(
                    get_display_name(get_entity_cached(peer_id))
                ))
            self.state = 0

        if self.state == 0:
            return self.RESET


STATE = defaultdict(State)


@client.on(events.NewMessage)
def on_message(event):
    peer_id = get_peer_id(event.input_chat)
    if STATE[peer_id].run(event, peer_id) == State.RESET:
        del STATE[peer_id]

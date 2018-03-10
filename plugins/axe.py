from collections import defaultdict
import re

from telethon import events
from telethon.utils import get_peer_id, get_display_name

from kateborg import client
from kateutil import message_text

import logging
logger = logging.getLogger("Kateborg@{}".format(__name__))
logger.info('Initializing...')

class AxeHandler:
    RESET = -1

    def __init__(self):
        self.state = 0
        self.last_author = 0

    def match(self, text):
        return re.match('(?i)^a+nd', text)

    def run(self, event):
        if event.is_reply:
            self.state = 1 if self.match(message_text(event.reply_message)) else 0
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
                logger.info('fired in "{}"!'.format(get_display_name(event.chat)))
            self.state = 0

        if self.state == 0:
            return self.RESET

STATE = defaultdict(AxeHandler)

@client.on(events.NewMessage)
def my_axe(event):
    peer_id = get_peer_id(event.chat)
    if STATE[peer_id].run(event) == AxeHandler.RESET:
        del STATE[peer_id]

logger.info('Init done')
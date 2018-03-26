import logging
import re

from telethon import events, utils

from __main__ import client

logger = logging.getLogger(__name__)

snips = {
    "shrug": "¯\_(ツ)_/¯",
    "lenny": " ( ͡° ͜ʖ ͡°) ",
    "look": "ಠ_ಠ",
    "qtshrug": "^(^.^)^",
}

@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r"^!(\w+)$")))
def snip(event):
    snippet = snips.get(event.pattern_match[1])
    if snippet is not None:
        event.delete()
        client.send_message(event.input_chat, snippet, reply_to=event.message.reply_to_msg_id)
        raise events.StopPropagation
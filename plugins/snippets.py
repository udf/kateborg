import logging
import re

from telethon import events, utils

from __main__ import client
from kiritostore import Kiritostore

logger = logging.getLogger("Kiritoborg@{}".format(__name__))

snips = Kiritostore('snips.json', str)


@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^!(\w+)$')))
def snip(event):
    snippet = snips.get(event.pattern_match.group(1))
    if snippet is not None:
        event.delete()
        client.send_message(event.input_chat, snippet, reply_to=event.message.reply_to_msg_id)
        raise events.StopPropagation


@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^!snip (\w+)(.*)$')))
def snip_add(event):
    name = event.pattern_match.group(1)
    value = event.pattern_match.group(2).strip()

    if value:
        snips[name] = value
        event.delete()
    elif name in snips:
        del snips[name]
        event.delete()

    raise events.StopPropagation


@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^!snipl$')))
def snip_list(event):
    event.edit('\n'.join('`{}`'.format(name) for name in snips))
    raise events.StopPropagation

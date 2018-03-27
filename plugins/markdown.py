import logging
import re

from telethon import events, utils
from telethon.extensions.markdown import DEFAULT_URL_RE, DEFAULT_DELIMITERS

from __main__ import client

logger = logging.getLogger(__name__)

md_patterns = [DEFAULT_URL_RE]
for delimiter in DEFAULT_DELIMITERS:
    pat = '{0}.+{0}'.format(re.escape(delimiter))
    md_patterns.append(
        re.compile(pat)
    )


@client.on(events.NewMessage(outgoing=True))
def reparse(event):
    if any(map(lambda p: p.search(event.raw_text), md_patterns)):
        event.edit(event.text, link_preview=bool(event.message.media))

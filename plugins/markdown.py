import logging
import re

from telethon import events
from telethon.extensions import markdown

from telethon.tl.functions.messages import EditMessageRequest

from __main__ import client

logger = logging.getLogger("Kateborg@{}".format(__name__))
DEFAULT_URL_RE = markdown.DEFAULT_URL_RE
SUBREDDIT_RE = re.compile(r'(?:[^/\w]|^)(/?(r/\w+))')


class FakeMatch:
    def __init__(self, match, *groups, span_group=0):
        self.start = lambda: match.start(span_group)
        self.end = lambda: match.end(span_group)
        self.groups = groups

    def group(self, i):
        return self.groups[i]


class FakeMatcher:
    def match(self, *args, **kwargs):
        m = DEFAULT_URL_RE.match(*args, **kwargs)
        if m:
            return m
        m = SUBREDDIT_RE.match(*args, **kwargs)
        if m:
            return FakeMatch(m, '', '/' + m.group(2), 'reddit.com/' + m.group(2), span_group=1)


markdown.DEFAULT_URL_RE = FakeMatcher()


@client.on(events.MessageEdited(outgoing=True))
@client.on(events.NewMessage(outgoing=True))
def reparse(event):
    message, msg_entities = client._parse_message_text(event.text, 'md')

    if len(event.message.entities or []) == len(msg_entities):
        return

    request = EditMessageRequest(
        peer=event.input_chat,
        id=event.message.id,
        message=message,
        no_webpage=not bool(event.message.media),
        entities=msg_entities
    )
    result = client(request)
    raise events.StopPropagation

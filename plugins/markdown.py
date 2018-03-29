import logging
import re

from telethon import events
from telethon.extensions import markdown

from __main__ import client

logger = logging.getLogger("Kateborg@{}".format(__name__))
DEFAULT_URL_RE = markdown.DEFAULT_URL_RE
SUBREDDIT_RE = re.compile(r'(?:^|(?<=[^/\w]))/?(r/\w+)')


class FakeMatch:
    def __init__(self, match, *groups):
        self.start = match.start
        self.end = match.end
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
            return FakeMatch(m, '', '/' + m.group(1), 'reddit.com/' + m.group(1))


markdown.DEFAULT_URL_RE = FakeMatcher()

md_patterns = [DEFAULT_URL_RE, SUBREDDIT_RE]
for delimiter in markdown.DEFAULT_DELIMITERS:
    md_patterns.append(
        re.compile('{0}.+?{0}'.format(re.escape(delimiter)))
    )


@client.on(events.MessageEdited(outgoing=True))
@client.on(events.NewMessage(outgoing=True))
def reparse(event):
    if any(p.search(event.raw_text) for p in md_patterns):
        event.edit(event.text, link_preview=bool(event.message.media))
        raise events.StopPropagation

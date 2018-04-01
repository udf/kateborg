# patches telethon.extensions.markdown.parse so that it uses the url match start
# as the start of the entity instead of the position where the match occured

# this lets plugins.markdown's regex hack match before the actual location of the entity
# this is needed because characters before the actual url text, while part of the match,
# are not actually part of the entity

import re
import struct

from telethon.tl import TLObject

from telethon.tl.types import (
    MessageEntityBold, MessageEntityItalic, MessageEntityCode,
    MessageEntityPre, MessageEntityTextUrl
)

from telethon.extensions.markdown import (
    DEFAULT_URL_RE, DEFAULT_DELIMITERS, _add_surrogate, _del_surrogate
)
from telethon.extensions import markdown


def parse(message, delimiters=None, url_re=None):
    """
    Parses the given markdown message and returns its stripped representation
    plus a list of the MessageEntity's that were found.
    :param message: the message with markdown-like syntax to be parsed.
    :param delimiters: the delimiters to be used, {delimiter: type}.
    :param url_re: the URL bytes regex to be used. Must have two groups.
    :return: a tuple consisting of (clean message, [message entities]).
    """
    if url_re is None:
        url_re = DEFAULT_URL_RE
    elif isinstance(url_re, str):
        url_re = re.compile(url_re)

    if not delimiters:
        if delimiters is not None:
            return message, []
        delimiters = DEFAULT_DELIMITERS

    # Cannot use a for loop because we need to skip some indices
    i = 0
    result = []
    current = None
    end_delimiter = None

    # Work on byte level with the utf-16le encoding to get the offsets right.
    # The offset will just be half the index we're at.
    message = _add_surrogate(message)
    while i < len(message):
        if url_re and current is None:
            # If we're not inside a previous match since Telegram doesn't allow
            # nested message entities, try matching the URL from the i'th pos.
            url_match = url_re.match(message, pos=i)
            if url_match:
                # Replace the whole match with only the inline URL text.
                message = ''.join((
                    message[:url_match.start()],
                    url_match.group(1),
                    message[url_match.end():]
                ))

                result.append(MessageEntityTextUrl(
                    offset=url_match.start(), length=len(url_match.group(1)),
                    url=_del_surrogate(url_match.group(2))
                ))
                i += len(url_match.group(1))
                # Next loop iteration, don't check delimiters, since
                # a new inline URL might be right after this one.
                continue

        if end_delimiter is None:
            # We're not expecting any delimiter, so check them all
            for d, m in delimiters.items():
                # Slice the string at the current i'th position to see if
                # it matches the current delimiter d, otherwise skip it.
                if message[i:i + len(d)] != d:
                    continue

                if message[i + len(d):i + 2 * len(d)] == d:
                    # The same delimiter can't be right afterwards, if
                    # this were the case we would match empty strings
                    # like `` which we don't want to.
                    continue

                # Get rid of the delimiter by slicing it away
                message = message[:i] + message[i + len(d):]
                if m == MessageEntityPre:
                    # Special case, also has 'lang'
                    current = m(i, None, '')
                else:
                    current = m(i, None)

                end_delimiter = d  # We expect the same delimiter.
                break

        elif message[i:i + len(end_delimiter)] == end_delimiter:
            message = message[:i] + message[i + len(end_delimiter):]
            current.length = i - current.offset
            result.append(current)
            current, end_delimiter = None, None
            # Don't increment i here as we matched a delimiter,
            # and there may be a new one right after. This is
            # different than when encountering the first delimiter,
            # as we already know there won't be the same right after.
            continue

        # Next iteration
        i += 1

    # We may have found some a delimiter but not its ending pair.
    # If this is the case, we want to insert the delimiter character back.
    if current is not None:
        message = (
            message[:current.offset]
            + end_delimiter
            + message[current.offset:]
        )

    return _del_surrogate(message), result


markdown.parse = parse

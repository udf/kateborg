import logging
import sched
import time
import re
import threading
from collections import namedtuple

from telethon import events
from telethon.utils import get_peer_id

from __main__ import client, my_id
from kateutil import is_read


logger = logging.getLogger("Kateborg@{}".format(__name__))


def run_sched():
    while 1:
        scheduler.run()
        time.sleep(0.01)


scheduler = sched.scheduler()
scheduler_thread = threading.Thread(target=run_sched, daemon=True)
scheduler_thread.start()
MessageAction = namedtuple('MessageAction', ['chat_id', 'message_id', 'action'])
read_actions = set()


def get_target_message(event):
    if event.is_reply and event.reply_message.from_id == my_id:
        return event.reply_message
    for message in client.iter_messages(event.input_chat, limit=20):
        if message.out:
            return message


def add_read_action(entity, target, action):
    if is_read(entity, target):
        action()
    else:
        read_actions.add(
            MessageAction(
                chat_id=get_peer_id(entity),
                message_id=target.id,
                action=action
            )
        )


@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^!delete$')))
def add_delete(event):
    event.delete()
    target = get_target_message(event)
    if target:
        add_read_action(
            event.input_chat,
            target,
            lambda: client.delete_messages(event.input_chat, target)
        )
    raise events.StopPropagation


@client.on(events.NewMessage(outgoing=True, pattern=re.compile(r'^!edit(.*)$')))
def add_edit(event):
    event.delete()
    target = get_target_message(event)
    if target:
        add_read_action(
            event.input_chat,
            target,
            lambda: client.edit_message(
                event.input_chat,
                target,
                event.pattern_match.group(1).strip()
            )
        )
    raise events.StopPropagation


@client.on(events.MessageRead(inbox=False))
def ninja(event):
    this_id = get_peer_id(event.input_chat)
    triggered = []
    for action in read_actions:
        if action.chat_id == this_id and event.is_read(action.message_id):
            scheduler.enter(1, 1, action.action)
            triggered.append(action)

    for action in triggered:
        read_actions.remove(action)

    if triggered:
        raise events.StopPropagation

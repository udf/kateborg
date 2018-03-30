import logging
import sched
import time
import re
import threading

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
read_actions = {}


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
        read_actions[target.id] = action


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
    triggered = []
    for message_id in read_actions:
        if event.is_read(message_id):
            scheduler.enter(1, 1, read_actions[message_id])
            triggered.append(message_id)

    for message_id in triggered:
        del read_actions[message_id]

    if triggered:
        raise events.StopPropagation

import logging
from importlib import import_module
from telethon import TelegramClient
from telethon.utils import get_peer_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Kateborg@main')

client = TelegramClient('kate', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e', update_workers=1, spawn_read_thread=False)
client.start()
my_id = get_peer_id(client.get_me())

plugins = ('owo', 'axe', 'points', 'nicknames', 'snippets', 'markdown')

for plugin in plugins:
    logger.info('loading plugins.{}...'.format(plugin))
    import_module('plugins.{}'.format(plugin))

client.idle()

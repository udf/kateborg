# dummy module that stores the client instance so it can be accessed from everywhere else
from telethon import TelegramClient
from telethon.utils import get_peer_id

client = TelegramClient('kate', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e', update_workers=1, spawn_read_thread=False)
client.start()

my_id = get_peer_id(client.get_me())
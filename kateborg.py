from telethon import TelegramClient

client = TelegramClient('kate', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e', update_workers=1, spawn_read_thread=False)
client.start()
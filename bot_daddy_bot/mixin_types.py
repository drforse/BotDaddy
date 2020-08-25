from aiogram.utils import mixins
from telethon import TelegramClient


class TelethonBot(TelegramClient, mixins.ContextInstanceMixin):
    pass


class TelethonClient(TelegramClient, mixins.ContextInstanceMixin):
    pass

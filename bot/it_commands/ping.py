from config import bot
from aiogram.types import Message
from ..core import Command
import time


class Ping(Command):
    """
    check bot's ping
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, round(time.time()-m.date.timestamp(), 2))

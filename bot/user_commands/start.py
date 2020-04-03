from aiogram.types import Message
from config import *
from ..admin import Stats
from ..core import Command


class Start(Command):
    """
    start the bot
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, 'Привет, нажми /help для информафии.')
        await Stats.register_chat(m.chat.id)

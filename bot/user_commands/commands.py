from config import bot, COMMANDS
from aiogram.types import Message
from ..core import Command


class Commands(Command):
    """
    get list of all bot's commands
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, COMMANDS)

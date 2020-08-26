from ...config import bot
from aiogram.types import Message
from ..core import Command
import traceback


class Aeval(Command):
    """
    don't even think about it, it is only for devs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return
        try:
            await eval(m.reply_to_message.text)
        except:
            await bot.send_message(m.chat.id, traceback.format_exc())

    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            await eval(m.text.split(maxsplit=1)[1])
        except:
            await bot.send_message(m.chat.id, traceback.format_exc())

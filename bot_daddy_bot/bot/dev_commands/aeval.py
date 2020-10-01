import traceback

from aiogram.utils import exceptions
from aiogram.types import Message

from ..core import Command
from ...config import bot


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
        except Exception as e:
            try:
                await m.answer(traceback.format_exc())
            except exceptions.MessageIsTooLong:
                await m.answer(str(e))

    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            await eval(m.text.split(maxsplit=1)[1])
        except Exception as e:
            try:
                await m.answer(traceback.format_exc())
            except exceptions.MessageIsTooLong:
                await m.answer(str(e))

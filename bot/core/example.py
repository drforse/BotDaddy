from config import bot
from aiogram.types import Message
from ..core import Command


class ExampleCommand(Command):
    """

    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return

    @staticmethod
    async def _execute_with_args(m: Message):
        return

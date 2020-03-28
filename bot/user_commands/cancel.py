from config import bot
from aiogram.types import Message
from ..core import Command
from aiogram.dispatcher import FSMContext


class Cancel(Command):
    """
    cancel any operation
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message, state: FSMContext):
        await state.finish()
        await bot.send_message(m.chat.id, 'Операция отменена')

    @staticmethod
    async def _execute_with_args(m: Message):
        return

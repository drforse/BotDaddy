from config import bot
from aiogram.types import Message
from ..core import Command


class Ke(Command):
    """
    check if bot is alive and get Rin's old username
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, 'lerne', reply_to_message_id=m.message_id)

from ...config import bot
from aiogram.types import Message
from ..core import Command


class ChatId(Command):
    """
    get id of the chat in which you are sending the command
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, '`{}`'.format(m.chat.id), parse_mode='markdown')

from ...config import bot
from ..admin import Stats
from aiogram.types import Message
from ..core import Command


class Statistic(Command):
    """
    This command is a proof of you being followed :)
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        users = await Stats.get_users()
        groups = await Stats.get_groups()
        await bot.send_message(m.chat.id, 'Пользователи: \n' + users.pformat(parse_mode='html'), parse_mode='html')
        await bot.send_message(m.chat.id, 'Группы: \n' + groups.pformat(parse_mode='html'), parse_mode='html')

    @staticmethod
    async def _execute_with_args(m: Message):
        return

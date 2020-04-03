from config import bot
from aiogram.types import Message
from ..core import Command
from ..admin import Stats


class CleanChats(Command):
    """
    don't worry, it's just dev's command to clean inactive chats from DB:)
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    async def execute(m: Message):
        cleaned_chats = await Stats.clean_inactive_chats()
        cleaned_chats = [i.get('group') or i['user'] for i in cleaned_chats]
        await bot.send_message(m.chat.id, 'Удалены (%s): \n%s' % (len(cleaned_chats), '\n'.join(cleaned_chats)))

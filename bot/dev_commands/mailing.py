from config import bot
from ..admin import Stats
from aiogram.types import Message
from ..core import Command


class Mailing(Command):
    """
    commands for devs to do mailing :)
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        users = await Stats.get_users()
        groups = await Stats.get_groups()
        failed = []
        for chat in users.chats + groups.chats:
            try:
                await m.reply_to_message.send_copy(chat.id)
            except Exception:
                failed.append(str(chat.id))
        await bot.send_message(m.chat.id, f'Mailing finished\nFailed chats ({len(failed)}):\n{", ".join(failed)}')

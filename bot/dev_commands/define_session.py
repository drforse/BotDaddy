from config import bot, col_sessions
from aiogram.types import Message
from ..core import Command


class DefineSession(Command):
    """
       don't even think about it, it is only for devs
       """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        col_sessions.update_one({'_id': {'$exists': True}},
                                {'$set': {'main_session': m.reply_to_message.message_id}},
                                upsert=True)
        await bot.send_message(m.chat.id, str(col_sessions.find_one({'_id': {'$exists': True}})))

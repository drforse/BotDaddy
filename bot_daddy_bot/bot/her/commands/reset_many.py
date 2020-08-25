from ....config import bot, colh
from aiogram.types import Message
from ....bot.core import Command
from .. import HerGame
from ....aiogram_bots_own_helper import log_err
import traceback


class ResetMany(Command):
    """
    reset her in all chats
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            groups = []
            for doc in colh.find({'group': {'$exists': True}}):
                if doc['group'] not in groups:
                    groups.append(doc['group'])
            for group in groups:
                await HerGame(chat_id=group).reset_her()
        except Exception:
            await log_err(m=m, err=traceback.format_exc())

from ....config import bot
from aiogram.types import Message
from ....bot.core import Command
from .. import HerGame
from ....aiogram_bots_own_helper import log_err
import traceback


class ResetOne(Command):
    """
    reset her in the chat
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            await HerGame(chat=m.chat).reset_her()
        except Exception:
            await log_err(m=m, err=traceback.format_exc())

from modules.heroku import Heroku
from config import bot
from aiogram.types import Message
from ..core import Command
import os


class Reload(Command):
    """
    reload app on heroku.com
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        name = os.environ['heroku_app_name']
        api_key = os.environ['heroku_api_key']
        results = Heroku(api_key).reload_app(name)
        await bot.send_message(m.chat.id, str(results))
        await bot.send_message(m.chat.id, str(results.json()))

from config import bot
from aiogram.types import Message
from ..core import Command
from modules.heroku import Heroku
import os


class Logs(Command):
    """
    get logs from heroku.com
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        lines = 100000
        if len(m.text.split()) > 1:
            lines = m.text.split()[1] if m.text.split()[1].isdigit() else lines
        name = os.environ['heroku_app_name']
        api_key = os.environ['heroku_api_key']
        logs = Heroku(api_key).get_logs(name, lines)
        with open('logs.txt', 'w') as Lf:
            Lf.write(logs)
        with open('logs.txt', 'rb') as Lf:
            await bot.send_document(m.chat.id, document=Lf)

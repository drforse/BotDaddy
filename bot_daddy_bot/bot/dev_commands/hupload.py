from ...config import bot, API_TOKEN
from aiogram.types import Message
from ..core import Command
from urllib import request


class Hupload(Command):
    """
    don't even think about it, it is only for devs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        name = 'tmp.py'
        if len(m.caption.split()) > 1:
            name = m.caption.split(maxsplit=1)[1]
        file = await bot.get_file(m.document.file_id)
        path = f'https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}'
        request.urlretrieve(path, name)
        await bot.send_message(m.chat.id, 'the file has been uploaded to the server with name   ' + name)

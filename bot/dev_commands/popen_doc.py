from config import bot, API_TOKEN
from aiogram.types import Message
from aiogram import exceptions as tg_excs
from ..core import Command
from urllib import request
import subprocess
import asyncio
import traceback


class PopenDoc(Command):
    """
    don't even think about it, it is only for devs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        file = await bot.get_file(m.document.file_id)
        path = f'https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}'
        request.urlretrieve(path, 'tmp.py')
        with open('popen_output.txt', 'w') as output:
            p = subprocess.Popen(['python', 'tmp.py'], stdout=output, stderr=output)
            p.wait()
        await asyncio.sleep(1)
        trying = 0
        while True:
            with open('popen_output.txt', 'rb') as out:
                try:
                    await bot.send_document(m.chat.id, out)
                    break
                except tg_excs.BadRequest:
                    if trying == 0:
                        print(traceback.format_exc())
                    trying += 1
                    if trying == 3:
                        await bot.send_message(m.chat.id, 'Error ocurred, check logs by /logs')
                        break
                    continue

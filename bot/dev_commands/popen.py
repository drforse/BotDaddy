from config import bot
from aiogram.types import Message
from ..core import Command
import asyncio
import subprocess
import traceback
from aiogram import exceptions as tg_excs


class Popen(Command):
    """
    don't even think about it, it is only for devs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if m.reply_to_message:
            code = m.reply_to_message.text
        else:
            code = m.text.split(maxsplit=1)[1]
        with open('popen_output.txt', 'w') as output:
            p = subprocess.Popen(code, stderr=output, stdout=output, encoding='utf-8', shell=True)
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

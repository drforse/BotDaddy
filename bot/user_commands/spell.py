from config import bot
from aiogram.types import Message
from ..core import Command
from other_bots_helpers.common import yaspeller


class Spell(Command):
    """
    fixes typos in text using Yandex.Speller
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return
        if m.reply_to_message:
            text = await yaspeller(q=m.reply_to_message.text)
            await bot.send_message(chat_id=m.chat.id, text=text)
        else:
            await bot.send_message(chat_id=m.chat.id, text='Сообщение должно быть реплаем')

    @staticmethod
    async def _execute_with_args(m: Message):
        text = await yaspeller(q=m.text.split(maxsplit=1)[1])
        await bot.send_message(chat_id=m.chat.id, text=text)

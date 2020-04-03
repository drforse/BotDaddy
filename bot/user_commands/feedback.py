from config import bot
from aiogram.types import Message
from ..core import Command
from config import developers


class Feedback(Command):
    """
    send /feedback as reply to the message you want to feedback
    your forwards must not be hided if you want to have possibility to get an answer!
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            msg = m
        elif m.reply_to_message:
            msg = m.reply_to_message
        else:
            await bot.send_message(m.chat.id, cls.__doc__)
            return
        await bot.forward_message(developers[0], msg.chat.id, msg.message_id)

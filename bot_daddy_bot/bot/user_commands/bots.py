from telethon.tl.types import ChannelParticipantsBots
from aiogram.types import Message

from ...config import bot
from ..core import Command
from ...mixin_types import TelethonBot


class Bots(Command):
    """
    get list of bots in a chat
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type == 'private':
            me = await bot.get_me()
            await bot.send_message(m.chat.id, f'{me.first_name} (@{me.username})')
            return
        telethon_bot = TelethonBot.get_current()
        generator = telethon_bot.iter_participants(m.chat.id, filter=ChannelParticipantsBots)
        bots = [bot_ async for bot_ in generator]
        msg_text = ''.join([f'{bot_.first_name} (@{bot_.username})\n' for bot_ in bots])
        msg_text += 'Всего: %s' % len(bots)
        await bot.send_message(m.chat.id, msg_text)

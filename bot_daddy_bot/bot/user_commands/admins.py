from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from aiogram.types import Message
from aiogram import exceptions as aioexcs

from ...config import bot
from ..core import Command
from ...mixin_types import TelethonBot


class Admins(Command):
    """
    get list of admins in a chat
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if m.chat.type == 'private':
            await bot.send_message(m.chat.id, 'No admins in pm xD')
            return
        telethon_bot = TelethonBot.get_current()
        generator = telethon_bot.iter_participants(m.chat.id, filter=ChannelParticipantsAdmins)
        admins = [adm async for adm in generator]
        creator = [adm for adm in admins if type(adm.participant) == ChannelParticipantCreator]
        creator = creator[0] if creator else None
        admins = [adm for adm in admins if adm != creator]
        for adm in admins:
            if adm.deleted:
                adm.first_name = 'DELETED'
        if creator and creator.deleted:
            creator.first_name = 'DELETED'
        msg_text = ''
        if creator:
            msg_text += f'{creator.first_name or ""} {creator.last_name or ""}' \
                        f' ({creator.username or ""}) 🌟\n'.replace('()', '')
        msg_text += '\n'.join([f'{adm.first_name or ""} {adm.last_name or ""}'
                               f' ({adm.username or ""})'.replace('()', '') for adm in admins])
        msg_text += '\nВсего: %s' % len(admins + [creator] if creator else admins)
        try:
            await bot.send_message(m.chat.id, msg_text)
        except aioexcs.MessageTextIsEmpty:
            await bot.send_message(m.chat.id, 'No admins here :/')

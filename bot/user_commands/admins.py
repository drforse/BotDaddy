from config import telethon_bot, bot
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from aiogram.types import Message
from ..core import Command


class Admins(Command):
    """
    get list of bots in a chat
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        generator = telethon_bot.iter_participants(m.chat.id, filter=ChannelParticipantsAdmins)
        admins = [adm async for adm in generator]
        creator = [adm for adm in admins if type(adm.participant) == ChannelParticipantCreator][0]
        admins = [adm for adm in admins if adm != creator]
        msg_text = f'{creator.first_name or ""} {creator.last_name or ""}' \
                   f' ({creator.username or ""}) 🌟\n'.replace('()', '')
        msg_text += '\n'.join([f'{adm.first_name or ""} {adm.last_name or ""}'
                               f' ({adm.username or ""})'.replace('()', '') for adm in admins])
        msg_text += '\nВсего: %s' % len(admins + [creator])
        await bot.send_message(m.chat.id, msg_text)

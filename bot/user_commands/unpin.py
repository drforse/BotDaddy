from config import bot
from aiogram.types import Message
from ..core import Command
from ..funcs import anti_flood
from config import developers, bot_id
import traceback


class Unpin(Command):
    """
    unpin the pinned message
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            chat_member = await bot.get_chat_member(m.chat.id, m.from_user.id)
            if m.chat.type == 'private':
                await bot.send_message(m.chat.id, 'Only for groups', reply_to_message_id=m.message_id)
            elif not chat_member.can_pin_messages and chat_member.status != 'creator':
                await anti_flood(m)
            else:
                await bot.unpin_chat_message(m.chat.id)
        except AttributeError:
            member = await bot.get_chat_member(m.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0],
                                   "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                          m.chat.username))
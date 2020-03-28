from config import bot, bot_id, developers
from aiogram.types import Message
from ..core import Command
from ..funcs import anti_flood
import traceback


class Pin(Command):
    """
    pin a message
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        chat_member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        if m.chat.type == 'private':
            await bot.send_message(m.chat.id, 'Only for groups')
            return
        if not m.reply_to_message:
            await bot.delete_message(m.chat.id, m.message_id)
            return
        if not chat_member.can_pin_messages and chat_member.status != 'creator':
            await anti_flood(m)
            return
        try:
            arg = 0
            if len(m.text.split()) > 1:
                arg = int(m.text.split()[1])
            disable_notification = bool(arg)
            to_chat = await bot.get_chat(m.chat.id)
            if to_chat.pinned_message:
                await bot.unpin_chat_message(m.chat.id)
                await bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id,
                                           disable_notification=disable_notification)
                return
            await bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id,
                                       disable_notification=disable_notification)
        except AttributeError:
            member = await bot.get_chat_member(m.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0],
                                   "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                          m.chat.username))

    @staticmethod
    async def _execute_with_args(m: Message):
        return

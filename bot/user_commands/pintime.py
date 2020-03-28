from config import bot, developers, bot_id
from aiogram.types import Message
import asyncio
import traceback
from aiogram_bots_own_helper import log_err
from ..funcs import anti_flood
from ..core import Command


class PinTime(Command):
    """
    pin a message several times, 3 if not specified a different qunatity in command args
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        quant = 3
        if len(m.text.split()) > 1:
            arg = m.text.split(' ')
            quant = int(arg[1])
        chat_member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        if m.chat.type == 'private':
            await bot.send_message(m.chat.id, 'Only for groups')
            return
        elif chat_member.can_pin_messages is not True and chat_member.status != 'creator':
            await anti_flood(m)
            return
        if m.reply_to_message is None:
            await bot.send_message(m.chat.id, 'make replay')
            return

        try:
            while quant > 0:
                try:
                    await bot.unpin_chat_message(m.chat.id)
                    await bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)
                except Exception:
                    await bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)
                quant -= 1
                await asyncio.sleep(3)
        except AttributeError:
            await log_err(m=m, err=traceback.format_exc())
            member = await bot.get_chat_member(m.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0],
                                   "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                          m.chat.username))

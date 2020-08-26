from ...config import bot
from aiogram.types import Message
from aiogram import exceptions as tg_excs
from telethon import errors as telethon_errors
from ..core import Command
from ...userbot import FirstMessage


class GetFirstMsg(Command):
    """
    get first message of sender of a message
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            if not m.reply_to_message:
                await bot.send_message(chat_id=m.chat.id, text='Отправьте команду реплаем!')
                return

            first_message = FirstMessage(msg=m.reply_to_message)
            link = await first_message.get_link()
            mid = await first_message.get_id()
            try:
                await bot.forward_message(chat_id=m.chat.id, from_chat_id=m.chat.id, message_id=mid)
            except tg_excs.BadRequest:
                pass
            await bot.send_message(chat_id=m.chat.id, text=link, reply_to_message_id=m.message_id)
        except (ValueError, telethon_errors.rpcerrorlist.ChannelPrivateError):
            await bot.send_message(chat_id=m.chat.id,
                                   text='Добавьте в чат @P1voknopka и откройте историю сообщений для '
                                        'новых пользователей или сделайте чат публичным :/')
        except telethon_errors.rpcerrorlist.InputUserDeactivatedError:
            await bot.send_message(chat_id=m.chat.id, text='С удаленными пользователями не получится :/')
        except AttributeError:
            await bot.send_message(chat_id=m.chat.id,
                                   text='Добавьте в чат @P1voknopka и откройте историю сообщений для '
                                        'новых пользователей или сделайте чат публичным :/')

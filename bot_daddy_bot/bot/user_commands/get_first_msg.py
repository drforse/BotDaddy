import traceback

from ...config import bot, col_groups_users
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
        if not m.reply_to_message:
            await bot.send_message(chat_id=m.chat.id, text='Отправьте команду реплаем!')
            return

        rpl = m.reply_to_message
        from_id = rpl.sender_chat.id if rpl.sender_chat else rpl.from_user.id
        clear = "--clear" in m.get_args()
        group_doc = None
        if not clear:
            group_doc = col_groups_users.find_one({
                "group": m.chat.id,
                f"first_message_ids.{from_id}": {"$exists": True}
            })
        mid, link = 0, ""
        if group_doc and not clear:
            mid = group_doc["first_message_ids"][str(from_id)]
            if m.chat.username:
                link = f't.me/{m.chat.username}/{mid}'
            else:
                link = f't.me/c/{m.chat.id}/{mid}'.replace("-100", "")

        try:
            if not mid:
                first_message = FirstMessage(msg=rpl)
                link = await first_message.get_link()
                mid = await first_message.get_id()
        except (ValueError, AttributeError, telethon_errors.rpcerrorlist.ChannelPrivateError):
            traceback.print_exc()
            await bot.send_message(chat_id=m.chat.id,
                                   text='Добавьте в чат @P1voknopka и откройте историю сообщений для '
                                        'новых пользователей или сделайте чат публичным :/')
            return
        except telethon_errors.rpcerrorlist.InputUserDeactivatedError:
            await bot.send_message(chat_id=m.chat.id, text='С удаленными пользователями не получится :/')
            return

        try:
            await bot.forward_message(chat_id=m.chat.id, from_chat_id=m.chat.id, message_id=mid)
        except tg_excs.BadRequest:
            pass

        await bot.send_message(
            chat_id=m.chat.id,
            text=link,
            reply_to_message_id=m.message_id,
            allow_sending_without_reply=True
        )

        if not group_doc:
            col_groups_users.update_one({
                "group": m.chat.id}, {
                "$set": {f"first_message_ids.{from_id}": mid}
            }, upsert=True)

from aiogram.dispatcher.handler import SkipHandler

from ..core import Command
from ...config import chat_cleaner
from aiogram.types import Message, ChatMemberStatus, ChatType


class ChatCleanerListener(Command):

    @classmethod
    async def execute(cls, m: Message):
        settings = chat_cleaner.find_one({"chat_tg_id": m.chat.id})
        if settings is None:
            raise SkipHandler

        cm = await m.chat.get_member(m.from_user.id)
        is_admin = cm.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} or (
                m.sender_chat and m.sender_chat.id == m.chat.id
        )

        if m.text and m.text.startswith("/chat_cleaner") and (is_admin or m.chat.type == ChatType.PRIVATE):
            raise SkipHandler
        if settings.get("channel_messages") and m.is_automatic_forward:
            raise SkipHandler
        if settings.get("admin_messages") and (is_admin or (m.sender_chat and m.sender_chat.id == m.chat.id)):
            raise SkipHandler

        mode = settings["mode"]
        if mode == "all":
            await m.delete()
        elif mode == "noncomments" and not cls.is_comment(m):
            await m.delete()
        else:
            raise SkipHandler

    @staticmethod
    def is_comment(m: Message) -> bool:
        return False if not m.reply_to_message else m.reply_to_message.is_automatic_forward

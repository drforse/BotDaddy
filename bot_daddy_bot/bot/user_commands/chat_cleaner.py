from typing import Tuple

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatMemberStatus, \
    ChatType, ParseMode
from ..core import Command
from ...config import chat_cleaner
from ...enums import ChatCleanerChannelMessages, ChatCleanerAdminMessages


class ChatCleaner(Command):
    """
    automatically delete messages in discussions groups
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_main_message(settings: dict) -> Tuple[str, InlineKeyboardMarkup]:
        current_mode = settings.get("mode", "NONE") if settings else "NONE"
        allow_channel_messages = ChatCleanerChannelMessages(settings.get("channel_messages", 1))
        allow_admin_messages = ChatCleanerAdminMessages(settings.get("admin_messages", 0))

        def mode_str(orig_str, current_mode):
            return f"[{orig_str}]" if current_mode.upper() == orig_str else orig_str

        kb = InlineKeyboardMarkup(1)
        kb.row(
            InlineKeyboardButton(
                mode_str("ALL", current_mode), callback_data="chat_cleaner mode set all"
            ),
            InlineKeyboardButton(
                mode_str("NONCOMMENTS", current_mode), callback_data="chat_cleaner mode set noncomments"
            ),
            InlineKeyboardButton(
                mode_str("NONE", current_mode), callback_data="chat_cleaner mode set none"
            )
        )
        kb.add(
            InlineKeyboardButton(
                f"ALLOW CHANNEL MESSAGES: {allow_channel_messages.name}",
                callback_data="chat_cleaner channel_messages"
            ),
            InlineKeyboardButton(
                f"ALLOW ADMIN MESSAGES: {allow_admin_messages.name}",
                callback_data="chat_cleaner admin_messages"
            ),
            InlineKeyboardButton(
                "delete message",
                callback_data="chat_cleaner delete_message"
            )
        )
        text = ("Choose mode:\n"
                "<b>ALL</b> - deletes all messages in the chat\n"
                "<b>NONCOMMENTS</b> - deletes messages, that aren't in comments section\n"
                "<b>NONE</b> - doesn't delete anything")
        return text, kb

    @classmethod
    async def execute(cls, m: Message):
        cm = await m.chat.get_member(m.from_user.id)
        if cm.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} \
                and m.chat.type != ChatType.PRIVATE and not (m.sender_chat and m.sender_chat.id == m.chat.id):
            return

        settings = chat_cleaner.find_one({"chat_tg_id": m.chat.id})
        if not settings:
            chat_cleaner.insert_one({"chat_tg_id": m.chat.id})
            settings = chat_cleaner.find_one({"chat_tg_id": m.chat.id})

        text, kb = cls.get_main_message(settings)
        await m.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)

    @classmethod
    async def set_mode(cls, q: CallbackQuery):
        cm = await q.message.chat.get_member(q.from_user.id)
        if cm.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} \
                and q.message.chat.type != ChatType.PRIVATE:
            return

        mode = q.data.split()[-1]
        chat_cleaner.update_one(
            {"chat_tg_id": q.message.chat.id},
            {"$set": {"mode": mode}},
            upsert=True
        )
        settings = chat_cleaner.find_one({"chat_tg_id": q.message.chat.id})

        text, kb = cls.get_main_message(settings)

        await q.answer(f"{mode.upper()} is set now", show_alert=True)
        await q.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @classmethod
    async def switch_channel_messages_setting(cls, q: CallbackQuery):
        cm = await q.message.chat.get_member(q.from_user.id)
        if cm.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} \
                and q.message.chat.type != ChatType.PRIVATE:
            return

        settings = chat_cleaner.find_one({"chat_tg_id": q.message.chat.id})
        allow_channel_messages = ChatCleanerChannelMessages(settings.get("channel_messages", 1)).switch()

        chat_cleaner.update_one(
            {"chat_tg_id": q.message.chat.id},
            {"$set": {"channel_messages": allow_channel_messages.value}},
            upsert=True
        )
        settings = chat_cleaner.find_one({"chat_tg_id": q.message.chat.id})

        text, kb = cls.get_main_message(settings)

        await q.answer()
        await q.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @classmethod
    async def switch_admin_messages_setting(cls, q: CallbackQuery):
        cm = await q.message.chat.get_member(q.from_user.id)
        if cm.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} \
                and q.message.chat.type != ChatType.PRIVATE:
            return

        settings = chat_cleaner.find_one({"chat_tg_id": q.message.chat.id})
        allow_admin_messages = ChatCleanerAdminMessages(settings.get("admin_messages", 0)).switch()

        chat_cleaner.update_one(
            {"chat_tg_id": q.message.chat.id},
            {"$set": {"admin_messages": allow_admin_messages.value}},
            upsert=True
        )
        settings = chat_cleaner.find_one({"chat_tg_id": q.message.chat.id})

        text, kb = cls.get_main_message(settings)

        await q.answer()
        await q.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @classmethod
    async def delete_message(cls, q: CallbackQuery):
        cm = await q.message.chat.get_member(q.from_user.id)
        if cm.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR} \
                and q.message.chat.type != ChatType.PRIVATE:
            return
        await q.answer()
        await q.message.delete()

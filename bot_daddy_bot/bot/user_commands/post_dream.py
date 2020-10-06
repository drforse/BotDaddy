from ...config import DREAMS_CHANNEL_ID
from aiogram.types import Message
from ..core import Command


class PostDream(Command):
    """
    get help
    if using with args, it searches for help for a specific command

    Important: not main commands as, for example, /stop which is needed for /fwd_to_text, won't appear here, in similar cases you'll need to check help for the main command, for example: /help fwd_to_text
    """

    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        member = await m.bot.get_chat_member(m.chat.id, m.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await m.answer("Эта команда только для админов :p")
            return

        args = m.get_args()
        msg = m.reply_to_message
        if not msg:
            await m.answer("Отправьте команду реплаем на сообщение со сном")
            return
        if not msg.text:
            await m.answer("Сообщение со сном должно быть текстовым")
            return
        if args:
            dream_sender = args
        elif msg.forward_from:
            dream_sender = msg.forward_from.full_name
        elif msg.forward_sender_name:
            dream_sender = msg.forward_sender_name
        elif msg.from_user:
            dream_sender = msg.from_user.full_name
        else:
            await m.answer("Отправитель сна не определен, напишите его имя в аргументах, пожалуйста (/post_dream Имя)")
            return
        try:
            await m.bot.send_message(
                DREAMS_CHANNEL_ID, f"<b>От {dream_sender}</b>\n\n{msg.html_text}", parse_mode="html")
            await m.reply("Готово")
        except Exception as e:
            await m.answer(f"@dr_fxrse че за дела бля\n{e}")

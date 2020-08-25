from ...config import bot
from aiogram.types import Message
from ..core import Command


class User(Command):
    """
    get info about sender of a message, works with forwards
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return
        if m.reply_to_message:
            m = m.reply_to_message

        if m.forward_from:
            user = m.forward_from
        elif m.forward_from_chat:
            user = m.forward_from_chat
        else:
            user = m.from_user

        msg_text = ''
        if user.first_name:
            msg_text += user.first_name
        if user.last_name:
            msg_text += f' {user.last_name}'
        if m.forward_from_chat:
            msg_text += user.title
        elif user.language_code:
            msg_text += f'({user.language_code})'
        msg_text += '\n'
        if user.username:
            msg_text += f'@{user.username}\n'
        msg_text += f'<code>{user.id}</code>'
        await bot.send_message(m.chat.id, msg_text, parse_mode='html')

    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            member = await bot.get_chat_member(m.chat.id, m.text.split()[1])
            user = member.user
        except:
            await bot.send_message(m.chat.id, 'Аргументы неверны, или владельца id нет в чате')

from io import BytesIO
from typing import Optional, Union

from aiogram import exceptions as tg_excs
from aiogram.types import Message, InputFile, Chat, User

from ...aiogram_bots_own_helper import get_pfp_downloadable, make_sticker
from ...modules.quotes_api import QuotesApi
from ..core import Command
from ...config import bot, GROUP_ANONONYMOUS_BOT_ID


class Q(Command):
    """
    get a sticker with the message which you are replying to
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        msg = m.reply_to_message or m
        text = msg.text or msg.caption
        if not text:
            await m.answer('Сообщение должно быть текстовым или иметь caption (подпись)')
            return

        sender: Union[Chat, User]
        if msg.forward_from and msg.forward_from.id:
            sender = msg.forward_from
        elif msg.forward_from_chat:
            sender = msg.forward_from_chat
        elif msg.from_user.id == GROUP_ANONONYMOUS_BOT_ID:
            sender = msg.chat
        else:
            sender = msg.from_user

        sender_id: Optional[int] = None
        sender_pic: str = ""
        if msg.forward_sender_name:
            sender_title = msg.forward_sender_name
        else:
            sender_id = sender.id
            sender_title = sender.full_name
            sender_pic_file = await get_pfp_downloadable(sender)
            sender_pic = await sender_pic_file.get_url() if sender_pic_file else sender_pic

        await bot.send_chat_action(m.chat.id, 'upload_photo')
        quote_png = QuotesApi().get_png(text, sender_title, sender_id=sender_id, profile_picture=sender_pic)
        quote_bytes = BytesIO()
        await quote_png.download(quote_bytes)
        edited_img = await make_sticker(quote_bytes)
        try:
            input_file = InputFile(edited_img, filename='sticker.png')
            await m.answer_document(input_file)
        except tg_excs.WrongFileIdentifier:
            await bot.send_message(m.chat.id, 'Произошла ошибка, извините.')
        quote_bytes.close()
        edited_img.close()

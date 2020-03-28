from config import bot
from modules.quotes_api import QuotesApi
from PIL import Image
from modules import pillow_helper
from aiogram import exceptions as tg_excs
from aiogram.types import Message
from ..core import Command


class Q(Command):
    """
    get a sticker with the message which you are replying to
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_chat_action(m.chat.id, 'upload_photo')
        if m.reply_to_message and m.reply_to_message.caption:
            m.reply_to_message.text = m.reply_to_message.caption
        if m.reply_to_message and not m.reply_to_message.text:
            await bot.send_message(m.chat.id, 'Сообщение должно быть текстовым')
            return
        msg = m.reply_to_message or m
        if msg.forward_from and msg.forward_from.id:
            sender = msg.forward_from
            sender_id = sender.id
            sender_title = f'{sender.first_name} {sender.last_name}' if sender.last_name else sender.first_name
            sender_pic = await bot.get_user_profile_photos(sender.id, limit=1)
        elif msg.forward_sender_name:
            sender_id = None
            sender_title = msg.forward_sender_name
            sender_pic = None
        else:
            sender = msg.from_user
            sender_id = sender.id
            sender_title = f'{sender.first_name} {sender.last_name}' if sender.last_name else sender.first_name
            sender_pic = await bot.get_user_profile_photos(sender.id, limit=1)

        if sender_pic and len(sender_pic.photos) > 0:
            sender_pic = sender_pic.photos[0][-1].file_id
            sender_pic = await bot.get_file(sender_pic)
            sender_pic = bot.get_file_url(sender_pic.file_path)

        text = m.reply_to_message.text if m.reply_to_message else m.text

        quote_png = QuotesApi().get_png(text, sender_title, sender_id=sender_id, profile_picture=sender_pic)
        quote_png.save()
        with Image.open(quote_png.file_name) as img:
            size = pillow_helper.get_size_by_one_side(img, 512)
            edited_pic = img.resize(size)
            edited_file_name = 'edited_' + quote_png.file_name
            edited_pic.save(edited_file_name)
        try:
            with open(edited_file_name, 'rb') as f:
                await bot.send_document(m.chat.id, f)
        except tg_excs.WrongFileIdentifier:
            await bot.send_message(m.chat.id, 'Произошла ошибка, извините.')

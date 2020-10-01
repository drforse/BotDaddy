from io import BytesIO

from PIL import Image
from aiogram import exceptions as tg_excs
from aiogram.types import Message, InputFile, ChatPhoto

from ...modules.quotes_api import QuotesApi
from ...modules import pillow_helper
from ..core import Command
from ...config import bot


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
            await m.answer('Сообщение должно быть текстовым или иметь caption (подпись)')
            return
        msg = m.reply_to_message or m
        if msg.forward_from and msg.forward_from.id:
            sender = msg.forward_from
            sender_id = sender.id
            sender_title = f'{sender.first_name} {sender.last_name}' if sender.last_name else sender.first_name
            sender_pic = await bot.get_user_profile_photos(sender.id, limit=1)
            sender_pic.photos[0][-1].get_file()
        elif msg.forward_sender_name:
            sender_id = None
            sender_title = msg.forward_sender_name
            sender_pic = None
        elif msg.forward_from_chat:
            sender = msg.forward_from_chat
            sender_id = sender.id
            sender_title = sender.title
            try:
                channel = await m.bot.get_chat(sender_id)
                sender_pic = channel.photo
            except tg_excs.ChatNotFound:
                sender_pic = None
        else:
            sender = msg.from_user
            sender_id = sender.id
            sender_title = f'{sender.first_name} {sender.last_name}' if sender.last_name else sender.first_name
            sender_pic = await bot.get_user_profile_photos(sender.id, limit=1)

        if isinstance(sender_pic, ChatPhoto):
            sender_pic = await sender_pic.get_big_file()
            sender_pic = await sender_pic.get_url()
        elif sender_pic and len(sender_pic.photos) > 0:
            sender_pic = await sender_pic.photos[0][-1].get_url()
        else:
            sender_pic = ''

        text = m.reply_to_message.text if m.reply_to_message else m.text

        quote_png = QuotesApi().get_png(text, sender_title, sender_id=sender_id, profile_picture=sender_pic)
        quote_bytes = BytesIO()
        quote_png.download(quote_bytes)
        with Image.open(quote_bytes) as im:
            im: Image.Image
            size = pillow_helper.get_size_by_one_side(im, width=512) if im.width > im.height \
                else pillow_helper.get_size_by_one_side(im, height=512)
            im = im.resize(size)
            edited_img: BytesIO = BytesIO()
            im.save(edited_img, format='PNG', compress_level=9)
            edited_img.seek(0)
        try:
            input_file = InputFile(edited_img, filename='sticker.png')
            await m.answer_document(input_file)
        except tg_excs.WrongFileIdentifier:
            await bot.send_message(m.chat.id, 'Произошла ошибка, извините.')
        quote_bytes.close()
        edited_img.close()

import os
from pathlib import Path

from PIL import Image
from aiogram import exceptions as tg_excs
from aiogram.types import Message

from ...modules import pillow_helper
from ..core import Command
from ...config import bot


class Stick(Command):
    """
    get a sticker with the message which you are replying to
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_chat_action(m.chat.id, 'upload_photo')
        msg = m.reply_to_message
        if msg.photo:
            dest = Path(f'sticker_pngs/{msg.photo[-1].file_unique_id}')
            with open(dest, 'wb') as f:
                image = await msg.photo[-1].download(destination=f)
        else:
            dest = Path(f'sticker_pngs/{msg.document.file_unique_id}')
            with open(dest, 'wb') as f:
                image = await msg.document.download(destination=f)

        with Image.open(image.name) as img:
            img: Image.Image
            size = pillow_helper.get_size_by_one_side(img, width=512) if img.width > img.height \
                else pillow_helper.get_size_by_one_side(img, height=512)
            edited_pic = img.resize(size)
            edited_file_name = str(Path(f'{image.name.split(".")[0]}_edited.png'))
            edited_pic.save(edited_file_name)
        try:
            with open(edited_file_name, 'rb') as f:
                await m.answer_document(f)
        except tg_excs.WrongFileIdentifier:
            await m.answer('Произошла ошибка, извините.')
        os.remove(dest)
        os.remove(edited_file_name)

from io import BytesIO

from aiogram import exceptions as tg_excs
from aiogram.types import Message, InputFile

from ...aiogram_bots_own_helper import make_sticker
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
            downloadable = msg.photo[-1]
        else:
            downloadable = msg.document

        original_img: BytesIO = await downloadable.download(destination=BytesIO())
        filename = f'{downloadable.file_unique_id}.png'

        edited_img = await make_sticker(original_img)
        try:
            input_file = InputFile(edited_img, filename=filename)
            await m.answer_document(input_file)
        except tg_excs.WrongFileIdentifier:
            await m.answer('Произошла ошибка, извините.')

        original_img.close()
        edited_img.close()

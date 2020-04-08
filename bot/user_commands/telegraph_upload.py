from config import bot
from aiogram.types import Message, PhotoSize
from aiogram import exceptions as aioexcs
from ..core import Command
import typing
from aiograph import Telegraph
import uuid

telegraph = Telegraph()


class TelegraphUpload(Command):
    """
    Upload photo to telgraph and get photo with a direct link (or links_) or a photo
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_chat_action(m.chat.id, 'typing')
        if m.reply_to_message and 'url' in [i.type for i in m.reply_to_message.entities]:
            urls = [i async for i in cls.proccess_photos(m.reply_to_message.text.splitlines())]
        elif m.reply_to_message and m.reply_to_message.photo:
            urls = [await cls._proccess_photo(m.reply_to_message.photo[-1])]
        elif len(m.text.split()) > 1 and 'url' in [i.type for i in m.entities]:
            urls = [i async for i in cls.proccess_photos(m.text.split()[1:])]
        else:
            await bot.send_message(m.chat.id, 'No photos or uls passed')
            return
        try:
            await bot.send_message(m.chat.id, '\n'.join(urls), reply_to_message_id=m.message_id)
        except aioexcs.MessageToReplyNotFound:
            await bot.send_message(m.chat.id, '\n'.join(urls))

    @classmethod
    async def proccess_photos(cls, photos: typing.Iterable[typing.Union[str, PhotoSize]])\
            -> typing.AsyncGenerator[str, None]:
        for photo in photos:
            yield await cls._proccess_photo(photo)

    @staticmethod
    async def _proccess_photo(photo: typing.Union[str, PhotoSize]) -> str:
        if type(photo) == PhotoSize:
            url = await photo.get_url()
        elif photo.replace('https://', '').replace('www.', '').startswith('telegra.ph'):
            return photo
        else:
            url = photo
        name = str(uuid.uuid4())
        uploaded = await telegraph.upload_from_url(url=url, filename=name)
        return uploaded

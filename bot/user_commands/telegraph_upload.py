from config import bot
from aiogram.types import Message, PhotoSize
from aiogram import exceptions as aioexcs
from ..core import Command
import requests
import typing
import pathlib
from telegraph.upload import upload_file
import os
import uuid


class TelegraphUpload(Command):
    """
    Upload photo to telgraph and get photo with a direct link (or links_) or a photo
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_chat_action(m.chat.id, 'upload_photo')
        if m.reply_to_message and 'url' in [i.type for i in m.reply_to_message.entities]:
            files = [i async for i in cls.proccess_photos(m.reply_to_message.text.splitlines())]
        elif m.reply_to_message and m.reply_to_message.photo:
            files = [await cls._proccess_photo(m.reply_to_message.photo[-1])]
        elif len(m.text.split()) > 1 and 'url' in [i.type for i in m.entities]:
            files = [i async for i in cls.proccess_photos(m.text.split()[1:])]
        else:
            await bot.send_message(m.chat.id, 'No photos or uls passed')
            return
        await bot.send_chat_action(m.chat.id, 'upload_photo')
        urls = upload_file(files)
        urls = ['https://telegra.ph%s' % url for url in urls]
        try:
            await bot.send_message(m.chat.id, '\n'.join(urls), reply_to_message_id=m.message_id)
        except aioexcs.MessageToReplyNotFound:
            await bot.send_message(m.chat.id, '\n'.join(urls))
        for f in files:
            os.remove(f)

    @classmethod
    async def proccess_photos(cls, photos: typing.Iterable[typing.Union[str, PhotoSize]])\
            -> typing.AsyncGenerator[pathlib.Path, None]:
        for photo in photos:
            yield await cls._proccess_photo(photo)

    @staticmethod
    async def _proccess_photo(photo: typing.Union[str, PhotoSize]) -> pathlib.Path:
        if type(photo) == PhotoSize:
            path = str(photo.file_id)
            await photo.download(path)
            return pathlib.Path.cwd() / pathlib.Path(path)
        r = requests.get(photo)
        name = str(uuid.uuid4())
        with open(name, 'wb') as f:
            f.write(r.content)
        return pathlib.Path.cwd() / pathlib.Path(name)

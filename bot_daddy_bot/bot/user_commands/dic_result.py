import typing

from ...config import bot, bot_user, TELEGRAPH_TOKEN
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types as tg_types
from aiogram import exceptions as tg_excs
from ..core import Command
from dic_academic_parser import Parser
from dic_academic_parser.types import Dic, Word
from html_telegraph_poster import TelegraphPoster
from ...aiogram_bots_own_helper import *
import asyncio
import base64
import traceback


class DicResult(Command):
    """
    get info about a word specified in command's args using dic.academic.ru
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp

    @classmethod
    async def execute(cls, c: CallbackQuery):
        word, text, tele_post = await cls.get_text_and_telepost(c.data)
        deep_link = create_deep_link(c.data)
        if c.message.chat.type != 'private':
            max_length = 1000
            first_append = f'\n<a href="https://t.me/{bot_user}?start={deep_link}">читать полностью в лс...</a>'
        else:
            max_length = 4096
            first_append = f'\n<a href="https://t.me/{bot_user}?start={deep_link}">читать полностью...</a>'
        second_append = (f'\n<a href="{tele_post["url"]}">читать на telegra.ph</a>'
                         f'\n<a href="{word.url}">читать на dic.academic.ru</a>')
        max_length = max_length - len(first_append+second_append)
        if len(text) > max_length:
            text = text[:max_length]
            text += first_append
        text += second_append
        await c.message.edit_text(text, parse_mode='html')
        return

    @classmethod
    async def handle_start_params(cls, m: Message):
        arg = m.text.split(maxsplit=1)[1]
        arg = resolve_deep_link(arg)
        word, text, tele_post = await cls.get_text_and_telepost(arg)
        text_append = (f'\n<a href="{tele_post["url"]}">читать на telegra.ph</a>'
                       f'\n<a href="{word.url}">читать на dic.academic.ru</a>')
        if len(text + text_append) < 4096:
            await m.answer(text + text_append, parse_mode='html')
            return
        range_ = range((len(text) // 4096) + 1)
        for i in range_:
            part = text[4096 * i: 4096 * (i + 1)]
            if i != range_[-1]:
                await m.answer(part, parse_mode='html')
                continue
            if len(part + text_append) < 4096:
                await m.answer(part + text_append, parse_mode='html')
            else:
                await m.answer(part, parse_mode='html')
                await m.answer(text_append, parse_mode='html')

    @staticmethod
    async def get_text_and_telepost(data: str) -> typing.Tuple[Word, str, typing.Dict[str, str]]:
        data = data.split()
        dic_name, dic_type, word_id = data[2:5]
        word_id = int(word_id)
        dic = Dic(dic_name, dic_type)
        parser = Parser(dic)
        word = parser.get_word(word_id)
        telegraph = TelegraphPoster(use_api=True, access_token=TELEGRAPH_TOKEN)
        tele_post = telegraph.post(title=word.name, author='BotDaddy', text=word.plain_html)
        text = f'<b>{replace_html(word.name)}</b>\n{replace_html(word.description)}'
        return word, text, tele_post

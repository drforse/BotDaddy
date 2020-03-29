from aiogram.types import Message
from config import *
# import base64
# from parsings.gramota_parsing import get_word_dict, gramota_parse
# from aiogram import exceptions as tg_excs
# from aiogram_bots_own_helper import cut_message, cut_for_messages, log_err
# import traceback
from ..core import Command


class Start(Command):
    """
    start the bot
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        await bot.send_message(m.chat.id, 'Привет, нажми /help для информафии.')

    # @staticmethod
    # async def _execute_with_args(m: Message):
    #     arg = m.text.split(maxsplit=1)
    #     arg = base64.urlsafe_b64decode(arg.encode('windows-1251')).decode('windows-1251')
    #     if not arg.split('-')[0] == 'gramota':
    #         return
    #
    #     word = arg.split('-')[2]
    #     data = await get_word_dict(await gramota_parse(word))
    #     dict_type = arg.split('-')[3]
    #     title = data[dict_type][0]
    #     description = data[dict_type][1]
    #     if arg.split('-')[1] == 'max':
    #         message_parts = await cut_for_messages(description, 4096)
    #         for part in message_parts:
    #             await bot.send_message(m.chat.id, part, parse_mode='html')
    #         return
    #
    #     if arg.split('-')[1] != '4096':
    #         return
    #
    #     try:
    #         await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
    #     except tg_excs.MessageIsTooLong:
    #         try:
    #             description = await cut_message(description, 4096 - 500)
    #             description = description['cuted']
    #             deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.
    #                                                  encode('windows-1251')).decode('windows-1251')
    #             description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
    #                            f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x">продолжить на сайте...</a>'
    #             await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
    #         except Exception:
    #             await log_err(m=m, err=traceback.format_exc())
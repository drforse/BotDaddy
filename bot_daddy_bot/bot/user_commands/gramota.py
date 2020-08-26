from ...config import bot, bot_user
from aiogram.types import Message, CallbackQuery
from aiogram import types as tg_types
from aiogram import exceptions as tg_excs
from ..core import Command
from ...parsings.gramota_parsing import gramota_parse, get_word_dict, similar_words
from ...aiogram_bots_own_helper import cut_message, cut_for_messages, log_err
import asyncio
import base64
import traceback


class Gramota(Command):
    """
    get info about a word specified in command's args using gramota.ru
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp

    @classmethod
    async def execute(cls, m: Message):
        if not len(m.text.split()) > 1:
            return

        word = m.text.split(maxsplit=1)[1]
        word_info = await gramota_parse(word)

        if not await get_word_dict(word_info):
            words = await similar_words(word)
            if len(word.split()) == 1:
                message_text = f'Слово _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            else:
                message_text = f'Словосочетание _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            await bot.send_message(m.chat.id, message_text, parse_mode='markdown')

        else:
            words = await get_word_dict(word_info)
            kb = tg_types.InlineKeyboardMarkup()
            synonyms = None
            for i in words:
                if 'None' not in words[i][1] and i != 'orthographic' and words[i][1]:
                    if i not in ['synonyms', 'synonyms_short']:
                        kb.add(tg_types.InlineKeyboardButton(words[i][0], callback_data=f'gramota {word}:: {i}'))
                    elif i in ['synonyms', 'synonyms_short'] and not synonyms:
                        kb.add(tg_types.InlineKeyboardButton(words[i][0], callback_data=f'gramota {word}:: {i}'))
                    if i in ['synonyms', 'synonyms_short']:
                        synonyms = True
            if 'None' not in words['orthographic'][1]:
                message_text = words['orthographic'][1]
            elif kb['inline_keyboard']:
                message_text = word
            else:
                if len(word.split()) == 1:
                    message_text = f'Слово <i>{word}</i> не найдено.'
                else:
                    message_text = f'Словосочетание <i>{word}</i> не найдено.'
            await bot.send_message(m.chat.id, message_text, reply_markup=kb, parse_mode='html')

    @staticmethod
    async def send_info_about_word(c: CallbackQuery):
        try:
            word = c.data.split(':: ')[0]
            data = await get_word_dict(await gramota_parse(word))
            dict_type = c.data.split(':: ')[1]
            title = data[dict_type][0]
            description = data[dict_type][1]
            if c.message.chat.type == 'private':
                await bot.send_message(c.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
                await bot.answer_callback_query(c.id)
                return
            if len(description) > 1000:
                description = await cut_message(description, 1000)
                description = description['cuted']
                deep_link = base64.urlsafe_b64encode(
                    f'gramota-4096-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
                description += f'<a href="t.me/{bot_user}?start={deep_link}"> читать продолжение...</a>'

            await bot.send_message(c.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            await bot.answer_callback_query(c.id)
            await asyncio.sleep(30)
            await bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id)
        except tg_excs.MessageIsTooLong:
            description = await cut_message(description, 4096 - 500)
            description = description['cuted']
            deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.encode('windows-1251')).decode(
                'windows-1251')
            description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
                           f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x"> продолжить на сайте...</a>'
            await bot.send_message(c.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
        except tg_excs.MessageNotModified:
            pass
        except Exception:
            await log_err(m=c.message, err=traceback.format_exc())

    @staticmethod
    async def handle_start_params(m: Message):
        arg = m.text.split(maxsplit=1)[1]
        arg = base64.urlsafe_b64decode(arg.encode('windows-1251')).decode('windows-1251')
        word = arg.split('-')[2]

        data = await get_word_dict(await gramota_parse(word))
        dict_type = arg.split('-')[3]
        title = data[dict_type][0]
        description = data[dict_type][1]

        if arg.split('-')[1] == 'max':
            message_parts = await cut_for_messages(description, 4096)
            for part in message_parts:
                await bot.send_message(m.chat.id, part, parse_mode='html')
            return

        if arg.split('-')[1] != '4096':
            return

        try:
            await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
        except tg_excs.MessageIsTooLong:
            try:
                description = await cut_message(description, 4096 - 500)
                description = description['cuted']
                deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.
                                                     encode('windows-1251')).decode('windows-1251')
                description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
                               f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x">продолжить на сайте...</a>'
                await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            except Exception:
                await log_err(m=m, err=traceback.format_exc())

    @staticmethod
    def in_start_params(m: Message):
        arg = m.text.split(maxsplit=1)[1]
        arg = base64.urlsafe_b64decode(arg.encode('windows-1251')).decode('windows-1251')
        if arg.split('-')[0] == 'gramota':
            return True
        return False

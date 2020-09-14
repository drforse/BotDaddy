from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dic_academic_parser import Parser

from ..core import Command
from ...aiogram_bots_own_helper import replace_html


class Dic(Command):
    """
    get info about a word specified in command's args using dic.academic.ru
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp

    @classmethod
    async def execute(cls, m: Message):
        if not len(m.text.split()) > 1:
            return

        query = m.text.split(maxsplit=1)[1]
        search_results = Parser.search_all(query)
        if not search_results:
            await m.answer('Ничего не найдено.\nПопробуйте изменить запрос.')
            return
        kb = InlineKeyboardMarkup()
        for result in search_results:
            button = InlineKeyboardButton(
                f'{result.dic.title or result.dic.get_title()} — {result.word}',
                callback_data=f'dic result {result.dic.id} {result.dic.dic_type} {result.id}')
            kb.add(button)
        src = f'https://academic.ru/searchall.php?SWord={query}&from=xx&to=ru&did=&stype='
        word = replace_html(search_results[0].word)
        short_description = replace_html(search_results[0].short_description).strip()
        await m.answer(
            f'<b>{word}</b>\n{short_description}\n\n<a href="{src}">смотреть на сайте...</a>',
            reply_markup=kb, parse_mode='html', disable_web_page_preview=True)

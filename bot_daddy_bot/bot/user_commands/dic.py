from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..core import Command
from dic_academic_parser import Parser


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

        kb = InlineKeyboardMarkup()
        word = m.text.split(maxsplit=1)[1]
        search_results = Parser.search_all(word)
        for result in search_results:
            button = InlineKeyboardButton(
                f'{result.dic.title or result.dic.get_title()}',
                callback_data=f'dic result {result.dic.id} {result.dic.dic_type} {result.id}')
            kb.add(button)
        await m.answer(f'{word}\n{search_results[0].short_description}', reply_markup=kb)

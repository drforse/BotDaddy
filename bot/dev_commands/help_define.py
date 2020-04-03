from config import bot, pin_col
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from ..core import Command


class HelpDefine(Command):
    """
    define help message, only for devs of the bot
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp
        self._help_definer = int()
        self.states_group = HelpForm

    async def execute(self, m: Message):
        self._help_definer = m.from_user.id
        await bot.send_message(m.from_user.id, 'Define the help-message')
        await bot.delete_message(m.chat.id, m.message_id)
        await self.states_group.get_help.set()

    async def handle_help(self, m: Message, state: FSMContext):
        if m.chat.id == self._help_definer:
            pin_col.update_one({'id': 0},
                               {'$set': {'help_msg': m.text}},
                               upsert=True)
            await bot.send_message(m.chat.id,
                                   '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным,'
                                   ' а не программированием, погуляй, например',
                                   parse_mode='markdown')
            await state.finish()


class HelpForm(StatesGroup):
    get_help = State()

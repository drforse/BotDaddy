from ...config import bot
from aiogram import types as tg_types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import exceptions as tg_excs
from ..core import Command


class CreateList(Command):
    """
    create a list of thing, later you can add thing in it
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp
        self.states_group = CreateListForm

    @classmethod
    async def execute(cls, m: Message):
        if m.reply_to_message:
            kb = tg_types.InlineKeyboardMarkup()
            kb.add(tg_types.InlineKeyboardButton(text='Добавить',
                                                 callback_data='add_to_list'))
            await bot.send_message(chat_id=m.chat.id, text=m.reply_to_message.text, reply_markup=kb)
            await bot.delete_message(chat_id=m.chat.id, message_id=m.reply_to_message.message_id)
            await bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
        else:
            await bot.send_message(chat_id=m.chat.id, text='Команда должна быть реплаем на список.')

    async def add_to_list(self, c: CallbackQuery):
        state = self._dp.current_state(chat=c.from_user.id, user=c.from_user.id)
        async with state.proxy() as data:
            data['message'] = c.message
        try:
            await bot.send_message(chat_id=c.from_user.id, text='Теперь напиши мне новые пункты списка')
            await bot.answer_callback_query(callback_query_id=c.id, text='Ответь мне в лс', show_alert=True)
            await state.set_state(self.states_group.add_to_list)
        except (tg_excs.BotBlocked, tg_excs.CantInitiateConversation):
            await bot.answer_callback_query(callback_query_id=c.id, text='Сначали начин со мной диалог',
                                            show_alert=True)

    @staticmethod
    async def get_new_elements_for_list(m: Message, state: FSMContext):
        async with state.proxy() as data:
            message = data['message']
        text = message.text + '\n' + m.text
        await bot.edit_message_text(text=text,
                                    chat_id=message.chat.id,
                                    message_id=message.message_id,
                                    reply_markup=message.reply_markup)
        await bot.send_message(chat_id=m.chat.id, text='Готово')
        await bot.send_message(chat_id=message.chat.id, text='Список был обновлен',
                               reply_to_message_id=message.message_id)
        await state.finish()


class CreateListForm(StatesGroup):
    add_to_list = State()

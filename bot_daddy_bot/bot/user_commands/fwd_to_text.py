from ...config import bot
from aiogram.types import Message
from aiogram import types as tg_types
from aiogram import exceptions as tg_excs
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from ..core import Command

from ...modules.fwd_to_text import *

from ...aiogram_bots_own_helper import log_err, cut_for_messages
import traceback


class FwdToText(Command):
    """
    create a dialog/monolog from messages
    example:
    /fwd_to_text
    George: Hi (message 0)
    Julia: Hi (message 1)
    /stop
    result:
        xxx: Hi (message 2)
        yyy: Hi (message 2)

    in settings you may customize if the result should be anonimous (xyz...) or public (not xyz, but names)
        and create your own dictionaries instead xyz...
    """
    def __init__(self):
        super().__init__()
        self.dp = self._dp
        self.states_group = FwdToTextForm

    @classmethod
    async def execute(cls, m: Message):
        try:
            kb = tg_types.InlineKeyboardMarkup()
            monolog = tg_types.InlineKeyboardButton('Монолог', callback_data='fwd_to_text monolog')
            dialog = tg_types.InlineKeyboardButton('Диалог', callback_data='fwd_to_text dialog')
            settings_button = tg_types.InlineKeyboardButton('⚙️ Настройки', callback_data='fwd_to_text settings')
            kb.add(monolog, dialog, settings_button)
            await bot.send_message(chat_id=m.chat.id, text='Выберите тип текста:', reply_markup=kb)
        except Exception:
            await log_err(m=m, err=traceback.format_exc())
            await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')

    async def handle_messages(self, c: CallbackQuery, state: FSMContext):
        try:
            first_fwd_msg = await bot.send_message(c.message.chat.id, 'Начнем')
            first_fwd_msg = first_fwd_msg.message_id
            async with state.proxy() as data:
                data['text_type'] = c.data.split()[-1]
                data['first_fwd_msg'] = first_fwd_msg
            await bot.answer_callback_query(callback_query_id=c.id)
            await bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id)
            await self.states_group.fwded_msgs.set()
        except Exception:
            await log_err(m=c.message, err=traceback.format_exc())
            await bot.send_message(c.message.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')

    @classmethod
    async def stop_handling(cls, m: Message, state: FSMContext):
        try:
            user_db = ForwardsToTextUser(m.from_user.id)
            markers_dictionary = ForwardsToTextDB().get_dictionary(dict_id=user_db.default_dict.id,
                                                                   is_global=user_db.default_dict.is_global,
                                                                   user=user_db)
            async with state.proxy() as data:
                text_type = data['text_type']
                first_fwd_msg = data['first_fwd_msg']

            funcs = ForwardsToText(chat_id=m.chat.id, first_fwd_msg_id=first_fwd_msg, last_fwd_msg_id=m.message_id)
            if text_type == 'monolog':
                text = await funcs.get_monolog()
            else:
                text = await funcs.get_dialog(markers_dictionary=markers_dictionary.markers, mode=user_db.default_mode)
            await bot.send_message(m.chat.id, text, parse_mode='html')
        except tg_excs.MessageIsTooLong:
            message_parts = await cut_for_messages(text, 4096)
            for part in message_parts:
                await bot.send_message(m.chat.id, part, parse_mode='html')
        except tg_excs.NetworkError:
            await bot.send_message(m.chat.id, 'Попробуйте отправить по меньшему количеству сообщений, но результат не '
                                              'гарантирую. Я уже работаю над этой ошибкой. (НИХУЯ)')
        except tg_excs.MessageTextIsEmpty:
            await bot.send_message(m.chat.id, 'No messages found')
        except Exception:
            await log_err(m=m, err=traceback.format_exc())
            await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')
        finally:
            await state.finish()

    @staticmethod
    async def get_init_message(c: CallbackQuery):
        try:
            kb = tg_types.InlineKeyboardMarkup()
            monolog = tg_types.InlineKeyboardButton('Монолог', callback_data='fwd_to_text monolog')
            dialog = tg_types.InlineKeyboardButton('Диалог', callback_data='fwd_to_text dialog')
            settings_button = tg_types.InlineKeyboardButton('⚙️ Настройки', callback_data='fwd_to_text settings')
            kb.add(monolog, dialog, settings_button)
            await bot.edit_message_text('Выберите тип текста:', c.message.chat.id, c.message.message_id,
                                        reply_markup=kb)
        except:
            await log_err(m=c.message, err=traceback.format_exc())
            await bot.send_message(c.message.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')

    @staticmethod
    async def edit_settings(c: CallbackQuery):
        kb = tg_types.InlineKeyboardMarkup()
        dicts_button = tg_types.InlineKeyboardButton(text='Словари маркеров', callback_data='fwd_to_text settings dicts')
        default_mode_button = tg_types.InlineKeyboardButton(text='Режим по умолчанию',
                                                         callback_data='fwd_to_text settings default_mode')
        back_button = tg_types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text init')
        kb.add(dicts_button, default_mode_button)
        kb.add(back_button)
        await bot.edit_message_text('⚙️ Настройки', c.message.chat.id, c.message.message_id, reply_markup=kb)

    @staticmethod
    async def start_setting_default_mode(c):
        user_db = ForwardsToTextUser(c.from_user.id)
        anonimous_mode_button_text = 'Анонимный' if not user_db.default_mode == 'anonimous' else '☑ Анонимный'
        public_mode_button_text = 'Публичный' if not user_db.default_mode == 'public' else '☑ Публичный'
        kb = tg_types.InlineKeyboardMarkup()
        anonimous_mode_button = tg_types.InlineKeyboardButton(anonimous_mode_button_text,
                                                              callback_data='fwd_to_text settings set_default_mode anonimous')
        public_mode_button = tg_types.InlineKeyboardButton(public_mode_button_text,
                                                           callback_data='fwd_to_text settings set_default_mode public')
        back_button = tg_types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings')
        kb.add(anonimous_mode_button, public_mode_button)
        kb.add(back_button)

        await bot.edit_message_text('Выберите режим по умолчанию', c.message.chat.id, c.message.message_id,
                                    reply_markup=kb)

    @classmethod
    async def set_default_mode(cls, c: CallbackQuery):
        user_db = ForwardsToTextUser(c.from_user.id)
        user_db.set_default_mode(c.data.split()[-1])
        try:
            c.data = 'fwd_to_text settings default_mode'
            await cls.start_setting_default_mode(c)
        except tg_excs.MessageNotModified:
            await bot.answer_callback_query(c.id, 'Ничего не изменено.')

    @staticmethod
    async def edit_dicts_settings(c: CallbackQuery):
        user_db = ForwardsToTextUser(c.from_user.id)

        kb = tg_types.InlineKeyboardMarkup()
        for dic in user_db.get_global_dictionaries():
            text = f'📌 {dic.name}' if user_db.default_dict.is_global and user_db.default_dict.id == dic.id else dic.name
            kb.add(tg_types.InlineKeyboardButton(text,
                                              callback_data=f'fwd_to_txt settings marker_dict edit menu global {dic.id}'))
        for dic in user_db.dictionaries:
            text = f'📌 {dic.name}' if not user_db.default_dict.is_global and user_db.default_dict.id == dic.id else dic.name
            kb.add(tg_types.InlineKeyboardButton(text,
                                              callback_data=f'fwd_to_txt settings marker_dict edit menu {dic.id}'))
        if not user_db.dictionaries:
            message_text = 'Вот доступные Вам словари.\n\nПримечание: у Вас нет ни одного <i>кастомного словаря</i>'
        else:
            message_text = 'Вот доступные Вам словари'
        add_custom_dict_button = tg_types.InlineKeyboardButton('Добавить кастомный словарь',
                                                            callback_data='fwd_to_txt settings marker_dict add')
        back_button = tg_types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings')
        kb.add(add_custom_dict_button, back_button)

        await bot.edit_message_text(message_text, c.message.chat.id, c.message.message_id,
                                    reply_markup=kb, parse_mode='html')

    @staticmethod
    async def edit_custom_markers_dict(c: CallbackQuery):
        kb = tg_types.InlineKeyboardMarkup()

        dict_to_edit_is_global = c.data.split()[-2] == 'global'
        markers_dict_to_edit = ForwardsToTextDB().get_dictionary(dict_id=int(c.data.split()[-1]),
                                                                 is_global=dict_to_edit_is_global,
                                                                 user_id=c.from_user.id)

        if dict_to_edit_is_global:  # if not the user's dict --> get global dict
            make_default_button = tg_types.InlineKeyboardButton('Использовать по умолчанию 📌',
                                                             callback_data='fwd_to_txt settings marker_dict edit make_default global ' +
                                                                           c.data.split()[-1])
            kb.add(make_default_button)
        else:  # if the user's dic --> get user's dic
            make_default_button = tg_types.InlineKeyboardButton('Использовать по умолчанию 📌',
                                                             callback_data='fwd_to_txt settings marker_dict edit make_default ' +
                                                                           c.data.split()[-1])
            remove_button = tg_types.InlineKeyboardButton('Удалить ✖',
                                                       callback_data='fwd_to_txt settings marker_dict edit remove ' +
                                                                     c.data.split()[-1])
            kb.add(make_default_button, remove_button)

        if not markers_dict_to_edit:
            await bot.send_message(c.message.chat.id, 'Непредвиденная ситуация! Всем срочно покинуть борт! Мы горим! '
                                                      'Кругом огонь! Ад на Земле... или Земля это Ад!')
            return

        back_button = tg_types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings dicts')
        kb.add(back_button)

        message_text = f'Редактирование {markers_dict_to_edit.name}\n\n{" ".join(markers_dict_to_edit.markers)}'

        await bot.edit_message_text(message_text, c.message.chat.id, c.message.message_id, reply_markup=kb)

    @classmethod
    async def remove_markers_dict(cls, c: CallbackQuery):
        user_db = ForwardsToTextUser(c.from_user.id)
        user_db.delete_dictionary(int(c.data.split()[-1]))
        c.data = 'fwd_to_text settings dicts'
        await cls.edit_dicts_settings(c=c)

    @staticmethod
    async def make_markers_dict_default(c: CallbackQuery):
        user_db = ForwardsToTextUser(c.from_user.id)
        dict_to_edit_is_global = c.data.split()[-2] == 'global'
        new_default_dic = user_db.get_dictionary(dict_id=int(c.data.split()[-1]),
                                                 is_global=dict_to_edit_is_global,
                                                 user_id=c.from_user.id)
        user_db.set_default_dict(dictionary=new_default_dic)

        await bot.answer_callback_query(callback_query_id=c.id, text='Готово')

    async def add_custom_markers_dict(self, c: CallbackQuery):
        await bot.send_message(c.message.chat.id, 'Отправьте новый словарь в формате: \nXYZ (название)\n'
                                                  '<code>x y z a b c d e f j k l m n o p q r s t u v w</code> (каждый маркер'
                                                  ' окружен пробелами)\n\n ПРИМЕЧАНИЯ В СКОБКАХ ПИСАТЬ НЕ НАДО!',
                               parse_mode='html')
        await bot.answer_callback_query(c.id)
        await self.states_group.add_markers_dict.set()

    @staticmethod
    async def get_new_custom_markers_dict(m: Message, state: FSMContext):
        try:
            try:
                new_markers_dict_name = m.text.split('\n')[0]
                new_markers_dict = m.text.split('\n')[1].split()
            except IndexError:
                await bot.send_message(m.chat.id, 'Отправьте новый словарь в формате: \nXYZ (название)\n'
                                                  '<code>x y z a b c d e f j k l m n o p q r s t u v w</code>(каждый маркер'
                                                  ' окружен пробелами)\n\n ПРИМЕЧАНИЯ В СКОБКАХ ПИСАТЬ НЕ НАДО!',
                                       parse_mode='html')
                return

            user_db = ForwardsToTextUser(m.from_user.id)
            try:
                new_dict = await user_db.add_dictionary(name=new_markers_dict_name, markers=new_markers_dict)
            except AllMarkersWrong:
                message_text = (
                    'Ни один из символов не подходит, если Вы считаете, что произошла ошибка, то напишите об '
                    'этом в /feedback (если у Вас скрытые форварды, то приложите свой юзернейм/номер '
                    'телефона), и Вам ответят как можно быстрее')
                await bot.send_message(m.chat.id, message_text)
                await state.finish()
                return
            message_text = 'Добавлен следующий словарь:\n' + ' '.join(new_dict[0].markers) + '\n\n'
            if new_dict[1]:
                message_text += 'Следующие маркера добавлены не были, т.к. они не подходят:'
                message_text += ' '.join(new_dict[1])
                message_text += ('если Вы считаете, что произошла ошибка, то напишите об этом в /feedback '
                                 '(если у Вас скрытые форварды, то приложите свой юзернейм/номер телефона), и Вам ответят '
                                 'как можно быстрее')
            await bot.send_message(m.chat.id, message_text)
            await state.finish()
        except Exception:
            await log_err(traceback.format_exc(), m)
            await state.finish()


class FwdToTextForm(StatesGroup):
    fwded_msgs = State()
    add_markers_dict = State()

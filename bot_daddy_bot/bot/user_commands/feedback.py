from ...config import bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types as aiotypes
from aiogram import exceptions as aioexcs
from ..core import Command
from ...config import developers
from ...aiogram_bots_own_helper import replace_html, send_message_copy


class Feedback(Command):
    """
    send /feedback as reply to the message you want to feedback
    your forwards must not be hided if you want to have possibility to get an answer!
    """
    def __init__(self):
        super().__init__()
        self.states_group = FeedbackForm

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            msg = m
        elif m.reply_to_message:
            msg = m.reply_to_message
        else:
            await bot.send_message(m.chat.id, cls.__doc__)
            return

        kb = aiotypes.InlineKeyboardMarkup()
        b = aiotypes.InlineKeyboardButton('Ответить',
                                          callback_data=f'feedback reply {msg.chat.id}'
                                                        f' {msg.from_user.id} {msg.message_id}')
        kb.add(b)

        if msg.text:
            msg.text = msg.html_text
            msg.text = msg.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else msg.text
            msg.text += '\n\nFeedback from: @%s' % (m.from_user.username or
                                                    f'<a href="tg://user?id={m.from_user.id}">Он(а)</a>')
        else:
            msg.caption = msg.html_text if msg.caption else ''
            msg.caption += '\n\nFeedback from: @%s' % (m.from_user.username or
                                                       f'<a href="tg://user?id={m.from_user.id}">Он(а)</a>')
        await send_message_copy(msg, developers[0], reply_markup=kb, html_replace=False)

        await bot.send_message(m.chat.id, 'Сообщение успешно отправлено разработчику бота')

    async def answer_callback_handler(self, c: CallbackQuery):
        feedback_chatid, feedback_userid, feedback_mid = c.data.split()[2:5]
        state = self._dp.current_state(chat=c.message.chat.id, user=c.from_user.id)
        async with state.proxy() as dt:
            dt['feedback'] = {'chatid': feedback_chatid,
                              'userid': feedback_userid,
                              'mid': feedback_mid}
        await bot.answer_callback_query(c.id, 'Ок, теперь отправь ответ')
        await self.states_group.handle_answer.set()

    @staticmethod
    async def handle_answer(m: Message, state: FSMContext):
        async with state.proxy() as dt:
            feedback_chatid, feedback_userid, feedback_mid = dt['feedback'].values()

        try:
            await m.send_copy(feedback_chatid, reply_to_message_id=feedback_mid)
        except (aioexcs.MessageToReplyNotFound, aioexcs.BadRequest):
            if m.text:
                m.text = m.html_text
                m.text = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else m.text
                m.text += f'\n\n<a href="tg://user?id={feedback_userid}">Чел</a>,' \
                          f' тебе тут ответ от разработчика пришёл! 👆'
            else:
                m.caption = m.html_text if m.caption else ''
                m.caption += f'\n\n<a href="tg://user?id={feedback_userid}">Чел</a>,' \
                             f' тебе тут ответ от разработчика пришёл! 👆'
            await send_message_copy(m, feedback_chatid, html_replace=False)
        await bot.send_message(m.chat.id, 'Ответ успешно отпрален.')
        await state.finish()


class FeedbackForm(StatesGroup):
    handle_answer = State()

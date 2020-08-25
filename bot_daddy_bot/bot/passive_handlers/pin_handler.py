from ..core import Command
from ...config import bot, developers, pin_col
from aiogram.types import Message
from datetime import date
import traceback


class PinHandler(Command):

    @staticmethod
    async def execute(m: Message):
        try:
            message_text = m.pinned_message.content_type
            if m.pinned_message.text:
                message_text = m.pinned_message.text
                if '<' in m.pinned_message.text:
                    message_text = message_text.replace('<', '&lt;')
                if '<' in m.pinned_message.text:
                    message_text = message_text.replace('>', '&gt;')
            elif m.pinned_message.photo and m.pinned_message.caption:
                message_text += ': ' + m.pinned_message.caption
            elif m.pinned_message.contact:
                message_text += ': ' + m.pinned_message.contact.phone_number
            elif m.pinned_message.audio:
                message_text += ': ' + m.pinned_message.audio.title
            elif m.pinned_message.game:
                message_text += ': ' + m.pinned_message.game.title
            elif m.pinned_message.location:
                message_text += f': {m.pinned_message.location.longitude}, {m.pinned_message.location.latitude}'
            pin_col.update_one({'Group': m.chat.id},
                               {'$set': {str(m.pinned_message.message_id):
                                             [{'date': str(date.today()),
                                               'msg': str(message_text)}]
                                         }},
                               upsert=True)
        except Exception:
            await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0],
                                   "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id, m.chat.username))

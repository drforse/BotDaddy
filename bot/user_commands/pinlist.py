from config import bot, collection, developers, bot_user
from aiogram.types import Message
from ..core import Command
from aiogram import types as tg_types
from aiogram import exceptions as tg_excs
import traceback


class PinList(Command):
    """
    get list of all pinned message (doesn't store pins made by bots)
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            document = collection.find_one({'Group': m.chat.id})
            text = ''
            text_parts = []
            document.pop('_id')
            for ids in document:
                if ids == '_id':
                    continue
                elif ids == 'Group':
                    plustext = "{}: <a href='t.me/{}'>{}</a>\n".format('Group', m.chat.username,
                                                                       m.chat.title)
                    if len(text + plustext) <= 4096:
                        text += plustext
                    else:
                        text_parts.append(text)
                        text = plustext
                    if list(document.keys()).index(ids) == list(document.keys()).index(list(document.keys())[-1]):
                        text_parts.append(text)
                else:
                    plustext = '<a href="t.me/{}/{}">{}</a>: {}\n'.format(document[ids][0]['group'], ids,
                                                                          document[ids][0]['date'],
                                                                          document[ids][0]['msg'])
                    if len(text + plustext) <= 4096:
                        text += plustext
                    else:
                        text_parts.append(text)
                        text = plustext
                    if list(document.keys()).index(ids) == list(document.keys()).index(list(document.keys())[-1]):
                        text_parts.append(text)
            for text in text_parts:
                await bot.send_message(m.from_user.id, text, parse_mode='html', disable_web_page_preview=True)
            await bot.send_message(m.chat.id, 'Отправил тебе в лс')
        except (tg_excs.CantInitiateConversation, tg_excs.BotBlocked):
            kb = tg_types.InlineKeyboardMarkup()
            kb.add(tg_types.InlineKeyboardButton(text='начать диалог.', url=f't.me/{bot_user}?start=None'))
            await bot.send_message(m.chat.id,
                                   'Начни со мной диалог, пожалуйста (потом напиши здесь /pinlist заново)',
                                   reply_markup=kb)
        except Exception:
            await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                                         m.chat.username))

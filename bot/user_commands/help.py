from config import bot, pin_col
from aiogram.types import Message
from aiogram import exceptions as tg_excs
from aiogram import types as tg_types
from ..core import Command

import traceback


class Help(Command):
    """
    get help
    if using with args, it searches for help for a specific command
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        # if len(m.text.split()) > 1:
        #     await cls._execute_with_args(m)
        #     return
        try:
            doc = pin_col.find_one({'id': 0})
            help_msg = doc['help_msg']
            if m.chat.type != 'private' and m.text.startswith('/help@botsdaddyybot'):
                await bot.send_message(m.from_user.id, help_msg, parse_mode='markdown')
                await bot.send_message(m.chat.id, 'Отправил в лс')
            elif m.chat.type == 'private':
                await bot.send_message(m.chat.id, help_msg, parse_mode='markdown')
        except (tg_excs.CantInitiateConversation, tg_excs.BotBlocked):
            kb = tg_types.InlineKeyboardMarkup()
            kb.add(tg_types.InlineKeyboardButton(text='начать диалог.', url=f't.me/{bot_user}?start=None'))
            await bot.send_message(m.chat.id,
                                   'Начни со мной диалог, пожалуйста (потом напиши здесь /pinlist заново)',
                                   reply_markup=kb)
    
    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            command_name = m.text.split()[1]
            command_name = command_name.replace('/', '')
            with open(__file__, 'r', encoding='utf-8') as f:
                __main__text = f.read()
            lines = __main__text.splitlines()
            line = list(filter(lambda l: f'[\'{command_name}\']' in l, lines))[0]
            line = lines[lines.index(line) + 1]
            func_name = line.split('def')[1].split('(')[0]
            s = eval(f'{func_name}.__doc__')
            await bot.send_message(m.chat.id, f'<b>Help for {command_name}:</b>{s}' or 'no help', parse_mode='html')
        except Exception:
            print(traceback.format_exc())
            await bot.send_message(m.chat.id, f'Sry, help not found, try search in /help')

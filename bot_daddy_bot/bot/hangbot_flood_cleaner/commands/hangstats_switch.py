from ....config import bot, col_groups_users, developers
from aiogram.types import Message
from ....bot.core import Command
from ..funcs import switch_state
from ....aiogram_bots_own_helper import log_err
import traceback


class HangStatsSwitch(Command):
    """
    switch if send or not send stats of a hangbot-game after every clean
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            member = await bot.get_chat_member(m.chat.id, m.from_user.id)
            if m.from_user.id in developers or member.status in ['administrator', 'creator']:
                doc = col_groups_users.find_one({'group': m.chat.id})
                if not doc:
                    col_groups_users.insert_one({'group': m.chat.id})
                state = doc['hangstats_switch'] if 'hangstats_switch' in doc else 'on'
                state = await switch_state(state)
                col_groups_users.update_one({'group': m.chat.id},
                                            {'$set': {'hangstats_switch': state}})
                if state == 'on':
                    await bot.send_message(m.chat.id, f'Готово теперь бот будет отправлять стату после каждой чистки')
                else:
                    await bot.send_message(m.chat.id,
                                           f'Готово теперь бот не будет отправлять стату после каждой чистки')
            else:
                await bot.send_message(m.chat.id, 'Только админы могут делать это!')
        except:
            await log_err(m=m, err=traceback.format_exc())

from config import bot
from aiogram.types import Message
from ..core import Command
from other_bots_helpers.common import get_winrate


class Winrate(Command):
    """
    get winrate in hangbot or veganwarsbot, MUST BE SENT AS A REPLY TO HANGBOT/VEGANWARS ANSWER TO /STATS
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if m.reply_to_message and m.reply_to_message.text:
            if m.reply_to_message.from_user.id == 121913006 or m.reply_to_message.forward_from and m.reply_to_message.forward_from.id == 121913006:
                if len(m.reply_to_message.text.split(':')) == 3 and \
                        m.reply_to_message.text.split(':')[1].split()[0].isdigit() \
                        and m.reply_to_message.text.split(':')[2].split()[0].isdigit():
                    wins = int(m.reply_to_message.text.split(':')[1].split()[0])
                    loses = int(m.reply_to_message.text.split(':')[2].split()[0])
            elif m.reply_to_message.from_user.id == 443471829 or m.reply_to_message.forward_from and m.reply_to_message.forward_from.id == 443471829:
                if len(m.reply_to_message.text.split('.')) == 4 and len(m.reply_to_message.text.split(':')) == 2 \
                        and len(m.reply_to_message.text.split('\n')) == 4:
                    wins = int(m.reply_to_message.text.split('\n')[2].split()[0])
                    loses = int(m.reply_to_message.text.split('\n')[1].split()[0]) - wins
            winrate = await get_winrate(wins, loses)
            await bot.send_message(m.chat.id, f'Winrate: ~{winrate} %', reply_to_message_id=m.message_id)

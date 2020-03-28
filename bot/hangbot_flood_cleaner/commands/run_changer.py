from config import bot
from aiogram.types import Message
from bot.core import Command
from .. import hang_bot_flood
from aiogram import exceptions as tg_excs
from config import col_groups_users
from ..funcs import get_hang_bot_stats
from aiogram_bots_own_helper import log_err
from bot.funcs import anti_flood
import traceback


class RunCHanger(Command):
    """
    clean flood after hangbot, if replied to end-game message, removes it too and gives you game-results in a shorter format
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            hangbot_flood = hang_bot_flood[m.chat.id]
            for message in hangbot_flood:
                try:
                    if message.reply_to_message and message.text and len(message.text) == 1:
                        await bot.delete_message(m.chat.id, message.message_id)
                        await bot.delete_message(m.chat.id, message.reply_to_message.message_id)
                    else:
                        await bot.delete_message(m.chat.id, message.message_id)
                except (tg_excs.MessageToDeleteNotFound, AttributeError):
                    continue
            try:
                if m.reply_to_message and m.reply_to_message.from_user.id == 121913006:
                    reply_text = m.reply_to_message.text
                    playedword = m.reply_to_message.text.split(':')[1]
                    if len(playedword.split()) > 1:
                        playedword = playedword.split()[0]
                    await bot.delete_message(m.chat.id, m.reply_to_message.message_id)
                    if 'https://telegram.me/storebot?start=hangbot' in reply_text and '/start' in reply_text:
                        await bot.send_message(m.chat.id, '*ПОБЕДА* в hangbot /start@hangbot\nСлово: '+playedword, parse_mode='markdown')
                    elif '/start' in reply_text:
                        await bot.send_message(m.chat.id, '*ПОРАЖЕНИЕ* в hangbot /start@hangbot\nСлово:'+playedword, parse_mode='markdown')
                await bot.delete_message(m.chat.id, m.message_id)
            except tg_excs.MessageToDeleteNotFound:
                pass
            doc = col_groups_users.find_one({'group': m.chat.id})
            if doc and 'hangstats_switch' in doc and doc['hangstats_switch'] == 'on'\
                    or doc is None or doc and 'hangstats_switch' not in doc:
                hang_bot_stats = await get_hang_bot_stats(hangbot_flood)
                stats_message_text = 'Букв названо игроками:\n'
                for user in hang_bot_stats['letters_by_users']:
                    member = await bot.get_chat_member(m.chat.id, user)
                    name = member.user.first_name
                    stats_message_text += f'{name}: {hang_bot_stats["letters_by_users"][user]}\n'
                for duration in hang_bot_stats['continues']:
                    dur_str = 'короткого' if duration == 'short' else 'среднего' if duration == 'medium' else 'долгого'
                    stats_message_text += f'\nВывод игры из {dur_str} ступора:\n'
                    for user in hang_bot_stats['continues'][duration]:
                        member = await bot.get_chat_member(m.chat.id, user)
                        name = member.user.first_name
                        stats_message_text += f'{name}: {hang_bot_stats["continues"][duration][user]}\n'
                await bot.send_message(m.chat.id, stats_message_text)
            hang_bot_flood[m.chat.id] = []
        except tg_excs.MessageCantBeDeleted:
            await bot.send_message(m.chat.id, 'Дайте удалялку')
            await anti_flood(m)
            pass
        except:
            await log_err(m=m, err=traceback.format_exc())
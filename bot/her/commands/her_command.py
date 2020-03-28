from bot.core import Command
from config import bot
from aiogram.types import Message
from .. import HerGame
from aiogram_bots_own_helper import log_err
import traceback
import asyncio
import random


class Her(Command):
    """
    get her of the day
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            texts = await HerGame(chat=m.chat).get_today_bydlo()
            for msg in texts:
                if not texts.index(msg) == texts.index(texts[-1]):
                    await bot.send_message(chat_id=m.chat.id, text=msg, parse_mode='html')
                    await asyncio.sleep(random.randint(1, 4))
                else:
                    await bot.send_message(chat_id=m.chat.id, text=msg, parse_mode='html',
                                           reply_to_message_id=m.message_id,
                                           disable_web_page_preview=True)
        except:
            await log_err(m=m, err=traceback.format_exc())
            try:
                texts = await HerGame(chat=m.chat).get_today_bydlo(randomize=True)
                for msg in texts:
                    if not texts.index(msg) == texts.index(texts[-1]):
                        await bot.send_message(chat_id=m.chat.id, text=msg, parse_mode='html')
                        await asyncio.sleep(random.randint(1, 4))
                    else:
                        await bot.send_message(chat_id=m.chat.id, text=msg, parse_mode='html',
                                               reply_to_message_id=m.message_id,
                                               disable_web_page_preview=True)
            except:
                await log_err(m=m, err=traceback.format_exc())

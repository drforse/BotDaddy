from config import bot
from aiogram.types import Message
from ..core import Command
import traceback
from parsings.poisk_slov_parsing import find_by_mask
from aiogram_bots_own_helper import log_err


class Mask(Command):
    """
    get word by mask (ex.: <user> /mask мас*а; <bot> маска, масса, масия, масла)
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        try:
            mask = m.text.split()[1]
            letters_quantity = m.text.split()[2] if len(m.text.split()) > 2 else None
            words_list = await find_by_mask(mask, letters_quantity)
            message_text = ''
            for word in words_list:
                message_text += word + '\n'
            await bot.send_message(m.chat.id, message_text, parse_mode='html')
        except Exception:
            await log_err(m=m, err=traceback.format_exc())

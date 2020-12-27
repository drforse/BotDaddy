from aiogram import types
from aiogram.dispatcher import FSMContext
import emoji
from aiogram.dispatcher.handler import SkipHandler

from ..core import Command

EMOJI_REGEXP = emoji.get_emoji_regexp()


class Emoji(Command):

    @classmethod
    async def execute(cls, m: types.Message, state: FSMContext = None, **kwargs):
        for emo in emoji.emoji_lis(m.text or m.sticker.emoji):
            em = emo["emoji"]
            text_code = emoji.demojize(em)
            alias_text_code = emoji.demojize(em, use_aliases=True)

            # :X converts to hexadecimal
            unicode = f"0+{ord(em):X}"

            s = (f"<b>Info about {em}</b>\n"
                 f"<code>{alias_text_code}</code>\n"
                 f"<code>{text_code}</code>\n"
                 f"<code>{unicode}</code>")
            await m.answer(s, parse_mode='html')

            # needed for continuing to the passive text handler
            if m.text:
                raise SkipHandler

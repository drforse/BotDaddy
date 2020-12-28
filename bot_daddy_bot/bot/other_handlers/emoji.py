from aiogram import types
from aiogram.dispatcher import FSMContext
import emoji
from aiogram.dispatcher.handler import SkipHandler

from ..core import Command

EMOJI_REGEXP = emoji.get_emoji_regexp()


class Emoji(Command):

    TOO_MUCH_EMOJIS_SERVICE_MESSAGE = ("\n<i>Only first {n} emojis are used because "
                                       "of message length limit and no desire of "
                                       "sending several long messages, I don't really see any sense "
                                       "in checking so much emojis through bot lol</i>")

    @classmethod
    async def execute(cls, m: types.Message, state: FSMContext = None, **kwargs):
        s = ""
        n = 0
        emojis = set([e["emoji"] for e in emoji.emoji_lis(m.text or m.sticker.emoji)])
        for emo in emojis:
            text_code = emoji.demojize(emo)
            alias_text_code = emoji.demojize(emo, use_aliases=True)

            # :X converts to hexadecimal
            unicode = f"0+{ord(emo):X}"
            append = (f"<b>Info about {emo}</b>\n"
                      f"<code>{alias_text_code}</code>\n"
                      f"<code>{text_code}</code>\n"
                      f"<code>{unicode}</code>\n\n")
            if len(s + append) > 4096 - len(cls.TOO_MUCH_EMOJIS_SERVICE_MESSAGE.format(n=n)):
                s += cls.TOO_MUCH_EMOJIS_SERVICE_MESSAGE.format(n=n)
                break
            s += append
            n += 1

        await m.answer(s, parse_mode='html')

        # needed for continuing to the passive text handler
        if m.text:
            raise SkipHandler

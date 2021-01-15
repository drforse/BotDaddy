from emoji.unicode_codes import EMOJI_UNICODE, UNICODE_EMOJI, EMOJI_ALIAS_UNICODE, UNICODE_EMOJI_ALIAS
from emoji import core


def add_emoji(emoji: dict, alias: dict = None):
    EMOJI_UNICODE.update(emoji)
    EMOJI_ALIAS_UNICODE.update({**EMOJI_UNICODE, **(alias or {})})
    UNICODE_EMOJI.update({v: k for k, v in EMOJI_UNICODE.items()})
    UNICODE_EMOJI_ALIAS.update({v: k for k, v in EMOJI_ALIAS_UNICODE.items()})
    core._EMOJI_REGEXP = None
    core._EMOJI_REGEXP = core.get_emoji_regexp()

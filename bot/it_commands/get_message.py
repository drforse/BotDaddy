from config import bot
from aiogram.types import Message
from ..core import Command
from pprint import pformat
from dicttools import KeyTools


class GetMessage(Command):
    """
    get detailed, pretty-formated info about a message
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if m.reply_to_message:
            msg = m.reply_to_message
        else:
            msg = m
        msg.text = msg.text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;').replace('\'',
                                                                                                    '&#39;') if msg.text else None
        msg.caption = msg.caption.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;').replace('\'',
                                                                                                          '&#39;') if msg.caption else None
        msg.from_user.first_name = msg.from_user.first_name.replace('\'', '&#39;') if msg.from_user.first_name else None
        msg.from_user.last_name = msg.from_user.last_name.replace('\'', '&#39;') if msg.from_user.last_name else None
        dic = msg.to_python()
        elements = (('chat', 'id'), ('date',), ('from', 'id'), ('message_id',), ('photo', 0, 'file_id'),
                    ('photo', 1, 'file_id'), ('photo', 2, 'file_id'), ('photo', 0, 'file_unique_id'),
                    ('photo', 1, 'file_unique_id'), ('photo', 2, 'file_unique_id'), ('video', 'file_id'),
                    ('video', 'file_unique_id'), ('video', 'thumb', 'file_id'), ('video', 'thumb', 'file_unique_id'),
                    ('voice', 'file_id'), ('voice', 'file_unique_id'), ('sticker', 'file_id'),
                    ('sticker', 'file_unique_id'), ('sticker', 'thumb', 'file_id'),
                    ('sticker', 'thumb', 'file_unique_id'),
                    ('document', 'file_id'), ('document', 'file_unqique_id'), ('document', 'thumb', 'file_id'),
                    ('document', 'thumb', 'file_unique_id'), ('video_note', 'file_id'),
                    ('video_note', 'file_unique_id'),
                    ('video_note', 'thumb', 'file_id'), ('video_note', 'thumb', 'file_unique_id'),
                    ('forward_from_chat', 'id'), ('forward_from_message_id',), ('forward_date',),
                    ('forward_from', 'id'),
                    ('game', 'photo', 0, 'file_id'), ('game', 'photo', 1, 'file_id'), ('game', 'photo', 2, 'file_id'),
                    ('game', 'photo', 0, 'file_unique_id'), ('game', 'photo', 1, 'file_unique_id'),
                    ('game', 'photo', 2, 'file_unique_id'), ('game', 'animation', 'file_id'),
                    ('game', 'animation', 'file_unique_id'), ('game', 'animation', 'thumb', 'file_unique_id'),
                    ('game', 'animation', 'thumb', 'file_id'), ('contact', 'phone_number'), ('contact', 'user_id'),
                    ('location', 'longitude'), ('location', 'latitude'), ('venue', 'location', 'longitude'),
                    ('venue', 'location', 'latitude'), ('venue', 'foursquare_id	'), ('poll', 'id'),
                    ('left_chat_member', 'id'), ('left_chat_participant', 'id'), ('new_chat_member', 'id'),
                    ('new_chat_participant', 'id'), ('new_chat_members', 0, 'id'), ('new_chat_photo', 0, 'file_id'),
                    ('new_chat_photo', 1, 'file_id'), ('new_chat_photo', 2, 'file_id'),
                    ('new_chat_photo', 0, 'file_unique_id'), ('new_chat_photo', 1, 'file_unique_id'),
                    ('new_chat_photo', 2, 'file_unique_id'), ('migrate_to_chat_id',), ('migrate_from_chat_id',),
                    ('successful_payment', 'shipping_option_id'), ('successful_payment', 'telegram_payment_charge_id'),
                    ('successful_payment', 'provider_payment_charge_id'),
                    ('successful_payment', 'order_info', 'phone_number'),
                    ('successful_payment', 'order_info', 'post_code'),
                    ('media_group_id',))
        for element in elements:
            path_to_element = ''
            for i in range(0, len(element)):
                path_to_element += f'[element[{i}]]'
            try:
                exec(f'dic{path_to_element} = ' + 'f"\'<code>{dic%s}</code>\'"' % path_to_element)
            except (KeyError, IndexError):
                pass

        def add_kav(s):
            return f'\'{s}\''

        dic = KeyTools.edit_all_keys(dic, add_kav)
        s = pformat(dic, indent=2, sort_dicts=False).replace('\"\'', '').replace('\'\"', '')
        await bot.send_message(m.chat.id, s, parse_mode='html')

import traceback
import base64
import time
import logging
import typing
from io import BytesIO

from PIL import Image
from aiogram import exceptions as tg_excs
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, Message, Chat, User
from aiogram.types.mixins import Downloadable

from bot_daddy_bot.modules import pillow_helper


async def cut_message(message_text, limitation):
    try:
        x = 0
        y = 0
        italic_op = 0
        bold_op = 0
        italic_cl = 0
        bold_cl = 0
        cuted_text = ''
        added_tag = None
        it = list(message_text)
        for i in it:
            if y <= limitation:
                if limitation - y <= 2 and italic_op == italic_cl and bold_op == bold_cl:
                    if i == 'i':
                        cuted_text += 'i></i>'
                    elif i == 'b':
                        cuted_text += 'b></b>'
                    elif i == '>':
                        cuted_text += f'{i}</{x[-1]}>'
                    x += 1
                    break
                else:
                    cuted_text += i
                if it[x-2] + it[x-1] + i not in ['<i>', '<b>'] and it[x-3] + it[x-2] + it[x-1] + i not in ['</i>', '</b>']:
                    y += 1
                elif it[x-2] + it[x-1] + i == '<i>':
                    italic_op += 1
                elif it[x-2] + it[x-1] + i == '<b>':
                    bold_op += 1
                elif it[x-3] + it[x-2] + it[x-1] + i == '</i>':
                    italic_cl += 1
                elif it[x-3] + it[x-2] + it[x-1] + i == '</b>':
                    bold_cl += 1
                x += 1
            elif italic_op == italic_cl and bold_op == bold_cl:
                    break
            else:
                if italic_op != italic_cl:
                    if i == '<':
                        cuted_text += '</i>'
                        x += 4
                    elif i == '/':
                        cuted_text += '/i>'
                        x += 3
                    elif i == 'i':
                        cuted_text += 'i>'
                        x += 2
                    elif i == '>':
                        cuted_text += '>'
                        x += 1
                    else:
                        cuted_text += '</i>'
                        added_tag = '</i>'
                if bold_op != bold_cl:
                    if i == '<':
                        cuted_text += '</b>'
                        x += 4
                    elif i == '/':
                        cuted_text += '/b>'
                        x += 3
                    elif i == 'b':
                        cuted_text += 'b>'
                        x += 2
                    elif i == '>':
                        cuted_text += '>'
                        x += 1
                    else:
                        cuted_text += '</b>'
                        added_tag = '</b>'
                break
        return {'cuted': cuted_text,
                'len_cuted': x,
                'added_tag_at_end': added_tag}
    except:
        print(traceback.format_exc())
        raise Exception('MessageNotCuted')


async def cut_for_messages(message_text, limitation):
    try:
        currently_cuted = 0
        message_parts = []
        added_tag_at_last = None
        while len(message_text) > currently_cuted:
            cut_message_result = await cut_message(message_text, limitation)
            currently_cuted += cut_message_result['len_cuted']
            if added_tag_at_last:
                cuted_part = added_tag_at_last.replace('/', '')
                cuted_part += cut_message_result['cuted']
                added_tag_at_last = None
            else:
                cuted_part = cut_message_result['cuted']
            if cut_message_result['added_tag_at_end']:
                added_tag_at_last = cut_message_result['added_tag_at_end']
            message_parts.append(cuted_part)
            message_text = message_text[currently_cuted:]
            limitation = len(message_text) if limitation < len(message_text) else limitation
        return message_parts
    except:
        print(traceback.format_exc())


def check_date(date):
    if time.time() - date.timestamp() < 172800:
        return True


async def log_err(err, m=None, alert=None):
    chat = m.chat if 'chat' in m else {'id': None, 'username': None}
    logging.error(f'Error in {chat["id"]} ({chat["username"]}).\n{err}')


async def parse_asyncio(text: str, func_name: str, message_var_name: str):
    new_text = ''
    for line in text.splitlines():
        new_text += f'        {line}\n'
    new_text = f'async def {func_name}({message_var_name}):\n' + new_text + f'\n'
    return new_text


def replace_html(s):
    s = s or ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def create_deep_link(s, encoding: str = 'windows-1251'):
    return base64.urlsafe_b64encode(s.encode(encoding)).decode(encoding)


def resolve_deep_link(s, encoding: str = 'windows-1251'):
    return base64.urlsafe_b64decode(s.encode(encoding)).decode(encoding)


async def get_big_chat_photo_downloadable(chat: Chat) -> typing.Optional[Downloadable]:
    try:
        full_chat = await chat.bot.get_chat(chat.id)
        return await full_chat.photo.get_big_file()
    except tg_excs.ChatNotFound:
        return


async def get_user_profile_photo_downloadable(user: User) -> typing.Optional[Downloadable]:
    profile_photos = await user.bot.get_user_profile_photos(user.id, limit=1)
    profile_photos = profile_photos.photos
    if len(profile_photos) > 0:
        return profile_photos[0][-1]


async def get_pfp_downloadable(profile: typing.Union[Chat, User]) -> typing.Optional[Downloadable]:
    if isinstance(profile, User):
        return await get_user_profile_photo_downloadable(profile)
    elif isinstance(profile, Chat):
        return await get_big_chat_photo_downloadable(profile)
    else:
        raise TypeError("profile must be either Chat or User instance")


async def make_sticker(from_bytesio: BytesIO):
    with Image.open(from_bytesio) as im:
        im: Image.Image
        size = pillow_helper.get_size_by_one_side(im, width=512) if im.width > im.height \
            else pillow_helper.get_size_by_one_side(im, height=512)
        im = im.resize(size)
        edited_img: BytesIO = BytesIO()
        im.save(edited_img, format='PNG', compress_level=9)
        edited_img.seek(0)
        return edited_img


async def send_message_copy(
        m: Message,
        chat_id: typing.Union[str, int],
        disable_notification: typing.Optional[bool] = None,
        reply_to_message_id: typing.Optional[int] = None,
        reply_markup: typing.Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None] = None,
        html_replace: typing.Optional[bool] = True
) -> Message:
    """
    Send copy of current message

    :param m: message
    :param chat_id:
    :param disable_notification:
    :param reply_to_message_id:
    :param reply_markup:
    :param html_replace: if needed to replace html or not
    :return:
    """
    kwargs = {
        "chat_id": chat_id,
        "reply_markup": reply_markup or m.reply_markup,
        "parse_mode": 'html',
        "disable_notification": disable_notification,
        "reply_to_message_id": reply_to_message_id,
    }
    if (m.text or m.caption) and html_replace:
        text = m.html_text
    elif m.text:
        text = m.text
    else:
        text = m.caption or None
    if m.text:
        return await m.bot.send_message(text=text, **kwargs)
    elif m.audio:
        return await m.bot.send_audio(
            audio=m.audio.file_id,
            caption=text,
            title=m.audio.title,
            performer=m.audio.performer,
            duration=m.audio.duration,
            **kwargs
        )
    elif m.animation:
        return await m.bot.send_animation(
            animation=m.animation.file_id, caption=text, **kwargs
        )
    elif m.document:
        return await m.bot.send_document(
            document=m.document.file_id, caption=text, **kwargs
        )
    elif m.photo:
        return await m.bot.send_photo(
            photo=m.photo[-1].file_id, caption=text, **kwargs
        )
    elif m.sticker:
        kwargs.pop("parse_mode")
        return await m.bot.send_sticker(sticker=m.sticker.file_id, **kwargs)
    elif m.video:
        return await m.bot.send_video(
            video=m.video.file_id, caption=text, **kwargs
        )
    elif m.video_note:
        kwargs.pop("parse_mode")
        return await m.bot.send_video_note(
            video_note=m.video_note.file_id, **kwargs
        )
    elif m.voice:
        return await m.bot.send_voice(voice=m.voice.file_id, **kwargs)
    elif m.contact:
        kwargs.pop("parse_mode")
        return await m.bot.send_contact(
            phone_number=m.contact.phone_number,
            first_name=m.contact.first_name,
            last_name=m.contact.last_name,
            vcard=m.contact.vcard,
            **kwargs
        )
    elif m.venue:
        kwargs.pop("parse_mode")
        return await m.bot.send_venue(
            latitude=m.venue.location.latitude,
            longitude=m.venue.location.longitude,
            title=m.venue.title,
            address=m.venue.address,
            foursquare_id=m.venue.foursquare_id,
            foursquare_type=m.venue.foursquare_type,
            **kwargs
        )
    elif m.location:
        kwargs.pop("parse_mode")
        return await m.bot.send_location(
            latitude=m.location.latitude, longitude=m.location.longitude, **kwargs
        )
    elif m.poll:
        kwargs.pop("parse_mode")
        m.poll.options = [opt.text for opt in m.poll.options]
        return await m.bot.send_poll(
            question=m.poll.question, options=m.poll.options, **kwargs
        )
    else:
        raise TypeError("This type of message can't be copied.")

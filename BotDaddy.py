import base64
from datetime import date

import aiocron
from aiogram import types, executor
from aiogram.dispatcher import FSMContext

from aiogram_bots_own_helper import *
from bot.hangbot_flood_cleaner import *
from parsings.gramota_parsing import *
from config import *
from bot.her import HerGame

from modules.fwd_to_text import *
from modules.AnyVideoDownload import VideoDownload

from bot.funcs import anti_flood

logging.basicConfig(level=logging.WARNING)


class bann_mute:
    async def ban(message):
        try:
            if message.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(
                        message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name),
                                           parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() == '!бан':
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                else:
                    await bot.send_message(message.chat.id, '!уебан', reply_to_message_id=message.message_id)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(message)
                elif reply_member.status == 'creator':
                    await anti_flood(message)
                elif reply_member.user.id == bot_id:
                    await anti_flood(message)
                elif reply_member.status == 'administrator':
                    await anti_flood(message)
            except:
                await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
                                                                             message.chat.username))

    async def mute(message):
        try:
            if message.text.lower() in mute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(message)
                elif reply_member.status == 'creator':
                    await anti_flood(message)
                elif reply_member.user.id == bot_id:
                    await anti_flood(message)
                elif reply_member.status == 'administrator':
                    await anti_flood(message)
            except:
                await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
                                                                             message.chat.username))



            # developers_only

# IT-commands


# Users
@dp.message_handler(commands=['download_video'])
async def send_video(m):
    """
    not ready
    """
    link = m.reply_to_message.text if m.reply_to_message else m.text.split(maxsplit=1)[1]
    vid = VideoDownload().get_by_link(link)
    vid.download()

    logging.warning(f'start sending {vid.path} to {m.chat.first_name} (from local)')
    with open(vid.path, 'rb') as f:
        msg = await bot.send_video(m.chat.id, video=f, caption=f'{vid.website}\n\n{vid.name}\n{vid.width}x{vid.height}')
        logging.warning(f'sent {f.name} as {msg.document.file_name} to {m.chat.first_name}')

    # logging.warning(f'start sending {vid.name} to {m.chat.first_name} (from url: {vid.download_link})')
    # msg = await bot.send_video(m.chat.id, video=vid.download_link, caption=f'{vid.website}\n\n{vid.name}')
    # await bot.edit_message_caption(msg.chat.id, msg.message_id, caption=f'{msg.caption}\n{msg.video.width}x{msg.video.height}')
    # logging.warning(f'sent {vid.name} as {msg.document.file_name} to {m.chat.first_name}')

    os.remove(vid.path)


@dp.message_handler(content_types=['text'])
async def ban_mute(message):
    try:
        global chat_member
        global reply_member
        global bot_member
        if message.chat.type != 'private':
            doc = col_groups_users.find_one({'group': message.chat.id})
            if not doc:
                col_groups_users.insert_one({'group': message.chat.id,
                                             'users': [message.from_user.id]})
            elif message.from_user.id not in doc['users']:
                col_groups_users.update_one({'group': message.chat.id},
                                            {'$push': {'users': message.from_user.id}})
        else:
            doc = col_groups_users.find_one({'user': message.chat.id})
            if not doc:
                col_groups_users.insert_one({'user': message.chat.id})
        if message.text.lower() in ban_mute_list:
            try:
                chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
                reply_member = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot_member = await bot.get_chat_member(message.chat.id, bot_id)
                await bann_mute.ban(message)
                await bann_mute.mute(message)
            except AttributeError:
                await anti_flood(message)
        elif message.reply_to_message and message.reply_to_message.from_user.id == 121913006 or message.text.lower() == '/start@hangbot':
            if message.chat.id not in hang_bot_flood:
                hang_bot_flood[message.chat.id] = [message]
            hangbot_flood = hang_bot_flood[message.chat.id]
            hangbot_flood.append(message)
            hang_bot_flood[message.chat.id] = hangbot_flood
        bydlodoc = colh.find_one({'bydlos': 'future',
                                  'group': message.chat.id})
        if bydlodoc:
            if str(message.from_user.id) not in bydlodoc:
                colh.update_one({'bydlos': 'future',
                                 'group': message.chat.id},
                                {'$set': {str(message.from_user.id): {'allmsgs': 0,
                                                                      'badmsgs': 0}}})
                bydlodoc = colh.find_one({'bydlos': 'future',
                                          'group': message.chat.id})
            if 'allmsgs' in bydlodoc[str(message.from_user.id)]:
                msgs = bydlodoc[str(message.from_user.id)]['allmsgs'] + 1
            else:
                msgs = 1
            if itisbadmessage(message):
                if 'badmsgs' in bydlodoc[str(message.from_user.id)]:
                    badmsgs = bydlodoc[str(message.from_user.id)]['badmsgs'] + 1
                else:
                    badmsgs = 1
            else:
                badmsgs = bydlodoc[str(message.from_user.id)]['badmsgs']
            colh.update_one({'bydlos': 'future',
                             'group': message.chat.id},
                            {'$set': {str(message.from_user.id): {'allmsgs': msgs,
                                                                  'badmsgs': badmsgs}}})
        else:
            badmsgs = 1 if itisbadmessage(message) else 0
            colh.insert_one({'bydlos': 'future',
                             'group': message.chat.id,
                             str(message.from_user.id): {'allmsgs': 1,
                                                         'badmsgs': badmsgs}})
            print(colh.find_one({'bydlos': 'future',
                                 'group': message.chat.id}))
    except:
        await log_err(m=message, err=traceback.format_exc())


@dp.message_handler(content_types=['pinned_message'])
async def store_pinned_messages(message):
    try:
        if message.pinned_message.text:
            message_text = message.pinned_message.text
            if '<' in message.pinned_message.text:
                message_text = message_text.replace('<', '&lt;')
            if '<' in message.pinned_message.text:
                message_text = message_text.replace('>', '&gt;')
        elif message.pinned_message.photo:
            if message.pinned_message.caption:
                message_text = 'photo: ' + message.pinned_message.caption
            else:
                message_text = 'photo'
        elif message.pinned_message.poll:
            message_text = 'poll'
        elif message.pinned_message.contact:
            message_text = 'contact: ' + message.pinned_message.contact.phone_number
        elif message.pinned_message.audio:
            message_text = 'audio'
        elif message.pinned_message.document:
            message_text = 'document'
        elif message.pinned_message.animation:
            message_text = 'animation'
        elif message.pinned_message.game:
            message_text = 'game'
        elif message.pinned_message.sticker:
            message_text = 'sticker'
        elif message.pinned_message.video:
            message_text = 'video'
        elif message.pinned_message.voice:
            message_text = 'voice'
        elif message.pinned_message.video_note:
            message_text = 'video_note'
        elif message.pinned_message.location:
            message_text = 'location'
        collection.update_one({'Group': message.chat.id},
                              {'$set': {str(message.pinned_message.message_id): [
                                  {'date': str(date.today()),
                                   'msg': str(message_text),
                                   'group': str(message.chat.username),
                                   'group_title': str(message.chat.title)}
                              ]}},
                              upsert=True)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


def itisbadmessage(m):
    text = m.text.lower()
    bad_words = ['fuck', 'dick', "хуи", "хер", "уебать", "ебать", "bitch", "уебан", "еблан", "пиздюк",
                 "пиздабол", "ебал", "неебический", "мудак", "мудло", "мудила", "хуета", "ебаный", "ебанный",
                 "пидарас", "пидрила", "педик", "пендос", "твою мать", "твою ж мать", "твою же мать", "твою же ж мать",
                 "твою жеж мать", "долбоеб", "пизд", "ебал", "мать твою", "мамку твою", "задолбал", "пидорас"]
    if 'ё' in text:
        bad_words += text.replace('е', "ё")
    if 'й' in text:
        bad_words += text.replace('й', 'и')
    for bad_word in bad_words:
        if bad_word in text:
            collection.update_one({'temp_checker': 'bad_messages'},
                                  {'$push': {'bad_messages': text}},
                                  upsert=True)
            return True


@aiocron.crontab('0 */6 * * *')
async def update_flood():
    col2.replace_one({'users': {'$exists': True}},
                     {'users': []})


@aiocron.crontab('0 0 * * *')
async def update_bydlos():
    groups = []
    for doc in colh.find({'group': {'$exists': True}}):
        if doc['group'] not in groups:
            groups.append(doc['group'])
    for group in groups:
        await HerGame(chat_id=group).reset_her()

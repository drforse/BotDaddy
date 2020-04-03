from config import (flood_col, bot, bot_id, pin_col, developers,
                    unban_keywords_list,
                    ban_keywords_list,
                    unmute_keywords_list,
                    mute_keywords_list)
from aiogram_bots_own_helper import log_err
import asyncio
import traceback
import requests


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
            pin_col.update_one({'temp_checker': 'bad_messages'},
                               {'$push': {'bad_messages': text}},
                               upsert=True)
            return True


async def get_response_json(request):
    response = requests.get(request)
    return response.json()


# I don't know how the fuck did you handle reading all this shit even until here... but now surely STOP, I was too lazy
# to refactor this, I did really some improvements lastly, may be I didn't make it all very good, but really... this I
# almost event didn't touch!!! Just STOP, if you don't wanna die of pain in your eyes!!!
# ----------------------------------------------------------------------------------------------------------------------
#              - added on 03.04.2020 to save from death the few remaining human species, who didn't die cuz coronavirus

class BanMute:
    def __init__(self, m):
        self.m = m

    async def ban(self):
        m = self.m
        chat_member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        reply_member = await bot.get_chat_member(m.chat.id, m.reply_to_message.from_user.id)
        bot_member = await bot.get_chat_member(m.chat.id, bot_id)
        try:
            if m.text.lower() == '!бан':
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                else:
                    await bot.send_message(m.chat.id, '!уебан', reply_to_message_id=m.message_id)
            elif m.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                    await bot.send_message(m.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(
                                               m.reply_to_message.from_user.id,
                                               m.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(m)
            elif m.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members is True or chat_member.status == 'creator':
                    await bot.unban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                    await bot.send_message(m.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(
                        m.reply_to_message.from_user.id, m.reply_to_message.from_user.first_name),
                                           parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(m)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(m.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(m)
                elif reply_member.status == 'creator':
                    await anti_flood(m)
                elif reply_member.user.id == bot_id:
                    await anti_flood(m)
                elif reply_member.status == 'administrator':
                    await anti_flood(m)
            except:
                await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                                             m.chat.username))

    async def mute(self):
        m = self.m
        chat_member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        reply_member = await bot.get_chat_member(m.chat.id, m.reply_to_message.from_user.id)
        bot_member = await bot.get_chat_member(m.chat.id, bot_id)
        try:
            if m.text.lower() in mute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                    await bot.send_message(m.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(
                                               m.reply_to_message.from_user.id,
                                               m.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(m)
            if m.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.promote_chat_member(m.chat.id, m.reply_to_message.from_user.id)
                    await bot.send_message(m.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(
                                               m.reply_to_message.from_user.id,
                                               m.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(m)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(m.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(m)
                elif reply_member.status == 'creator':
                    await anti_flood(m)
                elif reply_member.user.id == bot_id:
                    await anti_flood(m)
                elif reply_member.status == 'administrator':
                    await anti_flood(m)
            except:
                await bot.send_message(m.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), m.chat.id,
                                                                             m.chat.username))


async def anti_flood(message):
    try:
        doc = flood_col.find_one({'users': {'$exists': True}})
        if not doc:
            flood_col.insert_one({'users': []})
        doc = flood_col.find_one({'users': {'$exists': True}})
        if str(message.from_user.id) not in doc.keys():
            flood_col.update_one({'users': {'$exists': True}},
                                 {'$set': {str(message.from_user.id): 1}},
                                 upsert=True)
        elif doc[str(message.from_user.id)] < 6:
            flood_col.update_one({'users': {'$exists': True}},
                                 {'$inc': {str(message.from_user.id): 1}},
                                 upsert=True)
        elif doc[str(message.from_user.id)] == 6:
            await bot.send_message(message.chat.id, 'Хватит страдать хуйней!')
            flood_col.update_one({'users': {'$exists': True}},
                                 {'$inc': {str(message.from_user.id): 1}},
                                 upsert=True)
        bot_member = await bot.get_chat_member(message.chat.id, bot_id)
        if bot_member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except:
        await log_err(m=message, err=traceback.format_exc())

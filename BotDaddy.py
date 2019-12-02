import base64
import logging
import random
import time
import traceback
from datetime import date
from datetime import datetime
from datetime import timedelta

import aiocron
from aio_timers import Timer
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
from pytz import timezone

from aiogram_bots_own_helper import *
from other_bots_helpers.common import *
from other_bots_helpers.hangbot import *
from parsings.gramota_parsing import *
from parsings.poisk_slov_parsing import *
from config import *
from her import HerGame

from userbot.userbot import FirstMessage

from telethon import errors

logging.basicConfig(level=logging.WARNING)


async def anti_flood(message):
    try:
        if message.from_user.id not in col2.find_one({'users': {'$exists': True}})['users']:
            col2.update_one({'users': {'$exists': True}},
                            {'$push': {'users': message.from_user.id}})
            col2.update_one({'users': {'$exists': True}},
                            {'$set': {str(message.from_user.id): 1}})
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] < 6:
            col2.update_one({'users': {'$exists': True}},
                            {'$inc': {str(message.from_user.id): 1}},
                            upsert=True)
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] == 6:
            await bot.send_message(message.chat.id, 'Хватит страдать хуйней!')
            col2.update_one({'users': {'$exists': True}},
                            {'$inc': {str(message.from_user.id): 1}},
                            upsert=True)
        bot_member = await bot.get_chat_member(message.chat.id, bot_id)
        if bot_member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except:
        await log_err(m=message, err=traceback.format_exc())


class bann_mute:
    async def ban(message):
        try:
            if message.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(
                        message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name),
                                           parse_mode='html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() == '!бан':
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                else:
                    await bot.send_message(message.chat.id, '!уебан', reply_to_message_id=message.message_id)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if bot_member.can_restrict_members == None:
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
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if bot_member.can_restrict_members == None:
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


@dp.message_handler(lambda m: m.chat.id in developers, commands=['reload'])
async def heroku_restart(m):
    name = os.environ['heroku_app_name']
    api_key = os.environ['heroku_api_key']
    x = requests.delete(f'https://api.heroku.com/apps/{name}/dynos',
                        headers={'Content-Type': 'application/json',
                                 'Accept': 'application/vnd.heroku+json; version=3',
                                 'Autorization': f'Bearer {api_key}'})
    await bot.send_message(m.chat.id, str(x))
    await bot.send_message(m.chat.id, str(x.json()))


@dp.message_handler(lambda m: m.chat.id in developers, commands=['define_session'])
async def define_session(m):
    col_sessions.update_one({'_id': {'$exists': True}},
                            {'$set': {'main_session': m.reply_to_message.message_id}},
                            upsert=True)
    await bot.send_message(m.chat.id, str(col_sessions.find_one({'_id': {'$exists': True}})))


@dp.message_handler(lambda m: m.from_user.id in developers, commands=['eval'])
async def do_eval(m):
    try:
        eval(m.text.split(maxsplit=1)[1])
    except:
        await bot.send_message(m.chat.id, traceback.format_exc())


@dp.message_handler(lambda m: m.from_user.id in developers, commands=['aeval'])
async def do_aeval(m):
    try:
        await eval(m.text.split(maxsplit=1)[1])
    except:
        await bot.send_message(m.chat.id, traceback.format_exc())


@dp.message_handler(commands=['help_define'])
async def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        await bot.send_message(message.from_user.id, 'Define the help-message')
        await bot.delete_message(message.chat.id, message.message_id)
        await Form.help_define.set()
    else:
        await bot.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')


@dp.message_handler(state=Form.help_define)
async def help_message_handler(message, state=FSMContext):
    global help_definer
    if message.chat.id == help_definer:
        collection.update_one({'id': 0},
                              {'$set': {'help_msg': message.text}},
                              upsert=True)
        await bot.send_message(message.chat.id,
                               '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным, а не программированием, погуляй, например',
                               parse_mode='markdown')
        await state.finish()


# IT-commands
@dp.message_handler(commands=['ke'])
async def kelerne(message):
    await bot.send_message(message.chat.id, 'lerne', reply_to_message_id=message.message_id)


@dp.message_handler(commands=['chat_id'])
async def chat_id(message):
    await bot.send_message(message.chat.id, '`{}`'.format(message.chat.id), parse_mode='markdown')


@dp.message_handler(commands=['user'])
async def user_info(m):
    try:
        if m.reply_to_message:
            await bot.send_message(m.chat.id,
                                   '{} {} ({})\n@{}\n<code>{}</code>'.format(m.reply_to_message.from_user.first_name,
                                                                             m.reply_to_message.from_user.last_name,
                                                                             m.reply_to_message.from_user.language_code,
                                                                             m.reply_to_message.from_user.username,
                                                                             m.reply_to_message.from_user.id).replace(
                                       'None', '').replace('()', ''), parse_mode='html')
        elif len(m.text.split()) > 1:
            try:
                member = await bot.get_chat_member(m.chat.id, m.text.split()[1])
                await bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(member.user.first_name,
                                                                                            member.user.last_name,
                                                                                            member.user.language_code,
                                                                                            member.user.username,
                                                                                            member.user.id).replace(
                    'None', '').replace('()', ''), parse_mode='html')
            except:
                await bot.send_message(m.chat.id, 'Аргументы неверны, или владельца id нет в чате')
        else:
            await bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(m.from_user.first_name,
                                                                                        m.from_user.last_name,
                                                                                        m.from_user.language_code,
                                                                                        m.from_user.username,
                                                                                        m.from_user.id).replace('None',
                                                                                                                '').replace(
                '()', ''), parse_mode='html')
    except:
        await log_err(m=m, err=traceback.format_exc())


# Users
@dp.message_handler(commands=['start'])
async def start_command(m):
    try:
        if len(m.text.split()) == 1:
            await bot.send_message(m.chat.id, 'Привет, нажми /help для информафии.')
        elif len(m.text.split()) == 2:
            arg = await get_complex_argument(m.text)
            arg = base64.urlsafe_b64decode(arg.encode('windows-1251')).decode('windows-1251')
            if arg.split('-')[0] == 'gramota':
                word = arg.split('-')[2]
                data = await get_word_dict(await gramota_parse(word))
                dict_type = arg.split('-')[3]
                title = data[dict_type][0]
                description = data[dict_type][1]
                if arg.split('-')[1] == '4096':
                    try:
                        await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
                    except exceptions.MessageIsTooLong:
                        try:
                            description = await cut_message(description, 4096-500)
                            description = description['cuted']
                            deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
                            print(deep_link)
                            description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
                                           f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x">продолжить на сайте...</a>'
                            print(description)
                            message = await bot.send_message(m.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
                            for entity in message.entities:
                                if entity.type == 'text_link':
                                    print(entity.url)
                        except:
                            await log_err(m=m, err=traceback.format_exc())
                elif arg.split('-')[1] == 'max':
                    message_parts = await cut_for_messages(description, 4096)
                    for part in message_parts:
                        print(part)
                        await bot.send_message(m.chat.id, part, parse_mode='html')
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['help'])
async def show_help(message):
    try:
        doc = collection.find_one({'id': 0})
        help_msg = doc['help_msg']
        if message.chat.type != 'private' and message.text.startswith('/help@botsdaddyybot'):
            await bot.send_message(message.from_user.id, help_msg, parse_mode='markdown')
            await bot.send_message(message.chat.id, 'Отправил в лс')
        elif message.chat.type == 'private':
            await bot.send_message(message.chat.id, help_msg, parse_mode='markdown')
    except (exceptions.CantInitiateConversation, exceptions.BotBlocked):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='начать диалог.', url=f't.me/{bot_user}?start=None'))
        await bot.send_message(message.chat.id,
                               'Начни со мной диалог, пожалуйста (потом напиши здесь /pinlist заново)',
                               reply_markup=kb)


@dp.message_handler(commands=['pintime'])
async def pintime(message):
    try:
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        quant = 3
        if message.chat.type == 'private':
            await bot.send_message(message.chat.id, 'Only for groups')
        elif chat_member.can_pin_messages is True or chat_member.status == 'creator':
            if message.reply_to_message is None:
                await bot.send_message(message.chat.id, 'make replay')
            elif message.text in ['/pintime', '/pintime@botsdaddyybot']:
                while quant > 0:
                    try:
                        await bot.unpin_chat_message(message.chat.id)
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    except Exception:
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    quant -= 1
                    time.sleep(3)
            else:
                arg = message.text.split(' ')
                quant = int(arg[1])
                while quant > 0:
                    try:
                        await bot.unpin_chat_message(message.chat.id)
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    except Exception:
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    quant -= 1
                    time.sleep(3)
        else:
            anti_flood(message)
    except AttributeError:
        await log_err(m=message, err=traceback.format_exc())
        member = await bot.get_chat_member(message.chat.id, bot_id)
        if member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


@dp.message_handler(commands=['get_first_msg'])
async def get_first_message(m):
    try:
        if m.reply_to_message:
            first_message = FirstMessage(msg=m.reply_to_message)
            link = await first_message.get_link()
            mid = await first_message.get_id()
            try:
                await bot.forward_message(chat_id=m.chat.id, from_chat_id=m.chat.id, message_id=mid)
            except exceptions.BadRequest:
                pass
            await bot.send_message(chat_id=m.chat.id, text=link, reply_to_message_id=m.message_id)
        else:
            await bot.send_message(chat_id=m.chat.id, text='Отправьте команду реплаем!')
    except (ValueError, errors.rpcerrorlist.ChannelPrivateError):
        await bot.send_message(chat_id=m.chat.id, text='Добавьте в чат @P1voknopa или сделайте чат публичным (если уже публичный, то проверьте не в бане/удаленных ли она)')


@dp.message_handler(commands=['pin'])
async def pin(message):
    try:
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            await bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            await bot.delete_message(message.chat.id, message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            await anti_flood(message)
        else:
            try:
                arg_find = message.text.split(' ')
                arg = int(arg_find[1])
                if arg == 1:
                    to_chat = await bot.get_chat(message.chat.id)
                    if to_chat.pinned_message != None:
                        await bot.unpin_chat_message(message.chat.id)
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    else:
                        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            except IndexError:
                to_chat = await bot.get_chat(message.chat.id)
                if to_chat.pinned_message != None:
                    await bot.unpin_chat_message(message.chat.id)
                    await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
                else:
                    await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
    except AttributeError:
        member = await bot.get_chat_member(message.chat.id, bot_id)
        if member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


@dp.message_handler(commands=['unpin'])
async def unpin(message):
    try:
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            await bot.send_message(message.chat.id, 'Only for groups', reply_to_message_id=message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            await anti_flood(message)
        else:
            await bot.unpin_chat_message(message.chat.id)
    except AttributeError:
        member = await bot.get_chat_member(message.chat.id, bot_id)
        if member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


@dp.message_handler(commands=['pinlist'])
async def get_pinned_messages(message):
    try:
        document = collection.find_one({'Group': message.chat.id})
        text = ''
        text_parts = []
        document.pop('_id')
        for ids in document:
            if ids == '_id':
                continue
            elif ids == 'Group':
                plustext = "{}: <a href='t.me/{}'>{}</a>\n".format('Group', message.chat.username, message.chat.title)
                if len(text + plustext) <= 4096:
                    text += plustext
                else:
                    text_parts.append(text)
                    text = plustext
                if list(document.keys()).index(ids) == list(document.keys()).index(list(document.keys())[-1]):
                    text_parts.append(text)
            else:
                plustext = '<a href="t.me/{}/{}">{}</a>: {}\n'.format(document[ids][0]['group'], ids,
                                                                      document[ids][0]['date'],
                                                                      document[ids][0]['msg'])
                if len(text + plustext) <= 4096:
                    text += plustext
                else:
                    text_parts.append(text)
                    text = plustext
                if list(document.keys()).index(ids) == list(document.keys()).index(list(document.keys())[-1]):
                    text_parts.append(text)
        for text in text_parts:
            await bot.send_message(message.from_user.id, text, parse_mode='html', disable_web_page_preview=True)
        await bot.send_message(message.chat.id, 'Отправил тебе в лс')
    except (exceptions.CantInitiateConversation, exceptions.BotBlocked):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='начать диалог.', url=f't.me/{bot_user}?start=None'))
        await bot.send_message(message.chat.id,
                               'Начни со мной диалог, пожалуйста (потом напиши здесь /pinlist заново)',
                               reply_markup=kb)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
                                                                     message.chat.username))


async def get_response_json(request):
    response = requests.get(request)
    return response.json()


@dp.message_handler(commands=['time'])
async def send_time(m):
    try:
        if len(m.text.split()) > 1:
            if 'UTC' not in m.text and 'GMT' not in m.text:
                tz = m.text.split()[1]
                if len(m.text.split()) > 2:
                    for i in m.text.split()[2:]:
                        tz += ' ' + i
                lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
                postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(geotoken,
                                                                                                                  tz)
                response_json = await get_response_json(lociq)
                lat = float(response_json[0]['lat'])
                lon = float(response_json[0]['lon'])
                timezone_name = tf.timezone_at(lng=lon, lat=lat)
                if timezone_name is None:
                    timezone_name = tf.closest_timezone_at(lng=lon, lat=lat)
                zone = timezone(timezone_name)
                dt = datetime.now(tz=zone)
                utc_format = str(datetime.now(tz=zone)).split(':')[2]
                if '+' in utc_format:
                    x = utc_format.split('+')[0]
                    utc_format = utc_format.split(x)[1]
                elif '-' in utc_format:
                    x = utc_format.split('-')[0]
                    utc_format = utc_format.split(x)[1]
                else:
                    utc_format = '+0'
                utc_format = f'UTC{utc_format}'
            else:
                utc_format = m.text.split()[1]
                increment = utc_format.split('UTC')[1] if 'UTC' in utc_format else utc_format.split('GMT')[1]
                increment = int(increment) if increment != '' else 0
                if increment > 14 or increment < -12:
                    raise TypeError('Invalid UTC or GMT format!')
                else:
                    dt = datetime.utcnow() + timedelta(hours=increment)
        else: pass
        dt = dt.strftime('%H:%M:%S')
        if 'UTC' not in m.text and 'GMT' not in m.text:
            time_format = 'В {} сейчас:\n {} {}'.format(tz, dt, utc_format)
        elif 'UTC' in m.text:
            time_format = f'По {utc_format} сейчас:\n {dt}'
        else:
            time_format = f'По {utc_format} сейчас:\n {dt}'
        await bot.send_message(m.chat.id, time_format, reply_to_message_id=m.message_id)
    except TypeError:
        await bot.send_message(m.chat.id, 'Invalid UTC/GMT format')
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['weather'])
async def weather(m):
    try:
        if len(m.text.split()) > 1:
            tz = m.text.split()[1]
            if len(m.text.split()) > 2:
                for i in m.text.split()[2:]:
                    tz += ' ' + i
            lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
            postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(geotoken, tz)
            response_json = await get_response_json(lociq)
            lat = float(response_json[0]['lat'])
            lon = float(response_json[0]['lon'])
            request = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang=ru&appid={OSM_API}'
            response_json = await get_response_json(request)
            try:
                weather_variables = []
                timezone_name = tf.timezone_at(lng=lon, lat=lat)
                if timezone_name is None:
                    timezone_name = tf.closest_timezone_at(lng=lon, lat=lat)
                zone = timezone(timezone_name)
                local = response_json['name']
                sunrise = str(datetime.fromtimestamp(response_json['sys']['sunrise'])).split()[1]
                sunset = str(datetime.fromtimestamp(response_json['sys']['sunset'])).split()[1]
                city_time = str(datetime.now(tz=zone))
                x = city_time.split()[1]
                if '+' in x:
                    x = x.split('+')[0]
                elif '-' in x:
                    x = x.split('-')[0]
                utc_format = str(datetime.now(tz=zone)).split(':')[2]
                if '+' in utc_format:
                    y = utc_format.split('+')[0]
                    utc_format = utc_format.split(y)[1]
                elif '-' in utc_format:
                    y = utc_format.split('-')[0]
                    utc_format = utc_format.split(y)[1]
                else:
                    utc_format = '+0'
                sec = str(float(x.split(':')[2]))
                secs = str(int(float(x.split(':')[2])))
                city_time = x.replace(sec, secs)
                wind_speed = response_json['wind']['speed']
                try:
                    wind_direction = response_json['wind']['deg']
                except KeyError:
                    wind_direction = None
                main_state = response_json['weather'][0]['description'].upper()
                temp = response_json['main']['temp']
                temp_F = round((temp - 273.15) * 9/5 + 32, 2)
                temp_C = round(temp - 273.15, 2)
                pressure = response_json['main']['pressure']
                humidity = response_json['main']['humidity']
                try:
                    visibility = response_json['visibility']
                except KeyError:
                    visibility = None
                clouds = response_json['clouds']['all']
                weather_message = f"*{local}*\n_Время: {city_time} UTC{utc_format}_\n_{main_state}_\nТемпература: {temp}ºK, {temp_F}ºF, {temp_C}ºC\nОблачность: {clouds}%\n" \
                    f"Влажность: {humidity}%\nДавление: {pressure}hPa\nВидимость: {visibility}м\nСкорость и направление ветра:\n{wind_speed}м/с, {wind_direction}º\n" \
                    f"Восход солнца: {sunrise} UTC+0\nЗаход солнца: {sunset} UTC+0"
                await bot.send_message(m.chat.id, weather_message, parse_mode='markdown')
            except KeyError:
                error_code = response_json['cod']
                error_message = response_json['message']
                message_text = f'Error {error_code}: {error_message}'
                await bot.send_message(m.chat.id, message_text)
        else:
            pass
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['spell'])
async def speller(m):
    if m.reply_to_message:
        text = await yaspeller(q=m.reply_to_message.text)
        await bot.send_message(chat_id=m.chat.id, text=text)
    elif len(m.text.split()) > 1:
        text = await yaspeller(q=m.text.split(maxsplit=1)[1])
        await bot.send_message(chat_id=m.chat.id, text=text)
    else:
        await bot.send_message(chat_id=m.chat.id, text='Сообщение должно быть реплаем')


@dp.message_handler(commands=['create_list'])
async def new_list(m):
    if m.reply_to_message:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Добавить',
                                          callback_data='add_to_list'))
        await bot.send_message(chat_id=m.chat.id, text=m.reply_to_message.text, reply_markup=kb)
        await bot.delete_message(chat_id=m.chat.id, message_id=m.reply_to_message.message_id)
        await bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    else:
        await bot.send_message(chat_id=m.chat.id, text='Команда должна быть реплаем на список.')


@dp.callback_query_handler(lambda c: c.data == 'add_to_list')
async def add_to_list(c, state=FSMContext):
    state = dp.current_state(chat=c.from_user.id, user=c.from_user.id)
    async with state.proxy() as data:
        data['message'] = c.message
    try:
        await bot.send_message(chat_id=c.from_user.id, text='Теперь напиши мне новые пункты списка')
        await bot.answer_callback_query(callback_query_id=c.id, text='Ответь мне в лс', show_alert=True)
        await state.set_state(Form.add_to_list)
    except (exceptions.BotBlocked, exceptions.CantInitiateConversation):
        await bot.answer_callback_query(callback_query_id=c.id, text='Сначали начин со мной диалог', show_alert=True)


@dp.message_handler(state=Form.add_to_list)
async def get_new_elements_for_list(m, state=FSMContext):
    async with state.proxy() as data:
        message = data['message']
    text = message.text + '\n' + m.text
    await bot.edit_message_text(text=text,
                                chat_id=message.chat.id,
                                message_id=message.message_id,
                                reply_markup=message.reply_markup)
    await bot.send_message(chat_id=m.chat.id, text='Готово')
    await bot.send_message(chat_id=message.chat.id, text='Список был обновлен', reply_to_message_id=message.message_id)
    await state.finish()


@dp.message_handler(commands=['her'])
async def who_is_bydlo(m):
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


@dp.message_handler(commands=['reset_one'])
async def update_bydlos(m):
    try:
        if m.from_user.id in developers:
            await HerGame(chat=m.chat).reset_her()
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['reset_many'])
async def update_bydlos(m):
    try:
        if m.from_user.id in developers:
            groups = []
            for doc in colh.find({'group': {'$exists': True}}):
                if doc['group'] not in groups:
                    groups.append(doc['group'])
            for group in groups:
                await HerGame(chat_id=group).reset_her()
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['run_changer'])
async def clean_hang_bot_flood(m):
    try:
        hangbot_flood = hang_bot_flood[m.chat.id]
        for message in hangbot_flood:
            try:
                if message.reply_to_message and message.text and len(message.text) == 1:
                    await bot.delete_message(m.chat.id, message.message_id)
                    await bot.delete_message(m.chat.id, message.reply_to_message.message_id)
                else:
                    await bot.delete_message(m.chat.id, message.message_id)
            except (exceptions.MessageToDeleteNotFound, AttributeError):
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
        except exceptions.MessageToDeleteNotFound:
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
    except exceptions.MessageCantBeDeleted:
        await bot.send_message(m.chat.id, 'Дайте удалялку')
        await anti_flood(m)
        pass
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['hangstats_switch'])
async def set_auto_hangstats(m):
    try:
        member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        if m.from_user.id in developers or member.status in ['administrator', 'creator']:
            doc = col_groups_users.find_one({'group': m.chat.id})
            if not doc:
                col_groups_users.insert_one({'group': m.chat.id})
            state = doc['hangstats_switch'] if 'hangstats_switch' in doc else 'on'
            state = await switch_state(state)
            col_groups_users.update_one({'group': m.chat.id},
                                        {'$set': {'hangstats_switch': state}})
            if state == 'on':
                await bot.send_message(m.chat.id, f'Готово теперь бот будет отправлять стату после каждой чистки')
            else:
                await bot.send_message(m.chat.id, f'Готово теперь бот не будет отправлять стату после каждой чистки')
        else:
            await bot.send_message(m.chat.id, 'Только админы могут делать это!')
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['winrate'])
async def send_winrate(m):
    try:
        if m.reply_to_message and m.reply_to_message.text:
            if m.reply_to_message.from_user.id == 121913006 or m.reply_to_message.forward_from and m.reply_to_message.forward_from.id == 121913006:
                if len(m.reply_to_message.text.split(':')) == 3 and\
                        m.reply_to_message.text.split(':')[1].split()[0].isdigit()\
                        and m.reply_to_message.text.split(':')[2].split()[0].isdigit():
                    wins = int(m.reply_to_message.text.split(':')[1].split()[0])
                    loses = int(m.reply_to_message.text.split(':')[2].split()[0])
            elif m.reply_to_message.from_user.id == 443471829 or m.reply_to_message.forward_from and m.reply_to_message.forward_from.id == 443471829:
                if len(m.reply_to_message.text.split('.')) == 4 and len(m.reply_to_message.text.split(':')) == 2\
                        and len(m.reply_to_message.text.split('\n')) == 4:
                    wins = int(m.reply_to_message.text.split('\n')[2].split()[0])
                    loses = int(m.reply_to_message.text.split('\n')[1].split()[0]) - wins
            winrate = await get_hangbot_winrate(wins, loses)
            await bot.send_message(m.chat.id, f'Winrate: ~{winrate} %', reply_to_message_id=m.message_id)
    except:
        await log_err(m=m, err=traceback.format_exc())


async def get_hangbot_winrate(wins, loses):
    games = wins + loses
    percent = games / 100
    winrate = wins / percent
    winrate = round(winrate, 2)
    return winrate


@dp.message_handler(lambda m: m.text.lower() in ['/game@veganwarsbot'], content_types=['text'])
async def start_timer(m):
    doc = colv.find_one({'group': m.chat.id})
    if doc:
        if 'timer_check' in doc:
            vegan_timer_check = doc['timer_check']
        else:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'timer_check': False}})
            doc = colv.find_one({'group': m.chat.id})
            vegan_timer_check = doc['timer_check']
    else:
        colv.insert_one({'group': m.chat.id,
                         'joined': [],
                         'timer_check': False})
        doc = colv.find_one({'group': m.chat.id})
        vegan_timer_check = doc['timer_check']
    if vegan_timer_check is False:
        colv.update_one({'group': m.chat.id},
                        {'$set': {'timer_check': True}})
        minutes_left = 5
        message_text = 'Осталась 5 минут, чтобы джойнуться\n\nДжоин --> /join@veganwarsbot'
        await bot.send_message(m.chat.id, message_text)
        if 'minutes_left' in doc:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'minutes_left': 5}})
        Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)
        logging.warning('timer set: ' + str(minutes_left))


async def vegan_timer(minutes_left, m):
    minutes_left = minutes_left - 1
    doc = colv.find_one({'group': m.chat.id})
    if minutes_left > 0 and doc['timer_check'] is True:
        second_f = [4, 3, 2]
        if minutes_left in second_f:
            message_text = f'Осталось {minutes_left} минуты, чтобы джойнуться\n\nДжоин --> /join@veganwarsbot'
        else:
            message_text = 'Осталась одна минута, чтобы джойнуться\n\nДжоин --> /join@veganwarsbot'
        await bot.send_message(m.chat.id, message_text)
        Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)
        logging.warning('timer set: ' + str(minutes_left))
    elif doc['timer_check'] is False and minutes_left <= 0:
        joined = colv.find_one({'group': m.chat.id})['joined']
        for player in joined:
            colv.update_one({'group': m.chat.id},
                            {'$pull': {'joined': player}})
        colv.update_one({'group': m.chat.id},
                        {'$set': {'minutes_left': 0}})
        logging.warning('list cleaned')
        print(colv.find_one({'group': m.chat.id}))
    elif doc['timer_check'] is True and minutes_left <= 0:
        joined = colv.find_one({'group': m.chat.id})['joined']
        for player in joined:
            colv.update_one({'group': m.chat.id},
                            {'$pull': {'joined': player}})
        colv.update_one({'group': m.chat.id},
                        {'$set': {'timer_check': False}})
        colv.update_one({'group': m.chat.id},
                        {'$set': {'minutes_left': 0}})
        logging.warning('list cleaned')
        print(colv.find_one({'group': m.chat.id}))
    elif doc['timer_check'] is False and minutes_left > 0:
        Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)
        logging.warning('timer set: '+str(minutes_left))
    else:
        await bot.send_message(developers[0], 'veganwars error: line 855!!!\n'+str(traceback.format_exc()))


@dp.message_handler(lambda m: m.text.lower() == '/join@veganwarsbot', content_types=['text'])
async def vegan_joined(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        joined = doc['joined']
        if 'time_left' in doc and doc['time_left'] <= 0:
            return
        if m.from_user.id in joined:
            return
        joined_name = m.from_user.first_name
        players_quant = len(joined) + 1
        if players_quant % 2 == 0 or players_quant == 1:
            await bot.send_message(m.chat.id, f'{joined_name} joined. {players_quant} игроков жойнулись.')
        elif players_quant != 1:
            await bot.send_message(m.chat.id, f'{joined_name} joined. {players_quant} игроков жойнулись. В игре будет крыса!')
        colv.update_one({'group': m.chat.id},
                        {'$push': {'joined': m.from_user.id}})
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(lambda m: m.text.lower() == '/flee@veganwarsbot', content_types=['text'])
async def vegan_left(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        joined = doc['joined']
        if 'time_left' in doc and doc['time_left'] <= 0:
            return
        if m.from_user.id not in joined:
            return
        joined_name = m.from_user.first_name
        players_quant = len(joined) - 1
        if players_quant % 2 == 0:
            await bot.send_message(m.chat.id, f'{joined_name} left. {players_quant} игроков жойнулись.')
        elif players_quant != 1:
            await bot.send_message(m.chat.id,
                                   f'{joined_name} left. {players_quant} игроков жойнулись. В игре будет крыса!')
        colv.update_one({'group': m.chat.id},
                        {'$pull': {'joined': m.from_user.id}})
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(lambda m: m.text.lower() == '/cancel@veganwarsbot', content_types=['text'])
async def stop_vegan_timer(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        if doc and 'timer_check' in doc and doc['timer_check'] is True:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'timer_check': False}})
        if 'joined' not in doc or doc['joined'] is None:
            return
        if 'minutes_left' not in doc:
            return
        if doc['minutes_left'] == 0:
            joined = doc['joined']
            for player in joined:
                colv.update_one({'group': m.chat.id},
                                {'$pull': {'joined': player}})
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(lambda m: m.text.lower() == '/fight@veganwarsbot', content_types=['text'])
async def start_vegan_game(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        if doc and 'timer_check' in doc and doc['timer_check'] is True:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'timer_check': False}})
        colv.update_one({'group': m.chat.id},
                        {'$set': {'minutes_left': 0}})
        joined = doc['joined']
        for player in joined:
            colv.update_one({'group': m.chat.id},
                            {'$pull': {'joined': player}})
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(commands=['gramota'])
async def get_word(m):
    if len(m.text.split()) > 1:
        word = await get_complex_argument(m.text)
        word_info = await gramota_parse(word)
        if await get_word_dict(word_info):
            words = await get_word_dict(word_info)
            kb = types.InlineKeyboardMarkup()
            synonyms = None
            for i in words:
                if 'None' not in words[i][1] and i != 'orthographic' and words[i][1]:
                    if i not in ['synonyms', 'synonyms_short']:
                        kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
                    elif i in ['synonyms', 'synonyms_short'] and not synonyms:
                        kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
                    if i in ['synonyms', 'synonyms_short']:
                        synonyms = True
                # kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
            print(kb)
            if 'None' not in words['orthographic'][1]:
                message_text = words['orthographic'][1]
            elif kb['inline_keyboard']:
                message_text = word
            else:
                if len(word.split()) == 1:
                    message_text = f'Слово <i>{word}</i> не найдено.'
                else:
                    message_text = f'Словосочетание <i>{word}</i> не найдено.'
            await bot.send_message(m.chat.id, message_text, reply_markup=kb, parse_mode='html')
        else:
            words = await similar_words(word)
            if len(word.split()) == 1:
                message_text = f'Слово _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            else:
                message_text = f'Словосочетание _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            await bot.send_message(m.chat.id, message_text, parse_mode='markdown')


@dp.message_handler(commands=['mask'])
async def get_words_by_mask(m):
    try:
        mask = m.text.split()[1]
        letters_quantity = m.text.split()[2] if len(m.text.split()) > 2 else None
        words_list = await find_by_mask(mask, letters_quantity)
        message_text = ''
        for word in words_list:
            message_text += word + '\n'
        await bot.send_message(m.chat.id, message_text, parse_mode='html')
    except:
        await log_err(m=m, err=traceback.format_exc())


@dp.message_handler(lambda m: m.chat.type == 'private', commands=['fwd_to_text'])
async def setup_fwd(m):
    try:
        kb = types.InlineKeyboardMarkup()
        monolog = types.InlineKeyboardButton('Монолог', callback_data='monolog')
        dialog = types.InlineKeyboardButton('Диалог', callback_data='dialog')
        kb.add(monolog, dialog)
        await bot.send_message(chat_id=m.chat.id, text='Выберите тип текста:', reply_markup=kb)
    except:
        await log_err(m=m, err=traceback.format_exc())
        await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


@dp.callback_query_handler(lambda c: c.data in ['monolog', 'dialog'])
async def forward_to_text(c, state=FSMContext):
    try:
        first_fwd_msg = await bot.send_message(c.message.chat.id, 'Начнем')
        first_fwd_msg = first_fwd_msg.message_id
        async with state.proxy() as data:
            data['text_type'] = c.data
            data['first_fwd_msg'] = first_fwd_msg
        await bot.answer_callback_query(callback_query_id=c.id)
        await bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id)
        await Form.fwded_msgs.set()
    except:
        await log_err(m=c.message, err=traceback.format_exc())
        await bot.send_message(c.message.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


@dp.message_handler(commands=['stop'], state=Form.fwded_msgs)
async def send_fwded_msgs_in_single_msg(m, state=FSMContext):
    try:
        async with state.proxy() as data:
            text_type = data['text_type']
            first_fwd_msg = data['first_fwd_msg']
        if text_type == 'monolog':
            text = await get_monolog(bot=bot, m=m, first_fwd_msg=first_fwd_msg)
        elif text_type == 'dialog':
            text = await get_dialog(bot=bot, m=m, first_fwd_msg=first_fwd_msg)
        await bot.send_message(m.chat.id, text)
        await state.finish()
    except exceptions.MessageIsTooLong:
        message_parts = await cut_for_messages(text, 4096)
        for part in message_parts:
            await bot.send_message(m.chat.id, part)
        await state.finish()
    except exceptions.NetworkError:
        await bot.send_message('Попробуйте отправить по меньшему количеству сообщений, но результат не гарантирую.' \
                               ' Я уже работаю над этой ошибкой. (НИХУЯ)')
    except:
        await log_err(m=m, err=traceback.format_exc())
        await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


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


@dp.callback_query_handler(lambda call: check_date(call.message.date))
async def send_info_about_word(call):
    try:
        word = call.data.split(':: ')[0]
        data = await get_word_dict(await gramota_parse(word))
        dict_type = call.data.split(':: ')[1]
        title = data[dict_type][0]
        description = data[dict_type][1]
        if call.message.chat.type == 'private':
            await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            await bot.answer_callback_query(call.id)
        else:
            if len(description) > 1000:
                description = await cut_message(description, 1000)
                description = description['cuted']
                deep_link = base64.urlsafe_b64encode(f'gramota-4096-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
                description += f'<a href="t.me/{bot_user}?start={deep_link}"> читать продолжение...</a>'
            print(description)
            await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            await bot.answer_callback_query(call.id)
            await asyncio.sleep(30)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except exceptions.MessageIsTooLong:
        description = await cut_message(description, 4096 - 500)
        description = description['cuted']
        deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
        description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
                       f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x"> продолжить на сайте...</a>'
        await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
    except exceptions.MessageNotModified:
        pass
    except:
        await log_err(m=call.message, err=traceback.format_exc())


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
            break


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


executor.start_polling(dp, loop=loop, skip_updates=True)

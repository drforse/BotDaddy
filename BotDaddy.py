import pymongo
from pymongo import MongoClient
import traceback
import asyncio
import logging
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
from aiogram.utils import exceptions
import os
import aiocron
import time
import datetime
from datetime import date
from datetime import datetime
import requests
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
from aio_timers import Timer
import random

API_TOKEN = os.environ['token']

WEBHOOK_HOST = os.environ['heroku_app']
WEBHOOK_PORT = 443
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.WARNING)
loop = asyncio.get_event_loop()

storage = MemoryStorage()
client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
collection = db.pin_list
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)
col2 = db.users
colv = db.veganwars_helper
banned = col2.find_one()

developers = [500238135]
bot_id = os.environ['bot_id']
bot_user = '@botsdaddyybot'

OSM_API = os.environ['OSM_API']
geotoken = os.environ['geotoken']
tf = TimezoneFinder(in_memory=True)

ban_keywords_list = ['!иди в баню', '!иди в бан', '!банан тебе в жопу', '!нам будет тебя не хватать', '/ban', '/ban@botsdaddyybot']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban', '/unban@botsdaddyybot']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
OD_flood_list = ["Да как ты разговариваешь со старшими!"]
ban_mute_list = ban_keywords_list + unban_keywords_list + mute_keywords_list + unmute_keywords_list
hang_bot_flood = {}


class Form(StatesGroup):
    help_define = State()

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
        print(traceback.format_exc())

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
        except exceptions.BadRequest:
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
                await bot.send_message(developers[0],
                                       "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
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
        except exceptions.BadRequest:
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
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),
                                                                             message.chat.id, message.chat.username))

                                           # developers_only


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
        print(traceback.format_exc())


# Users
@dp.message_handler(commands=['help'])
async def show_help(message):
    doc = collection.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith('/help@botsdaddyybot'):
        await bot.send_message(message.from_user.id, help_msg, parse_mode='markdown')
        await bot.send_message(message.chat.id, 'Отправил в лс')
    elif message.chat.type == 'private':
        await bot.send_message(message.chat.id, help_msg, parse_mode='markdown')


@dp.message_handler(commands=['pintime'])
async def pintime(message):
    try:
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        quant = 3
        if message.chat.type == 'private':
            await bot.send_message(message.chat.id, 'Only for groups')
        elif chat_member.can_pin_messages == True or chat_member.status == 'creator':
            if message.reply_to_message == None:
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
            await anti_flood(message)
    except AttributeError:
        member = await bot.get_chat_member(message.chat.id, bot_id)
        if member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


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
    if message.text.startswith('/pinlist@botsdaddyybot'):
        try:
            document = collection.find_one({'Group': message.chat.id})
            text = ''
            document.pop('_id')
            for ids in document:
                if ids == '_id':
                    continue
                elif ids == 'Group':
                    text += "{}: <a href='t.me/{}'>{}</a>\n".format('Group', message.chat.username, message.chat.title)
                else:
                    text += '<a href="t.me/{}/{}">{}</a>: {}\n'.format(document[ids][0]['group'], ids,
                                                                       document[ids][0]['date'],
                                                                       document[ids][0]['msg'])
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    await bot.send_message(message.from_user.id, text[x:x + 4096], parse_mode='html',
                                           disable_web_page_preview=True)
            else:
                await bot.send_message(message.from_user.id, text, parse_mode='html', disable_web_page_preview=True)
            await bot.send_message(message.chat.id, 'Отправил тебе в лс')
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
            tz = m.text.split()[1]
            if len(m.text.split()) > 2:
                for i in m.text.split()[2:]:
                    tz += ' ' + i
            lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
            postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(geotoken,
                                                                                                              tz)
        else:
            pass
        response_json = await get_response_json(lociq)
        lat = float(response_json[0]['lat'])
        lon = float(response_json[0]['lon'])
        timezone_name = tf.timezone_at(lng=lon, lat=lat)
        if timezone_name is None:
            timezone_name = tf.closest_timezone_at(lng=lon, lat=lat)
        zone = timezone(timezone_name)
        hour = str(datetime.now(tz=zone).hour)
        minute = str(datetime.now(tz=zone).minute)
        second = str(datetime.now(tz=zone).second)
        utc_format = str(datetime.now(tz=zone)).split(':')[2]
        if '+' in utc_format:
            x = utc_format.split('+')[0]
            utc_format = utc_format.split(x)[1]
        elif '-' in utc_format:
            x = utc_format.split('-')[0]
            utc_format = utc_format.split(x)[1]
        else:
            utc_format = '+0'
        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
        if len(second) == 1:
            second = '0' + second
        time_format = 'В {} сейчас:\n {}:{}:{} UTC{}'.format(tz, hour, minute, second, utc_format)
        await bot.send_message(m.chat.id, time_format, reply_to_message_id = m.message_id)
    except:
        print(traceback.format_exc())


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
        print(traceback.format_exc())


@dp.message_handler(commands=['her'])
async def who_is_bydlo(m):
    try:
        if m.date().hour > 19:
            await bot.send_message(m.chat.id, 'У меня работа до 19 по UTC, потом поиграем!')
        else:
            bydlos = col2.find_one({'bydlos': True,
                                    'group': m.chat.id})
            print(bydlos)
            if 'done' not in bydlos:
                bydlos['done'] = False
            if not bydlos['done']:
                await bot.send_message(m.chat.id, 'Итак, кто же у нас хер тут, м?')
                await asyncio.sleep(0.5)
                bydlos.pop('bydlos')
                bydlos.pop('group')
                bydlos.pop('_id')
                bydlo_bad_messages_quant = max(list(bydlos.values()))
                main_bydlos = []
                await bot.send_message(m.chat.id, 'Чекаю базу данных...')
                await asyncio.sleep(0.5)
                for bydlo in bydlos.items():
                    if bydlo[1] == bydlo_bad_messages_quant:
                        main_bydlos.append(bydlo[0])
                if len(main_bydlos) > 1:
                    main_bydlo = random.choice(main_bydlos)
                    await bot.send_message(m.chat.id, 'Ну пиздец, вас тут сука несколько нахуй')
                    await asyncio.sleep(0.5)
                    await bot.send_message(m.chat.id, 'Кхм, прошу прощения, с волками жить...')
                    await asyncio.sleep(0.5)
                else:
                    print(main_bydlos)
                    main_bydlo = main_bydlos[0]
                main_bydlo_member = await bot.get_chat_member(m.chat.id, int(main_bydlo))
                main_bydlo_first_name = main_bydlo_member.user.first_name
                await bot.send_message(m.chat.id, f'<a href="tg://user?id={int(main_bydlo)}">{main_bydlo_first_name},'
                                                  f' {main_bydlo_first_name}</a>, хер моржовый!',
                                       parse_mode='html', disable_web_page_preview=True)
                col2.update_one({'bydlos': True,
                                 'group': m.chat.id},
                                {'$set': {'done': main_bydlo_first_name}})
            else:
                random_id = int(random.random()*int(10**random.randint(1, 10)))
                main_bydlo_first_name = bydlos['done']
                if m.chat.username:
                    await bot.send_message(m.chat.id,
                                           f'<a href="t.me/{m.chat.username}/{random_id}">Тык на сообщение с хером!</a>',
                                           parse_mode='html', disable_web_page_preview=True)
                    await asyncio.sleep(2.5)
                    await bot.send_message(m.chat.id, '...Ненавижу порталы!')
                    await asyncio.sleep(1)
                    await bot.send_message(m.chat.id, f'{main_bydlo_first_name}', reply_to_message_id=m.message_id)
                else:
                    await bot.send_message(m.chat.id,
                                           f'<a href="t.me/{m.chat.id}/{random_id}">Тык на сообщение с хером!</a>',
                                           parse_mode='html', disable_web_page_preview=True)
                    await asyncio.sleep(2.5)
                    await bot.send_message(m.chat.id, '...Ненавижу порталы!')
                    await asyncio.sleep(1)
                    await bot.send_message(m.chat.id, f'{main_bydlo_first_name}', reply_to_message_id=m.message_id)
    except TypeError:
        print(traceback.format_exc())
        await bot.send_message(m.chat.id, 'Я не в настроении.')
    except:
        print(traceback.format_exc())


@dp.message_handler(commands=['reset_one'])
async def update_bydlos(m):
    if m.from_user.id in developers:
        col2.delete_one({'bydlos': True,
                          'group': m.chat.id})


@dp.message_handler(commands=['reset_many'])
async def update_bydlos(m):
    if m.from_user.id in developers:
        col2.delete_many({'bydlos': True,
                          'group': {'$exists': True}})


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
        del hang_bot_flood[m.chat.id]
    except exceptions.MessageCantBeDeleted:
        await bot.send_message(m.chat.id, 'Дайте удалялку')
        await anti_flood(m)
        pass
    except:
        print(traceback.format_exc())


@dp.message_handler(commands=['winrate'])
async def send_winrate(m):
    try:
        if m.reply_to_message and m.reply_to_message.text and m.reply_to_message.from_user.id == 121913006:
            if len(m.reply_to_message.text.split(':')) == 3 and\
                    m.reply_to_message.text.split(':')[1].split()[0].isdigit()\
                    and m.reply_to_message.text.split(':')[2].split()[0].isdigit():
                wins = int(m.reply_to_message.text.split(':')[1].split()[0])
                loses = int(m.reply_to_message.text.split(':')[2].split()[0])
                winrate = await get_hangbot_winrate(wins, loses)
                await bot.send_message(m.chat.id, f'Winrate: ~{winrate} %', reply_to_message_id=m.message_id)
    except:
        print(traceback.format_exc())


async def get_hangbot_winrate(wins, loses):
    games = wins + loses
    percent = games / 100
    winrate = wins / percent
    winrate = round(winrate, 2)
    return winrate


@dp.message_handler(lambda m: m.text.lower() == '/game@veganwarsbot', content_types=['text'])
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
        if 'minutes_left' in doc:
            colv.update_one({'group': m.chat.id},
                            {'$unset': {'minutes_left': 0}})
        timer = Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)


async def vegan_timer(minutes_left, m):
    minutes_left = minutes_left - 1
    doc = colv.find_one({'group': m.chat.id})
    if 'minutes_left' not in doc:
        if minutes_left > 0 and doc['timer_check'] is True:
            second_f = [4, 3, 2]
            if minutes_left in second_f:
                message_text = f'Осталось {minutes_left} минуты, чтобы джойнуться\n\nДжоин --> /join@veganwarsbot'
            else:
                message_text = 'Осталась одна минута, чтобы джойнуться\n\nДжоин --> /join@veganwarsbot'
            await bot.send_message(m.chat.id, message_text)
            timer = Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)
        elif doc['timer_check'] is False and minutes_left <= 0:
            joined = colv.find_one({'group': m.chat.id})['joined']
            for player in joined:
                colv.update_one({'group': m.chat.id},
                                {'$pull': {'joined': player}})
            colv.update_one({'group': m.chat.id},
                            {'$set': {'minutes_left': 0}})
        elif doc['timer_check'] is True and minutes_left <= 0:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'timer_check': False}})
            colv.update_one({'group': m.chat.id},
                            {'$set': {'minutes_left': 0}})
        elif doc['timer_check'] is False and minutes_left > 0:
            timer = Timer(60, callback=vegan_timer, callback_args=(minutes_left, m), callback_async=True)
        else:
            await bot.send_message(developers[0], '560!!!')
    elif doc['timer_check'] is True:
        colv.update_one({'group': m.chat.id},
                        {'$set': {'timer_check': False}})


@dp.message_handler(lambda m: m.text.lower() == '/join@veganwarsbot', content_types=['text'])
async def vegan_joined(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        joined = doc['joined']
        vegan_timer_check = doc['timer_check']
        if m.from_user.id not in joined and vegan_timer_check is True:
            if m.from_user.username:
                joined_name = m.from_user.first_name
                players_quant = len(joined) + 1
                if players_quant % 2 == 0 or players_quant == 1:
                    await bot.send_message(m.chat.id, f'{joined_name} joined. {players_quant} игроков жойнулись.')
                elif players_quant != 1:
                    await bot.send_message(m.chat.id,
                                           f'{joined_name} joined. {players_quant} игроков жойнулись. В игре будет крыса!')
                colv.update_one({'group': m.chat.id},
                                {'$push': {'joined': m.from_user.id}})
            else:
                await bot.send_message(m.chat.id, 'Эт самое, если чо, для игры в VeganWars нужен юзернейм (@username)')
    except:
        print(traceback.format_exc())


@dp.message_handler(lambda m: m.text.lower() == '/flee@veganwarsbot', content_types=['text'])
async def vegan_left(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        joined = doc['joined']
        vegan_timer_check = doc['timer_check']
        if m.from_user.id in joined and vegan_timer_check is True:
            joined_name = m.from_user.first_name
            players_quant = len(joined) - 1
            if players_quant % 2 == 0 or players_quant == 1:
                await bot.send_message(m.chat.id, f'{joined_name} left. {players_quant} игроков жойнулись.')
            elif players_quant != 1:
                await bot.send_message(m.chat.id,
                                       f'{joined_name} left. {players_quant} игроков жойнулись. В игре будет крыса!')
            colv.update_one({'group': m.chat.id},
                            {'$pull': {'joined': m.from_user.id}})
    except:
        print(traceback.format_exc())


@dp.message_handler(lambda m: m.text.lower() == '/cancel@veganwarsbot', content_types=['text'])
async def stop_vegan_timer(m):
    try:
        doc = colv.find_one({'group': m.chat.id})
        if doc and 'timer_check' in doc and doc['timer_check'] is True:
            colv.update_one({'group': m.chat.id},
                            {'$set': {'timer_check': False}})
        if 'minutes_left' in doc and doc['minutes_left'] == 0:
            joined = doc['joined']
            for player in joined:
                colv.update_one({'group': m.chat.id},
                                {'$pull': {'joined': player}})
    except:
        print(traceback.format_exc())


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
        print(traceback.format_exc())


@dp.message_handler(content_types=['text'])
async def ban_mute(message):
    try:
        global chat_member
        global reply_member
        global bot_member
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
        if itisbadmessage(message):
            col2.update_one({'bydlos': True,
                             'group': message.chat.id},
                            {'$inc': {str(message.from_user.id): 1}},
                            upsert=True)
    except:
        print(traceback.format_exc())


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
    bad_words = ['fuck', 'dick', "хуй", "хер", "уеб", "еб"]
    for bad_word in bad_words:
        if 'е' in bad_word:
            bad_words.append(bad_word.replace('е', "ё"))
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


@aiocron.crontab('*/3 * * * *')
async def anti_idling():
    await bot.get_me()


@aiocron.crontab('0 0 * * *')
async def update_bydlos():
    col2.delete_many({'bydlos': True,
                      'group': {'$exists': True}})


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    pass

start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True, host='0.0.0.0', port=os.getenv('PORT'))

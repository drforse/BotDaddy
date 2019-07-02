import pymongo
from pymongo import MongoClient
import traceback
import asyncio
import logging
from typing import Optional
import aiogram.utils.markdown as md
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
##from aiogram.utils import executor

from aiogram.utils.executor import start_webhook

import random
import os
import schedule
import time
import datetime
from datetime import date
from datetime import datetime
import threading
import requests
import timezonefinder
from timezonefinder import TimezoneFinder
from pytz import timezone, utc

#TODO:
'''
#ALL
1) Сделать вебхуки
2) Задеплоить рабочую версию с вебхуками и аиограмом
3) Взаимодействие на старт
4) Сделать локализации
##BotDaddy
1) Сделать красиво time
2) Добавить weather 
##Jester
1) Добавить кидание задания шуту в личку
2) Добавить возможность заканчивать игру или узнавать короля администраторам
3) Добавить автоматическое окончание игры по расписанию
4) Сделать фичу от Рин (угадывание задания)
5) Сделать фидбек
6) Добавить в бд отдельную коллекцию для приватных чатов, перенести туда документы с приватными чатами из основной коллекции,
оптимизировать код под новую структуру бд.
7) Сделать хелп
'''

API_TOKEN_JR = os.environ['token_jr']
API_TOKEN = os.environ['token']

WEBHOOK_HOST = 'https://bottle-game-telebot.herokuapp.com'
WEBHOOK_PORT = 443
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


logging.basicConfig(level=logging.INFO)

##loop = asyncio.new_event_loop()
client_jr = pymongo.MongoClient(os.environ['db_jr'])
db_jr = client_jr.test
collection2 = db_jr.bottle
jr = Bot(API_TOKEN_JR)
storage = MemoryStorage()
jp = Dispatcher(jr, storage=storage)
jester_user = 'pictionary_bot'

client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
collection = db.pin_list
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)
col2 = db.users
banned = col2.find_one()

developers = [500238135]
bot_id = os.environ['bot_id']
bot_user = '@temp_tectu_bot'

geotoken = 'pk.13ffd5a51ce670436ccc53d931bc9715'
tf = TimezoneFinder(in_memory=True)

ban_keywords_list = ['!иди в баню','!иди в бан','!банан тебе в жопу','!нам будет тебя не хватать', '/ban', '/ban@botsdaddyybot']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban', '/unban@botsdaddyybot']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
OD_flood_list = ["Да как ты разговариваешь со старшими!"]
ban_mute_list = ban_keywords_list + unban_keywords_list + mute_keywords_list + unmute_keywords_list
'''
print(await jr.get_chat_member(-1001468828532, 828000649).user.username)
reg_kb = types.InlineKeyboardMarkup()
reg = types.InlineKeyboardButton('Тык', url='telegram.me/jester_day_bot?start=test')
reg_kb.add(reg)
groups = []
for group in collection2.find({'group':{'$exists':True}}):
    groups.append(group['group'])
    await jr.send_message(group['group'], 'Нажмите, пожалуйста на кнопку, чтобы победить баг вместе)0))', reply_markup = reg_kb)
'''

'''Jester'''

@jp.message_handler(content_types = ['left_chat_member'])
async def left_member(m):
    member = await jr.get_chat_member(m.chat.id, m.from_user.id)
    print(member.user.id)
    if member.user.id in collection2.find_one({'group': m.chat.id})['players']:
        collection2.update_one({'group': m.chat.id},
                               {'$pull':{'players':m.from_user.id}})


class Form(StatesGroup):
    help_define1 = State()
    help_define = State()
    getting_mission = State()
    
@jp.message_handler(commands = ['help_define'])
async def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        await jr.send_message(message.from_user.id, 'Define the help-message')
        await jr.delete_message(message.chat.id, message.message_id)
        await Form.help_define.set()
    else:
        await jr.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')
@jp.message_handler(state=Form.help_define)
async def help_message_handler(message, state: FSMContext):
    global help_definer
    if message.chat.id == help_definer:
        collection2.update_one({'id': 0},
                               {'$set': {'help_msg': message.text}},
                               upsert=True)
        await jr.send_message(message.chat.id, 'Updated.')
        await state.finish()

@jp.message_handler(commands = ['help'])
async def show_help(message):
    doc = collection2.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith('/help@jester_day_bot'):
        await jr.send_message(message.chat.id, help_msg, parse_mode = 'markdown')
    elif message.chat.type == 'private':
        await jr.send_message(message.chat.id, help_msg, parse_mode = 'markdown')

@jp.message_handler(commands = ['players'])
async def players_list(m):
    try:
        if collection2.find_one({'group': m.chat.id}):
            players = ''
            for gamer in collection2.find_one({'group':m.chat.id})['players']:
                if gamer != None:
                    player = await jr.get_chat_member(m.chat.id, gamer)
                    player = player.user.first_name
                    players += str(player) + ', '
            x = len(players)-2
            players = players[:x]
            await jr.send_message(m.chat.id, players, reply_to_message_id = m.message_id)
    except:
        print(traceback.format_exc())
            
@jp.message_handler(commands = ['leave_jester'])
async def leave_game(m):
    try:
        member = await jr.get_chat_member(m.chat.id, m.from_user.id)
        if member.user.id in collection2.find_one({'group': m.chat.id})['players']:
            collection2.update_one({'group': m.chat.id},
                                   {'$pull':{'players':m.from_user.id}})
            await jr.send_message(m.chat.id, 'Вы вышли из игры!')
    except:
        print(traceback.format_exc())
            
@jp.message_handler(commands = ['reset_game'])
async def reset_game(m):
    try:
        if m.from_user.id in developers or await jr.get_chat_member(m.chat.id, m.from_user.id).status == 'creator' or await jr.get_chat_member(m.chat.id, m.from_user.id).status == 'administrator':
            collection2.update_one({'group': m.chat.id},
                                   {'$set': {'status': '0'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'mission_text':'$exists'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'first_today_user':'$exists'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'second_today_user':'$exists'}})
            await jr.send_message(m.chat.id, 'Game reseted')
        else:
            await jr.send_message(m.chat.id, 'Вы не админ')
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc()) 

@jp.message_handler(commands = ['reg_me'])
async def reg_user(message):
    try:
        doc = collection2.find_one({'group': message.chat.id})
        reg_kb = types.InlineKeyboardMarkup()
        reg = types.InlineKeyboardButton('Тык', url='telegram.me/{}?start={}'.format(jester_user, message.chat.id))
        reg_kb.add(reg)
        if collection2.find_one({'group': message.chat.id}) == None:
            collection2.insert_one ({'group': message.chat.id,
                                    'players': [],
                                    'status': '0'})
            await jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id = message.message_id, reply_markup = reg_kb)
        elif message.from_user.id not in doc['players']:
            await jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id = message.message_id, reply_markup = reg_kb)
        else:
            await jr.send_message(message.chat.id, 'Вы уже в игре!', reply_to_message_id = message.message_id)
    except:
        await jr.send_message(message.chat.id, traceback.format_exc())
    
@jp.message_handler(commands = ['finish_it'])
async def finish_game(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if m.from_user.id != doc['king'] and doc['king']:
            await jr.send_message(m.chat.id, 'Вы - не король!')
        elif m.chat.type == 'private':
            await jr.send_message(m.chat.id, 'Так Вас никто не услышит!')
        elif doc['status'] == '2':
            if len(m.text.split()) < 2:
                await jr.send_message(m.chat.id, 'Скажите, как Вам понривалось шоу после команды, Ваше Величество', reply_to_message_id = m.message_id)
            else:
                list = m.text.split()
                result = ''
                for i in range(len(list)-1):
                    result += list[i+1]+' '
                await jr.send_message(m.chat.id, 'Мнение Его Величества:\n'+result)
                collection2.update_one({'group': m.chat.id},
                                       {'$set': {'status': '3'}})
                await jr.send_message(m.chat.id, "Задание было таким:\n" + doc['mission_text'])
        else:
            await jr.send_message(m.chat.id, 'Игра еще не начата, или уже закончена, или задание еще не выполнено (назначено)')
    except KeyError:
        await jr.send_message(m.chat.id, 'game not started yet')
    except:
        print(traceback.format_exc())

@jp.message_handler(commands = ['today_user'])
async def get_users(message):
    global x
    global message_chat_id
    message_chat_id = message.chat.id
    try:
        x = 0
        doc = collection2.find_one({'group': message.chat.id})
        list_users = doc['players']
        if len(doc['players']) < 3:
            await jr.send_message(message.chat.id, 'Not enough players, 3 needed.')
        elif doc['status'] == '0':
            first_user = random.choice(list_users)
            second_user = random.choice(list_users)
            king = random.choice(list_users)
            while first_user == second_user:
                second_user = random.choice(list_users)
            while king == first_user or king == second_user:
                king = random.choice(list_users)
            member = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = member.user.first_name
            member = await jr.get_chat_member(message.chat.id, second_user)
            second_user_name = member.user.first_name
            to_mission = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name), url = 'https://telegram.me/{}?start={}'.format(jester_user, message.chat.id))
            to_mission.add(butt)
            await jr.send_message(message.chat.id, 'Loading...')
            await jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, {}'.format(second_user, second_user_name, 'Вы грустите на пиру, король, обратив на Вас свое внимание, предлагает Вам придумать смешное задание для его шута, нравится вам это или нет - ничего не поделаешь, придется заняться, иначе кого-нибудь казнят, даже если не вас, ответственность нести за это Вам точно не хочется!'), parse_mode = 'html', reply_markup = to_mission)
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'status': '1'}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'first_today_user':first_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'second_today_user':second_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'king':king}})
            if message.chat.username != None:
                await jr.send_message(king, 'Вы - король в мире ' + '@' + message.chat.username + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена"')
            else:
                await jr.send_message(king, 'Вы - король в мире ' + '[{}](t.me/c/{})'.format(message.chat.first_name, message.chat.id) + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена")', parse_mode = 'markdown')
        elif doc['status'] == '1':
            first_user = doc['first_today_user']
            first_user_name = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = first_user_name.user.first_name
            second_user = doc['second_today_user']
            second_user_name = await jr.get_chat_member(message.chat.id, second_user)
            second_user_name = second_user_name.user.first_name
            kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name), url = 'https://telegram.me/{}?start={}'.format(jester_user, message.chat.id))
            kb.add(butt)
            await jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, придумывает задание для шута...'.format(second_user, second_user_name), parse_mode = 'html', reply_markup = kb)
        elif doc['status'] == '2':
            first_user = doc['first_today_user']
            first_user_name = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = first_user_name.user.first_name
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data = 'mission')
            jester_mission_kb.add(butt)            
            await jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, придворный шут, выполняет задание...'.format(first_user, first_user_name), parse_mode = 'html', reply_markup = jester_mission_kb)
        elif doc['status'] == '3':
            await jr.send_message(message.chat.id, 'Сегодняшняя игра уже закончена!')
    except:
        print(traceback.format_exc())


async def status_check(m, doc, second_user):
    if doc['status'] == '1':
        if m.from_user.id == second_user:
            await jr.send_message(m.chat.id, 'Отправь задание ответом на ЭТО сообщение', reply_to_message_id = m.message_id, reply_markup = types.ForceReply())
    elif doc['status'] == '0':
        await jr.send_message(m.chat.id, 'Игра еще не началась, начни ее командой /today_user')
    elif doc['status'] == '2':
        await jr.send_message(m.chat.id, 'Задание уже выбрано, перевыбрать не получится, потому что разраб - пидор, все претензии к [нему](t.me/dr_forse), я всего лишь бот.', parse_mode = 'markdown')
    elif doc['status'] == '3':
        await jr.send_message(m.chat.id, 'Дневной розыгрыш уже окончен, возвращайся завтра или зайди на гитхаб(в описании), возьми код, сделай розыгрыш постоянным и захости у себя, если, конечно не ужаснешься тому, какой это говнокод.')

@jp.message_handler(lambda m: m.chat.type == 'private', content_types = ['text'])
async def finish_reg(m):
    try:
        if len(m.text.split())>1:
            try:
                chat_id = int(m.text.split()[1])
            except:
                chat_id = collection2.find_one({'user': m.chat.id})['main_chat']
            try:
                doc = collection2.find_one({'group': chat_id})
                second_user = doc['second_today_user']
            except:
                pass
            if m.from_user.id not in doc['players'] and m.text.startswith('/start'):
                collection2.update_one({'group': chat_id},
                                       {'$push': {'players': m.from_user.id}})
                if None in doc['players']:
                    collection2.update_one({'group': chat_id},
                                           {'$pull': {'players': None}})
                await jr.send_message(m.chat.id, 'Вы зарегестрировались!')
            elif m.text.startswith('/start'):
                collection2.update_one({'user':m.chat.id},
                                       {'$set': {'main_chat':chat_id}},
                                       upsert = True)
                await status_check(m, doc, second_user)
                await Form.getting_mission.set()
            else:
                await Form.getting_mission.set()
        elif m.text.startswith('/start'):
            try:
                chat_id = int(m.text.split()[1])
            except:
                chat_id = collection2.find_one({'user': m.chat.id})['main_chat']
            doc = collection2.find_one({'group': chat_id})
            second_user = doc['second_today_user']
            collection2.update_one({'user':m.chat.id},
                                   {'$set': {'main_chat':chat_id}},
                                   upsert = True)
            await status_check(m, doc, second_user)
            await Form.getting_mission.set()
        else:
            await Form.getting_mission.set()
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())
@jp.message_handler(state=Form.getting_mission)
async def getting_mission(m, state: FSMContext):
    try:
        try:
            try:
                if m.text.startswith('/start'):
                    chat_id = int(m.text.split()[1])
                else:
                    chat_id = collection2.find_one({'user': m.chat.id})['main_chat']
            except:
                chat_id = collection2.find_one({'user': m.chat.id})['main_chat']
        except:
            chat_id = m.chat.id
        doc = collection2.find_one({'group': chat_id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user'] 
        if doc['status'] == '1':
            if m.from_user.id == second_user:
                collection2.update_one({'user':m.chat.id},
                                       {'$set':{'mission':m.text}},
                                       upsert = True)
                collection2.update_one({'user':m.chat.id},
                                       {'$set':{'main_chat':chat_id}})
                check_kb = types.InlineKeyboardMarkup()
                accept = types.InlineKeyboardButton('Да', callback_data = 'accept')
                decline = types.InlineKeyboardButton('Нет', url = 'https://telegram.me/jester_day_bot?start={}'.format(chat_id))
                check_kb.add(accept, decline)
                if m.reply_to_message != None:
                    if m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение' and (time.time() - (m.reply_to_message.date - datetime(1970,1,1)).total_seconds()) < 60:
                        await jr.send_message(m.chat.id, 'Вы уверены?', reply_markup = check_kb)
                        await state.finish()
                    elif m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение':
                        await jr.send_message(m.chat.id, 'Message is too old.')
                        await state.finish()
                else:
                    await jr.send_message(m.chat.id, 'Отправь задание ответом на ЭТО сообщение', reply_to_message_id = m.message_id, reply_markup = types.ForceReply())                    
            else:
                await jr.send_message(m.chat.id, 'ЭТА КОПКА НЕ ДЛЯ ТЕБЯ, АЛЕ! Неужели, игра такая сложная, что у тебя мозги превратились в кашу? Может, тебе новые подарить?')
                await state.finish()
        elif doc['status'] == '0':
            await jr.send_message(m.chat.id, 'Игра еще не началась, начни ее командой /today_user')
            await state.finish()
        elif doc['status'] == '2':
            await jr.send_message(m.chat.id, 'Задание уже выбрано, перевыбрать не получится, потому что разраб - пидор, все претензии к [нему](t.me/dr_forse), я всего лишь бот.', parse_mode = 'markdown')
            await state.finish()
        elif doc['status'] == '3':
            await jr.send_message(m.chat.id, 'Дневной розыгрыш уже окончен, возвращайся завтра или зайди на гитхаб(в описании), возьми код, сделай розыгрыш постоянным и захости у себя, если, конечно не ужаснешься тому, какой это говнокод.')
            await state.finish()
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())
        await state.finish()

@jp.callback_query_handler(lambda call: call.data == 'accept')
async def checking(call):
    try:
        call.data
        tdoc = collection2.find_one({'user': call.message.chat.id})
        main_chat = tdoc['main_chat']
        doc = collection2.find_one({'group': main_chat})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']
        if call.data == 'accept':
            member = await jr.get_chat(main_chat)
            if member.username != None:
                to_chat = await jr.get_chat(main_chat)
                await jr.send_message(call.message.chat.id, 'Хорошо. Задание в группе [{}](t.me/{}) оглашено.'.format(to_chat.title, to_chat.username), parse_mode = 'markdown')
            else:
                to_chat = await jr.get_chat(main_chat)
                await jr.send_message(call.message.chat.id, 'Хорошо. Задание в группе [{}](t.me/c/{}) оглашено.'.format(to_chat.title, main_chat), parse_mode = 'markdown')
            collection2.update_one({'group': main_chat},
                                   {'$set': {'mission_text': tdoc['mission']}})
            collection2.update_one({'group': main_chat},
                                   {'$set': {'status': '2'}})
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data = 'mission')
            jester_mission_kb.add(butt)
            await jr.send_message(main_chat, 'Всем внимание на <a href = "tg://user?id={}">Шута Дня</a>'.format(first_user), parse_mode = 'html', reply_markup = jester_mission_kb)
    except:
        print(traceback.format_exc())

@jp.callback_query_handler(lambda call: call.data == 'mission')
async def jester_mission(call):
    try:
        call.data
        doc = collection2.find_one({'group': call.message.chat.id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']  
        if call.from_user.id == first_user or call.from_user.id == second_user or call.from_user.id == king:
            await jr.answer_callback_query(callback_query_id=call.id, text=doc['mission_text'], show_alert=True)
        else:
            await jr.answer_callback_query(callback_query_id=call.id, text='Вы не можете прочитать это', show_alert=False)
    except:
        print(traceback.format_exc())

async def reset_game_shcedule():
    collection2.update_many({'group': {'$exists': True}},
                           {'$set': {'status': '0'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset': {'first_today_user':'$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset':{'second_today_user':'$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset':{'king':'$exists'}})


    
schedule.every().day.at("00:00").do(reset_game_shcedule)

'''
async def run_continuously(self, interval=1):

        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            async def run(cls):
                while not cease_continuous_run.is_set():
                    self.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run
'''
'''BotFather'''
async def update_flood():
    doc = col2.find_one({'users':{'$exists':True}})['users']
    col2.replace_one({'users':{'$exists':True}},
                     {'users': doc})
schedule.every(6).hours.do(update_flood)

async def anti_flood(message):
    try:
        if message.from_user.id not in col2.find_one({'users': {'$exists': True}})['users']:
                        col2.update_one({'users':{'$exists': True}},
                                        {'$push':{'users': message.from_user.id}})
                        col2.update_one({'users':{'$exists': True}},
                                        {'$set':{str(message.from_user.id): 0}})
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] < 6:
            col2.update_one({'users':{'$exists': True}},
                            {'$inc':{str(message.from_user.id): 1}},
                            upsert = True)
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] == 6:
            await bot.send_message(message.chat.id, 'Хватит страдать хуйней!')
            col2.update_one({'users':{'$exists': True}},
                            {'$inc':{str(message.from_user.id): 1}},
                            upsert = True)
        if await bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except:
        print(traceback.format_exc())
class bann_mute:
    async def ban(message):
        try:
            if message.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() == '!бан':
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                else:               
                    await bot.send_message(message.chat.id, '!уебан', reply_to_message_id = message.message_id)
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
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))
    async def mute(message):
        try:
            if message.text.lower() in mute_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    await anti_flood(message)
            if message.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
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
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username)) 
        
    
#developers_only

    
@dp.message_handler(commands = ['help_define'])
async def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        await bot.send_message(message.from_user.id, 'Define the help-message')
        await bot.delete_message(message.chat.id, message.message_id)
        await Form.help_define1.set()
    else:
        await bot.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')
@dp.message_handler(state=Form.help_define1)
async def help_message_handler(message, state = FSMContext):
    global help_definer
    if message.chat.id == help_definer:
        collection.update_one({'id': 0},
                              {'$set': {'help_msg': message.text}},
                              upsert=True)
        await bot.send_message(message.chat.id, '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным, а не программированием, погуляй, например', parse_mode = 'markdown')
        await state.finish()

#IT-commands
@dp.message_handler(commands = ['ke'])
async def kelerne(message):
    await bot.send_message(message.chat.id, 'lerne', reply_to_message_id = message.message_id)
    
@dp.message_handler(commands = ['chat_id'])
async def chat_id(message):
    await bot.send_message(message.chat.id, '`{}`'.format(message.chat.id),parse_mode = 'markdown')

@dp.message_handler(commands = ['user'])
async def user_info(m):
    try:
        if m.reply_to_message:
            await bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.last_name, m.reply_to_message.from_user.language_code, m.reply_to_message.from_user.username, m.reply_to_message.from_user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
        elif len(m.text.split())>1:
            try:
                member = await bot.get_chat_member(m.chat.id, m.text.split()[1])
                await bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(member.user.first_name, member.user.last_name, member.user.language_code, member.user.username, member.user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
            except:
                await bot.send_message(m.chat.id, 'Аргументы неверны, или владельца id нет в чате')
        else:
            await bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(m.from_user.first_name, m.from_user.last_name, m.from_user.language_code, m.from_user.username, m.from_user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
    except:
        print(traceback.format_exc())
    
#Users
@dp.message_handler(commands = ['help'])
async def show_help(message):
    doc = collection.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith('/help@botsdaddyybot'):
        await bot.send_message(message.from_user.id, help_msg, parse_mode = 'markdown')
        await bot.send_message(message.chat.id, 'Отправил в лс')
    elif message.chat.type == 'private':
        await bot.send_message(message.chat.id, help_msg, parse_mode = 'markdown')

@dp.message_handler(commands = ['pintime'])
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
            anti_flood(message)
    except AttributeError:
        member = await bot.get_chat_member(message.chat.id, bot_id)
        if member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

@dp.message_handler(commands = ['pin'])
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
        await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

@dp.message_handler(commands = ['unpin'])
async def unpin(message):
    try:
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            await bot.send_message(message.chat.id, 'Only for groups', reply_to_message_id = message.message_id)
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
        await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))   
        
@dp.message_handler(commands = ['pinlist'])
async def get_pinned_messages(message):
    if message.text.startswith('/pinlist@botsdaddyybot'):
        try:
            document = collection.find_one({'Group': message.chat.id})
            text=''        
            document.pop('_id')
            for ids in document:
                if ids == '_id':
                    continue
                elif ids == 'Group':
                    text += "{}: <a href='t.me/{}'>{}</a>\n".format('Group', message.chat.username, message.chat.title)
                else:
                    text += '<a href="t.me/{}/{}">{}</a>: {}\n'.format(document[ids][0]['group'], ids, document[ids][0]['date'], document[ids][0]['msg'])
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    await bot.send_message(message.from_user.id, text[x:x+4096], parse_mode = 'html', disable_web_page_preview = True)
            else:
                await bot.send_message(message.from_user.id, text, parse_mode = 'html', disable_web_page_preview = True)
            await bot.send_message(message.chat.id, 'Отправил тебе в лс')
        except Exception:
            await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

async def get_response_json(request):
    response = requests.get(request)
    return response.json()
@dp.message_handler(commands = ['time'])
async def send_time(m):
    try:
        if len(m.text.split()) > 1:
            tz = m.text.split()[1]
            if len(m.text.split()) > 2:
                for i in m.text.split()[2:]:
                    tz+=' '+i
            lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
            postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(geotoken, tz)
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
        if len(hour) == 1:
            hour = '0'+hour
        if len(minute) == 1:
            minute = '0'+minute
        if len(second) == 1:
            second = '0'+second
        time_format = '{}:{}:{}'.format(hour, minute, second)
        await bot.send_message(m.chat.id, time_format)
    except:
        print(traceback.format_exc())
    
@dp.message_handler(content_types = ['text'])
async def ban_mute(message):
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
    if message.text in OD_flood_list:
        await bot.delete_message(message.chat.id, message.message_id)
    
@dp.message_handler(content_types = ['pinned_message'])
async def store_pinned_messages(message):
    try:
                message_text = message.pinned_message.text
                if '<' in message.pinned_message.text:
                    message_text = message_text.replace('<', '&lt;')
                if '<' in message.pinned_message.text:
                    message_text = message_text.replace('>', '&gt;')
                collection.update_one({'Group': message.chat.id},
                                      {'$set': {str(message.pinned_message.message_id): [
                                          {'date': str(date.today()),
                                           'msg': str(message_text),
                                           'group': str(message.chat.username),
                                           'group_title': str(message.chat.title)}
                                              ]}},
                                      upsert = True)  
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

##def schedule_kostil():
##    while True:
##        schedule.run_pending()
##        time.sleep(1)
##threading.Thread(None, schedule_kostil)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

async def jr_on_startup(jp):
    pass

async def jr_on_shutdown(jp): 
    pass

    
def webh(robot, disp, on_start, on_shut):
    Bot.set_current(disp.bot)
    Dispatcher.set_current(disp) 
    start_webhook(dispatcher=disp, webhook_path=WEBHOOK_PATH, on_startup=on_start, on_shutdown=on_shut, skip_updates=True, host='0.0.0.0', port=os.getenv('PORT'))

def kostil(robot, disp, on_start, on_shut):
    asyncio.set_event_loop(asyncio.new_event_loop())
    webh(robot, disp, on_start, on_shut)
    asyncio.get_event_loop.run_forever()

kostil(bot, dp, on_startup, on_shutdown)
kostil(jr, jp, jr_on_startup, jr_on_shutdown)
'''

t = threading.Timer(1, kostil, args=[bot, dp, on_startup, on_shutdown])
t.start()
t = threading.Timer(1, kostil, args=[jr, jp, jr_on_startup, jr_on_shutdown])
t.start()
'''

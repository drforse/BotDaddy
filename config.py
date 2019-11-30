import pymongo
import asyncio
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from timezonefinder import TimezoneFinder


API_TOKEN = os.environ['daddy_token']

loop = asyncio.get_event_loop()

storage = MemoryStorage()
client = pymongo.MongoClient(os.environ['daddy_db'])
db = client.bot_father
collection = db.pin_list
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)
col2 = db.users
colv = db.veganwars_helper
colh = db.her_morzhovij
col_groups_users = db.groups_and_users
col_sessions = db.sessions
banned = col2.find_one()

developers = [879343317]
bot_user = loop.run_until_complete(bot.get_me())
bot_id = bot_user.id
bot_user = bot_user.username

OSM_API = os.environ['OSM_API']
geotoken = os.environ['geotoken']
tf = TimezoneFinder(in_memory=True)

tg_api_id = int(os.environ['tg_api_id'])
tg_api_hash = os.environ['tg_api_hash']

ban_keywords_list = ['!иди в баню', '!иди в бан', '!банан тебе в жопу', '!нам будет тебя не хватать', '/ban',
                     '/ban@botsdaddyybot']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban', '/unban@botsdaddyybot']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
OD_flood_list = ["Да как ты разговариваешь со старшими!"]
ban_mute_list = ban_keywords_list + unban_keywords_list + mute_keywords_list + unmute_keywords_list
hang_bot_flood = {}

compliments = ['ты сегодня такая красивая(ый)!',
               'твои губки напоминают мне сочные вишенки, за которые хочется укусить ~_~',
               'привет, ты с какой звезды детка',
               'даа, покажи мне свои мускулы, они такие красивыее',
               'твои волосы такие прекрасные, как ты за ними ухаживаешь?']


class Form(StatesGroup):
    help_define = State()
    fwded_msgs = State()
    add_to_list = State()

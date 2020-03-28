from bot.user_commands import *
from bot.it_commands import *
from bot.dev_commands import *
from aiogram import executor
from config import dp, developers
import logging

logging.basicConfig(level=logging.INFO)

# IT-commands
Kelerne().register(commands=['ke'])
ChatId().register(commands=['chat_id'])
Ping().register(commands=['ping'])
UserInfo().register(commands=['user'])
GetMessage().register(commands=['get_message'])

# Users
Commands().register(commands=['commands'])
GetFirstMsg().register(commands=['get_first_msg'])
Help().register(commands=['help'])
Pin().register(commands=['pin'])
PinList().register(commands=['pinlist'])
PinTime().register(commands=['pintime'])
Q().register(commands=['q'])
Mask().register(commands=['mask'])
Spell().register(commands=['spell'])
Start().register(commands=['start'])
Time().register(commands=['time'])
Unpin().register(commands=['unpin'])
Weather().register(commands=['weather'])
Her().register(commands=['her'])
RunCHanger().register(commands=['run_changer'])
HangStatsSwitch().register(commands=['hangstats_switch'])
Winrate().register(commands=['winrate'])
Cancel().register(commands=['cancel'], state='*')

# Developers
Logs().register(lambda m: m.from_user.id in developers, commands=['logs'])
Reload().register(lambda m: m.from_user.id in developers, commands=['reload'])
Aeval().register(lambda m: m.from_user.id in developers, commands=['aeval'])
Aexec().register(lambda m: m.from_user.id in developers, commands=['aexec'])
DefineSession().register(lambda m: m.from_user.id in developers, commands=['define_session'])
Hupload().register(lambda m: m.from_user.id in developers and m.caption.startswith('/hupload'),
                   content_types=['document'])
Popen().register(lambda m: m.from_user.id in developers, commands=['popen'])
PopenDoc().register(lambda m: m.from_user.id in developers and m.caption.startswith('/popen'),
                    content_types=['document'])

# import BotDaddy

executor.start_polling(dp, skip_updates=True)

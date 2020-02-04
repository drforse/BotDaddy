from telethon import TelegramClient
from config import TG_API_ID, TG_API_HASH, col_sessions
from config import bot, developers, API_TOKEN
from urllib import request
import logging
import traceback
import os


async def get_session_file():
    message_id = col_sessions.find_one({'_id': {'$exists': True}})['main_session']
    m = await bot.forward_message(developers[0], developers[0], message_id)
    await bot.delete_message(m.chat.id, m.message_id)
    session_document = m.document
    session_file = await bot.get_file(session_document.file_id)
    path = f'https://api.telegram.org/file/bot{API_TOKEN}/{session_file.file_path}'
    request.urlretrieve(path, 'main_session.session')

with open('main_session.session', 'wb') as f:
    try:
        try:
            os.environ['heroku_app_name']
            bot.loop.run_until_complete(get_session_file())
        except KeyError:
            logging.warning('It\'s not HEROKU!')
            pass
        client = TelegramClient(session='main_session',
                                api_id=TG_API_ID,
                                api_hash=TG_API_HASH)
    except:
        logging.error(msg=traceback.format_exc())
        logging.error(msg='telethon client not defined (probably, session_file not found)')
        pass


# with client:
#     print(client.loop.run_until_complete(client.get_me()))


class FirstMessage:
    def __init__(self, msg):
        self.m = msg
        self.link = None

    async def get_link(self):
        async with client:
            chat = self.m.chat.username or self.m.chat.id
            m = await client.get_messages(entity=chat, ids=[self.m.message_id])
            m = m[0]
            first_msg = await client.get_messages(entity=chat, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            if m.chat.username:
                self.link = f't.me/{m.chat.username}/{first_msg.id}'
            else:
                self.link = f't.me/c/{m.chat.id}/{first_msg.id}'
            return self.link

    async def get_id(self):
        async with client:
            chat = self.m.chat.username or self.m.chat.id
            m = await client.get_messages(entity=chat, ids=[self.m.message_id])
            m = m[0]
            first_msg = await client.get_messages(entity=chat, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            return first_msg.id

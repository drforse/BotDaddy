from telethon import TelegramClient
from config import tg_api_id, tg_api_hash, col_sessions
from config import bot, developers, API_TOKEN
from urllib import request
import logging


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
        bot.loop.run_until_complete(get_session_file())
        client = TelegramClient(session='main_session',
                                api_id=tg_api_id,
                                api_hash=tg_api_hash)
    except:
        logging.error(msg='telethon client not defined (probably, session_file not found)')
        pass


class FirstMessage:
    def __init__(self, msg):
        self.m = msg
        self.link = None

    async def get_link(self):
        async with client:
            m = await client.get_messages(entity=self.m.chat.id, ids=[self.m.message_id])
            m = m[0]
            first_msg = await client.get_messages(entity=m.chat.id, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            if m.chat.username:
                self.link = f't.me/{m.chat.username}/{first_msg.id}'
            else:
                self.link = f't.me/c/{m.chat.id}/{first_msg.id}'
            return self.link

    async def get_id(self):
        async with client:
            m = await client.get_messages(entity=self.m.chat.id, ids=[self.m.message_id])
            m = m[0]
            first_msg = await client.get_messages(entity=m.chat.id, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            return first_msg.id

from telethon import TelegramClient
from config import tg_api_id, tg_api_hash, col_sessions


with open('main_session.session', 'wb') as f:
    f.write(col_sessions.find_one({'_id': {'$exists': True}})['main_session'])

client = TelegramClient(session='main_session',
                        api_id=tg_api_id,
                        api_hash=tg_api_hash)


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

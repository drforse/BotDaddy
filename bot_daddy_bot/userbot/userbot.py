from telethon import TelegramClient
from telethon.sessions import StringSession

from ..config import TG_API_ID, TG_API_HASH#, TELETHON_SESSION_STRING


class FirstMessage:
    def __init__(self, msg):
        self.m = msg
        self.link = None
        self.client = TelegramClient(
            session=StringSession(TELETHON_SESSION_STRING),
            api_id=TG_API_ID,
            api_hash=TG_API_HASH)

    async def get_link(self):
        async with self.client:
            chat = self.m.chat.username or self.m.chat.id
            m = await self.client.get_messages(entity=chat, ids=[self.m.message_id])
            m = m[0]
            first_msg = await self.client.get_messages(entity=chat, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            if m.chat.username:
                self.link = f't.me/{m.chat.username}/{first_msg.id}'
            else:
                self.link = f't.me/c/{m.chat.id}/{first_msg.id}'
            return self.link

    async def get_id(self):
        async with self.client:
            chat = self.m.chat.username or self.m.chat.id
            m = await self.client.get_messages(entity=chat, ids=[self.m.message_id])
            m = m[0]
            first_msg = await self.client.get_messages(entity=chat, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            return first_msg.id

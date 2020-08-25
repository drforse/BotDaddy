from ..mixin_types import TelethonClient


class FirstMessage:
    def __init__(self, msg):
        self.m = msg
        self.link = None

    async def get_link(self):
        client = TelethonClient.get_current()
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
        client = TelethonClient.get_current()
        async with client:
            chat = self.m.chat.username or self.m.chat.id
            m = await client.get_messages(entity=chat, ids=[self.m.message_id])
            m = m[0]
            first_msg = await client.get_messages(entity=chat, from_user=m.from_id, limit=1, reverse=True)
            first_msg = first_msg[0]
            return first_msg.id

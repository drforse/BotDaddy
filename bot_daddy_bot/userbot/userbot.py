from aiogram.types import Message as BotApiMessage
from telethon.tl.types import Message

from ..mixin_types import TelethonClient


class FirstMessage:
    def __init__(self, msg: BotApiMessage):
        self.m = msg
        self._message = None
        self.link = None

    async def get_link(self):
        m = await self.message
        if m.chat.username:
            self.link = f't.me/{m.chat.username}/{m.id}'
        else:
            self.link = f't.me/c/{m.chat_id}/{m.id}'.replace("-100", "")
        return self.link

    async def get_id(self):
        """left for backward compatibility after creating message property"""
        return (await self.message).id

    @property
    async def message(self) -> Message:
        """
        gets the first message
        in case if message is sent by channel or group -> retrieves all messages and does filtering here
        in case if message is sent by user -> search request (from_user=m.from_user.id), so filtering is on telegram side
        it's made different because didn't work with from_user==channel_id/group_id neither 1087968824 or 777000
        """
        if self._message:
            return self._message
        client = TelethonClient.get_current()
        chat = self.m.chat.username or self.m.chat.id
        if self.m.sender_chat:
            messages = client.iter_messages(
                entity=chat,
                reverse=True,
            )
            async for msg in messages:
                if msg.sender_id == self.m.sender_chat.id:
                    self._message = msg
                    return msg
                elif self.m.from_user.id == 1087968824 and msg.sender_id is None:
                    return msg

        # needed for getting sender's input entity
        await client.get_messages(entity=chat, ids=[self.m.message_id])

        first_msg = await client.get_messages(
            entity=chat,
            from_user=self.m.from_user.id,
            limit=1,
            reverse=True
        )
        first_msg = first_msg[0]
        self._message = first_msg
        return self._message

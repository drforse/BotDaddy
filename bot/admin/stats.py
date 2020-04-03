from config import col_groups_users, bot
import typing
from aiogram.types import Chat
from aiogram import exceptions


class GroupsStats:
    def __init__(self, chats: typing.Iterable[Chat], inactive_chats: typing.Iterable[int] = None):
        self.chats = chats
        self.inactive_chats = inactive_chats or []

    def pformat(self):
        s = ''
        print([f'{i.id}: {i.title} @{i.username or " "}\n'.replace(' @ ', '') for i in self.chats])
        s = s.join([f'{i.id}: {i.title} @{i.username or " "}\n'.replace(' @ ', '') for i in self.chats])
        s += f'Всего: {len(self.chats)}\n'
        s += f'Неактивные чаты: {len(self.inactive_chats)}'
        return s


class UsersStats:
    def __init__(self, chats: typing.Iterable[Chat], inactive_chats: typing.Iterable[int] = None):
        self.chats = chats
        self.inactive_chats = inactive_chats or []

    def pformat(self):
        s = ''
        s = s.join([f'{i.id}: {i.first_name or ""} {i.last_name or ""} @{i.username or " "}\n'.replace(' @ ', '') for i in self.chats])
        s += f'Всего: {len(self.chats)}\n'
        s += f'Неактивные чаты: {len(self.inactive_chats)}'
        return s


class Stats:

    @staticmethod
    async def get_groups():
        groups_doc = col_groups_users.find({'group': {'$exists': True}})
        groups = []
        inactive_chats = []
        for g in groups_doc:
            try:
                chat = await bot.get_chat(g['group'])
                groups.append(chat)
            except exceptions.ChatNotFound:
                inactive_chats.append(g)
        return GroupsStats(groups, inactive_chats)

    @staticmethod
    async def get_users() -> UsersStats:
        users_doc = col_groups_users.find({'user': {'$exists': True}})
        users = []
        inactive_chats = []
        for u in users_doc:
            try:
                chat = await bot.get_chat(u['user'])
                users.append(chat)
            except exceptions.ChatNotFound:
                inactive_chats.append(u)
        return UsersStats(users, inactive_chats)


__all__ = ['GroupsStats', 'UsersStats', 'Stats']

from config import col_groups_users, bot
import typing
from aiogram.types import Chat
from aiogram import exceptions
from aiogram_bots_own_helper import replace_html
# import traceback


class GroupsStats:
    def __init__(self, chats: typing.Iterable[Chat], inactive_chats: typing.Iterable[int] = None,
                 inactive_reasons: typing.Iterable = None):
        self.chats = chats
        self.inactive_chats = inactive_chats or []
        self.inactive_reasons = inactive_reasons or []

    def pformat(self, parse_mode=None):
        s = ''
        if parse_mode.lower() == 'html':
            s = s.join([f'<code>{i.id}</code>: {replace_html(i.title)} @{replace_html(i.username) or " "}'
                        f'\n'.replace(' @ ', '') for i in self.chats])
        elif not parse_mode:
            s = s.join([f'{i.id}: {i.title} @{i.username or " "}\n'.replace(' @ ', '') for i in self.chats])
        s += f'Всего: {len(self.chats)}\n'
        s += f'Неактивные чаты: {len(self.inactive_chats)}\n\n'
        s += 'Причины: ' + '\n'.join([e for e in self.inactive_reasons])
        return s


class UsersStats:
    def __init__(self, chats: typing.Iterable[Chat], inactive_chats: typing.Iterable[int] = None,
                 inactive_reasons: typing.Iterable = None):
        self.chats = chats
        self.inactive_chats = inactive_chats or []
        self.inactive_reasons = inactive_reasons or []

    def pformat(self, parse_mode=None):
        s = ''
        if parse_mode.lower() == 'html':
            s = s.join([f'<code>{i.id}</code>: {replace_html(i.first_name) or ""} {replace_html(i.last_name) or ""}'
                        f' @{replace_html(i.username) or " "}\n'.replace(' @ ', '') for i in self.chats])
        elif not parse_mode:
            s = s.join([f'{i.id}: {i.first_name or ""} {i.last_name or ""}'
                        f' @{i.username or " "}\n'.replace(' @ ', '') for i in self.chats])
        s += f'Всего: {len(self.chats)}\n'
        s += f'Неактивные чаты: {len(self.inactive_chats)}\n\n'
        s += 'Причины: ' + '\n'.join([e for e in self.inactive_reasons])
        return s


class Stats:

    @staticmethod
    async def get_groups(migrated_chats_update=True):
        groups_doc = col_groups_users.find({'group': {'$exists': True}})
        groups = []
        inactive_chats = []
        inactive_reasons = []

        async def _check_group(g):
            try:
                chat = await bot.get_chat(g['group'])
                await bot.send_chat_action(chat.id, 'typing')
                groups.append(chat)
            except exceptions.MigrateToChat as e:
                if migrated_chats_update:
                    new_id = e.migrate_to_chat_id
                    await Stats.unregister_chat(int(g['group']))
                    chat = await Stats.register_chat(int(new_id))
                    return await _check_group(chat)
                inactive_chats.append(g)
                if str(e) not in inactive_reasons:
                    inactive_reasons.append(str(e))
                return
            except Exception as e:
                inactive_chats.append(g)
                if str(e) not in inactive_reasons:
                    inactive_reasons.append(str(e))

        for g in groups_doc:
            await _check_group(g)

        return GroupsStats(groups, inactive_chats, inactive_reasons)

    @staticmethod
    async def get_users() -> UsersStats:
        users_doc = col_groups_users.find({'user': {'$exists': True}})
        users = []
        inactive_chats = []
        inactive_reasons = []
        for u in users_doc:
            try:
                chat = await bot.get_chat(u['user'])
                await bot.send_chat_action(chat.id, 'typing')
                users.append(chat)
            # except TypeError:
            #     print(traceback.format_exc())
            except Exception as e:
                inactive_chats.append(u)
                if str(e) not in inactive_reasons:
                    inactive_reasons.append(str(e))
        return UsersStats(users, inactive_chats, inactive_reasons)

    @staticmethod
    async def register_chat(chat_id: int, upsert=True):
        if chat_id > 1:
            col_groups_users.update_one({'user': chat_id},
                                        {'$set': {'user': chat_id}},
                                        upsert=upsert)
            return col_groups_users.find_one({'group': chat_id})
        col_groups_users.update_one({'group': chat_id},
                                    {'$set': {'group': chat_id}},
                                    upsert=upsert)
        return col_groups_users.find_one({'group': chat_id})

    @staticmethod
    async def unregister_chat(chat_id: int):
        if chat_id > 1:
            col_groups_users.delete_one({'user': chat_id})
            return
        col_groups_users.delete_one({'group': chat_id})


__all__ = ['GroupsStats', 'UsersStats', 'Stats']

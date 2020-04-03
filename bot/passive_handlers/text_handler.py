from ..core import Command
from config import col_groups_users, colh, ban_mute_list, hang_bot_flood
from ..funcs import anti_flood, itisbadmessage, log_err, BanMute
from aiogram.types import Message
import traceback


class TextHandler(Command):

    @staticmethod
    async def execute(m: Message):
        try:
            if m.chat.type != 'private':
                doc = col_groups_users.find_one({'group': m.chat.id})
                if not doc:
                    col_groups_users.insert_one({'group': m.chat.id,
                                                 'users': [m.from_user.id]})
                elif m.from_user.id not in doc['users']:
                    col_groups_users.update_one({'group': m.chat.id},
                                                {'$push': {'users': m.from_user.id}})
            else:
                doc = col_groups_users.find_one({'user': m.chat.id})
                if not doc:
                    col_groups_users.insert_one({'user': m.chat.id})
            if m.text.lower() in ban_mute_list:
                try:
                    await BanMute(m).ban()
                    await BanMute(m).mute()
                except AttributeError:
                    await anti_flood(m)
            elif m.reply_to_message and m.reply_to_message.from_user.id == 121913006 or\
                    m.text.lower() == '/start@hangbot':
                if m.chat.id not in hang_bot_flood:
                    hang_bot_flood[m.chat.id] = [m]
                hangbot_flood = hang_bot_flood[m.chat.id]
                hangbot_flood.append(m)
                hang_bot_flood[m.chat.id] = hangbot_flood
            bydlodoc = colh.find_one({'bydlos': 'future',
                                      'group': m.chat.id})
            if bydlodoc:
                if str(m.from_user.id) not in bydlodoc:
                    colh.update_one({'bydlos': 'future',
                                     'group': m.chat.id},
                                    {'$set': {str(m.from_user.id): {'allmsgs': 0,
                                                                          'badmsgs': 0}}})
                    bydlodoc = colh.find_one({'bydlos': 'future',
                                              'group': m.chat.id})
                if 'allmsgs' in bydlodoc[str(m.from_user.id)]:
                    msgs = bydlodoc[str(m.from_user.id)]['allmsgs'] + 1
                else:
                    msgs = 1
                if itisbadmessage(m):
                    if 'badmsgs' in bydlodoc[str(m.from_user.id)]:
                        badmsgs = bydlodoc[str(m.from_user.id)]['badmsgs'] + 1
                    else:
                        badmsgs = 1
                else:
                    badmsgs = bydlodoc[str(m.from_user.id)]['badmsgs']
                colh.update_one({'bydlos': 'future',
                                 'group': m.chat.id},
                                {'$set': {str(m.from_user.id): {'allmsgs': msgs,
                                                                      'badmsgs': badmsgs}}})
            else:
                badmsgs = 1 if itisbadmessage(m) else 0
                colh.insert_one({'bydlos': 'future',
                                 'group': m.chat.id,
                                 str(m.from_user.id): {'allmsgs': 1,
                                                             'badmsgs': badmsgs}})
                print(colh.find_one({'bydlos': 'future',
                                     'group': m.chat.id}))
        except:
            await log_err(m=m, err=traceback.format_exc())
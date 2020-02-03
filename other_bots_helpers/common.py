import json
import requests
from aiogram.utils import exceptions


async def get_hangbot_winrate(wins, loses):
    games = wins + loses
    percent = games / 100
    winrate = wins / percent
    winrate = round(winrate, 2)
    return winrate


async def get_monolog(bot, m, first_fwd_msg):
    text = ''
    last_fwd_msg = m.message_id
    forwarded_messages = range(first_fwd_msg + 1, last_fwd_msg)
    if len(forwarded_messages) == 0:
        return 'No messages found'
    for i in forwarded_messages:
        try:
            mssg = await bot.forward_message(m.chat.id, m.chat.id, i, disable_notification=True)
            msg = mssg.text
            await bot.delete_message(m.chat.id, mssg.message_id)
            text += f'{msg}\n'
        except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
            pass
    return text


async def get_dialog(bot, m, first_fwd_msg):
    xyz = ['x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']
    text = ''
    last_fwd_msg = m.message_id
    forwarded_messages = range(first_fwd_msg + 1, last_fwd_msg)
    if len(forwarded_messages) == 0:
        return 'No messages found'
    senders_by_xyz = {}
    senders = []
    senders_quant = 0
    for i in forwarded_messages:
        try:
            mssg = await bot.forward_message(m.chat.id, m.chat.id, i, disable_notification=True)
            msg = mssg.text
            sender = mssg.forward_from if mssg.forward_from else mssg.from_user
            if sender.id in senders:
                xxx = senders_by_xyz[sender.id]
            else:
                try:
                    xxx = xyz[senders_quant]
                    senders_by_xyz[sender.id] = xxx
                    senders.append(sender.id)
                    senders_quant += 1
                except IndexError:
                    return 'Sorry, the maximum amount of senders is 23'
            await bot.delete_message(m.chat.id, mssg.message_id)
            text += f'{xxx*3}: {msg}\n'
        except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
            pass
    return text


async def yaspeller(q):
    try:
        answer = requests.get(f'https://speller.yandex.net/services/spellservice.json/checkText?text={q}&options=4').json()
        text = q.replace(answer[0]['word'], answer[0]['s'][0])
        for i in answer[1:]:
            text = text.replace(i['word'], i['s'][0])
        return text
    except IndexError:
        return q

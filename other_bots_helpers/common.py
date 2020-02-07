import requests
from aiogram.utils import exceptions
import typing
from config import SERVICE_ACCOUNT_ID
import aiogram


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


async def get_dialog(bot, m, first_fwd_msg, markers_dictionary=None):
    def_xyz = ['x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']
    xyz = markers_dictionary or def_xyz
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
            sender = mssg.forward_from or mssg.forward_sender_name or mssg.from_user
            sender = sender if isinstance(sender, str) else sender.id
            if sender in senders:
                xxx = senders_by_xyz[sender]
            else:
                try:
                    xxx = xyz[senders_quant]
                    senders_by_xyz[sender] = xxx
                    senders.append(sender)
                    senders_quant += 1
                except IndexError:
                    return (f'Извините, максимально количество учатников - {len(xyz)}.\n\n'
                            f'Вы можете добавить свой словарь с любым количеством участников в меню настроек: '
                            f'/fwd_to_text (количество участников зависит от количества знаков в словаре)')
            await bot.delete_message(m.chat.id, mssg.message_id)
            text += f'{xxx*3}: {msg}\n'
        except (exceptions.MessageToForwardNotFound, exceptions.MessageToDeleteNotFound):
            pass
    return text


async def check_markers_dict(bot: aiogram.Bot, markers_dict: typing.Sequence[str]):
    if not isinstance(markers_dict, list):
        raise Exception('check_markers_dict: markers_dict argument must be list or string')
    markers_dict = [i.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') for i in markers_dict]
    wrong_markers = []
    for i in markers_dict:
        try:
            await bot.send_message(SERVICE_ACCOUNT_ID, i*3, parse_mode='html')
        except:
            wrong_markers.append(i)
    for i in wrong_markers:
        del markers_dict[markers_dict.index(i)]
    return {'markers_dict': markers_dict,
            'wrong_markers': wrong_markers}


async def yaspeller(q):
    try:
        answer = requests.get(f'https://speller.yandex.net/services/spellservice.json/checkText?text={q}&options=4').json()
        text = q.replace(answer[0]['word'], answer[0]['s'][0])
        for i in answer[1:]:
            text = text.replace(i['word'], i['s'][0])
        return text
    except IndexError:
        return q

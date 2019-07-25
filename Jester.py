import pymongo
from pymongo import MongoClient
import traceback
import asyncio
import logging
import aiocron
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils import exceptions
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
import random
import os
import time
import datetime
from datetime import datetime

API_TOKEN_JR = os.environ['token_jr']

WEBHOOK_HOST = os.environ['heroku_app']
WEBHOOK_PORT = 443
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.WARNING)

loop = asyncio.get_event_loop()



client_jr = pymongo.MongoClient(os.environ['db_jr'])
db_jr = client_jr.test
collection2 = db_jr.bottle
col_private = db_jr.privates
jr = Bot(API_TOKEN_JR, loop=loop)
storage = MemoryStorage()
jp = Dispatcher(jr, storage=storage)
jester_user = 'jester_day_bot'
jester_id = 809900920

developers = [500238135]
team = {'main_developer': {'dr_forse': 'George Forse'},
        'testers': [{'dr_forse': 'George Forse'}, {'P1von': 'ApelsinkaS'}, {'kelerne': 'Рин'},
                    {'P0LUNIN': 'polunin.ai'}, {'gbball': 'Брит'}],
        'ideas': {'guesses': {'kelerne': 'Рин'}}}

skyrim_frases = ['Дай-ка угадаю, кто-то украл твой сладкий рулет?', ' Когда-то и меня вела дорога приключений... А потом мне прострелили колено.', 'Мой кузен борется с драконами, а мне что досталось? Караульная служба.', 'Поглядывай в небо и будь настороже!', 'В чем дело, каджит?', 'Это что, мех? У тебя из ушей торчит?', 'Если ты тут какой замок хоть пальцем ковырнешь — я тебе устрою кару божью.', 'Увижу твою руку у себя в кармане — отрублю!', 'Втяни свои когти, каджит.', ]


async def finish_poll_by_command(m):
    doc = collection2.find_one({'group': m.chat.id})
    if 'guess_m_id' in doc:  # added
        poll_m_id = doc['guess_m_id']
        try:
            await jr.edit_message_reply_markup(m.chat.id, poll_m_id)
        except MessageToDeleteNotFound:
            pass
    if doc['status'] == '3':
        rates = {}
        rates_list = []
        chat_id = doc['group']
        guesses = {}
        for key, value in doc.items():
            if key.startswith('guess') and len(key.split())>1 and key.split()[1].isdigit():
                guesses.update({key:value})
        winners = {}
        for guess, rate in guesses.items():
            rates.update({guess: rate})
            rates_list.append(rate)
            win_rate = max(rates_list)
        for guess, rate in rates.items():
            if rate == win_rate:
                winners.update({guess: rate})
        if len(winners) > 1:
            winners_names = ''
            guess_text_to_msg = ''
            for winner in winners:
                winner_id = winner.split()[1]
                member = await jr.get_chat_member(chat_id, winner_id)
                winner_name = member.user.first_name
                winners_names += f'<a href="tg://user?id={winner_id}">{winner_name}, </a>'
                guess_text = winner.split(f'guess {winner_id} ')[1]
                guess_text_to_msg += f'\n<b>{winner_name}:</b>\n {guess_text}'
            await jr.send_message(chat_id, f'{winners_names} выиграли, набрав по {win_rate} голосов со следующими догадками:\n{guess_text_to_msg}', parse_mode='html')
        elif len(winners) == 1:
            for winner in winners:
                winner_id = winner.split()[1]
                member = await jr.get_chat_member(chat_id, winner_id)
                winner_name = member.user.first_name
                guess_text = winner.split(f'guess {winner_id} ')[1]
            await jr.send_message(chat_id, f'<a href="tg://user?id={winner_id}">{winner_name}</a> выиграл(а), набрав {win_rate} голосов со следующей догадкой:\n{guess_text}', parse_mode = 'html')
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'status': '0'}})
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'voted_users': []}})
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'guesses': []}})
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'guessed_users': []}})  # added
        for key in collection2.find_one({'group': m.chat.id}):
            if key.startswith('guess') and len(key.split()) > 1 and key.split()[1].isdigit():
                collection2.update_one({'group': m.chat.id},
                                       {'$unset': {key: {'$exists': True}}})
            if key == 'guess_m_id':  # added
                collection2.update_one({'group': m.chat.id},
                                       {'$unset': {key: {'$exists': True}}})
        for user_doc in col_private.find({'user': {'$exists': True}}):
            if user_doc['user'] in doc['players']:
                for key in user_doc:
                    if key.startswith('guess in'):
                        col_private.update_one({'user': user_doc['user']},
                                               {'$unset': {key: {'$exists': True}}})
        print('Poll has finished by command in client.')
    else:
        await jr.send_message(m.chat.id, 'Сейчас не получится')


async def reset_game_command(m):
    try:
        member = await jr.get_chat_member(m.chat.id, m.from_user.id)
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'status': '0'}})
        collection2.update_one({'group': m.chat.id},
                               {'$unset': {'mission_text': '$exists'}})
        collection2.update_one({'group': m.chat.id},
                               {'$unset': {'first_today_user': '$exists'}})
        collection2.update_one({'group': m.chat.id},
                               {'$unset': {'second_today_user': '$exists'}})
        collection2.update_one({'group': m.chat.id},
                               {'$unset': {'mission_text': '$exists'}})
        collection2.update_one({'group': m.chat.id},
                               {'$unset': {'mission_complete': '$exists'}})
        for userdoc in col_private.find({'user': {'$exists': True}}):
            if userdoc['user'] in collection2.find_one({'group': m.chat.id})['players']:
                col_private.update_one({'user': userdoc['user']},
                                       {'$pull': {'guess_groups': collection2.find_one({'group': m.chat.id})['group']}})
        collection2.update_one({'group': m.chat.id},
                               {'$set': {'status': '3'}})
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())


async def guesses_poll(chat):
    try:
        msg_text = ''
        index = 0
        user_docs = col_private.find({'user': {'$exists': True}})
        buttons_list = []
        for user_doc in user_docs:
            try:
                if 'groups' in user_doc and chat in user_doc['groups'] and f'guess in {chat}' in user_doc:
                    index += 1
                    msg_text += '{}. <i>{}</i>\n'.format(index, user_doc[f'guess in {chat}'])
                    buttons_list.append(types.InlineKeyboardButton(text=index, callback_data='guess {} {}'.format(user_doc['user'], user_doc[f'guess in {chat}'])))
            except (exceptions.ChatNotFound, exceptions.BotKicked, exceptions.Unauthorized):
                pass
        if msg_text != '':
            guesses_kb = types.InlineKeyboardMarkup(row_width=4)
            guesses_kb.add(*buttons_list)
            if len(buttons_list) > 1:
                await jr.send_message(chat, f"Вот догадки игроков о том, каким было задание:\n{msg_text}\nВыбирайте то, что Вам больше нравится и кажется наиболее близким к реальному заданию:", reply_markup=guesses_kb, parse_mode = 'html')
            elif len(buttons_list) == 1:
                await jr.send_message(chat, f"Вот догадки игроков о том, каким было задание:\n{msg_text}", parse_mode='html')
    except:
        print(traceback.format_exc())


@jp.message_handler(content_types=['left_chat_member'])
async def left_member(m):
    try:
        member = await jr.get_chat_member(m.chat.id, m.from_user.id)
        doc = collection2.find_one({'group': m.chat.id})
        try:
            active_players = [doc['first_today_user'], doc['second_today_user'], doc['king']]
            if member.user.id in doc['players'] and member.user.id not in active_players:
                collection2.update_one({'group': m.chat.id},
                                       {'$pull': {'players': m.from_user.id}})
                col_private.update_one({'user': m.from_user.id},
                                       {'$pull': {'groups': m.chat.id}})
            elif member.user.id in doc['players']:
                await reset_game_command(m)
                await finish_poll_by_command(m)
                await jr.send_message(m.chat.id, 'Один из трех основных игроков покинул чат! Придется начать игру заново, нажмите /today_user')
        except (KeyError, TypeError):
            print(traceback.format_exc())
            if member.user.id in doc['players']:
                collection2.update_one({'group': m.chat.id},
                                       {'$pull': {'players': m.from_user.id}})
                col_private.update_one({'user': m.from_user.id},
                                       {'$pull': {'groups': m.chat.id}})
    except:
        print(traceback.format_exc())


class Form(StatesGroup):
    help_define1 = State()
    help_define = State()
    getting_mission = State()
    getting_feedback = State()
    start_guess_mission = State()
    guess_mission = State()
    guess_mission_step2 = State()
    guess_mission_last_step = State()
    mailing = State()


@jp.message_handler(lambda m: m.from_user.id in developers, commands=['mailing'])
async def mailing(message):
    try:
        await jr.send_message(message.from_user.id, 'Send the message to mail')
        await Form.mailing.set()
    except:
        print(traceback.format_exc())


@jp.message_handler(state=Form.mailing)
async def mail_handler(message, state: FSMContext):
    try:
        groups = collection2.find({'group': {'$exists': True}})
        users = col_private.find({'user': {'$exists': True}})
        for group in groups:
            chat_id = group['group']
            try:
                await jr.send_message(chat_id, message.text, parse_mode='markdown')
            except (exceptions.ChatNotFound, exceptions.Unauthorized, exceptions.BotKicked):
                continue
        for user in users:
            chat_id = user['user']
            try:
                await jr.send_message(chat_id, message.text, parse_mode='markdown')
            except (exceptions.CantInitiateConversation, exceptions.ChatNotFound, exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.CantTalkWithBots):
                continue
        await jr.send_message(message.chat.id, 'Finished.')
        await state.finish()
    except:
        print(traceback.format_exc())
        await state.finish()


@jp.message_handler(commands=['bot_team'])
async def bot_team(m):
    try:
        main_dev = team['main_developer']
        main_dev = '<a href="t.me/{}">{}</a>'.format(list(main_dev.keys())[0], main_dev[list(main_dev.keys())[0]])
        testers = team['testers']
        ideas_autors = team['ideas']
        idea_autor = main_dev
        msg_text = f'<b>Автор идеи и главный (и единственный) разработчик</b>:\n{main_dev}\n'
        guesses_idea_autor = '<a href="t.me/{}">{}</a>'.format(list(ideas_autors['guesses'].keys())[0], ideas_autors['guesses'][list(ideas_autors['guesses'].keys())[0]])
        msg_text += f'<b>Автор идеи угадывания задания</b>:\n{guesses_idea_autor}\n<b>Бета-тестеры</b>:\n'
        for tester in testers:
            msg_text += '  ! <a href="t.me/{}">{}</a>\n'.format(list(tester.keys())[0], tester[list(tester.keys())[0]])
        await jr.send_message(m.chat.id, msg_text, reply_to_message_id=m.message_id, parse_mode='html', disable_web_page_preview=True)
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['feedback'])
async def feedback(m: types.Message, state: FSMContext):
    try:
        if len(m.text.split()) > 1:
            await jr.forward_message(developers[0], m.chat.id, m.message_id)
            await jr.send_message(m.chat.id, 'Я передам Ваши слова богу', reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Говорите, что у Вас на уме',
                                  reply_to_message_id=m.message_id,reply_markup=types.ForceReply(selective=True))
            async with state.proxy() as data:
                data['feedback_sender_jr'] = m.from_user.id
            await Form.getting_feedback.set()
    except:
        print(traceback.format_exc())


@jp.message_handler(state=Form.getting_feedback)
async def feedback_handler(m, state: FSMContext):
    async with state.proxy() as data:
        feedback_sender_jr = data['feedback_sender_jr']
    if m.from_user.id == feedback_sender_jr and m.reply_to_message and m.reply_to_message.text == 'Говорите, что у Вас на уме' and (
            time.time() - (m.reply_to_message.date - datetime(1970, 1, 1)).total_seconds()) < 300:
        await jr.forward_message(developers[0], m.chat.id, m.message_id)
        await jr.send_message(m.chat.id, 'Я передам Ваши слова богу', reply_to_message_id=m.message_id)
        await state.finish()
    elif m.text.startswith('/') and jester_user in m.text:
        await state.finish()
    elif m.text.startswith('/') and m.chat.type == 'private':
        await state.finish()


@jp.message_handler(commands=['help_define'])
async def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        await jr.send_message(message.from_user.id, 'Define the help-message')
        await Form.help_define.set()
    else:
        await jr.send_message(message.chat.id, 'Эта команда - только для разработчиков бота!')


@jp.message_handler(state=Form.help_define)
async def help_message_handler(message, state: FSMContext):
    global help_definer
    if message.chat.id == help_definer:
        collection2.update_one({'id': 0},
                               {'$set': {'help_msg': message.text}},
                               upsert=True)
        await jr.send_message(message.chat.id, 'Updated.')
        await state.finish()


@jp.message_handler(commands=['help'])
async def show_help(message):
    doc = collection2.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith(f'/help@{jester_user}'):
        await jr.send_message(message.chat.id, help_msg, parse_mode='markdown')
    elif message.chat.type == 'private':
        await jr.send_message(message.chat.id, help_msg, parse_mode='markdown')


@jp.message_handler(commands=['players'])
async def players_list(m):
    try:
        if collection2.find_one({'group': m.chat.id}) is not None:
            players = ''
            for gamer in collection2.find_one({'group': m.chat.id})['players']:
                if gamer is not None:
                    player = await jr.get_chat_member(m.chat.id, gamer)
                    player = player.user.first_name
                    players += str(player) + ', '
            x = len(players) - 2
            players = players[:x]
            await jr.send_message(m.chat.id, players, reply_to_message_id=m.message_id)
    except exceptions.MessageTextIsEmpty:
        await jr.send_message(m.chat.id, "Пока никто не играет, нажмите /reg_me для регистрации.")
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['leave_jester'])
async def leave_game(m):
    try:
        member = await jr.get_chat_member(m.chat.id, m.from_user.id)
        doc = collection2.find_one({'group': m.chat.id})
        if doc is not None:
            try:
                active_players = [doc['first_today_user'], doc['second_today_user'], doc['king']]
                if member.user.id in doc['players'] and member.user.id not in active_players:
                    collection2.update_one({'group': m.chat.id},
                                           {'$pull': {'players': m.from_user.id}})
                    col_private.update_one({'user': m.from_user.id},
                                           {'$pull': {'groups': m.chat.id}})
                    await jr.send_message(m.chat.id,
                                          'Ну пока, чтоб те здохнуть', reply_to_message_id=m.message_id)
                elif member.user.id in doc['players']:
                    await jr.send_message(m.chat.id, 'Вы - один из основных участников сегодняшней игры, Вы не можете покинуть игру до окончания сегодняшней игры.')
            except (KeyError, TypeError):
                if member.user.id in doc['players']:
                    collection2.update_one({'group': m.chat.id},
                                           {'$pull': {'players': m.from_user.id}})
                    col_private.update_one({'user': m.from_user.id},
                                           {'$pull': {'groups': m.chat.id}})
                    await jr.send_message(m.chat.id,
                                          'Ну пока, чтоб те здохнуть', reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Вы и так не играете.')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['kick'])
async def kick_user(m):
    try:
        kicked_member = await jr.get_chat_member(m.chat.id, m.reply_to_message.from_user.id)
        member_kicker = await jr.get_chat_member(m.chat.id, m.from_user.id)
        if m.chat.type != 'private':
            if member_kicker.user.id in developers or member_kicker.status == 'creator' or member_kicker.can_change_info and member_kicker.can_delete_messages and member_kicker.can_invite_users and member_kicker.can_restrict_members and member_kicker.can_pin_messages and member_kicker.can_promote_members:
                if not kicked_member.can_promote_members and not kicked_member.can_pin_messages and not kicked_member.can_change_info and not kicked_member.can_restrict_members and not kicked_member.can_invite_users and not kicked_member.can_delete_messages and kicked_member.status != 'creator' and kicked_member.user.id not in developers:
                    if kicked_member in collection2.find_one({'group': m.chat.id})['players'] or m.chat.id in col_private.find_one({'user': m.reply_to_message.from_user.id})['groups']:
                        collection2.update_one({'group': m.chat.id},
                                               {'$pull': {'players': m.reply_to_message.from_user.id}})
                        col_private.update_one({'user': m.reply_to_message.from_user.id},
                                               {'$pull': {'groups': m.chat.id}})
                        await jr.send_message(m.chat.id, kicked_member.user.first_name+" был(а) выкинут(а) нахрен из игры")
                    else:
                        await jr.send_message(m.chat.id, kicked_member.user.first_name+" в общем то и не был(а) в игре")
                else:
                    await jr.send_message(m.chat.id, 'Вы не можете его удалить из игры.\n P.s. <i>если вы создатель, а он всего лишь фулладмин, то звиняйте, разрабу лень было норм делать чет, заберите на пару секунд одно из прав прост</i>', parse_mode='html')
            else:
                await jr.send_message(m.chat.id, "Это подвластно только создателю и его приближенным, фулл-админам")
        else:
                await jr.send_message(m.chat.id, 'Эта команда - для групп.')
    except KeyError:
        pass
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['add_key'])
async def add_keyword(m):
    try:
        if col_private.find_one({'user': m.from_user.id}) is not None:
            if m.chat.type == 'private':
                if len(m.text.split()) > 1:
                    user_doc = col_private.find_one({'user': m.from_user.id})
                    command = m.text.split()[0] + ' '
                    keyword = m.text.split(command)[1]
                    if keyword not in user_doc['guess_keys']:
                        col_private.update_one({'user': m.from_user.id},
                                               {'$push': {'guess_keys': keyword}})
                        await jr.send_message(m.chat.id, 'Готово!')
                    else:
                        await jr.send_message(m.chat.id, 'Эти ключевые слова у Вас уже существует')
                else:
                    await jr.send_message(m.chat.id, 'Недостаточно аргументов. Напишите /add_key <ключевые слова>')
            else:
                await jr.send_message(m.chat.id, 'Эта команда - для лс', reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Вы не зарегестрированы ни в одной группе, для начала зарегестрируйтесь')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['del_key'])
async def del_keyword(m):
    try:
        if col_private.find_one({'user': m.from_user.id}) is not None:
            if m.chat.type == 'private':
                if len(m.text.split()) > 1:
                    user_doc = col_private.find_one({'user': m.from_user.id})
                    command = m.text.split()[0] + ' '
                    keyword = m.text.split(command)[1]
                    if keyword in user_doc['guess_keys']:
                        col_private.update_one({'user': m.from_user.id},
                                               {'$pull': {'guess_keys': keyword}})
                        await jr.send_message(m.chat.id, 'Готово!')
                    else:
                        await jr.send_message(m.chat.id, 'Этих ключевых слов у Вас и так нет')
                else:
                    await jr.send_message(m.chat.id, 'Недостаточно аргументов. Напишите /del_key <ключевые слова>')
            else:
                await jr.send_message(m.chat.id, 'Эта команда - для лс', reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Вы не зарегестрированы ни в одной группе, для начала зарегестрируйтесь')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['my_keys'])
async def my_keys(m):
    try:
        if col_private.find_one({'user': m.from_user.id}) is not None:
            if m.chat.type == 'private':
                user_doc = col_private.find_one({'user': m.from_user.id})
                keywords = ''
                for keyword in user_doc['guess_keys']:
                    keywords += f'[ ] {keyword}\n'
                await jr.send_message(m.chat.id, keywords)
            else:
                await jr.send_message(m.chat.id, 'Эта команда - для лс', reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Вы не зарегестрированы ни в одной группе, для начала зарегестрируйтесь')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['reset_game'])
async def reset_game_by_command(m):
    try:
        if m.from_user.id in developers:
            await reset_game_command(m)
            await jr.send_message(m.chat.id, 'Game reseted')
        else:
            await jr.send_message(m.chat.id, 'Эта команда - только для разработчиков бота')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['reg_me'])
async def reg_user(message):
    try:
        if message.chat.type != 'private':
            doc = collection2.find_one({'group': message.chat.id})
            reg_kb = types.InlineKeyboardMarkup()
            reg = types.InlineKeyboardButton('Тык', url='telegram.me/{}?start=reg{}'.format(jester_user, message.chat.id))
            reg_kb.add(reg)
            if collection2.find_one({'group': message.chat.id}) is None:
                collection2.insert_one({'group': message.chat.id,
                                        'players': [],
                                        'status': '0',
                                        'stats': 0})
                await jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id=message.message_id,
                                      reply_markup=reg_kb)
            elif message.from_user.id not in doc['players']:
                await jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id=message.message_id,
                                      reply_markup=reg_kb)
            else:
                await jr.send_message(message.chat.id, 'Вы уже в игре!', reply_to_message_id=message.message_id)
        else:
            await jr.send_message(message.chat.id, 'Нихуя, дыра закрылась, пошел в группу, эта команда для привата!')
    except:
        await jr.send_message(message.chat.id, traceback.format_exc())


@jp.message_handler(commands=['finish_it'])
async def finish_game(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if doc is None and m.chat.type != 'private':
            collection2.insert_one({'group': m.chat.id,
                                    'players': [],
                                    'status': '0',
                                    'stats': 0})
            await jr.send_message(m.chat.id,
                                  'Игра еще не начата, или уже закончена, или задание еще не выполнено (назначено)')
        if m.chat.type == 'private':
            await jr.send_message(m.chat.id, 'Так Вас никто не услышит!')
        elif m.from_user.id not in developers and m.from_user.id != doc['king'] and doc['king']:
            await jr.send_message(m.chat.id, 'Вы - не король!')
        elif doc['status'] == '2':
            time_started = doc['time_started']
            if time.time() - time_started > 3600 or m.from_user.id in developers:
                if len(m.text.split()) < 2:
                    await jr.send_message(m.chat.id, 'Скажите, как Вам понривалось шоу после команды, Ваше Величество',
                                          reply_to_message_id=m.message_id)
                else:
                    list = m.text.split()
                    result = ''
                    for i in range(len(list) - 1):
                        result += list[i + 1] + ' '
                    await jr.send_message(m.chat.id, 'Мнение Его Величества:\n' + result)
                    collection2.update_one({'group': m.chat.id},
                                           {'$set': {'status': '3'}})
                    await jr.send_message(m.chat.id, "Задание было таким:\n" + doc['mission_text'])
                    await show_mission_complete(m.chat.id)
                    await guesses_poll(m.chat.id)
                    await reset_game()
            else:
                time_needed = 3600 - (int(time.time()) - int(time_started))
                if time_needed > 60:
                    time_needed //= 60
                    time_needed = int(time_needed)
                    time_needed = f'{time_needed} минут'
                else:
                    time_needed = int(time_needed)
                    time_needed = f'{time_needed} секунд'
                await jr.send_message(m.chat.id, f'Подождите {time_needed}, чтобы остальные игроки могли поугадывать задание, пожалуйста.',
                                      reply_to_message_id=m.message_id)
        else:

            await jr.send_message(m.chat.id,
                                  'Игра еще не начата, или уже закончена, или задание еще не выполнено (назначено)')
    except KeyError:
        await jr.send_message(m.chat.id, 'game not started yet')
        print(traceback.format_exc())
    except:
        print(traceback.format_exc())


@jp.message_handler(lambda m: m.chat.type != 'private', commands=['today_user'])
async def get_users(message):
    global x
    global message_chat_id
    message_chat_id = message.chat.id
    try:
        x = 0
        doc = collection2.find_one({'group': message.chat.id})
        if doc is None:
            collection2.insert_one({'group': message.chat.id,
                                    'players': [],
                                    'status': '0',
                                    'stats': 0})
            doc = collection2.find_one({'group': message.chat.id})
        list_users = doc['players']
        if len(doc['players']) < 3:
            await jr.send_message(message.chat.id, 'Not enough players, 3 needed.')
        elif doc['status'] == '0':
            if len(message.text.split()) > 1 and message.from_user.id in developers:
                first_user = int(message.text.split()[1])
                second_user = int(message.text.split()[2])
                king = int(message.text.split()[3])
            else:
                first_user = random.choice(list_users)
                second_user = random.choice(list_users)
                king = random.choice(list_users)
                while first_user == second_user:
                    second_user = random.choice(list_users)
                while king == first_user or king == second_user:
                    king = random.choice(list_users)
            member = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = member.user.first_name
            member = await jr.get_chat_member(message.chat.id, second_user)
            second_user_name = member.user.first_name
            to_mission = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name),
                                              url='https://telegram.me/{}?start={}'.format(jester_user,
                                                                                           message.chat.id))
            to_mission.add(butt)
            await jr.send_message(message.chat.id, 'Loading...')
            await jr.send_message(message.chat.id,
                                  '<a href="tg://user?id={}">{}</a>, {}'.format(second_user, second_user_name,
                                                                                'Вы грустите на пиру, король(лева), обратив на Вас свое внимание, предлагает Вам придумать смешное задание для его шута, нравится вам это или нет - ничего не поделаешь, придется заняться, иначе кого-нибудь казнят, даже если не вас, ответственность нести за это Вам точно не хочется!'),
                                  parse_mode='html', reply_markup=to_mission)
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'time_started': time.time()}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'status': '1'}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'first_today_user': first_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'second_today_user': second_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'king': king}})
            try:
                if message.chat.username is not None:
                    await jr.send_message(king,
                                          'Вы - король в мире ' + '@' + message.chat.username + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена"')
                else:
                    for_link_chat_id = str(message.chat.id).replace('-100', '')
                    await jr.send_message(king, 'Вы - король в мире ' + '[{}](t.me/c/{})'.format(message.chat.title,
                                                                                                 for_link_chat_id) + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена")',
                                          parse_mode='markdown')
            except (exceptions.CantInitiateConversation, exceptions.BotBlocked):
                try:
                    collection2.update_one({'group': message.chat.id},
                                           {'$inc': {f'{king} to_kick': 1}})
                except KeyError:
                    collection2.update_one({'group': message.chat.id},
                                           {'$set': {f'{king} to_kick': 1}})
                if collection2.find_one({'group': message.chat.id})[f'{king} to_kick'] < 3:
                    await jr.send_message(message.chat.id, f'<a href="tg://user?id={king}">Король(лева)</a>, напишите, пожалуйста боту в лс.\nВы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена"\n<b>Предупреждение! У каждого игрока есть возможность лишь два раза проигнорировать просьбу о написании в лс, после вы будете кикнуты из игры.</b>', parse_mode='html')
                else:
                    await reset_game_command(message)
                    collection2.update_one({'group': message.chat.id},
                                           {'$set': {'status': '0'}})
                    collection2.update_one({'group': message.chat.id},
                                           {'$set': {'voted_users': []}})
                    collection2.update_one({'group': message.chat.id},
                                           {'$set': {'guesses': []}})
                    collection2.update_one({'group': message.chat.id},
                                           {'$set': {'guessed_users': []}})  # added
                    for key in collection2.find_one({'group': message.chat.id}):
                        if key.startswith('guess') and len(key.split()) > 1 and key.split()[1].isdigit():
                            collection2.update_one({'group': message.chat.id},
                                                   {'$unset': {key: {'$exists': True}}})
                        if key == 'guess_m_id':  # added
                            collection2.update_one({'group': message.chat.id},
                                                   {'$unset': {key: {'$exists': True}}})
                    for user_doc in col_private.find({'user': {'$exists': True}}):
                        if user_doc['user'] in doc['players']:
                            for key in user_doc:
                                if key.startswith('guess in'):
                                    col_private.update_one({'user': user_doc['user']},
                                                           {'$unset': {key: {'$exists': True}}})
                    collection2.update_one({'group': message.chat.id},
                                           {'$pull': {'players': king}})
                    col_private.update_one({'user': king},
                                           {'$pull': {'groups': message.chat.id}})
                    king = await jr.get_chat_member(message.chat.id, king)
                    king = king.user.first_name
                    await jr.send_message(message.chat.id, f'Король(лева) не пишет мне в лс! Игра была сброшена, {king} был(а) удален(а) из игры')
            except exceptions.UserDeactivated:
                await reset_game_command(message)
                collection2.update_one({'group': message.chat.id},
                                       {'$set': {'status': '0'}})
                collection2.update_one({'group': message.chat.id},
                                       {'$set': {'voted_users': []}})
                collection2.update_one({'group': message.chat.id},
                                       {'$set': {'guesses': []}})
                collection2.update_one({'group': message.chat.id},
                                       {'$set': {'guessed_users': []}})  # added
                for key in collection2.find_one({'group': message.chat.id}):
                    if key.startswith('guess') and len(key.split()) > 1 and key.split()[1].isdigit():
                        collection2.update_one({'group': message.chat.id},
                                               {'$unset': {key: {'$exists': True}}})
                    if key == 'guess_m_id':  # added
                        collection2.update_one({'group': message.chat.id},
                                               {'$unset': {key: {'$exists': True}}})
                for user_doc in col_private.find({'user': {'$exists': True}}):
                    if user_doc['user'] in doc['players']:
                        for key in user_doc:
                            if key.startswith('guess in'):
                                col_private.update_one({'user': user_doc['user']},
                                                       {'$unset': {key: {'$exists': True}}})
                collection2.update_one({'group': message.chat.id},
                                       {'$pull': {'players': king}})
                col_private.update_one({'user': king},
                                       {'$pull': {'groups': message.chat.id}})
                await jr.send_message(message.chat.id, 'Король(лева) мертв(а). Игра сброшена в начальную стадию. \n/today_user')
        elif doc['status'] == '1':
            first_user = doc['first_today_user']
            first_user_name = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = first_user_name.user.first_name
            second_user = doc['second_today_user']
            second_user_name = await jr.get_chat_member(message.chat.id, second_user)
            second_user_name = second_user_name.user.first_name
            kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name),
                                              url='https://telegram.me/{}?start={}'.format(jester_user,
                                                                                           message.chat.id))
            kb.add(butt)
            await jr.send_message(message.chat.id,
                                  '<a href="tg://user?id={}">{}</a>, придумывает задание для шута...'.format(
                                      second_user, second_user_name), parse_mode='html', reply_markup=kb)
        elif doc['status'] == '2':
            first_user = doc['first_today_user']
            first_user_name = await jr.get_chat_member(message.chat.id, first_user)
            first_user_name = first_user_name.user.first_name
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data='mission')
            jester_mission_kb.add(butt)
            await jr.send_message(message.chat.id,
                                  '<a href="tg://user?id={}">{}</a>, придворный шут, выполняет задание...'.format(
                                      first_user, first_user_name), parse_mode='html', reply_markup=jester_mission_kb)
        elif doc['status'] == '3':
            await jr.send_message(message.chat.id, 'Сегодняшняя игра уже закончена!')
    except:
        print(traceback.format_exc())


async def status_check(m, doc, second_user, chat_id):
    if doc['status'] == '1':
        if m.from_user.id == second_user:
            await jr.send_message(m.chat.id, 'Отправь задание ответом на ЭТО сообщение',
                                  reply_to_message_id=m.message_id, reply_markup=types.ForceReply())
            col_private.update_one({'user': m.chat.id},
                                   {'$set': {'main_chat': chat_id}})
            await Form.getting_mission.set()
        else:
            await jr.send_message(m.chat.id,
                                  'ЭТА КОПКА НЕ ДЛЯ ТЕБЯ, АЛЕ! Неужели, игра такая сложная, что у тебя мозги превратились в кашу? Может, тебе новые подарить?')
    elif doc['status'] == '0':
        await jr.send_message(m.chat.id, 'Игра еще не началась, начни ее командой /today_user в группе')
    elif doc['status'] == '2':
        await jr.send_message(m.chat.id,
                              'Задание уже выбрано, перевыбрать не получится, потому что разраб - пидор, все претензии к [нему](t.me/dr_forse), я всего лишь бот.',
                              parse_mode='markdown')
    elif doc['status'] == '3':
        await jr.send_message(m.chat.id,
                              'Дневной розыгрыш уже окончен, возвращайся завтра или зайди на гитхаб(в описании), возьми код, сделай розыгрыш постоянным и захости у себя, если, конечно не ужаснешься тому, какой это говнокод.')


@jp.message_handler(lambda m: m.chat.type == 'private', commands=['start'])
async def start_command(m):
    try:
        if len(m.text.split()) == 2 and m.text.split()[1].startswith('-') and m.text.split('/start -')[1].isdigit():
            chat_id = int(m.text.split()[1])
            try:
                doc = collection2.find_one({'group': chat_id})
                if m.from_user.id not in doc['players']:
                    group = await jr.get_chat(chat_id)
                    if group.username is not None:
                        await jr.send_message(m.chat.id, 'Вы не в игре, вернитесь в группу <a href=t.me/{}>{}</a> и зарегестрируйтесь(/reg\_me)'.format(group.username, group.title), parse_mode='html')
                    else:
                        for_link_chat_id = str(chat_id).replace('-100', '')
                        await jr.send_message(m.chat.id, 'Вы не в игре, вернитесь в группу <a href=t.me/c/{}>{}</a> и зарегестрируйтесь(/reg\_me)'.format(for_link_chat_id, group.title), parse_mode='html')
                else:
                    second_user = doc['second_today_user']
                    col_private.update_one({'user': m.chat.id},
                                           {'$set': {'main_chat': chat_id}},
                                           upsert=True)
                    await status_check(m, doc, second_user, chat_id)
            except KeyError:
                group = await jr.get_chat(chat_id)
                if group.username is not None:
                    await jr.send_message(m.chat.id,
                                          'Вы не в игре, вернитесь в группу <a href=t.me/{}>{}</a> и зарегестрируйтесь(/reg\_me)'.format(group.username, group.title),
                                          parse_mode='html')
                else:
                    for_link_chat_id = str(chat_id).replace('-100', '')
                    await jr.send_message(m.chat.id,
                                          'Вы не в игре, вернитесь в группу <a href=t.me/c/{}>{}</a> и зарегестрируйтесь(/reg\_me)'.format(for_link_chat_id, group.title),
                                          parse_mode='html')
        elif len(m.text.split()) == 2 and m.text.split()[1].startswith('reg'):
            chat_id = int(m.text.split('/start reg')[1])
            if m.from_user.id not in collection2.find_one({'group': chat_id})['players']:
                collection2.update_one({'group': chat_id},
                                       {'$push': {'players': m.from_user.id}})
                if col_private.find_one({'user': m.chat.id}) is None:
                    col_private.insert_one({'user': m.from_user.id,
                                            'guess_keys': ['хочу угадывать задание'],
                                            'groups': [chat_id],
                                            'stats': 0})
                elif col_private.find_one({'user': m.chat.id}) is not None:
                    doc = col_private.find_one({'user': m.chat.id})
                    if chat_id not in doc['groups']:
                        col_private.update_one({'user': m.from_user.id},
                                               {'$push': {'groups': chat_id}})
                    if 'guess_keys' not in doc:
                        col_private.update_one({'user': m.from_user.id},
                                               {'$set': {'guess_keys': ['хочу угадывать задание']}})
                await jr.send_message(m.chat.id, 'Вы зарегестрированы!')
                await jr.send_message(chat_id, f'{m.from_user.first_name} зарегестрировался(лась).')
            else:
                await jr.send_message(m.chat.id, 'Вы уже в игре.')
        else:
            await jr.send_message(m.chat.id, 'Привет. Я игровой бот(ежедневные конкурсы). \nБольше в /help\nСаппорт-группа: @jestersupport (За вопросы, ответы на которые есть в хелпе - бан!)')
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())


@jp.message_handler(state=Form.getting_mission)
async def getting_mission(m, state: FSMContext):
    try:
        chat_id = col_private.find_one({'user': m.chat.id})['main_chat']
        doc = collection2.find_one({'group': chat_id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']
        col_private.update_one({'user': m.chat.id},
                               {'$set': {'mission': m.text}},
                               upsert=True)
        check_kb = types.InlineKeyboardMarkup()
        accept = types.InlineKeyboardButton('Да', callback_data='accept')
        decline = types.InlineKeyboardButton('Нет',
                                             url=f'https://telegram.me/{jester_user}?start={chat_id}')
        check_kb.add(accept, decline)
        if m.reply_to_message is not None:
            if m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение' and (
                    time.time() - (m.reply_to_message.date - datetime(1970, 1, 1)).total_seconds()) < 60:
                await jr.send_message(m.chat.id, 'Вы уверены?', reply_markup=check_kb)
                await state.finish()
            elif m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение':
                await jr.send_message(m.chat.id, 'Message is too old.')
                await state.finish()
        else:
            await jr.send_message(m.chat.id, 'Отправь задание ответом на ЭТО сообщение',
                                  reply_to_message_id=m.message_id, reply_markup=types.ForceReply())
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())
        await state.finish()


@jp.callback_query_handler(lambda call: call.data == 'accept')
async def checking(call):
    try:
        tdoc = col_private.find_one({'user': call.message.chat.id})
        main_chat = tdoc['main_chat']
        doc = collection2.find_one({'group': main_chat})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']
        if call.data == 'accept':
            member = await jr.get_chat(main_chat)
            if member.username != None:
                to_chat = await jr.get_chat(main_chat)
                await jr.send_message(call.message.chat.id,
                                      'Хорошо. Задание в группе [{}](t.me/{}) оглашено.'.format(to_chat.title,
                                                                                                to_chat.username),
                                      parse_mode='markdown')
            else:
                to_chat = await jr.get_chat(main_chat)
                for_link_chat_id = str(main_chat).replace('-100', '')
                await jr.send_message(call.message.chat.id,
                                      'Хорошо. Задание в группе [{}](t.me/c/{}) оглашено.'.format(to_chat.title,
                                                                                                  for_link_chat_id),
                                      parse_mode='markdown')
            collection2.update_one({'group': main_chat},
                                   {'$set': {'mission_text': tdoc['mission']}})
            collection2.update_one({'group': main_chat},
                                   {'$set': {'status': '2'}})
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data='mission')
            jester_mission_kb.add(butt)
            await jr.send_message(main_chat,
                                  'Всем внимание на <a href = "tg://user?id={}">Шута Дня</a>'.format(first_user),
                                  parse_mode='html', reply_markup=jester_mission_kb)
        await jr.answer_callback_query(call.id)
        await jr.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except:
        print(traceback.format_exc())


@jp.callback_query_handler(lambda call: call.data == 'mission')
async def jester_mission(call):
    try:
        call.data
        doc = collection2.find_one({'group': call.message.chat.id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']
        if call.from_user.id == first_user or call.from_user.id == second_user or call.from_user.id == king:
            await jr.answer_callback_query(callback_query_id=call.id, text=doc['mission_text'], show_alert=True)
        else:
            await jr.answer_callback_query(callback_query_id=call.id, text='Вы не можете прочитать это',
                                           show_alert=False)
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['stats'])
async def show_stats(m):
    try:
        doc = col_private.find_one({'user': m.from_user.id})
        if doc is not None:
            if 'stats' in doc:
                stats = col_private.find_one({'user': m.from_user.id})['stats']
                await jr.send_message(m.chat.id, f'Ваша статистика - {stats}', reply_to_message_id=m.message_id)
            else:
                await jr.send_message(m.chat.id, "Ваша статистика - 0", reply_to_message_id=m.message_id)
        else:
            await jr.send_message(m.chat.id, 'Вы не играете. Чтобы зарегестрироваться, нажмтие /reg_me', reply_to_message_id=m.message_id)
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['clean'])
async def clean(m):
    try:
        if m.from_user.id in developers:
            stopped_groups = await groups_check()
            for group in stopped_groups:
                collection2.delete_one({'group': group})
                for user in col_private.find({'user': {'$exists': True}}):
                    if group in user['groups']:
                        col_private.update_one({'user': user['user']},
                                               {'$pull': {'groups': group}})
            await jr.send_message(m.chat.id, str(stopped_groups) + ' cleaned.')
            stopped_users = await users_check()
            for user in stopped_users:
                col_private.delete_one({'user': user})
                for group in collection2.find({'group': {'$exists': True}}):
                    if user in group['players']:
                        collection2.update_one({'group': group['group']},
                                               {'$pull': {'players': user}})
            await jr.send_message(m.chat.id, str(stopped_users) + ' cleaned.')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['top'])
async def show_top(m):
    try:
        users_top = ''
        groups_top = ''
        users = col_private.find({'user': {'$exists': True}}).sort('stats', pymongo.DESCENDING)
        groups = collection2.find({'group': {'$exists': True}}).sort('stats', pymongo.DESCENDING)
        group_ind = 1
        user_ind = 1
        count_users = col_private.count_documents({'user': {'$exists': True}})
        count_groups = collection2.count_documents({'group': {'$exists': True}})
        for group in groups:
            grp_stats = group['stats']
            if group_ind < 11:
                try:
                    chat = await jr.get_chat(group['group'])
                    chat = chat.title
                    groups_top += f'{group_ind}. *{chat}*: {grp_stats}\n'
                    group_ind += 1
                except(exceptions.BotKicked, exceptions.ChatNotFound, exceptions.Unauthorized):
                    continue
            else:
                break
        for user in users:
            if user_ind < 11:
                if m.chat.id in user['groups']:
                    user_stats = user['stats']
                    try:
                        member = await jr.get_chat_member(m.chat.id, user['user'])
                        member = member.user.first_name
                        users_top += f'{user_ind}. *{member}*: {user_stats}\n'
                        user_ind += 1
                    except(exceptions.BotKicked, exceptions.ChatNotFound, exceptions.Unauthorized):
                        try:
                            member = await jr.get_chat(user['user'])
                            member = member.first_name
                            users_top += f'{user_ind}. *{member}*: {user_stats}\n'
                            user_ind += 1
                            continue
                        except(exceptions.BotBlocked, exceptions.Unauthorized, exceptions.UserDeactivated,
                               exceptions.InvalidUserId, exceptions.ChatNotFound):
                            print(traceback.format_exc())
                            continue
            else:
                break
        if len(m.text.split()) >= 2:
            command_args = ['-U', '-G']
            args = m.text.split()[1:3]
            for arg in args:
                if arg in command_args:
                    if arg == '-U' and m.chat.type != 'private':
                        await jr.send_message(m.chat.id, f'*Топ-10 участников чата*:\n{users_top}\nВсего юзеров в боте: {count_users}',
                                              reply_to_message_id=m.message_id, parse_mode='markdown')
                    elif arg == '-G':
                        await jr.send_message(m.chat.id, f'*Топ-10 групп*:\n{groups_top}\n Всего групп с ботом: {count_groups}',
                                              reply_to_message_id=m.message_id, parse_mode='markdown')
        elif m.chat.type != 'private':
            await jr.send_message(m.chat.id, f'*Топ-10 участников чата*:\n{users_top}\nВсего юзеров в боте: {count_users}',
                                  reply_to_message_id=m.message_id, parse_mode='markdown')
            await jr.send_message(m.chat.id, f'*Топ-10 групп*:\n{groups_top}\n Всего групп с ботом: {count_groups}',
                                  parse_mode='markdown')
        else:
            await jr.send_message(m.chat.id, f'*Топ-10 групп*:\n{groups_top}\n Всего групп с ботом: {count_groups}',
                                  parse_mode='markdown')
    except:
        print(traceback.format_exc())


@jp.message_handler(lambda m: m.chat.type == 'private', content_types=['text'])
async def start_guessing_mission(m):
    try:
        if col_private.find_one({'user': m.from_user.id}) is not None and 'guess_keys' in col_private.find_one({'user': m.from_user.id}):
            guess_keys = col_private.find_one({'user': m.from_user.id})['guess_keys']
        else:
            guess_keys = ['хочу угадывать задание']
        if m.text.lower() in guess_keys:
            doc = col_private.find_one({'user': m.from_user.id})
            groups = doc['groups']
            groups_kb = types.InlineKeyboardMarkup()
            buttons = []
            for group in groups:
                try:
                    grp = await jr.get_chat(group)
                    button_name = grp.title
                    buttons.append(types.InlineKeyboardButton(text=button_name, callback_data=group))
                except (exceptions.ChatNotFound, exceptions.Unauthorized, exceptions.BotKicked):
                    continue
            groups_kb.add(*buttons)
            await jr.send_message(m.chat.id, 'Выберите группу:', reply_markup=groups_kb)
            await Form.guess_mission.set()
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())


@jp.callback_query_handler(state=Form.guess_mission)
async def guess_mission_func(call: types.CallbackQuery, state=FSMContext):
    try:
        doc = collection2.find_one({'group': int(call.data)})
        user = call.from_user.id
        if 'guessed_users' in doc:
            if call.from_user.id in doc['guessed_users']:
                await jr.send_message(call.message.chat.id, 'Вы уже сегодня гадали в этой группе')
                await state.finish()
            elif doc['status'] == '2':
                if user != doc['king'] and user != doc['second_today_user'] and user != doc['first_today_user']:
                    await jr.send_message(call.message.chat.id, 'Пишите Вашу догадку!', reply_markup=types.ForceReply())
                    collection2.update_one({'group': int(call.data)},
                                           {'$push': {'guessed_users': call.from_user.id}})
                    await state.finish()
                    async with state.proxy() as data:
                        data['guess_group'] = call.data
                    await Form.guess_mission_step2.set()
                elif user == doc['king']:
                    await jr.send_message(call.message.chat.id, 'Вы не можете гадать в этой группе, потому что Вы в ней - король!')
                    await state.finish()
                elif user == doc['second_today_user']:
                    await jr.send_message(call.message.chat.id, 'Вы не можете гадать в этой группе, потому что Вы были выбраны королем для придумывания задания в ней!')
                    await state.finish()
                elif user == doc['first_today_user']:
                    await jr.send_message(call.message.chat.id, 'Ты не можешь гадать в этой группе, потому что ты шут этой группы!')
                    await state.finish()
                else:
                    print('wtf 649')
            else:
                await jr.send_message(call.message.chat.id, 'Вы не можете сейчас голосовать(игра еще не началась, шут еще не придумал задание, или уже проводится опрос).')
                await state.finish()
        else:
            await jr.send_message(call.message.chat.id, 'Пишите Вашу догадку!', reply_markup=types.ForceReply())
            collection2.update_one({'group': int(call.data)},
                                   {'$set': {'guessed_users': [call.from_user.id]}})
            await state.finish()
            async with state.proxy() as data:
                data['guess_group'] = call.data
            await Form.guess_mission_step2.set()
        await jr.answer_callback_query(call.id)
        await jr.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except:
        print(traceback.format_exc())
        await state.finish()


@jp.message_handler(state=Form.guess_mission_step2)
async def guess_mission_step2_func(m, state=FSMContext):
    try:
        if m.reply_to_message.text == 'Пишите Вашу догадку!':
            if(time.time() - (m.reply_to_message.date - datetime(1970, 1, 1)).total_seconds()) < 300:
                sure_kb = types.InlineKeyboardMarkup()
                accept = types.InlineKeyboardButton('Да', callback_data='accept_guess')
                decline = types.InlineKeyboardButton('Нет', callback_data='decline_guess')
                sure_kb.add(accept, decline)
                await jr.send_message(m.chat.id, 'Вы уверены?', reply_markup=sure_kb, reply_to_message_id=m.message_id)
                async with state.proxy() as data:
                    guess_group = data['guess_group']
                await state.finish()
                async with state.proxy() as data:
                    data['guess_group'] = guess_group
                await Form.guess_mission_last_step.set()
            else:
                await jr.send_message(m.chat.id, 'А? Что? О чем это мы? Я уже забыл.')
                await state.finish()
    except:
        print(traceback.format_exc())


@jp.callback_query_handler(lambda call: call.data == 'accept_guess', state='*')
async def accept_guess(call: types.CallbackQuery, state=FSMContext):
    try:
        async with state.proxy() as data:
            guess_group = data['guess_group']
        if 'guess_groups' not in col_private.find_one({'user': call.message.chat.id}):
            col_private.update_one({'user': call.message.chat.id},
                                   {'$set': {'guess_groups': [guess_group]}})
            col_private.update_one({'user': call.message.chat.id},
                                   {'$set': {'guess in {}'.format(guess_group): call.message.reply_to_message.text}})
            await jr.send_message(call.message.chat.id, 'Хорошо, я запомню.')
        elif guess_group not in col_private.find_one({'user': call.message.chat.id})['guess_groups']:
            col_private.update_one({'user': call.message.chat.id},
                                   {'$push': {'guess_groups': guess_group}})
            col_private.update_one({'user': call.message.chat.id},
                                   {'$set': {'guess in {}'.format(guess_group): call.message.reply_to_message.text}})
            await jr.send_message(call.message.chat.id, 'Хорошо, я запомню.')
        else:
            await jr.send_message(call.message.chat.id, 'Вы уже гадали сегодня в этой группе.')
        await state.finish()
        await jr.answer_callback_query(call.id)
        await jr.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except:
        print(traceback.format_exc())
        await state.finish()


@jp.callback_query_handler(lambda call: call.data == 'decline_guess', state='*')
async def decline_guess(call: types.CallbackQuery, state=FSMContext):
    try:
        async with state.proxy() as data:
            guess_group = data['guess_group']
        await jr.send_message(call.message.chat.id, 'Ок!')
        await jr.answer_callback_query(call.id)
        collection2.update_one({'group': guess_group},
                               {'$pull': {'guessed_users': call.message.from_user.id}})
        await jr.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        await state.finish()
    except:
        print(traceback.format_exc())
        await state.finish()


async def reset_game():
    collection2.update_many({'group': {'$exists': True}},
                            {'$unset': {'first_today_user': '$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                            {'$unset': {'second_today_user': '$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                            {'$unset': {'king': '$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                            {'$unset': {'mission_text': '$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                            {'$unset': {'mission_complete': '$exists'}})
    col_private.update_many({'user': {'$exists': True}},
                            {'$unset': {'guess_groups': '$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                            {'$set': {'status': '3'}})


@jp.callback_query_handler(lambda call: call.data.startswith('guess'))
async def guesses_poll_step_2(call):
    print('handlered')
    try:
        gdoc = collection2.find_one({'group': call.message.chat.id})
        if call.from_user.id in gdoc['players']:
            if 'voted_users' not in gdoc:
                user = call.data.split()[1]
                if call.from_user.id != user:
                    guess = call.data
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$inc': {guess: 1}})
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$push': {'guesses': guess}},
                                           upsert=True)
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$set': {'guess_m_id': call.message.message_id}})
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$set': {'voted_users': [call.from_user.id]}})
                    await jr.answer_callback_query(callback_query_id=call.id, text='Ваш голос принят')
                else:
                    await jr.answer_callback_query(callback_query_id=call.id, text='Вы не можете голосовать за себя',
                                                   show_alert=True)
            elif call.from_user.id not in gdoc['voted_users']:
                user = call.data.split()[1]
                if call.from_user.id != user:
                    guess = call.data
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$inc': {guess: 1}})
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$set': {'guess_m_id': call.message.message_id}})
                    collection2.update_one({'group': call.message.chat.id},
                                           {'$push': {'voted_users': call.from_user.id}})
                    await jr.answer_callback_query(callback_query_id=call.id, text=f'Ваш голос принят')
                else:
                    await jr.answer_callback_query(callback_query_id=call.id, text='Вы не можете голосовать за себя',
                                                   show_alert=True)
            else:
                await jr.answer_callback_query(callback_query_id=call.id, text='Вы уже проголосовали')
        else:
            await jr.answer_callback_query(call.id, text='Вы не играете.')
    except:
        print(traceback.format_exc())


'''
async def groups_and_users_verification():
    groups = collection2.find({'group': {'$exists': True}})
    users = col_private.find({'user': {'$exists': True}})
    for group in groups:
        try:
            await jr.send_message(group['group'], 'check')
            #  delete_check_message!
        except (exceptions.ChatNotFound, exceptions.Unauthorized, exceptions.BotKicked):
            exceptions
    for user in users:
        if len(user['groups']) == 0:
            try:
                await jr.send_message(user['user'], 'Are u alive? You are not playing me in any group.')
            except (exceptions.UserDeactivated):
                col_private.delete_one({'user': user['user']})
                '''


@aiocron.crontab('0 0 * * *')
async def reset_game_aiocron():
    try:
        for doc in collection2.find({'group': {'$exists': True}}):
            try:
                if doc['status'] == '2':
                    try:
                        await jr.send_message(doc['group'],
                                              '<a href = "tg://user?id={}">Король(лева)</a> не удостоил(а) шоу своим вниманием, меж тем задание было таким:\n{}'.format(doc['king'], doc['mission_text']),
                                              parse_mode='html')
                        await show_mission_complete(doc['group'])
                    except (exceptions.ChatNotFound, exceptions.BotKicked, exceptions.Unauthorized):
                        continue
                elif doc['status'] == '1':
                    try:
                        await jr.send_message(doc['group'],
                                              '<a href = "tg://user?id={}">Боярин</a> не выполнил приказ короля, не сносить ему головы!'.format(doc['second_today_user']),
                                              parse_mode='html')
                    except (exceptions.ChatNotFound, exceptions.BotKicked, exceptions.Unauthorized):
                        continue
                await guesses_poll(doc['group'])
            except (exceptions.ChatNotFound, exceptions.BotKicked, exceptions.Unauthorized):
                continue
        await reset_game()
    except:
        print(traceback.format_exc())


@aiocron.crontab('0 12 * * *')
async def guess_poll_finish():
    try:
        print(time.ctime())
        for doc in collection2.find({'group': {'$exists': True}}):
            try:
                if 'guess_m_id' in doc:
                    poll_m_id = doc['guess_m_id']
                    try:
                        await jr.edit_message_reply_markup(doc['group'], poll_m_id)
                    except MessageToDeleteNotFound:
                        pass
                rates = {}
                rates_list = []
                chat_id = doc['group']
                guesses = {}
                for key, value in doc.items():
                    if key.startswith('guess') and len(key.split()) > 1 and key.split()[1].isdigit():
                        guesses.update({key: value})
                winners = {}
                for guess, rate in guesses.items():
                    rates.update({guess: rate})
                    rates_list.append(rate)
                    win_rate = max(rates_list)
                for guess, rate in rates.items():
                    if rate == win_rate:
                        winners.update({guess: rate})
                winner_ids = []  # for stats
                if len(winners) > 1:
                    winners_names = ''
                    guess_text_to_msg = ''
                    for winner in winners:
                        winner_id = winner.split()[1]
                        winner_ids.append(winner_id)  # for stats
                        member = await jr.get_chat_member(chat_id, winner_id)
                        winner_name = member.user.first_name
                        winners_names += f', <a href="tg://user?id={winner_id}">{winner_name}</a>'
                        guess_text = winner.split(f'guess {winner_id} ')[1]
                        guess_text_to_msg += f'\n<b>{winner_name}:</b>\n {guess_text}'
                    await jr.send_message(chat_id,
                                          f'{winners_names} выиграли, набрав по {win_rate} голосов со следующими догадками:\n{guess_text_to_msg}',
                                          parse_mode='html')
                    await show_mission_complete(doc['group'])
                elif len(winners) == 1:
                    for winner in winners:
                        winner_id = winner.split()[1]
                        winner_ids.append(winner_id)  # for stats
                        member = await jr.get_chat_member(chat_id, winner_id)
                        winner_name = member.user.first_name
                        guess_text = winner.split(f'guess {winner_id} ')[1]
                    await jr.send_message(chat_id,
                                          f'<a href="tg://user?id={winner_id}">{winner_name}</a> выиграл(а), набрав {win_rate} голосов со следующей догадкой:\n{guess_text}',
                                          parse_mode='html')
                    await show_mission_complete(doc['group'])
                collection2.update_many({'group': {'$exists': True}},
                                        {'$set': {'status': '0'}})
                collection2.update_many({'group': {'$exists': True}},
                                        {'$set': {'voted_users': []}})
                collection2.update_many({'group': {'$exists': True}},
                                        {'$set': {'guesses': []}})
                collection2.update_one({'group': chat_id},
                                       {'$set': {'guessed_users': []}})
                grp_stats_inc = 0
                for winner_id in winner_ids:
                    if col_private.find_one({'user': winner_id})['stats'] > 10:
                        stats = col_private.find_one({'user': winner_id})['stats']
                        if stats < 150:
                            stats += stats + stats * 0.30
                        elif stats < 400:
                            stats += stats + stats * 0.15
                        else:
                            stats += stats + stats * 0.10
                        col_private.update_one({'user': winner_id},
                                               {'$set': {'stats': round(stats)}})
                        grp_stats_inc += round(stats)
                    else:
                        col_private.update_one({'user': winner_id},
                                               {'$set': {'stats': 10}})
                        grp_stats_inc += 10
                collection2.update_one({'group': doc['group']},
                                       {'$inc': {'stats': grp_stats_inc}})
                for key in collection2.find_one({'group': doc['group']}):
                    if key.startswith('guess') and len(key.split()) > 1 and key.split()[1].isdigit():
                        collection2.update_one({'group': doc['group']},
                                               {'$unset': {key: {'$exists': True}}})
                    if key == 'guess_m_id':
                        collection2.update_one({'group': doc['group']},
                                               {'$unset': {key: {'$exists': True}}})
                for user_doc in col_private.find({'user': {'$exists': True}}):
                    if user_doc['user'] in doc['players']:
                        for key in user_doc:
                            if key.startswith('guess in'):
                                col_private.update_one({'user': user_doc['user']},
                                                       {'$unset': {key: {'$exists': True}}})
            except (exceptions.ChatNotFound, exceptions.BotKicked, exceptions.Unauthorized):
                continue
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['finish_poll'])
async def guess_poll_finish(m):
    try:
        if m.from_user.id in developers:
            await finish_poll_by_command(m)
        else:
            await jr.send_message(m.chat.id, 'Эта команда - только для разработчиков бота!')
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['lastdone'])
async def check_last_done(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if 'mission_complete' in doc:
            await jr.forward_message(chat_id=m.chat.id, from_chat_id=m.chat.id, message_id=doc['mission_complete'])
        else:
            await jr.send_message(m.chat.id, random.choice(skyrim_frases))
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['done'])
async def save_mission_message_by_command(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if doc['status'] == '2':
            from_member = await jr.get_chat_member(m.chat.id, m.from_user.id)
            if m.from_user.id == doc['first_today_user'] or m.from_user.id in developers or from_member.status == 'creator' or from_member.status == 'administrator':
                collection2.update_one({'group': m.chat.id},
                                       {'$set': {'mission_complete': m.reply_to_message.message_id}})
                await jr.send_message(m.chat.id, 'okay, fine')
            else:
                await jr.send_message(m.chat.id, 'Это могут сделать только шут, разраб, создатель и админы чата.')
        else:
            await jr.send_message(m.chat.id, random.choice(skyrim_frases))
    except:
        print(traceback.format_exc())


@jp.message_handler(commands=['give_stats'])
async def give_stats(m):
    try:
        if m.from_user.id in developers:
            if m.reply_to_message:
                arg = int(m.text.split()[1])
                user_id = m.reply_to_message.from_user.id
                stats = col_private.find_one({'user': user_id})['stats']
                col_private.update_one({'user': user_id},
                                       {'$inc': {'stats': arg}})
                new_stats = stats+arg
                await jr.send_message(m.chat.id, f'Успех для {user_id}\n Было: {stats}\n Стало: {new_stats}')
            else:
                arg = int(m.text.split()[1])
                stats = collection2.find_one({'group': m.chat.id})['stats']
                collection2.update_one({'group': m.chat.id},
                                       {'$inc': {'stats': arg}})
                new_stats = stats + arg
                await jr.send_message(m.chat.id, f'Успех для {m.chat.id}\n Было: {stats}\n Стало: {new_stats}')
    except:
        print(traceback.format_exc())


@jp.message_handler(lambda m: m.reply_to_message and m.reply_to_message.from_user.id == jester_id, content_types=['text', 'photo', 'video', 'sticker', 'animation', 'audio', 'document', 'voice', 'video_note', 'contact, location', 'venue', 'poll'])
async def save_mission_message_ai(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if doc['status'] == '2':
            if ', придворный шут, выполняет задание...' in m.reply_to_message.text or 'Всем внимание на Шута Дня' in m.reply_to_message.text:
                if m.reply_to_message.from_user.id == jester_id and time.time() - time.mktime(
                        m.reply_to_message.date.timetuple()) < 43200 \
                        and m.from_user.id == doc['first_today_user']:
                    collection2.update_one({'group': m.chat.id},
                                           {'$set': {'mission_complete': m.message_id}})
    except:
        print(traceback.format_exc())


async def show_mission_complete(chat_id):
    doc = collection2.find_one({'group': chat_id})
    if 'mission_complete' in doc:
        await jr.send_message(chat_id=chat_id, text='Выполнение задания:')
        await jr.forward_message(chat_id=chat_id, from_chat_id=chat_id, message_id=doc['mission_complete'])


async def groups_check():
    groups = collection2.find({'group': {'$exists': True}}).sort('stats', pymongo.DESCENDING)
    blocked = []
    for group in groups:
        try:
            await jr.get_chat_members_count(group['group'])
        except(exceptions.BotKicked, exceptions.Unauthorized):
            blocked.append(group['group'])
            continue
        except exceptions.ChatNotFound:
            continue
    return blocked


async def users_check():
    users = col_private.find({'user': {'$exists': True}})
    blocked = []
    for user in users:
        try:
            await jr.send_chat_action(user['user'], 'typing')
        except(exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.Unauthorized, exceptions.UserDeactivated):
            if user['groups'] == []:
                blocked.append(user['user'])
            continue
        except(exceptions.ChatNotFound, exceptions.InvalidUserId):
            continue
    return blocked


@aiocron.crontab('*/5 * * * *')
async def anti_idling():
    await jr.get_me()


async def jr_on_startup(jp):
    await jr.set_webhook(WEBHOOK_URL)


async def jr_on_shutdown(jp):
    pass


start_webhook(dispatcher=jp, webhook_path=WEBHOOK_PATH, on_startup=jr_on_startup, on_shutdown=jr_on_shutdown,
              skip_updates=True, host='0.0.0.0', port=os.getenv('PORT'))
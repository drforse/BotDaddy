import pymongo
from pymongo import MongoClient
import traceback
import telebot
from telebot import types
import random
import os
import schedule
import time
import threading

client_jr = pymongo.MongoClient(os.environ['db_jr'])
db_jr = client_jr.test
collection2 = db_jr.bottle
jr = telebot.TeleBot(os.environ['token_jr'])

client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
collection = db.pin_list
bot = telebot.TeleBot (os.environ['token'])
col2 = db.users
banned = col2.find_one()

developers = [500238135]
bot_id = os.environ['bot_id']
bot_user = '@botsdaddyybot'

def skip_pending(bot):
    print('Skipping pendings...')
    bot.skip_pending = True
    print('Ready!!')
    time.sleep(1)
if True:
    t = threading.Timer(1, skip_pending, args=[jr])
    t.start()
    t = threading.Timer(1, skip_pending, args=[bot])
    t.start()

ban_keywords_list = ['!иди в баню','!иди в бан','!банан тебе в жопу','!нам будет тебя не хватать', '/ban', '/ban@botsdaddyybot']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban', '/unban@botsdaddyybot']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
OD_flood_list = ["Да как ты разговариваешь со старшими!"]
ban_mute_list = ban_keywords_list + unban_keywords_list + mute_keywords_list + unmute_keywords_list
'''
print(jr.get_chat_member(-1001468828532, 828000649).user.username)
reg_kb = types.InlineKeyboardMarkup()
reg = types.InlineKeyboardButton('Тык', url='telegram.me/jester_day_bot?start=test')
reg_kb.add(reg)
groups = []
for group in collection2.find({'group':{'$exists':True}}):
    groups.append(group['group'])
    jr.send_message(group['group'], 'Нажмите, пожалуйста на кнопку, чтобы победить баг вместе)0))', reply_markup = reg_kb)
'''

@jr.message_handler(content_types = ['left_chat_member'])
def left_member(m):
    if jr.get_chat_member(m.chat.id, m.from_user.id).user.id in collection2.find_one({'group': m.chat.id})['players']:
        collection2.update_one({'group': m.chat.id},
                               {'$pull':{'players':m.from_user.id}})

@jr.message_handler(commands = ['help_define'])
def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        jr.send_message(message.from_user.id, 'Define the help-message')
        jr.delete_message(message.chat.id, message.message_id)
        jr.register_next_step_handler(message, help_message_handler)
    else:
        jr.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')
def help_message_handler(message):
    global help_definer
    if message.chat.id == help_definer:
        collection2.update_one({'id': 0},
                               {'$set': {'help_msg': message.text}},
                               upsert=True)
        jr.send_message(message.chat.id, 'Updated.')

@jr.message_handler(commands = ['help'])
def show_help(message):
    doc = collection2.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith('/help@jester_day_bot'):
        jr.send_message(message.chat.id, help_msg, parse_mode = 'markdown')
    elif message.chat.type == 'private':
        jr.send_message(message.chat.id, help_msg, parse_mode = 'markdown')

@jr.message_handler(commands = ['players'])
def players_list(m):
    if m.text.startswith('/players@jester_day_bot'):
        if collection2.find_one({'group': m.chat.id}):
            players = ''
            for gamer in collection2.find_one({'group':m.chat.id})['players']:
                if gamer != None:
                    player = jr.get_chat_member(m.chat.id, gamer).user.first_name
                    players += str(player) + ', '
            x = len(players)-2
            players = players[:x]
            jr.send_message(m.chat.id, players, reply_to_message_id = m.message_id)

@jr.message_handler(commands = ['leave_jester'])
def leave_game(m):
    if jr.get_chat_member(m.chat.id, m.from_user.id).user.id in collection2.find_one({'group': m.chat.id})['players']:
        collection2.update_one({'group': m.chat.id},
                               {'$pull':{'players':m.from_user.id}})
        jr.send_message(m.chat.id, 'Вы вышли из игры!')

@jr.message_handler(commands = ['reset_game'])
def reset_game(m):
    try:
        if jr.get_chat_member(m.chat.id, m.from_user.id).status == 'creator' or jr.get_chat_member(m.chat.id, m.from_user.id).status == 'administrator':
            collection2.update_one({'group': m.chat.id},
                                   {'$set': {'status': '0'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'mission_text':'$exists'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'first_today_user':'$exists'}})
            collection2.update_one({'group': m.chat.id},
                                   {'$unset': {'second_today_user':'$exists'}})
            jr.send_message(m.chat.id, 'Game reseted')
        else:
            jr.send_message(m.chat.id, 'Вы не админ')
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc()) 

@jr.message_handler(commands = ['reg_me'])
def reg_user(message):
    global message_chat_id
    message_chat_id = message.chat.id
    try:
        doc = collection2.find_one({'group': message.chat.id})
        reg_kb = types.InlineKeyboardMarkup()
        reg = types.InlineKeyboardButton('Тык', url='telegram.me/jester_day_bot?start='+str(message.chat.id))
        reg_kb.add(reg)
        if collection2.find_one({'group': message.chat.id}) == None:
            collection2.insert_one ({'group': message.chat.id,
                                    'players': [],
                                    'status': '0'})
            jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id = message.message_id, reply_markup = reg_kb)
        elif message.from_user.id not in doc['players']:
            jr.send_message(message.chat.id, 'Нажмите для регистрации!', reply_to_message_id = message.message_id, reply_markup = reg_kb)
        else:
            jr.send_message(message.chat.id, 'Вы уже в игре!', reply_to_message_id = message.message_id)
    except:
        jr.send_message(message.chat.id, traceback.format_exc())
    
@jr.message_handler(commands = ['finish_it'])
def finish_game(m):
    try:
        doc = collection2.find_one({'group': m.chat.id})
        if m.from_user.id != doc['king'] and doc['king']:
            jr.send_message(m.chat.id, 'Вы - не король!')
        elif m.chat.type == 'private':
            jr.send_message(m.chat.id, 'Так Вас никто не услышит!')
        elif doc['status'] == '2':
            if len(m.text.split()) < 2:
                jr.send_message(m.chat.id, 'Скажите, как Вам понривалось шоу после команды, Ваше Величество', reply_to_message_id = m.message_id)
            else:
                list = m.text.split()
                result = ''
                for i in range(len(list)-1):
                    result += list[i+1]+' '
                jr.send_message(m.chat.id, 'Мнение Его Величества:\n'+result)
                collection2.update_one({'group': m.chat.id},
                                       {'$set': {'status': '3'}})
                jr.send_message(m.chat.id, "Задание было таким:\n" + doc['mission_text'])
        else:
            jr.send_message(m.chat.id, 'Игра еще не начата, или уже закончена, или задание еще не выполнено (назначено)')
    except KeyError:
        jr.send_message(m.chat.id, 'game not started yet')
    except:
        print(traceback.format_exc())

@jr.message_handler(commands = ['today_user'])
def get_users(message):
    global x
    global message_chat_id
    message_chat_id = message.chat.id
    try:
        x = 0
        doc = collection2.find_one({'group': message.chat.id})
        list_users = doc['players']
        if len(doc['players']) < 3:
            jr.send_message(message.chat.id, 'Not enough players, 3 needed.')
        elif doc['status'] == '0':
            first_user = random.choice(list_users)
            second_user = random.choice(list_users)
            king = random.choice(list_users)
            while first_user == second_user:
                second_user = random.choice(list_users)
            while king == first_user or king == second_user:
                king = random.choice(list_users)
            first_user_name = jr.get_chat_member(message.chat.id, first_user).user.first_name
            second_user_name = jr.get_chat_member(message.chat.id, second_user).user.first_name
            to_mission = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name), url = 'https://telegram.me/jester_day_bot?start={}'.format(message.chat.id))
            to_mission.add(butt)
            jr.send_message(message.chat.id, 'Loading...')
            jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, {}'.format(second_user, second_user_name, 'Вы грустите на пиру, король, обратив на Вас свое внимание, предлагает Вам придумать смешное задание для его шута, нравится вам это или нет - ничего не поделаешь, придется заняться, иначе кого-нибудь казнят, даже если не вас, ответственность нести за это Вам точно не хочется!'), parse_mode = 'html', reply_markup = to_mission)
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'status': '1'}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'first_today_user':first_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'second_today_user':second_user}})
            collection2.update_one({'group': message.chat.id},
                                   {'$set': {'king':king}})
            if message.chat.username != None:
                jr.send_message(king, 'Вы - король в мире ' + '@' + message.chat.username + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена"')
            else:
                jr.send_message(king, 'Вы - король в мире ' + '[{}](t.me/c/{})'.format(message.chat.first_name, message.chat.id) + '! Вы будете решать, понравилось ли Вам то, как шут выполнил задание! (От этого ничего не зависит, кроме перехода игры в статус "Закончена")', parse_mode = 'markdown')
        elif doc['status'] == '1':
            first_user = doc['first_today_user']
            first_user_name = jr.get_chat_member(message.chat.id, first_user).user.first_name
            second_user = doc['second_today_user']
            second_user_name = jr.get_chat_member(message.chat.id, second_user).user.first_name
            kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('{}, придумывай задание и жми сюда'.format(second_user_name), url = 'https://telegram.me/jester_day_bot?start={}'.format(message.chat.id))
            kb.add(butt)
            jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, придумывает задание для шута...'.format(second_user, second_user_name), parse_mode = 'html', reply_markup = kb)
        elif doc['status'] == '2':
            first_user = doc['first_today_user']
            first_user_name = jr.get_chat_member(message.chat.id, first_user).user.first_name
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data = 'mission')
            jester_mission_kb.add(butt)            
            jr.send_message(message.chat.id, '<a href="tg://user?id={}">{}</a>, придворный шут, выполняет задание...'.format(first_user, first_user_name), parse_mode = 'html', reply_markup = jester_mission_kb)
        elif doc['status'] == '3':
            jr.send_message(message.chat.id, 'Сегодняшняя игра уже закончена!')
    except:
        jr.send_message(message.chat.id, traceback.format_exc())

@jr.message_handler(content_types = ['text'])
def finish_reg(m):
    try:
        if len(m.text.split())>1:
            try:
                chat_id = int(m.text.split()[1])
            except:
                chat_id = collection2.find_one({'group': m.chat.id})['main_chat']
            doc = collection2.find_one({'group': chat_id})
            if m.from_user.id not in doc['players'] and m.text.startswith('/start'):
                collection2.update_one({'group': chat_id},
                                       {'$push': {'players': m.from_user.id}})
                if None in doc['players']:
                    collection2.update_one({'group': chat_id},
                                           {'$pull': {'players': None}})
                jr.send_message(m.chat.id, 'Вы зарегестрировались!')
            elif m.text.startswith('/start'):
                collection2.update_one({'group':m.chat.id},
                                       {'$set': {'main_chat':chat_id}})
                jr.register_next_step_handler(m, getting_mission)
            else:
                jr.register_next_step_handler(m, getting_mission)
        elif m.text.startswith('/start'):
            collection2.update_one({'group':m.chat.id},
                                   {'$set': {'main_chat':chat_id}})
            jr.register_next_step_handler(m, getting_mission)
        else:
            jr.register_next_step_handler(m, getting_mission)
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())
def getting_mission(m):
    try:
        try:
            if m.text.startswith('/start'):
                chat_id = int(m.text.split()[1])
            else:
                chat_id = collection2.find_one({'group': m.chat.id})['main_chat']
        except:
            chat_id = collection2.find_one({'group': m.chat.id})['main_chat']
        doc = collection2.find_one({'group': chat_id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user'] 
        if doc['status'] == '1':
            if m.from_user.id == second_user:
                collection2.update_one({'group':m.chat.id},
                                       {'$set':{'mission':m.text}},
                                       upsert = True)
                collection2.update_one({'group':m.chat.id},
                                       {'$set':{'main_chat':chat_id}})
                check_kb = types.InlineKeyboardMarkup()
                accept = types.InlineKeyboardButton('Да', callback_data = 'accept')
                decline = types.InlineKeyboardButton('Нет', url = 'https://telegram.me/jester_day_bot?start={}'.format(chat_id))
                check_kb.add(accept, decline)
                if m.reply_to_message != None:
                    if m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение' and (time.time() - m.reply_to_message.date) < 60:
                        jr.send_message(m.chat.id, 'Вы уверены?', reply_markup = check_kb)
                    elif m.reply_to_message.text == 'Отправь задание ответом на ЭТО сообщение':
                        jr.send_message(m.chat.id, 'Message is too old.')
                else:
                    jr.send_message(m.chat.id, 'Отправь задание ответом на ЭТО сообщение', reply_to_message_id = m.message_id, reply_markup = types.ForceReply())
                    jr.register_next_step_handler(m, getting_mission)
            else:
                jr.send_message(m.chat.id, 'ЭТА КОПКА НЕ ДЛЯ ТЕБЯ, АЛЕ! Неужели, игра такая сложная, что у тебя мозги превратились в кашу? Может, тебе новые подарить?')
        elif doc['status'] == '0':
            jr.send_message(m.chat.id, 'Игра еще не началась, начни ее командой /today_user')
        elif doc['status'] == '2':
            jr.send_message(m.chat.id, 'Задание уже выбрано, перевыбрать не получится, потому что разраб - пидор, все претензии к [нему](t.me/dr_forse), я всего лишь бот.', parse_mode = 'markdown')
        elif doc['status'] == '3':
            jr.send_message(m.chat.id, 'Дневной розыгрыш уже окончен, возвращайся завтра или зайди на гитхаб(в описании), возьми код, сделай розыгрыш постоянным и захости у себя, если, конечно не ужаснешься тому, какой это говнокод.')
    except:
        print(str(m.chat.id) + '\n' + traceback.format_exc())            

@jr.callback_query_handler(func=lambda call: call.data == 'accept')
def checking(call):
    try:
        call.data
        tdoc = collection2.find_one({'group': call.message.chat.id})
        main_chat = tdoc['main_chat']
        doc = collection2.find_one({'group': main_chat})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']
        if call.data == 'accept':
            if jr.get_chat(main_chat).username != None:
                jr.send_message(call.message.chat.id, 'Хорошо. Задание в группе [{}](t.me/{}) оглашено.'.format(jr.get_chat(main_chat).title, jr.get_chat(main_chat).username), parse_mode = 'markdown')
            else:
                jr.send_message(call.message.chat.id, 'Хорошо. Задание в группе [{}](t.me/c/{}) оглашено.'.format(jr.get_chat(main_chat).title, main_chat), parse_mode = 'markdown')
            collection2.update_one({'group': main_chat},
                                   {'$set': {'mission_text': tdoc['mission']}})
            jester_mission_kb = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton('Задание для шута', callback_data = 'mission')
            jester_mission_kb.add(butt)
            jr.send_message(main_chat, 'Всем внимание на <a href = "tg://user?id={}">Шута Дня</a>'.format(first_user), parse_mode = 'html', reply_markup = jester_mission_kb)
    except:
        print(traceback.format_exc())

@jr.callback_query_handler(func=lambda call: call.data == 'mission')
def jester_mission(call):
    try:
        call.data
        doc = collection2.find_one({'group': call.message.chat.id})
        first_user = doc['first_today_user']
        king = doc['king']
        second_user = doc['second_today_user']  
        if call.from_user.id == first_user or call.from_user.id == second_user or call.from_user.id == king:
            jr.answer_callback_query(callback_query_id=call.id, text=doc['mission_text'], show_alert=True)
        else:
            jr.answer_callback_query(callback_query_id=call.id, text='Вы не можете прочитать это', show_alert=False)
    except:
        print(traceback.format_exc())

def reset_game_shcedule():
    collection2.update_many({'group': {'$exists': True}},
                           {'$set': {'status': '0'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset': {'first_today_user':'$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset':{'second_today_user':'$exists'}})
    collection2.update_many({'group': {'$exists': True}},
                           {'$unset':{'king':'$exists'}})
    
schedule.every().day.at("00:00").do(reset_game_shcedule)

def run_continuously(self, interval=1):

        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    self.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run

"""BotFather"""
def update_flood():
    doc = col2.find_one({'users':{'$exists':True}})['users']
    col2.replace_one({'users':{'$exists':True}},
                     {'users': doc})
schedule.every(6).hours.do(update_flood)

def anti_flood(message):
    if message.from_user.id not in col2.find_one({'users': {'$exists': True}})['users']:
                    col2.update_one({'users':{'$exists': True}},
                                    {'$push':{'users': message.from_user.id}})
                    col2.update_one({'users':{'$exists': True}},
                                    {'$set':{str(message.from_user.id): 0}})
    elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] < 6:
        col2.update_one({'users':{'$exists': True}},
                        {'$inc':{str(message.from_user.id): 1}},
                        upsert = True)
    elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] == 6:
        bot.send_message(message.chat.id, 'Хватит страдать хуйней!')
        col2.update_one({'users':{'$exists': True}},
                        {'$inc':{str(message.from_user.id): 1}},
                        upsert = True)
    if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
        bot.delete_message(message.chat.id, message.message_id)
class bann_mute:
    def ban(message):
        try:
            if message.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    anti_flood(message)
            if message.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    anti_flood(message)
            if message.text.lower() == '!бан':
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                else:               
                    bot.send_message(message.chat.id, '!уебан', reply_to_message_id = message.message_id)
        except (AttributeError, UnboundLocalError):
            if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
                bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if bot_member.can_restrict_members == None:
                    anti_flood(message)
                elif reply_member.status == 'creator':
                    anti_flood(message)
                elif reply_member.user.id == bot_id:
                    anti_flood(message)
                elif reply_member.status == 'administrator':
                    anti_flood(message)
            except:
                bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))
    def mute(message):
        try:
            if message.text.lower() in mute_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    anti_flood(message)
            if message.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
                elif chat_member.can_restrict_members == None:
                    anti_flood(message)
        except (AttributeError, UnboundLocalError):
            if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
                bot.delete_message(message.chat.id, message.message_id)    
        except Exception:
            try:
                if bot_member.can_restrict_members == None:
                    anti_flood(message)
                elif reply_member.status == 'creator':
                    anti_flood(message)
                elif reply_member.user.id == bot_id:
                    anti_flood(message)
                elif reply_member.status == 'administrator':
                    anti_flood(message)
            except:
                bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username)) 
        
    
#developers_only

    
@bot.message_handler(commands = ['help_define'])
def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        bot.send_message(message.from_user.id, 'Define the help-message')
        bot.delete_message(message.chat.id, message.message_id)
        bot.register_next_step_handler(message, help_message_handler)
    else:
        bot.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')

def help_message_handler(message):
    global help_definer
    if message.chat.id == help_definer:
        collection.update_one({'id': 0},
                              {'$set': {'help_msg': message.text}},
                              upsert=True)
        bot.send_message(message.chat.id, '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным, а не программированием, погуляй, например', parse_mode = 'markdown')

#IT-commands
@bot.message_handler(commands = ['ke'])
def kelerne(message):
    bot.send_message(message.chat.id, 'lerne', reply_to_message_id = message.message_id)
    
@bot.message_handler(commands = ['chat_id'])
def chat_id(message):
    bot.send_message(message.chat.id, '`{}`'.format(message.chat.id),parse_mode = 'markdown')

@bot.message_handler(commands = ['user'])
def user_info(m):
    try:
        if m.reply_to_message:
            bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(m.reply_to_message.from_user.first_name, m.reply_to_message.from_user.last_name, m.reply_to_message.from_user.language_code, m.reply_to_message.from_user.username, m.reply_to_message.from_user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
        elif len(m.text.split())>1:
            try:
                member = bot.get_chat_member(m.chat.id, m.text.split()[1])
                bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(member.user.first_name, member.user.last_name, member.user.language_code, member.user.username, member.user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
            except:
                bot.send_message(m.chat.id, 'Аргументы неверны, или владельца id нет в чате')
        else:
            bot.send_message(m.chat.id, '{} {} ({})\n@{}\n<code>{}</code>'.format(m.from_user.first_name, m.from_user.last_name, m.from_user.language_code, m.from_user.username, m.from_user.id).replace('None', '').replace('()', ''), parse_mode = 'html')
    except:
        print(traceback.format_exc())
    
#Users
@bot.message_handler(commands = ['help'])
def show_help(message):
    doc = collection.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private' and message.text.startswith('/help@botsdaddyybot'):
        bot.send_message(message.from_user.id, help_msg, parse_mode = 'markdown')
        bot.send_message(message.chat.id, 'Отправил в лс')
    elif message.chat.type == 'private':
        bot.send_message(message.chat.id, help_msg, parse_mode = 'markdown')

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        quant = 3
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif chat_member.can_pin_messages == True or chat_member.status == 'creator':
            if message.reply_to_message == None:
                bot.send_message(message.chat.id, 'make replay')
            elif message.text in ['/pintime', '/pintime@botsdaddyybot']:
                while quant > 0:
                    try:
                        bot.unpin_chat_message(message.chat.id)
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    except Exception:
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    quant -= 1
                    time.sleep(3)
            else:
                arg = message.text.split(' ')
                quant = int(arg[1])
                while quant > 0:
                    try:
                        bot.unpin_chat_message(message.chat.id)
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    except Exception:
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    quant -= 1
                    time.sleep(3)
        else:
            anti_flood(message)
    except AttributeError:
        if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
            bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

@bot.message_handler(commands = ['pin'])
def pin(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.delete_message(message.chat.id, message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            anti_flood(message)
        else:
            try:
                arg_find = message.text.split(' ')
                arg = int(arg_find[1])
                if arg == 1:
                    if bot.get_chat(message.chat.id).pinned_message != None:
                        bot.unpin_chat_message(message.chat.id)
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    else:
                        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            except IndexError:
                if bot.get_chat(message.chat.id).pinned_message != None:
                    bot.unpin_chat_message(message.chat.id)
                    bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
                else:
                    bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
    except AttributeError:
        if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
            bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))

@bot.message_handler(commands = ['unpin'])
def unpin(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups', reply_to_message_id = message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            anti_flood(message)
        else:
            bot.unpin_chat_message(message.chat.id)
    except AttributeError:
        if bot.get_chat_member(message.chat.id, bot_id).can_delete_messages:
            bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))   
        
@bot.message_handler(commands = ['pinlist'])
def get_pinned_messages(message):
    if message.text.startswith('/pinlist@botsdaddyybot'):
        try:
            document = collection.find_one({'Group': message.chat.id})
            text=''        
            document.pop('_id')
            for ids in document:
                if ids == '_id':
                    continue
                elif ids == 'Group':
                    text += "{}: <a href='t.me/{}'>{}</a>\n".format('Group', message.chat.username, message.chat.title)
                else:
                    text += '<a href="t.me/{}/{}">{}</a>: {}\n'.format(document[ids][0]['group'], ids, document[ids][0]['date'], document[ids][0]['msg'])
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    bot.send_message(message.from_user.id, text[x:x+4096], parse_mode = 'html', disable_web_page_preview = True)
            else:
                bot.send_message(message.from_user.id, text, parse_mode = 'html', disable_web_page_preview = True)
            bot.send_message(message.chat.id, 'Отправил тебе в лс')
        except Exception:
            bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
            bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))
    
@bot.message_handler(content_types = ['text'])
def ban_mute(message):
    global chat_member
    global reply_member
    global bot_member
    if message.text.lower() in ban_mute_list:
        try:
            chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
            reply_member = bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot_member = bot.get_chat_member(message.chat.id, bot_id)
            bann_mute.ban(message)
            bann_mute.mute(message)
        except AttributeError:
            anti_flood(message)
    if message.text in OD_flood_list:
        bot.delete_message(message.chat.id, message.message_id)
    
@bot.message_handler(content_types = ['pinned_message'])
def store_pinned_messages(message):
    try:
        message_text = (message.pinned_message.text).replace('<', '&lt;')
        message_text = message_text.replace('>', '&gt;')
        collection.update_one({'Group': message.chat.id},
                              {'$set': {str(message.pinned_message.message_id): [
                                  {'date': str(datetime.date.today()),
                                   'msg': str(message_text),
                                   'group': str(message.chat.username),
                                   'group_title': str(message.chat.title)}
                                      ]}},
                              upsert = True)  
    except Exception:
        bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(),message.chat.id, message.chat.username))



"""Polling"""

def polling(pollingbot):
    pollingbot.polling(none_stop=True)

if True:
    t = threading.Timer(1, polling, args=[jr])
    t.start()
    t = threading.Timer(1, polling, args=[bot])
    t.start()

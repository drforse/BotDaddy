import pymongo
from pymongo import MongoClient
import traceback
import telebot
import os
import time
import pprint
import datetime
import pytz
import schedule
import time


client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father

collection = db.pin_list
col2 = db.users
banned = col2.find_one()

def update_flood():
    doc = col2.find_one({'users':{'$exists':True}})['users']
    col2.replace_one({'users':{'$exists':True}},
                     {'users': doc})
#schedule.every(6).hours.do(update_flood)
#while True:
#    schedule.run_pending()
#    time.sleep(60)

bot = telebot.TeleBot (os.environ['token'])
bot_id = os.environ['bot_id']
bot_user = '@botsdaddyybot'

ban_keywords_list = ['!иди в баню','!иди в бан','!банан тебе в жопу','!нам будет тебя не хватать', '/ban', '/ban@botsdaddyybot']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban', '/unban@botsdaddyybot']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
OD_flood_list = ["Да как ты разговариваешь со старшими!"]
ban_mute_list = ban_keywords_list + unban_keywords_list + mute_keywords_list + unmute_keywords_list
developers = [500238135]

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

#Users
@bot.message_handler(commands = ['help'])
def show_help(message):
    doc = collection.find_one({'id': 0})
    help_msg = doc['help_msg']
    if message.chat.type != 'private':
        bot.send_message(message.from_user.id, help_msg, parse_mode = 'markdown')
        bot.send_message(message.chat.id, 'Отправил в лс')
    else:
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
        
@bot.message_handler(commands = ['pinlist'+bot_user])
def get_pinned_messages(message):
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

bot.polling()

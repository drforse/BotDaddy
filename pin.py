import pymongo
from pymongo import MongoClient
import traceback
import telebot
import os
import time
import pprint
import datetime

client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
collection = db.pin_list
posts = db.posts

bot = telebot.TeleBot (os.environ['token'])

ban_keywords_list = ['!иди в баню','!иди в бан','!банан тебе в жопу','!нам будет тебя не хватать', '/ban']
unban_keywords_list = ['!мы скучаем', '!выходи из бани', '!кончил', '/unban']
mute_keywords_list = ['!мут']
unmute_keywords_list = ['!анмут']
developers = [500238135]
help_definer = ''

#developers_only
   
@bot.message_handler(commands = ['help_define'])
def help_define(message):
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        bot.send_message(message.from_user.id, 'Define the help-message')
        bot.register_next_step_handler(message, help_message_handler)
    else:
        bot.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')

def help_message_handler(message):
    global help_definer
    if message.chat.id == help_definer:
        file = open('help_msg.txt', 'w')
        file.write(message.text)
        file.close()
        bot.send_message(message.chat.id, '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным, а не программированием, погуляй, например', parse_mode = 'markdown')

#IT-commands
@bot.message_handler(commands = ['chat_id'])
def chat_id(message):
    bot.send_message(message.chat.id, '`{}`'.format(message.chat.id),parse_mode = 'markdown')

#Users
@bot.message_handler(commands = ['help'])
def show_help(message):
    file = open('help_msg.txt', 'r')
    if message.chat.type != 'private':
        bot.send_message(message.from_user.id, file.read(), parse_mode = 'markdown')
        bot.send_message(message.chat.id, 'Отправил в лс')
    else:
        bot.send_message(message.chat.id, file.read(), parse_mode = 'markdown')

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        quant = 3
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay')
        elif chat_member.can_pin_messages == True or chat_member.status == 'creator':
            if message.text in ['/pintime', '/pintime@botsdaddyybot']:
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
            bot.send_message(message.chat.id, 'У тебя нет пинилки', reply_to_message_id = message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['pinn'])
def pin(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay', reply_to_message_id = message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            bot.send_message(message.chat.id, 'У тебя нет пинилки', reply_to_message_id = message.message_id)
        elif bot.get_chat(message.chat.id).pinned_message != None:
            bot.unpin_chat_message(message.chat.id)
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
        else:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['pin'])
def pin_silent(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay', reply_to_message_id = message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            bot.send_message(message.chat.id, 'У тебя нет пинилки', reply_to_message_id = message.message_id)
        elif bot.get_chat(message.chat.id).pinned_message != None:
            bot.unpin_chat_message(message.chat.id)
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
        else:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['unpin'])
def unpin(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups', reply_to_message_id = message.message_id)
        elif chat_member.can_pin_messages == None and chat_member.status != 'creator':
            bot.send_message(message.chat.id, 'У тебя нет пинилки', reply_to_message_id = message.message_id)
        else:
            bot.unpin_chat_message(message.chat.id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())   
        
@bot.message_handler(commands = ['pinlist'])
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
        bot.send_message(message.chat.id, traceback.format_exc())
    
@bot.message_handler(content_types = ['text'])
def ban_mute(message):
#ban
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.text.lower() in ban_keywords_list:
            if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
            else:
                bot.send_message(message.chat.id, 'у тебя нет банилки',reply_to_message_id = message.message_id)
        if message.text.lower() in unban_keywords_list:
            if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
            else:
                bot.send_message(message.chat.id, 'у тебя нет банилки',reply_to_message_id = message.message_id)
        if message.text.lower() == '!бан':
            if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            else:               
                bot.send_message(message.chat.id, '!уебан', reply_to_message_id = message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, 'make reply', reply_to_message_id = message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())   
#mute
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.text.lower() in mute_keywords_list:
            if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
            else:
                bot.send_message(message.chat.id, 'У тебя нет таких прав, холоп!',reply_to_message_id = message.message_id)
        if message.text.lower() in unmute_keywords_list:
            if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name), parse_mode = 'html')
            else:
                bot.send_message(message.chat.id, 'У тебя нет таких прав, холоп!',reply_to_message_id = message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, 'make reply', reply_to_message_id = message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())   
    
@bot.message_handler(content_types = ['pinned_message'])
def store_pinned_messages(message):
    try:
        message_text = (message.pinned_message.text).replace('<', '&lt;')
        message_text = message_text.replace('>', '&gt;')
        if collection.find_one({'Group': message.chat.id}) == None:
            collection.insert_one({'Group': message.chat.id})
        collection.update_one({'Group': message.chat.id},
                              {'$set': {str(message.pinned_message.message_id): [
                                  {'date': str(datetime.date.today()),
                                   'msg': str(message_text),
                                   'group': str(message.chat.username),
                                   'group_title': str(message.chat.title)}
                                      ]}})  
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())
       
bot.polling()

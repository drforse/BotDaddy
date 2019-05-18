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

ban_keywords_list = ['иди в баню','иди в бан','банан тебе в жопу','нам будет тебя не хватать', '/ban']
unban_keywords_list = ['мы скучаем', 'выходи из бани', 'кончил', '/unban']

@bot.message_handler(commands = ['chat_id'])
def chat_id(message):
    bot.send_message(message.chat.id, '`'+str(message.chat.id)+'`',parse_mode = 'markdown')

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        quant = 3
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay')
        elif chat_member.can_pin_messages == True or chat.member.status == 'creator':
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
        bot.send_message(message.from_user.id, text, parse_mode = 'html', disable_web_page_preview = True)
        bot.send_message(message.chat.id, 'Отправил тебе в лс')
    except Exception:
        try:
            document = collection.find_one({'Group': message.chat.id})
            text=''
            document.pop('_id')
            for ids in document:
                    if ids == '_id':
                        continue
                    elif ids == 'Group':
                        text += "[{}](t.me/{}):{}\n".format('Group', message.chat.username, message.chat.title)
                    else:
                        text += '[{}](t.me/{}/{}): {}\n'.format(document[ids][0]['date'], document[ids][0]['group'], ids, document[ids][0]['msg'])
            bot.send_message(message.from_user.id, text, parse_mode = 'markdown', disable_web_page_preview = True)
            bot.send_message(message.chat.id, 'Отправил тебе в лс')
        except Exception:
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
                bot.send_message(message.from_user.id, text+'/nИзвините за отсутствие ссылок, какие-то сообщения нарушают работу форматирования', disable_web_page_preview = True)
                bot.send_message(message.chat.id, 'Отправил тебе в лс')
            except Exception:
                bot.send_message(message.chat.id, traceback.format_exc())
    
@bot.message_handler(content_types = ['text'])
def ban(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if message.text.lower() in ban_keywords_list:
            if chat_member.can_restrict_members == True:
                bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            else:
                bot.send_message(message.chat.id, 'у тебя нет банилки',reply_to_message_id = message.message_id)
        if message.text.lower() in unban_keywords_list:
            if chat_member.can_restrict_members == True:
                bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            else:
                bot.send_message(message.chat.id, 'у тебя нет банилки',reply_to_message_id = message.message_id)
        if message.text.lower() == 'бан':
            if chat_member.can_restrict_members == True and bot.get_chat_member(message.chat.id, message.from_user.id).can_restrict_members == True or bot.get_chat_member(message.chat.id, message.from_user.id).status == 'creator':
                bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            else:               
                bot.send_message(message.chat.id, 'уебан', reply_to_message_id = message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())   
        
@bot.message_handler(content_types = ['pinned_message'])
def store_pinned_messages(message):
    try:
        if collection.find_one({'Group': message.chat.id}) == None:
            collection.insert_one({'Group': message.chat.id})
        collection.update_one({'Group': message.chat.id},
                              {'$set': {str(message.pinned_message.message_id): [
                                  {'date': str(datetime.date.today()),
                                   'msg': str(message.pinned_message.text),
                                   'group': str(message.chat.username),
                                   'group_title': str(message.chat.title)}
                                      ]}})  
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())
        
bot.polling()

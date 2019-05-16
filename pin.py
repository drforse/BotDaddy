import pymongo
from pymongo import MongoClient
import traceback
import telebot
import os
import time
import pprint

client = pymongo.MongoClient(os.environ['db'])
db = client.bot_father
collection = db.pin_list
posts = db.posts

bot = telebot.TeleBot (os.environ['token'])

ban_keywords_list = ['иди в баню','иди в бан','банан тебе в жопу','нам будет тебя не хватать', '/ban']
unban_keywords_list = ['мы скучаем', 'выходи из бани', 'кончил', '/unban']

@bot.message_handler(command = ['restmem'])
def check(message):
    bot.send_message(message.chat.id, str(bot.get_chat_member(message.chat.id, message.from_user.id).can_restrict_members),parse_mode = 'markdown')

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    try:
        quant = 3
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
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
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['pinn'])
def pin(message):
    try:
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay')
        else:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['pin'])
def pin_silent(message):
    try:
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.send_message(message.chat.id, 'make replay')
        else:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, True)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

@bot.message_handler(commands = ['unpin'])
def unpin(message):
    try:
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, 'Only for groups')
        elif message.reply_to_message == None:
            bot.unpin_chat_message(message.chat.id, message.message_id)
        else:
            bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())   
        
@bot.message_handler(commands = ['pinlist'])
def get_pinned_messages(message):
    try:
        document = collection.find_one({'Group':  '['+message.chat.title+']'+'(t.me/'+str(message.chat.username)+')'})
        text=''
        document.pop('_id')
        for ids in document:
            if ids == 'Group':
                text += '{}: {}\n'.format(ids, document[ids])
            else:
                text += '{}: {}\n'.format('['+ids+'](t.me/'+message.chat.username+'/'+ids+')', document[ids])
        bot.send_message(message.from_user.id, text, parse_mode = 'markdown', disable_web_page_preview = True)
        bot.send_message(message.chat.id, 'Отправил тебе в лс')
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())
    
@bot.message_handler(content_types = ['text'])
def ban(message):
    try:
        bot.get_chat_member(message.chat.id, message.from_user.id)
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
        if collection.find_one({'Group': '['+message.chat.title+']'+'(t.me/'+str(message.chat.username)+')'}) == None:
            collection.insert_one({'Group': '['+message.chat.title+']'+'(t.me/'+str(message.chat.username)+')'})
        collection.update_one({'Group':  '['+message.chat.title+']'+'(t.me/'+str(message.chat.username)+')'},
                              {'$set': {str(message.pinned_message.message_id):str(message.pinned_message.text)}})
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())
        
bot.polling()

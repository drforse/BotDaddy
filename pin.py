import traceback
import telebot
import os
import time

bot = telebot.TeleBot (os.environ['token'])

ban_keywords_list = ['бан','иди в баню','иди в бан','банан тебе в жопу','нам будет тебя не хватать', '/ban']
unban_keywords_list = ['мы скучаем', 'выходи из бани', 'кончил', '/unban']

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

@bot.message_handler(content_types = ['text'])
def ban(message):
    try:
        if message.text.lower() in ban_keywords_list:
            bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        if message.text.lower() in unban_keywords_list:
            bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    except Exception:
        bot.send_message(message.chat.id, traceback.format_exc())

bot.polling()

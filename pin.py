import traceback
import telebot
import os
import time

bot = telebot.TeleBot (os.environ['token'])

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    quant = 3
    try:
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
bot.polling()


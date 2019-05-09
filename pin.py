import telebot
import os

bot = telebot.TeleBot (os.environ['token'])

#def pin(message, quant):
#    if quant > 0:
 #       bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
  #      bot.unpin_chat_message(message.chat.id)
   #     quant -=1
    #    return

@bot.message_handler(commands = ['pintime'])
def pintime(message):
    quant = 3
    if message.text in ['/pintime', '/pintime@botsdaddyybot']:
        while quant > 0:
            try:
                bot.unpin_chat_message(message.chat.id)
                bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            except Exception:
                bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            quant -= 1
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

bot.polling()

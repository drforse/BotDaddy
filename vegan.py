import os
import telebot
import emoji
from emoji import emojize
from telebot import types
bot = telebot.TeleBot(os.environ['token'])

e = emoji.emojize
boom = e(':boom:', use_aliases = True)
energy = e(':zap:', use_aliases = True)
accur = e(':dart:', use_aliases = True)
uron = "Урон: "
energia = "Энергия/Выстрел: "
accuracy = "Точность выстрела(%, 5-1 энергии): "
accuracy_with_aim = "Точность выстрела с прицелом: "
line = '*______________________________________*'
spec = "Особенность: "
group_list = '@mtsgameh\n@LastVegan'

@bot.message_handler(commands=['help','start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, 'Привет! Я помогу тебе с поиском информации по игре [VeganWars](t.me/veganwarsbot)!\nСписок команд:\n/weapons - Оружие\n/perks - Способности(перки)\n/items - Предметы\n**\nБот находтся на стадии разработки!!', parse_mode = 'markdown')

@bot.message_handler(commands=['grouplist'])
def send_group_list(message):
    bot.send_message(message.chat.id, "Некоторые из групп, в которых можно поиграть в [VeganWars](t.me/veganwarsbot)\n" + group_list, parse_mode = 'markdown', disable_web_page_preview = True)

@bot.message_handler(commands=['feedback'])
def feedback_work(message):
    if message.text in ['/feedback', '/feedback ']:
        bot.send_message(message.chat.id, "Напишите предложение или отзыв после /feedback, в том же сообщения, что и команда")
    else:
        bot.forward_message(500238135, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "Спасибо за ваше предложение/отзыв, ваше мнение очень важно нам")

@bot.message_handler(commands=['weapons'])
def send_weapons(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    distant_b = types.KeyboardButton('Оружие дальнего боя')
    close_b = types.KeyboardButton('Оружие ближнего боя')
    markup.add(distant_b, close_b)
    msg = bot.send_message(message.chat.id, 'Выберите тип оружия:', reply_markup=markup)

@bot.message_handler(commands=['perks', 'items'])
def send_error(message):
    bot.send_message(message.chat.id, 'Извините, функция недоступна, т.к. бот находится на стадии разработки')

@bot.message_handler(content_types=['text'])
def send_distant_weapons(message):
    list = ['Оружие дальнего боя', 'Дробовик', "Револьвер", "Огнемет", "Снайперская винтовка", "Пистолет", "Обрез"]
    if message.text in list:
        markup_distant = types.ReplyKeyboardMarkup(row_width=1)
        kb = types.KeyboardButton
        revolver = kb("Револьвер")
        firegun = kb("Огнемет")
        shotgun = kb("Дробовик")
        sniper = kb("Снайперская винтовка")
        pistol = kb("Пистолет")
        shotgunn = kb("Обрез")
        _exit_ = kb("Выход")
        markup_distant.add(revolver, firegun, shotgun, sniper, pistol, shotgunn, _exit_)
        msg = bot.send_message(message.chat.id, 'Выберите оружие:', reply_markup=markup_distant)
        bot.register_next_step_handler(message, send_weapon_info)
        
def send_weapon_info(message):
    list = ['Оружие дальнего боя', 'Дробовик', "Револьвер", "Огнемет", "Снайперская винтовка", "Пистолет", "Обрез", "/help", "/weapons", "/start", "/perks", "/items"]
    if message.text == 'Выход':
        markup_rem = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Quit. /help', reply_markup = markup_rem)
    elif message.text == 'Револьвер':
        bot.send_message(message.chat.id, "_РЕВОЛЬВЕР_\n" + line + "\n\n" + boom + uron + "`3`\n" + energy + energia + "`3`\n" + accur + accuracy + "`80-70-60-50-40`\n" + accur + accuracy_with_aim + "`100-90-80-60`\n" + spec + "_None_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Огнемет':
        bot.send_message(message.chat.id, "_ОГНЕМЕТ_\n" + line + "\n\n" + boom + uron + "`1`\n" + energy + energia + "`3`\n" + accur + accuracy + "`80-?-60-50-40`\n" + accur + accuracy_with_aim + "_TODO_\n" + spec + "_Поджигает цель_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Дробовик':
        bot.send_message(message.chat.id, "_ДРОБОВИК_\n" + line + "\n\n" + boom + uron + "`2-7`\n" + energy + energia + "`4`\n" + accur + accuracy + "`88-73-46-0-0`\n" + accur + accuracy_with_aim + "`99-88-72-64-46`\n" + spec + "_+1 урона, если стрелять в игрока, который стоит вплотную_", parse_mode = 'markdown')
        send_distant_weapons(message) 
    elif message.text == 'Снайперская винтовка':
        bot.send_message(message.chat.id, "_СНАЙПЕРСКАЯ ВИНТОВКА_\n" + line + "\n\n" + boom + uron + "`8`\n" + energy + energia + "`5`\n" + accur + accuracy + "`10-?-?-?-?`\n" + accur + accuracy_with_aim + "`40-?-20-?-?`\n" + spec + "_точность можно повышать, выцеливая игрока. При выцеливании другого, точность сбрасывается_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Пистолет':
        bot.send_message(message.chat.id, "_ПИСТОЛЕТ_\n" + line + "\n\n" + boom + uron + "`2-3`\n" + energy + energia + "`3`\n" + accur + accuracy + "`91-?-75-64-51`\n" + accur + accuracy_with_aim + "`99-?-91-?-84-?`\n" + spec + "_None_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Обрез':
        bot.send_message(message.chat.id, "_ОБРЕЗ_\n" + line + "\n\n" + boom + uron + "`1-4`\n" + energy + energia + "`3`\n" + accur + accuracy + "`97-?-87-75-59`\n" + accur + accuracy_with_aim + "`?`\n" + spec + "_None_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text not in list:
        bot.send.message(message.chat.id, 'Пожалуйста, выберите один из предложенных вариантов')
bot.polling()

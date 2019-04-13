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
fist = e(':fist:', use_aliases = True)
uron = "Урон: "
energia = "Энергия/Выстрел: "
accuracy = "Точность выстрела(%, 5-1 энергии): "
accuraci = "Точность попадания(%, 8-1 энергии): "
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
    super_b = types.KeyboardButton('Наградное оружие')
    markup.add(distant_b, close_b, super_b)
    msg = bot.send_message(message.chat.id, 'Выберите тип оружия:', reply_markup=markup)

@bot.message_handler(commands=['perks', 'items'])
def send_error(message):
    bot.send_message(message.chat.id, 'Извините, функция недоступна, т.к. бот находится на стадии разработки')

@bot.message_handler(content_types=['text'])
def send_distant_weapons(message):
    list = ['Оружие дальнего боя', 'Дробовик', "Револьвер", "Огнемет", "Снайперская винтовка", "Пистолет", "Обрез"]
    list2 = ['Оружие ближнего боя', 'Цепь', 'Факел', 'Копье', 'Топор', 'Нож', 'Полицейская дубинка', 'Бейсбольная бита', 'Кастет', 'Кувалда', 'Булава']
    list3 = ['Наградное оружие', 'Лук Асгард', 'Катана', 'Копье Нарсил']
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
        back = kb("Назад")
        markup_distant.add(revolver, firegun, shotgun, sniper, pistol, shotgunn, back, _exit_)
        msg = bot.send_message(message.chat.id, 'Выберите оружие:', reply_markup=markup_distant)
        bot.register_next_step_handler(message, send_weapon_info)
    elif message.text in list2:
        markup_close = types.ReplyKeyboardMarkup(row_width=2)
        k = types.KeyboardButton
        itm0 = k(list2[1])
        itm1 = k(list2[2])
        itm2 = k(list2[3])
        itm3 = k(list2[4])
        itm4 = k(list2[5])
        itm5 = k(list2[6])
        itm6 = k(list2[7])
        itm7 = k(list2[8])
        itm8 = k(list2[9])
        itm9 = k(list2[10])
        __exit__ = k('Выход')
        back = k("Назад")        
        markup_close.add(itm0, itm1,itm2,itm3,itm4,itm5,itm6,itm7,itm8, itm9, back, __exit__)
        bot.send_message(message.chat.id, 'Выберите оружие:', reply_markup = markup_close)
        bot.register_next_step_handler(message, send_arm_info)
    elif message.text in list3:
        markup_super = types.ReplyKeyboardMarkup(row_width=1)
        k = types.KeyboardButton
        s0 = k(list3[1])
        s1 = k(list3[2])
        s2 = k(list3[3])
        __exit__ = k("Выход")
        back = k("Назад")
        markup_super.add(s0, s1, s2, back, __exit__)
        bot.send_message(message.chat.id, "Выберите оружие:", reply_markup = markup_super)
        bot.register_next_step_handler(message, send_superweapon_info)
    elif message.text not in list and message.text not in list2 and message.text not in list3:
        send_weapons(message)
        
def send_superweapon_info(message):
    list = ['Наградное оружие', 'Лук Асгард', 'Катана', 'Копье Нарсил', "/help", "/weapons", "/start", "/perks", "/items", "Назад"]
    if message.text == 'Выход':
        markup_rem = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Quit. /help', reply_markup = markup_rem)
    elif message.text == 'Лук Асгард':
        bot.send_message(message.chat.id, "ЗАСЕКРЕЧЕНО! Наши разведчики собирают информацию...")
        send_distant_weapons(message)
    elif message.text == 'Катана':
        bot.send_message(message.chat.id, "ЗАСЕКРЕЧЕНО! Наши разведчики собирают информацию...")
        send_distant_weapons(message)
    elif message.text == 'Копье Нарсил':
        bot.send_message(message.chat.id, "Обычное копье с несколькими отличиями:\n1)Контратака стоит 3 энергии вместо 2\n2)Копье можно метнуть (затем нужно его поднять для дальнейшего использования) . Стоит 3 энергии, наносит 2-6 урона.")
        send_distant_weapons(message)
    elif message.text == 'Назад':
        send_weapons(message)
    elif message.text not in list:
        send_distant_weapons(message)
        
def send_weapon_info(message):
    list = ['Оружие дальнего боя', 'Дробовик', "Револьвер", "Огнемет", "Снайперская винтовка", "Пистолет", "Обрез", "/help", "/weapons", "/start", "/perks", "/items", "Назад"]
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
    elif message.text == 'Назад':
        send_weapons(message)
    elif message.text not in list:
        send_distant_weapons(message)

def send_arm_info(message):
    list = ['Оружие ближнего боя', 'Цепь', 'Факел', 'Копье', 'Топор', 'Нож', 'Полицейская дубинка', 'Бейсбольная бита', 'Кастет', 'Кувалда', 'Булава',"/help", "/weapons", "/start", "/perks", "/items", "Назад"]
    ur = line + "\n\n" + fist+uron
    en = energy+energia
    ac = accur+accuraci+"`100-99-99-97-93-87-78-65`\n"
    if message.text == 'Выход':
        markup_rem = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Quit. /help', reply_markup = markup_rem)
    elif message.text == 'Цепь':
        bot.send_message(message.chat.id, "_ЦЕПЬ_\n" + ur + "`1-3`\n" + en + "`2`\n" + ac + spec + "_позволяет каждую вторую атаку выбить оружие из рук противника и нанести 2 урона_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Факел':
        bot.send_message(message.chat.id, "_ФАКЕЛ_\n" + ur + "`1-3`\n" + en + "`2`\n" + ac + spec + "_c вероятностью 50% поджигает_", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Копье':
        bot.send_message(message.chat.id, "_Копье_\n" + ur + "`1-4`\n" + en + "`3`\n" + ac + spec + '_позволяет каждую вторую атаку использовать специальный прием "Контратака": бьет всех соперников (не более двух), которые использовали оружие в этот ход. Тратит 2 энергии._', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Топор':
        bot.send_message(message.chat.id, "_ТОПОР_\n" + ur + "`1-3`\n" + en + "`2`\n" + ac + spec + '_c вероятностью в 70% калечит соперника_', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Нож':
        bot.send_message(message.chat.id, "_НОЖ_\n" + ur + "`1-2`\n" + en + "`2`\n" + ac + spec + '_c вероятностью в 50% вызывает кровотечение_', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Полицейская дубинка':
        bot.send_message(message.chat.id, "_ПОЛИЦЕСЙКАЯЯ ДУБИНКА_" + ur + "`1-3`\n" + ac + spec + '_отнимает 1 энергию у цели_', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Бейсбольная бита':
        bot.send_message(message.chat.id, "_БЕЙСБОЛЬНАЯ БИТА_" + ur + "`1-3`\n" + ac + spec + '_с вероятностью в 20% оглушает соперника на 1 ход_', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Кастет':
        bot.send_message(message.chat.id, "_КАСТЕТ_" + ur + "`1-2`\n" + ac + spec + '_отнимает 4 энергии у цели, если в момент удара цель отдыхала/перезаряжалась_', parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Булава':
        bot.send_message(message.chat.id, "БУЛАВА" + line + "\n\n" + "Информация собирается, если у вас есть, что сказать по поводу булавы, пишите /feedback", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Кувалда':
        bot.send_message(message.chat.id, "КУВАЛДА" + line + "\n\n" + "Информация собирается, если у вас есть, что сказать по поводу булавы, пишите /feedback", parse_mode = 'markdown')
        send_distant_weapons(message)
    elif message.text == 'Назад':
        send_weapons(message)
    elif message.text not in list:
        send_distant_weapons(message)
        
                
bot.polling()

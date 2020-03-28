import base64
from datetime import date

import aiocron
from aiogram import types, executor
from aiogram.dispatcher import FSMContext

from aiogram_bots_own_helper import *
from bot.hangbot_flood_cleaner import *
from parsings.gramota_parsing import *
from config import *
from bot.her import HerGame

from modules.fwd_to_text import *
from modules.AnyVideoDownload import VideoDownload

from bot.funcs import anti_flood

logging.basicConfig(level=logging.WARNING)


class bann_mute:
    async def ban(message):
        try:
            if message.text.lower() in ban_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> забанен, вините во всем Путина!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() in unban_keywords_list:
                if chat_member.can_restrict_members == True or chat_member.status == 'creator':
                    await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id, '<a href="tg://user?id="{}">{}</a> разбанен!'.format(
                        message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name),
                                           parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() == '!бан':
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                else:
                    await bot.send_message(message.chat.id, '!уебан', reply_to_message_id=message.message_id)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(message)
                elif reply_member.status == 'creator':
                    await anti_flood(message)
                elif reply_member.user.id == bot_id:
                    await anti_flood(message)
                elif reply_member.status == 'administrator':
                    await anti_flood(message)
            except:
                await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
                                                                             message.chat.username))

    async def mute(message):
        try:
            if message.text.lower() in mute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был брошен в мут!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
            if message.text.lower() in unmute_keywords_list:
                if chat_member.can_restrict_members or chat_member.status == 'creator':
                    await bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                    await bot.send_message(message.chat.id,
                                           '<a href="tg://user?id="{}">{}</a> был вызволен из мута!'.format(
                                               message.reply_to_message.from_user.id,
                                               message.reply_to_message.from_user.first_name), parse_mode='html')
                elif not chat_member.can_restrict_members:
                    await anti_flood(message)
        except (AttributeError, UnboundLocalError):
            member = await bot.get_chat_member(message.chat.id, bot_id)
            if member.can_delete_messages:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            try:
                if not bot_member.can_restrict_members:
                    await anti_flood(message)
                elif reply_member.status == 'creator':
                    await anti_flood(message)
                elif reply_member.user.id == bot_id:
                    await anti_flood(message)
                elif reply_member.status == 'administrator':
                    await anti_flood(message)
            except:
                await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
                await bot.send_message(developers[0], "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id,
                                                                             message.chat.username))



            # developers_only

@dp.message_handler(commands=['help_define'])
async def help_define(message):
    """
    define help message, only for devs of the bot
    """
    if message.from_user.id in developers:
        global help_definer
        help_definer = message.from_user.id
        await bot.send_message(message.from_user.id, 'Define the help-message')
        await bot.delete_message(message.chat.id, message.message_id)
        await Form.help_define.set()
    else:
        await bot.send_message(message.chat.id, 'Эта команда только для разработчиков бота!')


@dp.message_handler(state=Form.help_define)
async def help_message_handler(message, state=FSMContext):
    global help_definer
    if message.chat.id == help_definer:
        collection.update_one({'id': 0},
                              {'$set': {'help_msg': message.text}},
                              upsert=True)
        await bot.send_message(message.chat.id,
                               '*help* обновлен, пиздуй отсюда и займись уже чем-то интересным, а не программированием, погуляй, например',
                               parse_mode='markdown')
        await state.finish()


# IT-commands


# Users
@dp.message_handler(commands=['download_video'])
async def send_video(m):
    """
    not ready
    """
    link = m.reply_to_message.text if m.reply_to_message else m.text.split(maxsplit=1)[1]
    vid = VideoDownload().get_by_link(link)
    vid.download()

    logging.warning(f'start sending {vid.path} to {m.chat.first_name} (from local)')
    with open(vid.path, 'rb') as f:
        msg = await bot.send_video(m.chat.id, video=f, caption=f'{vid.website}\n\n{vid.name}\n{vid.width}x{vid.height}')
        logging.warning(f'sent {f.name} as {msg.document.file_name} to {m.chat.first_name}')

    # logging.warning(f'start sending {vid.name} to {m.chat.first_name} (from url: {vid.download_link})')
    # msg = await bot.send_video(m.chat.id, video=vid.download_link, caption=f'{vid.website}\n\n{vid.name}')
    # await bot.edit_message_caption(msg.chat.id, msg.message_id, caption=f'{msg.caption}\n{msg.video.width}x{msg.video.height}')
    # logging.warning(f'sent {vid.name} as {msg.document.file_name} to {m.chat.first_name}')

    os.remove(vid.path)


@dp.message_handler(commands=['create_list'])
async def new_list(m):
    """
    create a list of thing, later you can add thing in it
    """
    if m.reply_to_message:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Добавить',
                                          callback_data='add_to_list'))
        await bot.send_message(chat_id=m.chat.id, text=m.reply_to_message.text, reply_markup=kb)
        await bot.delete_message(chat_id=m.chat.id, message_id=m.reply_to_message.message_id)
        await bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    else:
        await bot.send_message(chat_id=m.chat.id, text='Команда должна быть реплаем на список.')


@dp.callback_query_handler(lambda c: c.data == 'add_to_list')
async def add_to_list(c, state=FSMContext):
    state = dp.current_state(chat=c.from_user.id, user=c.from_user.id)
    async with state.proxy() as data:
        data['message'] = c.message
    try:
        await bot.send_message(chat_id=c.from_user.id, text='Теперь напиши мне новые пункты списка')
        await bot.answer_callback_query(callback_query_id=c.id, text='Ответь мне в лс', show_alert=True)
        await state.set_state(Form.add_to_list)
    except (exceptions.BotBlocked, exceptions.CantInitiateConversation):
        await bot.answer_callback_query(callback_query_id=c.id, text='Сначали начин со мной диалог', show_alert=True)


@dp.message_handler(state=Form.add_to_list)
async def get_new_elements_for_list(m, state=FSMContext):
    async with state.proxy() as data:
        message = data['message']
    text = message.text + '\n' + m.text
    await bot.edit_message_text(text=text,
                                chat_id=message.chat.id,
                                message_id=message.message_id,
                                reply_markup=message.reply_markup)
    await bot.send_message(chat_id=m.chat.id, text='Готово')
    await bot.send_message(chat_id=message.chat.id, text='Список был обновлен', reply_to_message_id=message.message_id)
    await state.finish()


@dp.message_handler(commands=['gramota'])
async def get_word(m):
    """
    get info about a word specified in command's args using gramota.ru
    """
    if len(m.text.split()) > 1:
        word = await get_complex_argument(m.text)
        word_info = await gramota_parse(word)
        if await get_word_dict(word_info):
            words = await get_word_dict(word_info)
            kb = types.InlineKeyboardMarkup()
            synonyms = None
            for i in words:
                if 'None' not in words[i][1] and i != 'orthographic' and words[i][1]:
                    if i not in ['synonyms', 'synonyms_short']:
                        kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
                    elif i in ['synonyms', 'synonyms_short'] and not synonyms:
                        kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
                    if i in ['synonyms', 'synonyms_short']:
                        synonyms = True
                # kb.add(types.InlineKeyboardButton(words[i][0], callback_data=f'{word}:: {i}'))
            print(kb)
            if 'None' not in words['orthographic'][1]:
                message_text = words['orthographic'][1]
            elif kb['inline_keyboard']:
                message_text = word
            else:
                if len(word.split()) == 1:
                    message_text = f'Слово <i>{word}</i> не найдено.'
                else:
                    message_text = f'Словосочетание <i>{word}</i> не найдено.'
            await bot.send_message(m.chat.id, message_text, reply_markup=kb, parse_mode='html')
        else:
            words = await similar_words(word)
            if len(word.split()) == 1:
                message_text = f'Слово _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            else:
                message_text = f'Словосочетание _{word}_ не найдено.\nВозможно, вы имели ввиду одно из:\n_{words}_'
            await bot.send_message(m.chat.id, message_text, parse_mode='markdown')


@dp.message_handler(lambda m: m.chat.type == 'private', commands=['fwd_to_text'])
async def setup_fwd(m):
    """
    create a dialog/monolog from messages
    example:
    /fwd_to_text
    George: Hi (message 0)
    Julia: Hi (message 1)
    /stop
    result:
        xxx: Hi (message 2)
        yyy: Hi (message 2)

    in settings you may customize if the result should be anonimous (xyz...) or public (not xyz, but names)
        and create your own dictionaries instead xyz...
    """
    try:
        kb = types.InlineKeyboardMarkup()
        monolog = types.InlineKeyboardButton('Монолог', callback_data='fwd_to_text monolog')
        dialog = types.InlineKeyboardButton('Диалог', callback_data='fwd_to_text dialog')
        settings_button = types.InlineKeyboardButton('⚙️ Настройки', callback_data='fwd_to_text settings')
        kb.add(monolog, dialog, settings_button)
        await bot.send_message(chat_id=m.chat.id, text='Выберите тип текста:', reply_markup=kb)
    except:
        await log_err(m=m, err=traceback.format_exc())
        await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


@dp.callback_query_handler(lambda c: c.data in ['fwd_to_text monolog', 'fwd_to_text dialog'])
async def forward_to_text(c, state=FSMContext):
    try:
        first_fwd_msg = await bot.send_message(c.message.chat.id, 'Начнем')
        first_fwd_msg = first_fwd_msg.message_id
        async with state.proxy() as data:
            data['text_type'] = c.data.split()[-1]
            data['first_fwd_msg'] = first_fwd_msg
        await bot.answer_callback_query(callback_query_id=c.id)
        await bot.edit_message_reply_markup(chat_id=c.message.chat.id, message_id=c.message.message_id)
        await Form.fwded_msgs.set()
    except:
        await log_err(m=c.message, err=traceback.format_exc())
        await bot.send_message(c.message.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


@dp.message_handler(commands=['stop'], state=Form.fwded_msgs)
async def send_fwded_msgs_in_single_msg(m, state=FSMContext):
    """
    stop sending messages for a dialog/monolog, see more in /help fwd_to_text
    """
    try:
        user_db = ForwardsToTextUser(m.from_user.id)
        markers_dictionary = ForwardsToTextDB().get_dictionary(dict_id=user_db.default_dict.id,
                                                               is_global=user_db.default_dict.is_global,
                                                               user=user_db)
        async with state.proxy() as data:
            text_type = data['text_type']
            first_fwd_msg = data['first_fwd_msg']

        funcs = ForwardsToText(chat_id=m.chat.id, first_fwd_msg_id=first_fwd_msg, last_fwd_msg_id=m.message_id)
        if text_type == 'monolog':
            text = await funcs.get_monolog()
        else:
            text = await funcs.get_dialog(markers_dictionary=markers_dictionary.markers, mode=user_db.default_mode)
        await bot.send_message(m.chat.id, text, parse_mode='html')
    except exceptions.MessageIsTooLong:
        message_parts = await cut_for_messages(text, 4096)
        for part in message_parts:
            await bot.send_message(m.chat.id, part, parse_mode='html')
    except exceptions.NetworkError:
        await bot.send_message(m.chat.id, 'Попробуйте отправить по меньшему количеству сообщений, но результат не '
                                          'гарантирую. Я уже работаю над этой ошибкой. (НИХУЯ)')
    except exceptions.MessageTextIsEmpty:
        await bot.send_message(m.chat.id, 'No messages found')
    except:
        await log_err(m=m, err=traceback.format_exc())
        await bot.send_message(m.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')
    finally:
        await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'fwd_to_text init')
async def fwd_to_text_get_init_message(c):
    try:
        kb = types.InlineKeyboardMarkup()
        monolog = types.InlineKeyboardButton('Монолог', callback_data='fwd_to_text monolog')
        dialog = types.InlineKeyboardButton('Диалог', callback_data='fwd_to_text dialog')
        settings_button = types.InlineKeyboardButton('⚙️ Настройки', callback_data='fwd_to_text settings')
        kb.add(monolog, dialog, settings_button)
        await bot.edit_message_text('Выберите тип текста:', c.message.chat.id, c.message.message_id, reply_markup=kb)
    except:
        await log_err(m=c.message, err=traceback.format_exc())
        await bot.send_message(c.message.chat.id, 'Sry, We got an error. We are already fixing it (НИХУЯ).')


@dp.callback_query_handler(lambda c: c.data == 'fwd_to_text settings')
async def edit_fwd_to_text_settings(c):
    kb = types.InlineKeyboardMarkup()
    dicts_button = types.InlineKeyboardButton(text='Словари маркеров', callback_data='fwd_to_text settings dicts')
    default_mode_button = types.InlineKeyboardButton(text='Режим по умолчанию',
                                                     callback_data='fwd_to_text settings default_mode')
    back_button = types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text init')
    kb.add(dicts_button, default_mode_button)
    kb.add(back_button)
    await bot.edit_message_text('⚙️ Настройки', c.message.chat.id, c.message.message_id, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == 'fwd_to_text settings default_mode')
async def start_setting_fwd_to_text_default_mode(c):
    user_db = ForwardsToTextUser(c.from_user.id)
    anonimous_mode_button_text = 'Анонимный' if not user_db.default_mode == 'anonimous' else '☑ Анонимный'
    public_mode_button_text = 'Публичный' if not user_db.default_mode == 'public' else '☑ Публичный'
    kb = types.InlineKeyboardMarkup()
    anonimous_mode_button = types.InlineKeyboardButton(anonimous_mode_button_text,
                                                       callback_data='fwd_to_text settings set_default_mode anonimous')
    public_mode_button = types.InlineKeyboardButton(public_mode_button_text,
                                                    callback_data='fwd_to_text settings set_default_mode public')
    back_button = types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings')
    kb.add(anonimous_mode_button, public_mode_button)
    kb.add(back_button)

    await bot.edit_message_text('Выберите режим по умолчанию', c.message.chat.id, c.message.message_id, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith('fwd_to_text settings set_default_mode '))
async def set_fwd_to_text_default_mode(c):
    user_db = ForwardsToTextUser(c.from_user.id)
    user_db.set_default_mode(c.data.split()[-1])
    try:
        c.data = 'fwd_to_text settings default_mode'
        await start_setting_fwd_to_text_default_mode(c)
    except exceptions.MessageNotModified:
        await bot.answer_callback_query(c.id, 'Ничего не изменено.')


@dp.callback_query_handler(lambda c: c.data == 'fwd_to_text settings dicts')
async def edit_fwd_to_text_dicts_settings(c):
    user_db = ForwardsToTextUser(c.from_user.id)

    kb = types.InlineKeyboardMarkup()
    for dic in user_db.get_global_dictionaries():
        text = f'📌 {dic.name}' if user_db.default_dict.is_global and user_db.default_dict.id == dic.id else dic.name
        kb.add(types.InlineKeyboardButton(text,
                                          callback_data=f'fwd_to_txt settings marker_dict edit menu global {dic.id}'))
    for dic in user_db.dictionaries:
        text = f'📌 {dic.name}' if not user_db.default_dict.is_global and user_db.default_dict.id == dic.id else dic.name
        kb.add(types.InlineKeyboardButton(text,
                                          callback_data=f'fwd_to_txt settings marker_dict edit menu {dic.id}'))
    if not user_db.dictionaries:
        message_text = 'Вот доступные Вам словари.\n\nПримечание: у Вас нет ни одного <i>кастомного словаря</i>'
    else:
        message_text = 'Вот доступные Вам словари'
    add_custom_dict_button = types.InlineKeyboardButton('Добавить кастомный словарь',
                                                        callback_data='fwd_to_txt settings marker_dict add')
    back_button = types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings')
    kb.add(add_custom_dict_button, back_button)

    await bot.edit_message_text(message_text, c.message.chat.id, c.message.message_id,
                                reply_markup=kb, parse_mode='html')


@dp.callback_query_handler(lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit menu '))
async def edit_custom_markers_dict(c):
    kb = types.InlineKeyboardMarkup()

    dict_to_edit_is_global = c.data.split()[-2] == 'global'
    markers_dict_to_edit = ForwardsToTextDB().get_dictionary(dict_id=int(c.data.split()[-1]),
                                                             is_global=dict_to_edit_is_global,
                                                             user_id=c.from_user.id)

    if dict_to_edit_is_global:  # if not the user's dict --> get global dict
        make_default_button = types.InlineKeyboardButton('Использовать по умолчанию 📌',
                                                         callback_data='fwd_to_txt settings marker_dict edit make_default global ' +
                                                                       c.data.split()[-1])
        kb.add(make_default_button)
    else:  # if the user's dic --> get user's dic
        make_default_button = types.InlineKeyboardButton('Использовать по умолчанию 📌',
                                                         callback_data='fwd_to_txt settings marker_dict edit make_default ' +
                                                                       c.data.split()[-1])
        remove_button = types.InlineKeyboardButton('Удалить ✖',
                                                   callback_data='fwd_to_txt settings marker_dict edit remove ' +
                                                                 c.data.split()[-1])
        kb.add(make_default_button, remove_button)

    if not markers_dict_to_edit:
        await bot.send_message(c.message.chat.id, 'Непредвиденная ситуация! Всем срочно покинуть борт! Мы горим! '
                                                  'Кругом огонь! Ад на Земле... или Земля это Ад!')
        return

    back_button = types.InlineKeyboardButton('🔙Назад', callback_data='fwd_to_text settings dicts')
    kb.add(back_button)

    message_text = f'Редактирование {markers_dict_to_edit.name}\n\n{" ".join(markers_dict_to_edit.markers)}'

    await bot.edit_message_text(message_text, c.message.chat.id, c.message.message_id, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit remove '))
async def remove_markers_dict(c):
    user_db = ForwardsToTextUser(c.from_user.id)
    user_db.delete_dictionary(int(c.data.split()[-1]))
    c.data = 'fwd_to_text settings dicts'
    await edit_fwd_to_text_dicts_settings(c)


@dp.callback_query_handler(lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit make_default '))
async def make_markers_dict_default(c):
    user_db = ForwardsToTextUser(c.from_user.id)
    dict_to_edit_is_global = c.data.split()[-2] == 'global'
    new_default_dic = user_db.get_dictionary(dict_id=int(c.data.split()[-1]),
                                             is_global=dict_to_edit_is_global,
                                             user_id=c.from_user.id)
    user_db.set_default_dict(dictionary=new_default_dic)

    await bot.answer_callback_query(callback_query_id=c.id, text='Готово')


@dp.callback_query_handler(lambda c: c.data == 'fwd_to_txt settings marker_dict add')
async def add_custom_markers_dict(c):
    await bot.send_message(c.message.chat.id, 'Отправьте новый словарь в формате: \nXYZ (название)\n'
                                              '<code>x y z a b c d e f j k l m n o p q r s t u v w</code> (каждый маркер'
                                              ' окружен пробелами)\n\n ПРИМЕЧАНИЯ В СКОБКАХ ПИСАТЬ НЕ НАДО!',
                           parse_mode='html')
    await bot.answer_callback_query(c.id)
    await Form.add_markers_dict.set()


@dp.message_handler(state=Form.add_markers_dict)
async def get_new_custom_markers_dict(m, state=FSMContext):
    try:
        try:
            new_markers_dict_name = m.text.split('\n')[0]
            new_markers_dict = m.text.split('\n')[1].split()
        except IndexError:
            await bot.send_message(m.chat.id, 'Отправьте новый словарь в формате: \nXYZ (название)\n'
                                              '<code>x y z a b c d e f j k l m n o p q r s t u v w</code>(каждый маркер'
                                              ' окружен пробелами)\n\n ПРИМЕЧАНИЯ В СКОБКАХ ПИСАТЬ НЕ НАДО!',
                                   parse_mode='html')
            return

        user_db = ForwardsToTextUser(m.from_user.id)
        try:
            new_dict = await user_db.add_dictionary(name=new_markers_dict_name, markers=new_markers_dict)
        except AllMarkersWrong:
            message_text = ('Ни один из символов не подходит, если Вы считаете, что произошла ошибка, то напишите об '
                            'этом в /feedback (если у Вас скрытые форварды, то приложите свой юзернейм/номер '
                            'телефона), и Вам ответят как можно быстрее')
            await bot.send_message(m.chat.id, message_text)
            await state.finish()
            return
        message_text = 'Добавлен следующий словарь:\n' + ' '.join(new_dict[0].markers) + '\n\n'
        if new_dict[1]:
            message_text += 'Следующие маркера добавлены не были, т.к. они не подходят:'
            message_text += ' '.join(new_dict[1])
            message_text += ('если Вы считаете, что произошла ошибка, то напишите об этом в /feedback '
                             '(если у Вас скрытые форварды, то приложите свой юзернейм/номер телефона), и Вам ответят '
                             'как можно быстрее')
        await bot.send_message(m.chat.id, message_text)
        await state.finish()
    except:
        await log_err(traceback.format_exc(), m)
        await state.finish()


@dp.message_handler(content_types=['text'])
async def ban_mute(message):
    try:
        global chat_member
        global reply_member
        global bot_member
        if message.chat.type != 'private':
            doc = col_groups_users.find_one({'group': message.chat.id})
            if not doc:
                col_groups_users.insert_one({'group': message.chat.id,
                                             'users': [message.from_user.id]})
            elif message.from_user.id not in doc['users']:
                col_groups_users.update_one({'group': message.chat.id},
                                            {'$push': {'users': message.from_user.id}})
        else:
            doc = col_groups_users.find_one({'user': message.chat.id})
            if not doc:
                col_groups_users.insert_one({'user': message.chat.id})
        if message.text.lower() in ban_mute_list:
            try:
                chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
                reply_member = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                bot_member = await bot.get_chat_member(message.chat.id, bot_id)
                await bann_mute.ban(message)
                await bann_mute.mute(message)
            except AttributeError:
                await anti_flood(message)
        elif message.reply_to_message and message.reply_to_message.from_user.id == 121913006 or message.text.lower() == '/start@hangbot':
            if message.chat.id not in hang_bot_flood:
                hang_bot_flood[message.chat.id] = [message]
            hangbot_flood = hang_bot_flood[message.chat.id]
            hangbot_flood.append(message)
            hang_bot_flood[message.chat.id] = hangbot_flood
        bydlodoc = colh.find_one({'bydlos': 'future',
                                  'group': message.chat.id})
        if bydlodoc:
            if str(message.from_user.id) not in bydlodoc:
                colh.update_one({'bydlos': 'future',
                                 'group': message.chat.id},
                                {'$set': {str(message.from_user.id): {'allmsgs': 0,
                                                                      'badmsgs': 0}}})
                bydlodoc = colh.find_one({'bydlos': 'future',
                                          'group': message.chat.id})
            if 'allmsgs' in bydlodoc[str(message.from_user.id)]:
                msgs = bydlodoc[str(message.from_user.id)]['allmsgs'] + 1
            else:
                msgs = 1
            if itisbadmessage(message):
                if 'badmsgs' in bydlodoc[str(message.from_user.id)]:
                    badmsgs = bydlodoc[str(message.from_user.id)]['badmsgs'] + 1
                else:
                    badmsgs = 1
            else:
                badmsgs = bydlodoc[str(message.from_user.id)]['badmsgs']
            colh.update_one({'bydlos': 'future',
                             'group': message.chat.id},
                            {'$set': {str(message.from_user.id): {'allmsgs': msgs,
                                                                  'badmsgs': badmsgs}}})
        else:
            badmsgs = 1 if itisbadmessage(message) else 0
            colh.insert_one({'bydlos': 'future',
                             'group': message.chat.id,
                             str(message.from_user.id): {'allmsgs': 1,
                                                         'badmsgs': badmsgs}})
            print(colh.find_one({'bydlos': 'future',
                                 'group': message.chat.id}))
    except:
        await log_err(m=message, err=traceback.format_exc())


@dp.message_handler(content_types=['pinned_message'])
async def store_pinned_messages(message):
    try:
        if message.pinned_message.text:
            message_text = message.pinned_message.text
            if '<' in message.pinned_message.text:
                message_text = message_text.replace('<', '&lt;')
            if '<' in message.pinned_message.text:
                message_text = message_text.replace('>', '&gt;')
        elif message.pinned_message.photo:
            if message.pinned_message.caption:
                message_text = 'photo: ' + message.pinned_message.caption
            else:
                message_text = 'photo'
        elif message.pinned_message.poll:
            message_text = 'poll'
        elif message.pinned_message.contact:
            message_text = 'contact: ' + message.pinned_message.contact.phone_number
        elif message.pinned_message.audio:
            message_text = 'audio'
        elif message.pinned_message.document:
            message_text = 'document'
        elif message.pinned_message.animation:
            message_text = 'animation'
        elif message.pinned_message.game:
            message_text = 'game'
        elif message.pinned_message.sticker:
            message_text = 'sticker'
        elif message.pinned_message.video:
            message_text = 'video'
        elif message.pinned_message.voice:
            message_text = 'voice'
        elif message.pinned_message.video_note:
            message_text = 'video_note'
        elif message.pinned_message.location:
            message_text = 'location'
        collection.update_one({'Group': message.chat.id},
                              {'$set': {str(message.pinned_message.message_id): [
                                  {'date': str(date.today()),
                                   'msg': str(message_text),
                                   'group': str(message.chat.username),
                                   'group_title': str(message.chat.title)}
                              ]}},
                              upsert=True)
    except Exception:
        await bot.send_message(message.chat.id, 'Some error occured. Speak to bot-developer(@dr_forse)')
        await bot.send_message(developers[0],
                               "{}\n\n{} ({})".format(traceback.format_exc(), message.chat.id, message.chat.username))


@dp.callback_query_handler(lambda call: check_date(call.message.date))
async def send_info_about_word(call):
    try:
        word = call.data.split(':: ')[0]
        data = await get_word_dict(await gramota_parse(word))
        dict_type = call.data.split(':: ')[1]
        title = data[dict_type][0]
        description = data[dict_type][1]
        if call.message.chat.type == 'private':
            await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            await bot.answer_callback_query(call.id)
        else:
            if len(description) > 1000:
                description = await cut_message(description, 1000)
                description = description['cuted']
                deep_link = base64.urlsafe_b64encode(f'gramota-4096-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
                description += f'<a href="t.me/{bot_user}?start={deep_link}"> читать продолжение...</a>'
            print(description)
            await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
            await bot.answer_callback_query(call.id)
            await asyncio.sleep(30)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except exceptions.MessageIsTooLong:
        description = await cut_message(description, 4096 - 500)
        description = description['cuted']
        deep_link = base64.urlsafe_b64encode(f'gramota-max-{word}-{dict_type}'.encode('windows-1251')).decode('windows-1251')
        description += f'<a href="t.me/{bot_user}?start={deep_link}"> показать всё...</a>\n' \
                       f'<a href="http://gramota.ru/slovari/dic/?word={word}&all=x"> продолжить на сайте...</a>'
        await bot.send_message(call.message.chat.id, f'<b>{title}</b>\n{description}', parse_mode='html')
    except exceptions.MessageNotModified:
        pass
    except:
        await log_err(m=call.message, err=traceback.format_exc())


def itisbadmessage(m):
    text = m.text.lower()
    bad_words = ['fuck', 'dick', "хуи", "хер", "уебать", "ебать", "bitch", "уебан", "еблан", "пиздюк",
                 "пиздабол", "ебал", "неебический", "мудак", "мудло", "мудила", "хуета", "ебаный", "ебанный",
                 "пидарас", "пидрила", "педик", "пендос", "твою мать", "твою ж мать", "твою же мать", "твою же ж мать",
                 "твою жеж мать", "долбоеб", "пизд", "ебал", "мать твою", "мамку твою", "задолбал", "пидорас"]
    if 'ё' in text:
        bad_words += text.replace('е', "ё")
    if 'й' in text:
        bad_words += text.replace('й', 'и')
    for bad_word in bad_words:
        if bad_word in text:
            collection.update_one({'temp_checker': 'bad_messages'},
                                  {'$push': {'bad_messages': text}},
                                  upsert=True)
            return True


@aiocron.crontab('0 */6 * * *')
async def update_flood():
    col2.replace_one({'users': {'$exists': True}},
                     {'users': []})


@aiocron.crontab('0 0 * * *')
async def update_bydlos():
    groups = []
    for doc in colh.find({'group': {'$exists': True}}):
        if doc['group'] not in groups:
            groups.append(doc['group'])
    for group in groups:
        await HerGame(chat_id=group).reset_her()

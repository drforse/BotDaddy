import logging

from aiogram import executor
from telethon.sessions import StringSession

from .bot.user_commands import *
from .bot.it_commands import *
from .bot.dev_commands import *
from .bot.passive_handlers import *
from .config import dp, developers, TG_API_HASH, TG_API_ID, API_TOKEN, TELETHON_SESSION_STRING
from .aiogram_bots_own_helper import *
from .mixin_types import TelethonBot, TelethonClient


def register_handlers():
    Cancel().register(commands=['cancel'], state='*')

    # IT-commands
    Ke().register(commands=['ke'])
    ChatId().register(commands=['chat_id'])
    Ping().register(commands=['ping'])
    User().register(commands=['user'])
    GetMessage().register(commands=['get_message'])

    # Users
    Commands().register(commands=['commands'])
    GetFirstMsg().register(commands=['get_first_msg'])
    Help().register(commands=['help'])
    Pin().register(commands=['pin'])
    PinList().register(commands=['pinlist'])
    PinTime().register(commands=['pintime'])
    Q().register(commands=['q'])
    Mask().register(commands=['mask'])
    Spell().register(commands=['spell'])
    Start().register(lambda m: len(m.text.split()) == 1, commands=['start'])
    Time().register(commands=['time'])
    Unpin().register(commands=['unpin'])
    Weather().register(commands=['weather'])
    Her().register(commands=['her'])
    RunCHanger().register(commands=['run_changer'])
    HangStatsSwitch().register(commands=['hangstats_switch'])
    Winrate().register(commands=['winrate'])
    Bots().register(commands=['bots'])
    Admins().register(commands=['admins'])
    TelegraphUpload().register(commands=['telegraph_upload'])

    Dic().register(commands=['dic'])
    DicResult().reg_callback(DicResult.execute, lambda c: c.data.startswith('dic result'))

    def dic_start_params_filter(m):
        split_ = m.text.split(maxsplit=1)
        if len(split_) <= 1:
            return False
        return resolve_deep_link(split_[1]).startswith('dic result')

    DicResult().reg_message(DicResult.handle_start_params, dic_start_params_filter)

    # feedback register
    fb = Feedback()
    fb.register(commands=['feedback'])
    fb.reg_callback(fb.answer_callback_handler, lambda c: c.data.startswith('feedback reply'))
    fb.reg_message(fb.handle_answer, state=fb.states_group.handle_answer)

    # create_list register
    create_l = CreateList()
    create_l.register(commands=['create_list'])
    reg_message = create_l.reg_message
    reg_callback = create_l.reg_callback
    reg_callback(create_l.add_to_list, lambda c: c.data == 'add_to_list')
    reg_message(create_l.get_new_elements_for_list, state=create_l.states_group.add_to_list)

    # gramota register
    gramota = Gramota()
    gramota.register(commands=['gramota'])
    reg_message = gramota.reg_message
    reg_callback = gramota.reg_callback
    reg_callback(gramota.send_info_about_word, lambda c: c.data.startswith('gramota') and check_date(c.message.date))
    reg_message(gramota.handle_start_params, gramota.in_start_params, commands=['start'])

    # fwd_to_text register
    cmd = FwdToText()
    cmd.register(lambda m: m.chat.type == 'private', commands=['fwd_to_text'])
    reg_message = cmd.reg_message
    reg_callback = cmd.reg_callback

    reg_callback(cmd.handle_messages, lambda c: c.data in ['fwd_to_text monolog', 'fwd_to_text dialog'])
    reg_message(cmd.stop_handling, commands=['stop'], state=cmd.states_group.fwded_msgs)
    reg_callback(cmd.get_init_message, lambda c: c.data == 'fwd_to_text init')
    reg_callback(cmd.edit_settings, lambda c: c.data == 'fwd_to_text settings')
    reg_callback(cmd.start_setting_default_mode, lambda c: c.data == 'fwd_to_text settings default_mode')
    reg_callback(cmd.set_default_mode, lambda c: c.data.startswith('fwd_to_text settings set_default_mode '))
    reg_callback(cmd.edit_dicts_settings, lambda c: c.data == 'fwd_to_text settings dicts')
    reg_callback(cmd.edit_custom_markers_dict, lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit menu '))
    reg_callback(cmd.remove_markers_dict, lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit remove '))
    reg_callback(cmd.make_markers_dict_default, lambda c: c.data.startswith('fwd_to_txt settings marker_dict edit make_default '))
    reg_callback(cmd.add_custom_markers_dict, lambda c: c.data == 'fwd_to_txt settings marker_dict add')
    reg_message(cmd.get_new_custom_markers_dict, state=cmd.states_group.add_markers_dict)

    # Developers
    Logs().register(lambda m: m.from_user.id in developers, commands=['logs'])
    Reload().register(lambda m: m.from_user.id in developers, commands=['reload'])
    Aeval().register(lambda m: m.from_user.id in developers, commands=['aeval'])
    Aexec().register(lambda m: m.from_user.id in developers, commands=['aexec'])
    Hupload().register(lambda m: m.from_user.id in developers and m.caption.startswith('/hupload'),
                       content_types=['document'])
    Popen().register(lambda m: m.from_user.id in developers, commands=['popen'])
    PopenDoc().register(lambda m: m.from_user.id in developers and m.caption.startswith('/popen'),
                        content_types=['document'])
    Statistic().register(lambda m: m.from_user.id in developers, commands=['statistic'])
    Mailing().register(lambda m: m.from_user.id in developers, commands=['mailing'])
    CleanChats().register(lambda m: m.from_user.id in developers, commands=['clean_chats'])

    # help_define register
    helpd = HelpDefine()
    helpd.register(lambda m: m.from_user.id in developers, commands=['help_define'])
    helpd.dp.register_message_handler(helpd.handle_help, state=helpd.states_group.get_help)

    # passive_handlers register
    PinHandler().register(content_types=['pinned_message'])
    TextHandler().register(content_types=['text'])


def main():
    logging.basicConfig(level=logging.INFO)
    from .bot import sheduled_tasks
    register_handlers()
    tl_bot = TelethonBot(
        session='telethon_bot',
        api_id=TG_API_ID,
        api_hash=TG_API_HASH)
    TelethonBot.set_current(tl_bot)
    tl_bot.start(bot_token=API_TOKEN)
    tl_client = TelethonClient(
        session=StringSession(TELETHON_SESSION_STRING),
        api_id=TG_API_ID,
        api_hash=TG_API_HASH)
    TelethonClient.set_current(tl_client)
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()

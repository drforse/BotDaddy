from bot.user_commands import *
from bot.it_commands import *
from bot.dev_commands import *
from bot.passive_handlers import *
from bot import sheduled_tasks
from aiogram import executor
from config import dp, developers
from aiogram_bots_own_helper import check_date
import logging

logging.basicConfig(level=logging.INFO)

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

# Developers
Logs().register(lambda m: m.from_user.id in developers, commands=['logs'])
Reload().register(lambda m: m.from_user.id in developers, commands=['reload'])
Aeval().register(lambda m: m.from_user.id in developers, commands=['aeval'])
Aexec().register(lambda m: m.from_user.id in developers, commands=['aexec'])
DefineSession().register(lambda m: m.from_user.id in developers, commands=['define_session'])
Hupload().register(lambda m: m.from_user.id in developers and m.caption.startswith('/hupload'),
                   content_types=['document'])
Popen().register(lambda m: m.from_user.id in developers, commands=['popen'])
PopenDoc().register(lambda m: m.from_user.id in developers and m.caption.startswith('/popen'),
                    content_types=['document'])

# help_define register
helpd = HelpDefine()
helpd.register(lambda m: m.from_user.id in developers, commands=['help_define'])
helpd.dp.register_message_handler(helpd.handle_help, state=helpd.states_group.get_help)

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

# passive_handlers register
PinHandler().register(content_types=['pinned_message'])
TextHandler().register(content_types=['text'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

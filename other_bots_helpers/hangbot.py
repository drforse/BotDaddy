async def switch_state(state):
    if state == 'off':
        state = 'on'
    elif state == 'on':
        state = 'off'
    return state


async def get_hang_bot_stats(mlist):
    mlist = list(filter(lambda msg: len(msg.text) == 1, mlist))
    letters = {}
    one_message_for_user_list = []
    letters_by_users = {}
    continue_game_times_by_users = {}
    for m in mlist:
        if m.from_user.id not in one_message_for_user_list:
            one_message_for_user_list.append(m)
    for m in one_message_for_user_list:
        letters[m.from_user.id] = {m.message_id: m.date}
    for m in mlist:
        if m.message_id not in letters[m.from_user.id].keys():
            letters[m.from_user.id][m.message_id] = m.date
    for user in letters:
        for mes in letters[user]:
            if user not in letters_by_users:
                letters_by_users[user] = 1
            else:
                letters_by_users[user] += 1
            try:
                if letters[user][mes].timestamp() - last_m_date >= 180:
                    if 'long' in continue_game_times_by_users and user in continue_game_times_by_users['long']:
                        continue_game_times_by_users['long'][user] += 1
                    else:
                        continue_game_times_by_users['long'] = {user: 1}
                elif letters[user][mes].timestamp() - last_m_date >= 60:
                    if 'medium' in continue_game_times_by_users and user in continue_game_times_by_users['medium']:
                        continue_game_times_by_users['medium'][user] += 1
                    else:
                        continue_game_times_by_users['medium'] = {user: 1}
                elif letters[user][mes].timestamp() - last_m_date >= 20:
                    if 'short' in continue_game_times_by_users and user in continue_game_times_by_users['short']:
                        continue_game_times_by_users['short'][user] += 1
                    else:
                        continue_game_times_by_users['short'] = {user: 1}
            except UnboundLocalError:
                pass
            last_m_date = letters[user][mes].timestamp()
    return {'continues': continue_game_times_by_users,
            'letters_by_users': letters_by_users}

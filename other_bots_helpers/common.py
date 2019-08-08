async def get_hangbot_winrate(wins, loses):
    games = wins + loses
    percent = games / 100
    winrate = wins / percent
    winrate = round(winrate, 2)
    return winrate
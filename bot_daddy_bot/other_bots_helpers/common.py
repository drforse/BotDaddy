import requests


async def get_winrate(wins, loses):
    games = wins + loses
    percent = games / 100
    winrate = wins / percent
    winrate = round(winrate, 2)
    return winrate


async def yaspeller(q):
    try:
        answer = requests.get(f'https://speller.yandex.net/services/spellservice.json/checkText?text={q}&options=4').json()
        text = q.replace(answer[0]['word'], answer[0]['s'][0])
        for i in answer[1:]:
            text = text.replace(i['word'], i['s'][0])
        return text
    except IndexError:
        return q

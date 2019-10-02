import requests
import bs4
import asyncio
import sys


async def find_by_mask(mask, letters_quantity=None):
    try:
        if letters_quantity:
            g = requests.get(f'https://поискслов.рф/mask/{mask}/{letters_quantity}')
        else:
            g = requests.get(f'https://поискслов.рф/mask/{mask}')
        gsoup = bs4.BeautifulSoup(g.text, 'lxml').select('div.dict-definition')[0]
        words = []
        for tag in gsoup.find_all('a'):
            word = ''
            for part in tag:
                if part not in tag.find_all('span'):
                    word += f'<i>{part}</i>'
                else:
                    word += part.getText()
            words.append(word)
        return words
    except:
        return ['Неизвестная ошибка']

import requests
import bs4
import asyncio
import sys
import traceback


async def find_by_mask():
    try:
        g = requests.get('https://www.aliexpress.com/item/32811927991.html')
        gsoup = bs4.BeautifulSoup(g.text, 'lxml').select('script')
        print(gsoup)
        '''
        for tag in gsoup:
            print('window.runParams' in tag.getText())'''
    except:
        print(traceback.format_exc())

asyncio.run(find_by_mask())

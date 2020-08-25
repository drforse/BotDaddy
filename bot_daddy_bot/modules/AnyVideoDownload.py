from urllib import request
import requests
import bs4
import json
import os
import cv2
import logging


class VideoDownload:
    def __init__(self):
        self.name = None
        self.link = None
        self.download_link = None
        self.website = None
        self.path = None
        self.height = 0
        self.width = 0
        self.size = (0, 0)
        self.__soup = None

    def get_by_link(self, link: str):
        link = link if link.startswith('https://') or link.startswith('http://') else 'https://' + link
        website = link.split('https://')[-1].split('/')[0] if link.startswith('https') else link.split('http://')[-1].split('/')[0]
        print(f'{link=}')
        r = requests.get(link)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        print(soup.getText())
        if website == 'porn.24video.net':
            name = soup.find('title').text
        else:
            raise UnknownResourse(website)

        for tag in soup.find_all('meta'):
            if tag.attrs.get('property') == 'ya:ovs:content_url':
                self.download_link = tag.attrs.get('content')

        self.link = link
        self.website = website
        self.name = name
        self.__soup = soup
        return self

    def download(self):
        filename = f'{self.name}.mp4'
        logging.warning(f'start downloading {filename}')
        request.urlretrieve(self.download_link, filename=filename)
        self.path = f'{os.getcwd()}\\{filename}'
        logging.warning(f'downloaded {filename} into {self.path}')

        vid = cv2.VideoCapture(self.path)
        self.height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.size = (self.width, self.height)

    def json(self):
        return {'name': self.name,
                'link': self.link,
                'path': self.path,
                'website': self.website,
                'download_link': self.download_link}

    def __str__(self):
        return json.dumps(self.json())


class UnknownResourse(Exception):
    def __init__(self, resource_name):
        self.txt = resource_name

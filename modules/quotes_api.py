import requests
import glob

from config import QUOTES_API_TOKEN


class QuotesApi:
    def __init__(self):
        self.token = QUOTES_API_TOKEN
        self.api_link = 'http://rsdev.ml/dev/quote'
        self.file_url = None
        self.file_name = None

    def get_png(self, message_text, sender_title, profile_picture='', color='#ccc', sender_id=None, admin_title='', style='desk'):
        """
        if sender_id is specified and color is None or '#ccc', color is based on sender_id
        """
        no_profile_picture = False
        if not color and sender_id or color == '#ccc' and sender_id:
            colors = ["#fb6169", "#85de85", "#f3bc5c", "#65bdf3", "#b48bf2", "#ff5694", "#62d4e3", "#faa357"]
            num1 = sender_id % 7
            num2 = [0, 7, 4, 1, 6, 3, 5]
            color = colors[num2[num1]]
        if not profile_picture:
            no_profile_picture = True
            profile_picture = ''
        values = {
            'pfp': profile_picture,
            'no_pfp': str(no_profile_picture),
            'colour': color,
            'username': sender_title,
            'admintitle': admin_title,
            'raw_text': message_text,
            'token': self.token,
            'style': style
        }

        r = requests.post(self.api_link, data=values)
        self.file_url = r.json()['success']['file']
        return self

    def save(self, name: bool = None):
        r = requests.get(self.file_url, stream=True)
        search = glob.glob('stickertemp*.png')
        if search:
            n = int(search[-1].replace('stickertemp', '').replace('.png', '')) + 1
        else:
            n = 0
        name = name or f'stickertemp{n}.png'
        self.file_name = name
        with open(name, 'wb') as file:
            file.write(r.content)

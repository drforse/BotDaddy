import requests
import json


class DicAcademicBase:

    __link = 'https://orthographic.academic.ru/seek4term.php?json=true&limit=%d&did=%s&q=%s'

    def __init__(self):
        pass

    def request(self, dic: str, q: str, limit: int = 20):
        r = requests.get(self.__link % (limit, dic, q))
        results = r.json().get('results')
        if not results:
            raise RequestFailed(status_code=r.status_code)
        return results

    def to_json(self):
        return json.dumps(self.to_python())

    def to_python(self):
        # print(self.__dict__)
        attrs = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if isinstance(value, DicAcademicBase):
                value = value.to_python()
            if isinstance(value, list):
                value = [i.to_python() for i in value]
            attrs[key] = value

        # attrs = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
        # print(attrs)
        return attrs


class RequestFailed(Exception):
    def __init__(self, status_code, text=''):
        self.txt = f'{text}, status_code={status_code}'

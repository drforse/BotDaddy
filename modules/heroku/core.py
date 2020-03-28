from requests import Session
import json


class Heroku:
    def __init__(self, api_key):
        self.session = Session()

    def reload_app(self, app_name):
        return self.session.delete(f'https://api.heroku.com/apps/{app_name}/dynos',
                                   headers={'Content-Type': 'application/json',
                                            'Accept': 'application/vnd.heroku+json; version=3',
                                            'Authorization': f'Bearer {self.api_key}'})

    def get_logs(self, app_name, lines=100000):
        x = self.session.post(f'https://api.heroku.com/apps/{app_name}/log-sessions',
                              data=json.dumps({'lines': lines}),
                              headers={'Content-Type': 'application/json',
                                       'Accept': 'application/vnd.heroku+json; version=3',
                                       'Authorization': f'Bearer {self.api_key}'})
        if x.status_code >= 400:
            return x
        logs = x.json()['logplex_url']
        logs = self.session.get(logs)
        return logs.text

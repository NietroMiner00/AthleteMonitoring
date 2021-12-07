import utils
import requests

class API:
    def __init__(self):
        self.update_config()

    def update_config(self):
        config = utils.config
        if 'access_token' in config.keys() and config['access_token'] != None:
            self.access_token = config['access_token']

            self.headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + str(config['access_token'])
            }
        else:
            self.access_token = None
            self.headers = None
        
        if 'refresh_token' in config.keys() and config['refresh_token'] != None:
            self.refresh_token = config['refresh_token']
        else: self.refresh_token = None

    def error_handling(func):
        def wrapper(self, *args):
            for i in range(0,5):
                data = {}
                if self.headers != None:
                    data = func(self, args).json()
                if('data' not in data.keys()):
                    result = utils.accesslink.new_access_token()
                    if not result[0]:
                        return result[1]
                    self.update_config()
                    continue
                return data['data']
        return wrapper
    
    @error_handling
    def get_teams(self, args):
        data = requests.get('https://teampro.api.polar.com/v1/teams/', params={}, headers=self.headers)
        return data

    @error_handling   
    def get_sessions(self, args):
        data = requests.get(f'https://teampro.api.polar.com/v1/teams/{args[0]}/training_sessions/', params={}, headers=self.headers)          
        print(f'{data.content}')
        print(f'https://teampro.api.polar.com/v1/teams/{args[0]}/training_sessions/')
        return data

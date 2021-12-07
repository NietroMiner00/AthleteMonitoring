import utils
import requests

class API:
    def __init__(self):
        self.update_config()

    def update_config(self):
        config = utils.config
        self.access_token = config['access_token']
        self.refresh_token = config['refresh_token']
        self.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + str(config['access_token'])
        }
    
    def get_teams(self):
        for i in range(0,5):
            data = requests.get('https://teampro.api.polar.com/v1/teams/', params={}, headers=self.headers).json()
            if('data' not in data.keys()):
                result = utils.accesslink.new_access_token()
                if not result[0]:
                    return result[1]
                self.update_config()
                continue
            return data['data']
        print('timed out')
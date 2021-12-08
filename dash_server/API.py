import utils
import requests
import pandas
import numpy as np

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
        return data

    @error_handling
    def get_session(self, args):
        details = requests.get(f'https://teampro.api.polar.com/v1/teams/training_sessions/{args[0]}', params={}, headers = self.headers)
        return details

    @error_handling
    def get_participant_data(self, args):
        return requests.get(f'https://teampro.api.polar.com/v1/training_sessions/{args[0]}/?samples=all', params={}, headers=self.headers)

    def get_participants_data(self, session_id):
        session = self.get_session(session_id)

        participants = session['participants']

        all_player_data = pandas.DataFrame()
        for player in participants:
            player_session_id = player['player_session_id']
            
            player_session_details = self.get_participant_data(player_session_id)

            player_raw_data = player_session_details['samples']['values']
            player_columns = player_session_details['samples']['fields']

            player_table = pandas.DataFrame(player_raw_data, columns=player_columns)
            player_table['player_id'] = player['player_id']

            start_time = player_session_details['start_time']

            dates = pandas.date_range(start_time, periods=len(player_raw_data), freq="100ms")

            player_table['time'] = dates

            all_player_data = all_player_data.append(player_table)

        all_player_data = all_player_data.reset_index()
        all_player_data = all_player_data.replace("NaN", np.nan)

        return all_player_data
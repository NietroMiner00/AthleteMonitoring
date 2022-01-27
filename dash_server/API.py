import utils
import requests
import pandas
import numpy as np

class API:
    def __init__(self):
        self.update_config()

    #loads access- and refresh token from config for easier access
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


    #function for error handling primarily used for data fetching below
    #implemented as wrapper for a more structured look and easier application
    def error_handling(func):
        def wrapper(self, *args):

            #checks up to 5 times if access token is valid
            for i in range(0,5):
                data = {}

                #is valid
                #function which is wrapped is called
                if self.headers != None:
                    data = func(self, args).json()

                #is not valid
                #gets new access token and tries again
                if('data' not in data.keys()):
                    result = utils.accesslink.new_access_token()
                    if not result[0]:
                        return result[1]
                    self.update_config()
                    continue

                return data['data'] #return function
        return wrapper
    
    #fetches available teams
    @error_handling
    def get_teams(self, args):
        data = requests.get('https://teampro.api.polar.com/v1/teams/', params={}, headers=self.headers)
        return data

    #receives team_id an fetches all associated sessions
    @error_handling   
    def get_sessions(self, args):
        data = requests.get(f'https://teampro.api.polar.com/v1/teams/{args[0]}/training_sessions/', params={}, headers=self.headers)
        return data

    #receives team_id and fetches a single session
    @error_handling
    def get_session(self, args):
        details = requests.get(f'https://teampro.api.polar.com/v1/teams/training_sessions/{args[0]}', params={}, headers = self.headers)
        return details

    #receives session_id and fetches data of one participant
    @error_handling
    def get_participant_data(self, args):
        return requests.get(f'https://teampro.api.polar.com/v1/training_sessions/{args[0]}/?samples=all', params={}, headers=self.headers)

    #receives session_id and returns and saves dataframe of all participants 
    def get_participants_data(self, session_id):
        session = self.get_session(session_id)

        participants = session['participants']

        #dataframe for data of every player in the session
        all_player_data = pandas.DataFrame()

        #create entry for every player
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

            #appends single player dataframe to overall player dataframe 
            all_player_data = all_player_data.append(player_table)

        #resets index and replaces "NaN" string with Numpys NaN for further processing down the line
        all_player_data = all_player_data.reset_index()
        all_player_data = all_player_data.replace("NaN", np.nan)

        return all_player_data #return processed dataframe with all players in the session

    def get_timestamps(self, session_id):
        session = self.get_session(session_id)
        start_time = session['start_time']
        end_time = session['end_time']
        return start_time, end_time


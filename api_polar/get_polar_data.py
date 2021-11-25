from datetime import datetime
import utils
import requests
import pandas
import numpy as np
import os

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

config = utils.load_config("config.yml")

headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer ' + config['access_token']
}

# pagination?!?
teams = requests.get('https://teampro.api.polar.com/v1/teams/', params={}, headers=headers).json()['data']

print("Select team:\n")

for (index, team) in enumerate(teams):
    print(str(index+1) + ": " + team['name'])

team_index = 0
try:
    team_index = int(input("Team Nr: "))
except ValueError:
    raise Exception("Value must be a whole number in range 1 to " + str(len(teams)))

if team_index > len(team) or team_index < 0:
    raise Exception("Value must be a whole number in range 1 to " + str(len(teams)))

team_id = teams[team_index-1]['id']

# pagination?!?
trainings_sessions = requests.get(f'https://teampro.api.polar.com/v1/teams/{team_id}/training_sessions/', params={}, headers=headers).json()['data']

printProgressBar(0, len(trainings_sessions), prefix = 'Progress:', suffix = 'Complete', length = 50)

for progress, trainings_session in enumerate(trainings_sessions):
    trainings_session_id = trainings_session['id']
    details = requests.get(f'https://teampro.api.polar.com/v1/teams/training_sessions/{trainings_session_id}', params={}, headers = headers).json()['data']

    participants = details['participants']

    all_player_data = pandas.DataFrame()
    for player in participants:
        player_session_id = player['player_session_id']
        
        player_session_details = requests.get(f'https://teampro.api.polar.com/v1/training_sessions/{player_session_id}/?samples=all', params={}, headers=headers).json()['data']

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
    
    session_path = f"..\Soccer Data\{teams[team_index-1]['name']}"
    if not os.path.exists(session_path):
        os.mkdir(session_path)
    all_player_data.to_parquet(session_path + f"\{trainings_session['start_time'].replace(':', '-')}-{trainings_session_id}.parquet")
    
    printProgressBar(progress+1, len(trainings_sessions), prefix = 'Progress:', suffix = 'Complete', length = 50)
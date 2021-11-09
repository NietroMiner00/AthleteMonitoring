import numpy as np
import plotly.express as pex
import pandas as pd
import datetime as dt

max_speed = 2 # m/s
current_speed = max_speed
poll_speed = 10 # 1/s

width = 105
height = 68

max_angle = np.pi/64 # Angle in radians
current_angle = 0

train_duration = 60*60 # Duration in seconds

start_time = dt.datetime.now()

df = pd.DataFrame()

for player in range(11):
    current_position = np.array([np.random.randint(0, 68), np.random.randint(0, 105)])
    #print(current_position)
    positions = np.array([current_position])
    timings = np.array([start_time])
    current_time = start_time
    for time in range(0, train_duration * poll_speed):

        error = np.random.random() * 0.02 + 0.99
        current_speed = current_speed * error
        length = (1/poll_speed) * current_speed
        #print(length)

        angle = current_angle + np.random.random() * max_angle*2 - max_angle
        #print(angle)

        ak = np.cos(angle) * length # Ankathete
        gk = np.sin(angle) * length # Gegenkathete

        current_position = current_position + [ak, gk]
        #print(current_position)
        positions = np.append(positions, current_position)

        current_angle = angle

        current_time = current_time + dt.timedelta(seconds=(1/poll_speed))
        timings = np.append(timings, [current_time])

    positions = positions.reshape((int(positions.shape[0]/2), 2))

    player_df = pd.DataFrame({'Time': timings, 'playerID': np.ones(timings.shape[0], dtype=np.int32)*player, 'groupID': np.ones(timings.shape[0], dtype=np.int32),'X':positions[:, 0], 'Y':positions[:, 1]})
    #print(player_df)

    df = df.append(player_df)

print(df)

df_np = df.to_numpy()
np.save("positions.npy", df_np)

fig = pex.line(df, x='X', y='Y', color='playerID')
fig.show()
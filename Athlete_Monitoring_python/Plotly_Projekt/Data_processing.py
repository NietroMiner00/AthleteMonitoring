import pandas as pd             # data wrangling
import numpy as np              # fast numeric calculations
from scipy import signal        # filtering
import glob                     # read file structure
import re                       # regular expression  
from datetime import datetime               
from pylab import rcParams      # change figure size
rcParams['figure.figsize'] = 18, 8

def bw_filt(vec, fc, fs, order):     
    Wn = fc/(fs/2)
    m, n = signal.butter(order,Wn,'low') 
    return signal.filtfilt(m,n,vec)

def metpow(a,v, ec=4.35):
    g = 9.81
    ind = abs(a)>4.5
    a[ind] = 4.5 * np.sign(a[ind])
    es = a/g
    em = np.sqrt(a**2/g**2 + 1)
    ecr = (155.4 * es**5 - 30.4 * es**4 - 43.3 * es**3 + 46.3 * es**2 + 19.5 * es + ec ) * em
    mp = ecr * v
    return mp, ecr

"""creates new columns: returns dataframe"""
def get_cols(df):
    if len(df)>12:
        fs = 15.15  #fs?
        df['dt'] = df['Time'].diff().dt.total_seconds()
        #Umrechnung in Minuten
        df['tmin'] = 1/fs/60

        #Distance
        x_value=df.X.astype(np.float32)
        y_value=df.Y.astype(np.float32)
        df['ds'] = np.sqrt(x_value.diff()**2 + y_value.diff()**2)

        #Velocity
        df['v'] = df.ds/df.dt

        #Removes missing Data from subset v
        df = df.dropna(subset=['v'])

        #Velocityfactor?
        df['vf'] = bw_filt(df.v, 0.5, fs, 3)

        df['a'] = df.vf.diff()/df.dt
        df = df.dropna(subset=['a'])
        df['af'] = bw_filt(df.a, 0.5, fs, 3)
        df['mp'], df['ecr'] = metpow(df.af,df.vf)
        df['ee'] = df.ecr*df.ds
    return df

def histo(LowThresh, v1, v2): 
    # returns sum of v2 values when v1 is in bins of Zones ('LowThresh')
    HighThresh=np.append(LowThresh[1:],1e4)
    agg_v2 = np.array([])
    for count in range (0, len(LowThresh)):
        bool_vec = (v1 >= LowThresh[count]) & (v1 < HighThresh[count])
        agg_v2 = np.append(agg_v2, np.sum(bool_vec * v2))
    return agg_v2

"""Aggregates columns per playerid"""
def agg_func(df):
    mpz = [0,10,20,35,55]
    ec = 4.35
    d = {
        #'Game':     int(re.findall(r'\d+', )[0]),
        'Team':     df.groupID.iloc[0],
        'Start':    df.Time.iloc[0],
        'End':      df.Time.iloc[-1],
        'Time':     df.tmin.sum(),
        'Distance': df.ds.sum(),
        'ED':       df.ee.sum()/ec,
        'EEjkg':    df.ee.sum(),
        'EDI':      df.ee.sum()/ec/df.ds.sum(),
        'AI_20':    df.ee[df.mp>20].sum()/
                    df.ee.sum(),
        'MPmean':   df.mp.mean(),
        #'ee_mp_z':  histo(mpz,df.mp,df.ee),
        #'d_mp_z':   histo(mpz,df.mp,df.ds),
        #'t_mp_z':   histo(mpz,df.mp,df.tmin)
    }

    eempz = histo(mpz,df.mp,df.ee)
    dmpz = histo(mpz,df.mp,df.ds)
    tmpz = histo(mpz,df.mp,df.tmin)

    for i in range(len(mpz)):
        d[f'ee_mp_z_{mpz[i]}'] = eempz[i]
        d[f'd_mp_z_{mpz[i]}'] = dmpz[i]
        d[f't_mp_z_{mpz[i]}'] = tmpz[i]
        
    return pd.Series(d)

def process_data():
    #Einlesen von csv
    #df = pd.read_csv(file)
    #Einlesen von npy datei
    df_np = np.load("data/positions.npy", allow_pickle=True)
    df = pd.DataFrame({'Time':df_np[:, 0], 'playerID':df_np[:, 1], 'groupID':df_np[:, 2], 'X':df_np[:, 3], 'Y':df_np[:, 4]})
    #Time in Dataframe
    df['Time']= pd.to_datetime(df['Time'])
    #df['X'].astype(np.float32, copy= False)
    #df['Y'].astype(np.float32, copy= False)

    dfgroup = df.groupby('playerID')
    dfcols = dfgroup.apply(get_cols)
    dfrestdex = dfcols.reset_index(level='playerID', drop=True)
    print(dfrestdex)
    dfgroup_two = dfrestdex.groupby('playerID').apply(agg_func)
    #print(dfgroup_two)
    return dfrestdex

def run():
    
    files = glob.glob("data/*position.csv")
    file = files[0]
    process_data(file)
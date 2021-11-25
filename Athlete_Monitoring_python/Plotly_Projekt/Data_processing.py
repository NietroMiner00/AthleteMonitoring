import pandas as pd             # data wrangling
import numpy as np              # fast numeric calculations
from scipy import signal        # filtering
import glob                     # read file structure
import re                       # regular expression  
from datetime import datetime               
from pylab import rcParams      # change figure size
#rcParams['figure.figsize'] = 18, 8

# Low Pass Filter
def bw_filt(vec, fc, fs, order):     
    Wn = fc/(fs/2)
    m, n = signal.butter(order,Wn,'low') 
    return signal.filtfilt(m,n,vec)

#Metabloic power
def metpow(a,v, ec=4.35):
    # Acceleration of gravity on earth
    g = 9.81

    a = np.clip(a, -4.5, 4.5)
    # Equivalant slope
    es = a/g
    # Equivalant mass
    em = np.sqrt(a**2/g**2 + 1)
    # Energie cost of running
    ecr = (155.4 * es**5 - 30.4 * es**4 - 43.3 * es**3 + 46.3 * es**2 + 19.5 * es + ec ) * em
    # Metabolic power
    mp = ecr * v
    return mp, ecr

#creates new columns: returns dataframe
def get_cols(df):
    if len(df)>12:
        fs = 15.15  # Sampling Rate (Input from user or calculate from data)
        df['dt'] = df['Time'].diff().dt.total_seconds()
        #convertion to minutes
        df['tmin'] = 1/fs/60

        #Distance
        x_value=df.X.astype(np.float32)
        y_value=df.Y.astype(np.float32)
        df['ds'] = np.sqrt(x_value.diff()**2 + y_value.diff()**2)

        #Velocity
        df['v'] = df.ds/df.dt

        #Removes missing Data from subset v
        df = df.dropna(subset=['v'])

        # Low pass filter for velocity
        df['vf'] = bw_filt(df.v, 0.5, fs, 3)

        df['a'] = df.vf.diff()/df.dt
        df = df.dropna(subset=['a'])

        # Low pass filter for acceleration
        df['af'] = bw_filt(df.a, 0.5, fs, 3)

        # Calculate metabolic power
        df['mp'], df['ecr'] = metpow(df.af,df.vf)

        # Energie expenditure
        df['ee'] = df.ecr*df.ds
    return df

#Histogram
def histo(LowThresh, v1, v2): 
    # returns sum of v2 values when v1 is in bins of Zones ('LowThresh')
    HighThresh=np.append(LowThresh[1:],1e4)
    agg_v2 = np.array([])
    for count in range (0, len(LowThresh)):
        bool_vec = (v1 >= LowThresh[count]) & (v1 < HighThresh[count])
        agg_v2 = np.append(agg_v2, np.sum(bool_vec * v2))
    return agg_v2

#Aggregates columns per playerid
def agg_func(df):
    # Threshholds for metabolic power zones (Input from user from dictionary) indiviual for team or per session
    mpz = [0,10,20,35,55]

    # Energie Cost (Input from user) individual for team
    ec = 4.35

    d = {
        #'Game':     int(re.findall(r'\d+', )[0]),
        'Team':     df.groupID.iloc[0],
        'Start':    df.Time.iloc[0],
        'End':      df.Time.iloc[-1],
        'Time':     df.tmin.sum(),
        'Distance': df.ds.sum(),
        # Equivalant Distance
        'ED':       df.ee.sum()/ec,
        # Energie expenditure
        'EEjkg':    df.ee.sum(),
        # Equivalant Distance index
        'EDI':      df.ee.sum()/ec/df.ds.sum(),
        # Anaerobic Index
        'AI_20':    df.ee[df.mp>20].sum()/
                    df.ee.sum(),
        'MPmean':   df.mp.mean(),
        #'ee_mp_z':  histo(mpz,df.mp,df.ee),
        #'d_mp_z':   histo(mpz,df.mp,df.ds),
        #'t_mp_z':   histo(mpz,df.mp,df.tmin)
    }

    # Energie spend in metabolic power zones
    eempz = histo(mpz,df.mp,df.ee)
    # Distance spend in metabolic power zones
    dmpz = histo(mpz,df.mp,df.ds)
    # Time spend in metabolic power zones
    tmpz = histo(mpz,df.mp,df.tmin)

    for i in range(len(mpz)):
        d[f'ee_mp_z_{mpz[i]}'] = eempz[i]
        d[f'd_mp_z_{mpz[i]}'] = dmpz[i]
        d[f't_mp_z_{mpz[i]}'] = tmpz[i]
        
    return pd.Series(d)


def process_data(path):
    #Read csv file
    #df = pd.read_csv(file)

    #Read npy files
    df_np = np.load(path, allow_pickle=True)
    df = pd.DataFrame({'Time':df_np[:, 0], 'playerID':df_np[:, 1], 'groupID':df_np[:, 2], 'X':df_np[:, 3], 'Y':df_np[:, 4]})
   
    #Time in dataframe
    df['Time']= pd.to_datetime(df['Time'])

    #Return for original dataframe grouped by Playerid
    dfgroup = df.groupby('playerID')

    #Return dfrestdex for dataframe with new calculated columns
    dfcols = dfgroup.apply(get_cols)
    #Reverse GroupBy
    dfrestdex = dfcols.reset_index(level='playerID', drop=True)

    #Return for dataframe with the aggregated values
    dfgroup_two = dfrestdex.groupby('playerID').apply(agg_func)

    #Return 
    return dfrestdex


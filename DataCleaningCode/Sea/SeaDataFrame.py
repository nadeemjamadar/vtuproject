import pandas as pd
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv(r"C:\Users\LalithaShankar\Desktop\FinalYearProject\TrialAndError\SeaST.csv").set_index('date')

df = df.apply(lambda x: x.str.strip()).replace('', np.nan)

features = ['Sea_Level_Pressure','Air_Temperature','Dew_Point_Temperature','Wind_Direction','Wind_Speed']

N = 1

to_keep = ['Sea_Level_Pressure','Air_Temperature','Dew_Point_Temperature','Wind_Direction','Wind_Speed']


df = df[to_keep]

df.columns

df = df.apply(pd.to_numeric, errors='coerce')

mean = df.mean()

df['Sea_Level_Pressure'].replace(to_replace=np.nan, value=mean[0])

df['Dew_Point_Temperature'].replace(to_replace=np.nan, value=mean[1])

df['Air_Temperature'].replace(to_replace=np.nan, value=mean[2])

df['Wind_Direction'].replace(to_replace=np.nan, value=mean[3])

df['Wind_Speed'].replace(to_replace=np.nan, value=mean[4])

def derive_nth_day_feature(df, feature, N):  
    rows = df.shape[0]
    nth_prior_measurements = [None]*N + [df[feature][i-N] for i in range(N, rows)]
    col_name = "{}_{}".format(feature, N)
    df[col_name] = nth_prior_measurements


for feature in features:  
    if feature != 'Date_of_observation':
        for N in range(1, 4):
            derive_nth_day_feature(df, feature, N)

df.describe().T

spread = df.describe().T

IQR = spread['75%'] - spread['25%']

spread['outliers'] = (spread['min']<(spread['25%']-(3*IQR)))|(spread['max'] > (spread['75%']+3*IQR))

spread.loc[spread.outliers,] 

get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.figsize'] = [14, 8]  
df.Sea_Level_Pressure_1.hist()  
plt.title('Distribution of maxhumidity_1')  
plt.xlabel('Sea_Level_Pressure_1')  
plt.show() 


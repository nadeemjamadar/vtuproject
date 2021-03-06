import pandas as pd
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from IPython import get_ipython
from pandas.core import datetools
from sklearn.model_selection import train_test_split  
from sklearn.linear_model import LinearRegression 
import statsmodels.api as sm 
import operator
from sklearn.metrics import mean_absolute_error, median_absolute_error 

df = pd.read_csv(r"SeaST.csv")

df = df.apply(lambda x: x.str.strip()).replace('', np.nan)

features = ['sealevelpressure','airtemperature','dewpoint','winddirection','windspeed']

N = 1

to_keep = ['sealevelpressure','airtemperature','dewpoint','winddirection','windspeed']

df = df[to_keep]

df = df.apply(pd.to_numeric, errors='coerce')

mean = df.mean()

#replacing NaN values with mean 
df['sealevelpressure'].replace(to_replace=np.nan, value=mean[0])

df['airtemperature'].replace(to_replace=np.nan, value=mean[1])

df['dewpoint'].replace(to_replace=np.nan, value=mean[2])

df['winddirection'].replace(to_replace=np.nan, value=mean[3])

df['windspeed'].replace(to_replace=np.nan, value=mean[4])

def derive_nth_day_feature(df, feature, N):  
    rows = df.shape[0]
    nth_prior_measurements = [None]*N + [df[feature][i-N] for i in range(N, rows)]
    col_name = "{}_{}".format(feature, N)
    df[col_name] = nth_prior_measurements


for feature in features:  
    if feature != 'date':
        for N in range(1, 5):
            derive_nth_day_feature(df, feature, N)


spread = df.describe().T

IQR = spread['75%'] - spread['25%']

spread['outliers'] = (spread['min']<(spread['25%']-(3*IQR)))|(spread['max'] > (spread['75%']+3*IQR))

spread.loc[spread.outliers,] 

df = df.dropna() 

#pearson correlation
df.corr()[['airtemperature']].sort_values('airtemperature') 


predictors = ['sealevelpressure_1' , 'sealevelpressure_2' , 'sealevelpressure_3' , 
              'airtemperature_1' , 'airtemperature_2' , 'airtemperature_3' , 
              'dewpoint_1' , 'dewpoint_2' , 'dewpoint_3'
             ] 

df2 = df[['airtemperature'] + predictors]


#mean temp with otherfeatures
get_ipython().run_line_magic('matplotlib', 'inline')

# manually set the parameters of the figure to and appropriate size
plt.rcParams['figure.figsize'] = [16, 22]

# call subplots specifying the grid structure we desire and that 
# the y axes should be shared
fig, axes = plt.subplots(nrows=3, ncols=3, sharey=True)

# Since it would be nice to loop through the features in to build this plot
# let us rearrange our data into a 2D array of 6 rows and 3 columns
arr = np.array(predictors).reshape(3, 3)

# use enumerate to loop over the arr 2D array of rows and columns
# and create scatter plots of each meantempm vs each feature
for row, col_arr in enumerate(arr):  
    for col, feature in enumerate(col_arr):
        axes[row, col].scatter(df2[feature], df2['airtemperature'])
        if col == 0:
            axes[row, col].set(xlabel=feature, ylabel='airtemperature')
        else:
            axes[row, col].set(xlabel=feature)
plt.show()
#mean temp with otherfeatures


# histogram of the features 
"""get_ipython().run_line_magic('matplotlib', 'inline')

 for sp in spread.index:
    plt.rcParams['figure.figsize'] = [14, 8]  
    print(sp)
    df[sp].hist() 
    plt.title('Distribution of {}'.format(sp))  
    plt.xlabel(sp)  
    plt.show()"""

# separate our my predictor variables (X) from my outcome variable y
X = df2[predictors]  
y = df2['airtemperature']

# Add a constant to the predictor variable set to represent the Bo intercept
X = sm.add_constant(X)  
X.iloc[:5, :5]


#backward elimination
# (1) set a significance value
alpha = 0.05

# (2) Fit the model
model = sm.OLS(y, X).fit()

# (3) evaluate the coefficients' p-values
model.summary()


# (4) backward elimination
q = True
while q:
    max_index, max_value = max(enumerate(model.pvalues), key=operator.itemgetter(1))
    if (max_value > 0.05):
        X = X.drop(model.pvalues.index[max_index], axis=1)
        model = sm.OLS(y, X).fit()
        print(model.summary())
    else:
        q = False
# back ward eliminatio end

 
X = X.drop('const', axis=1)


#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=12) 

X_train = X.head(800)
X_test = X.tail(397)

y_train = y.head(800)
y_test = y.tail(397)

regressor = LinearRegression()

# fit the build the model by fitting the regressor to the training data
regressor.fit(X_train, y_train)

# make a prediction set using the test set
prediction = regressor.predict(X_test)

# Evaluate the prediction accuracy of the model

print("The Explained Variance: %.2f" % regressor.score(X_test, y_test))  
print("The Mean Absolute Error: %.2f degrees celsius" % mean_absolute_error(y_test, prediction))  
print("The Median Absolute Error: %.2f degrees celsius" % median_absolute_error(y_test, prediction))


fig = plt.figure(figsize=(20,10))
ax1 = fig.add_subplot(111)
ax1.plot(y_test.tolist(), label='actual values')
ax1.plot(prediction,label='predicted values')
plt.xlabel('Training dataset')  
plt.ylabel('Mean temperature') 
plt.legend(loc='upper left');
plt.show()




 
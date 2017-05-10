import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
import operator
#import os
#os.chdir("C:/Users/yuzem_000/Desktop/")

###Weather Data Preparation
weather = pd.read_csv("agg_weather.csv")
weather['DT'] = pd.to_datetime(weather.year*10000 + weather.month*100 + weather.date, format='%Y%m%d')
weather['precip'] = weather['precip'].round(1)
weather = weather[weather['wind_high'] != 99].reset_index(drop=True)

###Crime Data Preparation
crime = pd.read_table("cat_crime_date.out", header=None, names=['date', 'crime','count'])
crime = crime[crime['date'] != 'RPT_DT'].reset_index(drop=True)
crime['day_month'] =  crime['date'].str.rpartition('/')[0]
crime['year'] = crime['date'].str.rpartition('/')[2].astype(int)
crime['month'] =  crime['day_month'].str.rpartition('/')[0].astype(int)
crime['day'] = crime['day_month'].str.rpartition('/')[2].astype(int)
crime['DT'] = pd.to_datetime(crime.year*10000 + crime.month*100 + crime.day, format='%Y%m%d')
crime = crime.dropna()

###Merge Two Datasets
count_weather = pd.merge(weather, crime, how='left', on=['DT'])
count_weather['precip'] = count_weather['precip'].fillna(0)
df = count_weather[['DT', 'f_avg', 'precip', 'wind_high', 'crime', 'count']]
crime_cat = df['crime'].unique().tolist()

def prepare_df(df, col, cat):
    if not cat:
        day_count = pd.DataFrame(df.groupby(['DT'])['count'].sum())
        day_count['DT'] = day_count.index
        trans = pd.merge(day_count, weather[['DT', col]], on=['DT'])
    else:
        trans = df[df['crime'] == cat]
        trans = trans[['DT', col, 'count']]
    return trans 

###Correlation (3*correlaion)
def count_corr(df, col, cat=None):
    trans = prepare_df(df, col, cat)
    count_mean = trans.groupby([col])['count'].mean().to_frame()
    count_mean[col] = count_mean.index
    out = trans[col].value_counts()
    for i in out[out==1].index:
        count_mean = count_mean[count_mean[col] != i]         
    return count_mean

print(count_corr(df, 'f_avg').corr())
print(count_corr(df, 'wind_high').corr())
print(count_corr(df, 'precip').corr())

###Top 5 Categories vs Avg Temperature (1*Top5 figure)
corr_list = {}
for i in crime_cat:
    df_f = count_corr(df, 'f_avg', i)
    corr_list[i] = df_f.corr().iloc[0,1]
sorted_x = sorted(corr_list.items(), key=operator.itemgetter(1), reverse=True)
sorted_x = sorted_x[0:5]

c = [i[0] for i in sorted_x]
score = [i[1] for i in sorted_x]
c[0] = 'ASSAULT 3'
c[4] = 'CRIMINAL MISCHIEF'
x_pos = np.arange(len(c)) 

plt.bar(x_pos, score)
plt.xticks(rotation=30)
plt.xticks(x_pos, c) 
plt.ylabel("Correlation")
plt.title("Top 5 Crime Categories with Highest Correlation to Average Temperature")

###Top 5 Categories vs Avg Wind (1*top5 figure)
corr_list = {}
for i in crime_cat:
    df_f = count_corr(df, 'wind_high', i)
    corr_list[i] = df_f.corr().iloc[0,1]
sorted_x = sorted(corr_list.items(), key=operator.itemgetter(1))
sorted_x = sorted_x[0:5]

c = [i[0] for i in sorted_x]
c[0] = 'PENAL LAW'
c[2] = 'ASSAULT 3'
score = [i[1] for i in sorted_x]
x_pos = np.arange(len(c)) 

plt.bar(x_pos, score)
plt.xticks(rotation=30)
plt.xticks(x_pos, c) 
plt.ylabel("Correlation")
plt.title("Top 5 Crime Categories with Highest Correlation to Average Wind")

### Extreme Precipitation (1*boxplot + 1*t-stat)
def extreme_corr(df, col, cat, per=0.9):
    trans = prepare_df(df, col, cat)
    thd = trans[col].quantile(per)
    extr = []
    rest = []
    for index, row in trans.iterrows():
        if row[col] > thd:
            extr.append(row['count'])
        else:
            rest.append(row['count'])
    extr = np.array(extr)
    rest = np.array(rest)
    return extr, rest, stats.ttest_ind(extr, rest, equal_var=False)

extr, rest, tstat = extreme_corr(df, 'precip', cat=None, per=0.85)
plt.boxplot([extr, rest], widths=[0.3, 0.3], 
            labels=["Extreme Precipitation", "Non-extreme Precipitation"])
plt.ylabel("Average Crime")
plt.title("Crime Distribution under Extreme and Non-Extreme Precipitation")
print(tstat)

###Histogram (3*Histogram)
def hist(df, col, x_label):
    df_trans = count_corr(df, col)
    ax = df_trans.plot(x=col, y='count', kind='bar', width=0.7,
                title="Relationship between Average Crime and %s" %x_label)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Average Crime")
    ax.legend_.remove()
    if col == "f_avg":
        for label in ax.xaxis.get_ticklabels()[::2]:
            label.set_visible(False)
hist(df, 'f_avg', 'Average Temperature')
hist(df, 'wind_high', 'Average Wind')
hist(df, 'precip', 'Precipitation')

###Outliers
def outliers_z_score(df, thres=2):
    mean_y = df['count'].mean()
    stdev_y = df['count'].std()
    df['z_scores'] = (df['count'] - mean_y) / stdev_y 
    return df[np.abs(df['z_scores']) < thres]
        
###OLS (2*OLS graphs + 2*OLS stats)
def ols_est(df, col, x_label):
    df = df.dropna()
    df_trans = prepare_df(df, col, cat=None)
    df_trans = outliers_z_score(df_trans)
    X_train = df_trans[[col]]
    X_train = sm.add_constant(X_train)
    y_train = df_trans[['count']]
    est = sm.OLS(y_train, X_train)
    est = est.fit()
   
    X_prime = np.linspace(X_train.min()[1], X_train.max()[1], 100)[:, np.newaxis]
    X_prime = sm.add_constant(X_prime)
    y_hat = est.predict(X_prime)
    
    plt.scatter(X_train.ix[:,1], y_train, alpha=0.3)
    plt.xlabel(x_label)
    plt.ylabel("Crime Counts")
    plt.title("Relationship between Crime Counts and %s" %x_label)
    plt.plot(X_prime[:,1], y_hat, 'r', alpha=0.9)
    return est

est1 = ols_est(df, 'f_avg', x_label='Average Temperature')
print(est1.summary())
est2 = ols_est(df, 'wind_high', x_label='Average Wind')
print(est2.summary())
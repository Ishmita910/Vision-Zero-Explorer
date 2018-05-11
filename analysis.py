
# coding: utf-8

# In[9]:


import os
import pandas as pd
import matplotlib.pyplot as plt


# In[19]:


# Function to load the complete dataset and perform the data manipulations in-house
def load_data_complete():
    cur_dir = os.path.dirname('__file__')
    # Read the csv
    dfcsv = pd.read_csv(os.path.join(cur_dir, "NYPD_Motor_Vehicle_Collisions.csv"))

    # Converting the date column to its specified data type
    dfcsv['DATE'] = pd.to_datetime(dfcsv.DATE)

    # Creating three new columns for easy querying
    dfcsv['YEAR'] = dfcsv.DATE.dt.year
    dfcsv['MONTH'] = dfcsv.DATE.dt.month
    dfcsv['DAY'] = dfcsv.DATE.dt.day
    
    # Considering columns beneficial for visualizing on carto
    dfcsv = dfcsv[['DATE', 'TIME', 'BOROUGH', 'ZIP CODE', 'LATITUDE', 'LONGITUDE',
                 'CONTRIBUTING FACTOR VEHICLE 1', 'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
       'NUMBER OF CYCLIST INJURED', 'NUMBER OF CYCLIST KILLED',
       'NUMBER OF MOTORIST INJURED', 'NUMBER OF MOTORIST KILLED']]

    # We notice that zip codes are of object datatype instead of the required integer data type
    dfcsv = dfcsv[pd.notnull(dfcsv['ZIP CODE'])]

    # Converting zip codes datatype to numeric
    dfcsv['ZIP CODE'] = pd.to_numeric(dfcsv['ZIP CODE'], errors='coerce')

    # Removing outliers and unrecorded zip code values from the data( i.e. zero values and those outside the NTC city limits)
    dfcsv = dfcsv[(dfcsv['LATITUDE'] > 0.1) & (dfcsv['LATITUDE'] < 41)]
    dfcsv = dfcsv.drop(dfcsv[dfcsv['CONTRIBUTING FACTOR VEHICLE 1']=='Unspecified'].index)

    # Merging the dataframe for carto with above zip counts
    dfcsv = pd.merge(dfcsv, dfcsv['ZIP CODE'].value_counts().to_frame().reset_index().rename(columns={"ZIP CODE": "ZIP COUNTS"}),
            how='left', left_on='ZIP CODE', right_on='index'
            ).drop(columns='index')

    dfcsv = dfcsv.rename(columns={"CONTRIBUTING FACTOR VEHICLE 1": "CONTRIBUTING FACTOR"})

    return dfcsv.sort_values('DATE', ascending=False)[:499999]#.to_csv('dropped_500k_wCounts.csv', index=False)


# In[44]:


# Function to load the processed data obtained from running the above function 'load_data_complete' on the dataset
def load_data_concise():
    cur_dir = os.path.dirname('__file__')
    return pd.read_csv(os.path.join(cur_dir, "dropped_500k_wCounts.csv"))


# In[48]:


# Returns Viz 1: Total accidents per year for each borough
def time_pivot(data):
    tdf = data[['YEAR', 'BOROUGH']].groupby(['YEAR', 'BOROUGH']).size().rename('Count').reset_index()
    return pd.pivot_table(tdf, columns='YEAR', index='BOROUGH')


# In[75]:


# Returns Viz 2:  Injury/Fatality of a specific mode per year for each borough
def mode_pivot(data, mode):
    mdf = data[['DATE', 'BOROUGH', 'YEAR',
                   'NUMBER OF PEDESTRIANS INJURED', 'NUMBER OF PEDESTRIANS KILLED',
                   'NUMBER OF CYCLIST INJURED'    , 'NUMBER OF CYCLIST KILLED',
                   'NUMBER OF MOTORIST INJURED'   , 'NUMBER OF MOTORIST KILLED']].groupby(['YEAR', 'BOROUGH']).sum()
    return pd.pivot_table(mdf, columns='YEAR', index='BOROUGH', values=mode)


# In[69]:


# Returns Viz 3:  Collision due to a specific Contriburing Factor per year for each borough
def factor_pivot(data, factor):
    top20_factors = ['Driver Inattention--Distraction',
                     'Failure to Yield Right-of-Way',
                     'Fatigued--Drowsy',
                     'Backing Unsafely',
                     'Other Vehicular',
                     'Following Too Closely',
                     'Turning Improperly',
                     'Lost Consciousness',
                     'Passing or Lane Usage Improper',
                     'Traffic Control Disregarded',
                     'Driver Inexperience',
                     'Prescription Medication',
                     'Unsafe Lane Changing',
                     'Pavement Slippery',
                     'Outside Car Distraction',
                     'Alcohol Involvement',
                     'Physical Disability',
                     'Oversized Vehicle',
                     'Reaction to Other Uninvolved Vehicle',
                     'Unsafe Speed']
    fdf = data[['BOROUGH', 'YEAR', 'CONTRIBUTING FACTOR']].groupby(['YEAR', 'BOROUGH', 'CONTRIBUTING FACTOR']).size().rename('Count').reset_index()
    fdf = fdf[fdf['CONTRIBUTING FACTOR'].isin(top20_factors)]
    return pd.pivot_table(fdf, columns='YEAR', index=['BOROUGH', 'CONTRIBUTING FACTOR']).xs(factor, level=1)#.to_csv('viz3_factor_pivot_'+factor+'.csv')

# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 16:17:30 2019

@author: Travis Whitfield
"""

"""
This code creates a new dataframe, df_specs_num, which includes the cleaned
data from the last script, and does some preliminary analysis on that data. 
The code then saves that dataframe with selected columns to a json file
to be uploaded to a website.
"""


import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
import seaborn as sns

# Read in previous data
df_infoboxes = pd.read_pickle('Script_Data/04_df_infoboxes.pkl')
df_specs = pd.read_pickle('Script_Data/04_df_specs.pkl')

df_specs = df_specs.drop_duplicates()
df_infoboxes = df_infoboxes.drop_duplicates()


def top_5_value_counts(df):
    """ Function to generate summary information for string or categorical
    data in dataframes"""
    
    df_top5 = pd.DataFrame()
    for col in df.columns:
        try:
            if df[col].dtype != 'O':
                continue
        except:
            continue
        counts = df[col].value_counts()[:5]
        iters = [iter(list(counts.index)),iter(list(counts))]
        top5 = list(next(it) for it in itertools.cycle(iters))
        if len(top5)<10:
            for i in range(10-len(top5)):
                top5.append(np.nan)
        top5.insert(0,df[col].nunique())
        top5.insert(0,df[col].count())
        df_top5[col] = top5
        new_index = list(df_top5.index)
        new_index[0] = 'count'
        new_index[1] = 'nunique'
        df_top5.index = new_index
    
    return(df_top5)

# Review data
df_info_top5 = top_5_value_counts(df_infoboxes)
df_specs_top5 = top_5_value_counts(df_specs)

# Create dataframe including only columns with numerical data
df_specs_num = df_specs.select_dtypes(include=[np.float])
df_specs_num['aircraft'] = df_specs['aircraft_wikipage_title']
cols = list(df_specs_num.columns)
cols.remove('aircraft')
cols.insert(0,'aircraft')
df_specs_num = df_specs_num[cols]
df_specs_num.drop(['service_ceiling_ft','never_exceed_speed_kn'],
                  axis=1,inplace=True)

# Labels from infoboxes dataframe to include
labels_infoboxes = ['aircraft_wikipage_title','role','manufacturer',
                    'number_built_qty','first_flight_date','national_origin']

# Merge selected infobox columns with df_specs_num
df_specs_num = df_specs_num.merge(df_infoboxes[labels_infoboxes],how='left',
                          left_on='aircraft',right_on='aircraft_wikipage_title')
df_specs_num.drop('aircraft_wikipage_title',axis=1,inplace=True)
cols = ['aircraft', 'manufacturer','role','number_built_qty',
        'first_flight_date', 'national_origin','wingspan_ft', 'length_ft',
        'height_ft', 'empty_weight_lb','gross_weight_lb',
        'max_takeoff_weight_lb', 'maximum_speed_kn','cruise_speed_kn',
        'stall_speed_kn']

# Select and reorder columns 
df_specs_num = df_specs_num[cols]

# Convert first flight date to just the year, saved as an integer
df_specs_num['first_flight_date'] = (df_specs_num['first_flight_date'].dt.year
                                    .astype('Int64'))
# Convert the number built to int
df_specs_num['number_built_qty'] = df_specs_num['number_built_qty'].astype('Int64')

# Count the non-null values in each column
counts = df_specs_num.count(axis=1)
counts = counts.sort_values(ascending=False)

non_num_cols = ['manufacturer','role','national_origin']
num_cols = [col for col in df_specs_num.columns if col not in non_num_cols]

# Fill in non-numeric column null values with 'UNKNOWN'
df_specs_num[non_num_cols] = df_specs_num[non_num_cols].fillna('UNKNOWN')

count = df_specs_num.count(axis=0)

# Save the df_specs_num dataframe as a json for upload to website
cols_to_use = ['aircraft','manufacturer','role','national_origin',
               'first_flight_date','number_built_qty','wingspan_ft']
df_specs_num.to_json(r'C:\Users\thwhi\Dropbox\Personal\Programming\Aircraft Stuff\Aircraft Wiki Database Stuff\website\aircraft_specs.json',
                         orient='records',double_precision=2)


#df_specs_num[num_cols] = df_specs_num[num_cols].fillna('UNKNOWN')


#table2 = (df_specs_num.to_html(index=False,float_format='%.2f'))

#table = df_specs_num.iloc[:2000,:].fillna(-1).to_html()


#sns.set()
#
#fig,ax = plt.subplots()
#df_specs_num.plot.scatter('first_flight_date','gross_weight_lb',ax=ax)
#ax.set_yscale('log')
#
#
#fig,ax = plt.subplots()
#df_specs_num.plot.scatter('wingspan_ft','length_ft',ax=ax)
#ax.set_yscale('log')
#ax.set_xscale('log')
#
#
#fig,ax = plt.subplots()
#df_specs_num.drop(1922,axis=0).plot.scatter('wingspan_ft','empty_weight_lb',ax=ax)
#ax.set_yscale('log')
#ax.set_xscale('log')

fig,ax = plt.subplots()
df_specs_num['first_flight_date'].dropna().astype(float).hist(bins=30,ax=ax)

sns.pairplot(df_specs_num[df_specs_num['empty_weight_lb'] < 100000][['wingspan_ft',
             'length_ft','empty_weight_lb','number_built_qty']].astype(float))








df_specs_num.to_pickle('Script_Data/05_df_specs_num.pkl')







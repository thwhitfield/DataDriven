# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 11:02:20 2019

@author: thwhi
"""

import pandas as pd
import numpy as np
import re
import importlib
import itertools
import pickle
import dateutil
import matplotlib.pyplot as plt
import seaborn as sns

df_infoboxes = pd.read_pickle('Script_Data/03_df_infoboxes.pkl')
df_specs = pd.read_pickle('Script_Data/03_df_specs.pkl')

data_cleaning = __import__('04_2_data_cleaning_functions')

def convert_to_snake(string):
    ''' Converts a given string to snake_case'''
    s1 = string.replace(' ','_')
    s1 = s1.replace(u'\xa0', u'_')
    s1 = s1.lower()
#    s1 = re.sub('(.)([A-Z][a-z]+)',r'\1_\2',s1)
#    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2',s1).lower()
    return(s1)
    
def fix_lengths(s):
    """converts strings with lengths to float values of feet"""
    s = s.astype(str)
    s = s.str.lower()
    s = s.replace(',','')
    
    num_ft = '(?:(\d+\.?\d*)\s*(?:ft|feet))*'
    num_in = '(?:(\d+\.?\d*)\s*(?:in|inches))*'
    num_m = '(?:(\d+\.?\d*)\s*(?:m|meters))*'
    
    re_pattern = num_ft + '\s*' + num_in + '\s*' + num_m

    vals = s.str.extract(re_pattern)
    vals.columns = ['ft','in','m']
    vals = vals.astype(float)
    label = s.name + '_ft'
    vals[label] = (vals['ft'].fillna(0) + vals['in'].fillna(0)/12 
                        + vals['m'].fillna(0)*3.28084)
    
    vals[label].replace(0,np.nan,inplace=True)
    
    return(vals[label])
    
def fix_weights(s):
    """Converts strings with weights to float values of pounds"""
    
    s = s.astype(str)
    s = s.str.lower()
    s = s.str.replace(',','')
    
    num_lb = '(?:(\d+\.?\d*)\s*(?:lb|pounds))*'
    num_kg = '(?:(\d+\.?\d*)\s*(?:kg|kilograms))*'
        
    re_pattern = num_lb + num_kg
    
    vals = s.str.extract(re_pattern)
    vals.columns = ['lb','kg']
    vals = vals.astype(float)
    label = s.name + '_lb'
    vals[label] = vals['lb'].fillna(0) + vals['kg'].fillna(0) * 2.20462
    
    vals[label].replace(0,np.nan,inplace=True)
    
    return(vals[label])
    
def fix_speeds(s):
    """Converts strings with speeds to float values of knots"""
    s = s.astype(str)
    s = s.str.lower()
    s = s.str.replace(',','')
    
    num_kph = '(?:(\d+\.?\d*)\s*(?:km/h))*'
    num_mph = '(?:(\d+\.?\d*)\s*(?:mph))*'
    num_kn = '(?:(\d+\.?\d*)\s*(?:kn))*'
    
    re_pattern = num_kph + num_mph + num_kn
    
    vals = s.str.extract(re_pattern)
    vals.columns = ['kph','mph','kn']
    vals = vals.astype(float)
    label = s.name + '_kn'
    vals[label] = (vals['kph'].fillna(0)*.539957 
                   + vals['mph'].fillna(0)*.868976 
                   + vals['kn'].fillna(0))
    
    vals[label].replace(0,np.nan,inplace=True)
    return(vals[label])
    
def fix_quantities(s):
    """Cleans up quantity data"""
    s = s.astype(str)
    s = s.str.lower()
    s = s.str.replace(',','')
    
    numbers = ['zero','one','two','three','four','five','six','seven','eight',
               'nine','ten']
    
    num_dict = dict([(x,str(y)) for y,x in enumerate(numbers)])
    
    for key,val in num_dict.items():
        s = s.str.replace(key,val)
    
    num = '(\d+)'
    
    vals = s.str.extract(num)
    label = s.name
    vals.columns = [label]
    vals[label] = vals[label].astype(float)
    
    return(vals[label])
    
def fix_dates(s):
    
    s = s.astype(str)
    s = s.str.lower()
    
    brackets = '\[.*\]'
    parentheses = '\(.*\)'
    seasons = '(?:autumn|summer|spring|winter|early|late|mid|before)*'
    
    re_pattern = '|'.join([brackets,parentheses,seasons])
    
    s = s.str.replace(re_pattern,'')
    s = s.str.strip()
    
    dates = pd.to_datetime(s,errors='coerce')
    dates.name = 'date1'
    year = '(\d{4})'
    s2 = s[dates.isnull()]
    s2 = s2.str.extract(year)
    dates2 = pd.to_datetime(s2[0].astype(str))
    
    dates = pd.DataFrame(dates)
    dates['date2'] = dates2
    dates = combine_columns(dates,['date1','date2'])
    
    return(dates['date1'])
    
df_infoboxes=pd.read_pickle('03_df_infoboxes.pkl')
df_specs = pd.read_pickle('03_df_specs.pkl')
    
df_infoboxes.columns = [convert_to_snake(col) for col in df_infoboxes.columns]
df_specs.columns = [convert_to_snake(col) for col in df_specs.columns]

def combine_columns(df,cols):
    df[cols[0]] = df[cols].ffill(axis=1).iloc[:,-1]
    df.drop(cols[1:],axis=1,inplace=True)
    return(df)    

df_specs = combine_columns(df_specs,['cruise_speed','cruising_speed'])
df_specs = combine_columns(df_specs,['max_takeoff_weight',
                                     'max._takeoff_weight'])
df_specs = combine_columns(df_specs,['max_landing_weight','landing_weight',
                                     'maximum_landing_weight'])

df_infoboxes = combine_columns(df_infoboxes,['primary_users','primary_user'])
df_infoboxes = combine_columns(df_infoboxes,['national_origin','country',
                                             'country_of_origin'])


#df_infoboxes.columns = list(df_infoboxes.columns).index('in_service')] = 'in_service2'
#
#df_infoboxes['in_service'] = df_infoboxes.combine_first(')

# Fixing df_specs
lengths = ['wingspan','length','height','service_ceiling']
for length in lengths:
    label = length + '_ft'
    df_specs[label] = fix_lengths(df_specs[length])
    
weights = ['empty_weight','gross_weight','max_takeoff_weight']
for weight in weights:
    label = weight + '_lb'
    df_specs[label] = fix_weights(df_specs[weight])
    
speeds = ['maximum_speed','cruise_speed','stall_speed','never_exceed_speed']
for speed in speeds:
    label = speed + '_kn'
    df_specs[label] = fix_speeds(df_specs[speed])

# Fixing df_infoboxes
quantities = ['number_built']
for quantity in quantities:
    label = quantity + '_qty'
    df_infoboxes[label] = fix_quantities(df_infoboxes[quantity]) 

dates = ['first_flight','introduction','retired']
for date in dates:
    label = date + '_date'
    df_infoboxes[label] = fix_dates(df_infoboxes[date])


us_list = ['UNITED STATES OF AMERICA','AMERICA','UNITED STATES OF AMERICA (USA)',
           'USA','US','U.S.','U.S.A','U.S.A.']

df_infoboxes['national_origin'] = (df_infoboxes['national_origin']
        .replace(us_list,'UNITED STATES'))

ussr_list = ['USSR','U.S.S.R.']

df_infoboxes['national_origin'] = (df_infoboxes['national_origin']
        .replace(ussr_list,'SOVIET UNION'))

#aa = pd.DataFrame(df_infoboxes['role'].value_counts()).reset_index()













# Save dataframes to pickles for next script
df_infoboxes.to_pickle('Script_Data/04_df_infoboxes.pkl')
df_specs.to_pickle('Script_Data/04_df_specs.pkl')





#
#cc = pd.DataFrame(s)
#cc['date1'] = pd.to_datetime(cc['first_flight'],errors='coerce')
#cc['first_flight2'] = cc[cc['date1'].isnull()]['first_flight']
#
#year = '(\d{4})'
#cc['date2'] = cc['first_flight2'].str.extract(year)
#cc['date3'] = pd.to_datetime(cc['date2'])
#
#cc = combine_columns(cc,['date1','date3'])
#
#print('nulls: ',cc['date1'].isnull().sum())




#punctuations = '(?:;|"|\+)*'
#years_ago = '\;*\s*\d+\s*years\s*ago\s*'
#c_start = 'c\.\s*'
#ca_start = 'ca\.\s*'
    
    































#df_f = df_infoboxes[['first_flight']]
#df_f['first_flight_date'] = pd.to_datetime(df_infoboxes['first_flight'])









#df_specs['max_takeoff_weight'] = (df_specs['max_takeoff_weight']
#                                  .combine_first(df_specs['max._takeoff_weight']))
#df_specs.drop('max._takeoff_weight',axis=1,inplace=True)
#
#df_specs['max_landing_weight'] = (df_specs['max_landing_weight']
#                                 .combine_first(df_specs['maximum_landing_weight'])
#                                 .combine_first(df_specs['landing_weight']))
#df_specs.drop(['maximum_landing_weight','landing_weight'],axis=1,inplace=True)








##df_specs['wingspan_ft'] = data_cleaning.fix_lengths(list(df_specs['wingspan'].astype('O').str.lower()))
#
#s = df_specs['wingspan']
#
##a = s.str.extract(r'(\d+\.?\d*)\s*ft\s*(?:(\d+\.?\d*)\s*in)*')










#s = s.astype(str)
#s = s.str.lower()

#a = vals[vals.isnull().all(1)]
#a = s[vals.isnull().all(1)]











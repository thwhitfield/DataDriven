# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 22:16:18 2019

@author: thwhi

Data exploration and analysis of crash data from the FAA database.
Looking at trends and interesting relationships related to aircraft accidents.
"""

import pandas as pd
import numpy as np
import pyodbc
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter 
import re

# Connect to Access Database downloaded from 'https://app.ntsb.gov/avdata/'
# This database contains all accident data from 1982 to the present, in a
# relational database accessed with SQL commands.
access_database = r'C:\Users\thwhi\Dropbox\Personal\Programming\Aircraft Stuff\avall_full_aircraft_crash_database\avall.mdb'
driver = r'Microsoft Access Driver (*.mdb, *.accdb)'
conn = pyodbc.connect(r'DRIVER={' + driver + '};DBQ=' + access_database + ';')

# Import data dictionary which has what the different codes in cells actually
# mean. The ct_iaids also contains similar coding information

df_data_dictionary = pd.read_sql_query('SELECT * FROM eADMSPUB_DataDictionary',conn)
df_ct_iaids = pd.read_sql_query('SELECT * FROM ct_iaids',conn)

# Ok, now that I've imported those into dataframes, let's look at the actual
# interesting data from the database. We'll start with separating out the
# accidents with fatal injuries, and only those from 2001-2010 inclusive, 
# and then only those from the USA.

sql_event_id_and_date = '''
SELECT ev_id, ntsb_no, ev_date
FROM events
WHERE ev_type = 'ACC' AND ev_highest_injury = 'FATL' AND ev_country='USA';
'''
df_event_info = pd.read_sql_query(sql_event_id_and_date,conn)
df_event_info = df_event_info[(df_event_info['ev_date'] >= '2001-01-01') & (df_event_info['ev_date'] <= '2010-12-31')]
df_event_info['ev_date'] = pd.to_datetime(df_event_info['ev_date'])
df_event_info['Year'] = df_event_info['ev_date'].dt.year

# Next I'll grab the flight hours for the pilot in command for each of those
# flights, and discard a few erroneous values.I'll also only grab aircraft
# 1 from these events (where there might be more than 1 aircraft)

sql_flight_time_tot = '''
SELECT ev_id, flight_hours 
FROM flight_time 
WHERE flight_type = 'TOTL' AND flight_craft = 'ALL' AND flight_hours <> 999999
AND flight_hours <> 99999 AND crew_no = 1 AND Aircraft_Key = 1;
'''
df_flight_time_tot = pd.read_sql_query(sql_flight_time_tot,conn)

# Now I'll merge these two together, and keep only the flight times that have
# event_id's in the date range from 2001-2010, I'll also drop the rows with
# NaN values

df_flight_time_tot = df_flight_time_tot.merge(df_event_info,how='right',
                                              left_on='ev_id', right_on='ev_id')
df_flight_time_tot = df_flight_time_tot.dropna(axis=0)

# Next I'll plot a histogram of the Pilot in Command's total flying hours
# with a logarithm x axis to show the distribution more clearly. The

def plot_flight_time_tot():
    _, bins = np.histogram(np.log10(df_flight_time_tot['flight_hours']+1), bins=75)
    
    fig, ax = plt.subplots()
    ax.hist(df_flight_time_tot['flight_hours'],bins=10**bins)
    plt.gca().set_xscale("log")
    ax.xaxis.set_major_formatter(ScalarFormatter())
    plt.xlim(1,100000)
    ax.set_xlabel("Total Flying Hours (Pilot in Command)")
    ax.set_ylabel('Frequency')
    ax.set_title("Histogram of Total Flying Hours for Pilot in Command\nof Fatal Accidents from 2001-2010")
    
    mean = df_flight_time_tot['flight_hours'].mean()
    median = df_flight_time_tot['flight_hours'].median()
    textstr = '\n'.join(('Mean = {:.0f}'.format(mean),'Median = {:.0f}'.format(median)))
    
    ax.text(0.05, 0.95,textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top')
    plt.show()
    return

# What next? Let's look at statistics for the phase of flight
sql_phase = '''
SELECT ev_id, phase_flt_spec
FROM aircraft
'''

# Grab the dictionary to translate the codes into actual labels
sql_phase_dict = '''
SELECT code_iaids, meaning
FROM eADMSPUB_DataDictionary
WHERE Table = 'aircraft' AND ct_name = 'ct_phase_flt_spec';
'''

phase_dict = pd.read_sql_query(sql_phase_dict,conn)
phase_dict['code_iaids'] = phase_dict['code_iaids'].astype(float)
phase_dict = phase_dict.set_index('code_iaids')['meaning'].to_dict()

# Grab the specific and broad phases of flight, dropping in NaN values
df_phase = pd.read_sql_query(sql_phase, conn)
df_phase = df_phase.merge(df_event_info, how='right',left_on='ev_id',
                          right_on='ev_id')
df_phase = df_phase.dropna(axis=0)

df_phase['phase_flt_broad'] = df_phase['phase_flt_spec'].astype(str).str[:2]+'0'
df_phase['phase_flt_broad'] = df_phase['phase_flt_broad'].astype(float)

df_phase['phase_flt_spec'] = (df_phase['phase_flt_spec']
                             .astype('category')
                             .cat.rename_categories(phase_dict))

df_phase['phase_flt_broad'] = (df_phase['phase_flt_broad']
                             .astype('category')
                             .cat.rename_categories(phase_dict))

# Get the frequencies of each broad phase of flight and plot as a bar chart
broad_phase_counts = df_phase['phase_flt_broad'].value_counts().drop(0.0)

def plot_broad_phase_of_flight():
    fig, ax = plt.subplots()
    broad_phase_counts.plot.bar()
    ax.set_title('Broad Phase of Flight\nFatal Accidents from 2001-2010')
    ax.set_ylabel('Number of Fatal Accidents')
    ax.set_xticklabels(broad_phase_counts.index,rotation=45, ha='right')
    fig.tight_layout()
    return

# Get those same frequencies by year:
broad_phase_counts_by_year = (df_phase[['phase_flt_broad','ev_id','Year']]
                             .groupby(['phase_flt_broad','Year'],as_index=False)
                             .count())
phases_to_include = list(broad_phase_counts.index[:7])
broad_phase_counts_by_year = broad_phase_counts_by_year[broad_phase_counts_by_year['phase_flt_broad'].isin(phases_to_include)]
# I just realized that they stopped recording the phase_flt_spec values in
# the aircraft table starting midway through 2008. That's annoying, I guess
# I can go to the Occurences tab and try and use that data instead.

def plot_broad_phase_of_flight_over_time():
    #TODO
    return
    


# Where I stopped on 7/17/2019
#===========================================================================

# Heatmap of accidents by lat lon gps coordinates.
    
sql_event_location = '''
SELECT ev_id, ntsb_no, ev_type, ev_date, latitude, longitude, ev_site_zipcode,
ev_city, ev_state
FROM events
WHERE ev_country='USA'
'''
df_event_locations = pd.read_sql_query(sql_event_location,conn)
df_event_locations['ev_date'] = pd.to_datetime(df_event_info['ev_date'])
#df_event_locations = df_event_locations[(df_event_locations['ev_date'] >= '2001-01-01') & (df_event_locations['ev_date']<= '2010-12-31')]

for col in df_event_locations.columns:
    if df_event_locations[col].dtype == 'O':
        df_event_locations[col] = df_event_locations[col].str.strip()

lat_regex = r'(\d{6}N)'
lon_regex = r'(\d{7}W)'

df_event_locations = (df_event_locations[df_event_locations['latitude']
                     .astype(str)
                     .str.match(lat_regex)])
df_event_locations = (df_event_locations[df_event_locations['longitude']
                     .astype(str)                     
                     .str.match(lon_regex)])

lats = (df_event_locations['latitude'].str[:6]
        .astype(int).values)
lons = (df_event_locations['longitude'].str[:7]
        .astype(int).values)

plt.figure()
_ = plt.hist2d(lats,lons,bins=75)




#=======================================================================
# Started back up on 7/19/2019

# Get pilot information for all accidents, things like Gender, 

#db_table_names = ['events','dt_events','aircraft','cabin_crew','flight_crew',
#                  'narratives','engines','injury','Occurrences','dt_aircraft',
#                  'flight_time','dt_flight_crew','seq_of_events']

db_table_names = ['aircraft','Country','ct_iaids','ct_seqevt','dt_aircraft',
                  'dt_events','dt_Flight_Crew','eADMSPUB_DataDictionary',
                  'engines','events','Events_Sequence','Findings','Flight_Crew',
                  'flight_time','injury','narratives','NTSB_Admin',
                  'Occurrences','seq_of_events','states']

db_col_names = set()
db_table_col_names = {}

for name in db_table_names:
    sql_get_col_names = 'SELECT TOP 10 * FROM ' + name
    db_table = pd.read_sql_query(sql_get_col_names,conn)
    db_table_col_names[name]=list(db_table.columns)
    for col in db_table.columns:
        db_col_names.add(col)

db_col_names = list(db_col_names)

#sql_get_all_col_names


#sql_get_table_names = '''
#SELECT MSysObjects.Name AS table_name
#FROM MSysObjects
#WHERE (((Left([Name],1))<>"~") 
#        AND ((Left([Name],4))<>"MSys") 
#        AND ((MSysObjects.Type) In (1,4,6)))
#order by MSysObjects.Name 
#'''
#
#db_table_names = pd.read_sql_query(sql_get_table_names,conn)
#
#sql_accident_data = '''
#SELECT *
#FROM events
#INNER JOIN aircraft
#ON events.ev_id = aircraft.ev_id;
#'''
#
#df_accidents = pd.read_sql_query(sql_accident_data,conn)









df_occurences = pd.read_sql_query('SELECT TOP 1000 * FROM Occurrences',conn)
df_aircraft = pd.read_sql_query('SELECT TOP 1000 * FROM aircraft',conn)
df_data_dictionary = pd.read_sql_query('SELECT * FROM eADMSPUB_DataDictionary',conn)


df_events = pd.read_sql_query('SELECT TOP 1000 * FROM events',conn)
df_country = pd.read_sql_query('SELECT TOP 1000 * FROM Country',conn)
df_ct_iaids = pd.read_sql_query('SELECT TOP 1000 * FROM ct_iaids',conn)
df_flight_crew = pd.read_sql_query('SELECT TOP 1000 * FROM Flight_Crew',conn)
df_flight_crew_dictionary = df_data_dictionary[df_data_dictionary['Table']=='Flight_Crew']
df_flight_time = pd.read_sql_query('SELECT TOP 1000 * FROM flight_time',conn)
df_narratives = pd.read_sql_query('SELECT TOP 1000 * FROM narratives',conn)
df_findings = pd.read_sql_query('SELECT TOP 1000 * FROM Findings',conn)
df_engines = pd.read_sql_query('SELECT TOP 1000 * FROM engines',conn)
df_event_sequence = pd.read_sql_query('SELECT TOP 1000 * FROM Events_Sequence',conn)
df_injury = pd.read_sql_query('SELECT TOP 1000 * FROM injury',conn)
df_ntsb_admin = pd.read_sql_query('SELECT TOP 1000 * FROM NTSB_Admin',conn)

df_findings = df_findings.merge(df_events[['ev_id','ntsb_no']],
                                how='left',left_on='ev_id',right_on='ev_id')

df_event_dictionary = df_data_dictionary[df_data_dictionary['Table']=='events']
df_aircraft_dictionary = df_data_dictionary[df_data_dictionary['Table']=='aircraft']
df_findings_dictionary = df_data_dictionary[df_data_dictionary['Table']=='Findings']
df_narratives_dictionary = df_data_dictionary[df_data_dictionary['Table']=='narratives']

df1 = df_data_dictionary[df_data_dictionary['Table'] == 'flight_time']

df2_flight_time = pd.read_sql_query("SELECT * FROM flight_time WHERE flight_type = 'TOTL' AND flight_craft = 'ALL';",conn)

df2_flight_time = df2_flight_time[df2_flight_time['flight_hours'] < 50000]


df_occurences = df_occurences[(df_occurences['Aircraft_Key']==1) & (df_occurences['Occurrence_No'] == 1)]

df_airmen_stats = pd.read_excel(r'C:\Users\thwhi\Dropbox\Personal\Programming\Misc Practice\2018-civil-airmen-stats.xlsx')
xls = pd.ExcelFile(r'C:\Users\thwhi\Dropbox\Personal\Programming\Misc Practice\2018-civil-airmen-stats.xlsx')

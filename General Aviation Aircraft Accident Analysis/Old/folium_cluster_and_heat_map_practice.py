# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 01:49:15 2019

@author: thwhi
"""

import folium
from folium.plugins import MarkerCluster
from folium import plugins
from folium import Popup
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

sql_aircraft_type = '''
SELECT ev_id, acft_make, acft_model
FROM aircraft
'''
df_aircraft_type = pd.read_sql_query(sql_aircraft_type,conn)

# Heatmap of accidents by lat lon gps coordinates.
sql_event_location = '''
SELECT ev_id, ntsb_no, ev_type, ev_date, latitude, longitude, ev_site_zipcode,
ev_city, ev_state
FROM events
WHERE ev_country='USA'
'''
df_event_locations = pd.read_sql_query(sql_event_location,conn)
df_event_locations['ev_date'] = pd.to_datetime(df_event_locations['ev_date'])
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

df_event_locations['lat'] = (df_event_locations['latitude']
                            .str[:6]
                            .astype(int)/10000)

df_event_locations['lon'] = (df_event_locations['longitude']
                            .str[:7]
                            .astype(int)/-10000)
    
df_event_locations = df_event_locations.merge(df_aircraft_type,how='left',
                                              left_on='ev_id',right_on='ev_id')

#lats = (df_event_locations['latitude'].str[:6]
#        .astype(int).values)
#lons = (df_event_locations['longitude'].str[:7]
#        .astype(int).values)

# Accident Cluster Map
accident_map = folium.Map(location = [48, -102], zoom_start=4)
marker_cluster = MarkerCluster().add_to(accident_map)

for _, row in df_event_locations.iterrows():
    lat = row['lat']
    lon = row['lon']
    if not pd.isnull(row['ev_date']):
        date = row['ev_date'].strftime('%B %d, %Y')
    else: date='Unknown'
    if not (pd.isnull(row['acft_make']) or pd.isnull(row['acft_model'])): 
        aircraft = row['acft_make'] + ' ' + row['acft_model']
    popup_text = 'NTSB #: ' + row['ntsb_no'] + '\nDate: ' + date + '\nAircraft: ' + aircraft
    folium.Marker([lat,lon],popup=Popup(popup_text,min_width=500)).add_to(marker_cluster)
accident_map.save('aircraft_accident_cluster_map_full.html')


# Accident heat map
accident_heatmap = folium.Map(location = [48, -102], zoom_start=4)
heat_data = [[lat/10000, -lon/10000] for lat, lon in zip(lats,lons)]
plugins.HeatMap(heat_data,min_opacity=0.5,radius=10).add_to(accident_heatmap)
accident_heatmap.save('aircraft_accident_heatmap.html')






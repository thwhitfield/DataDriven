# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:42:42 2019

@author: Travis Whitfield
"""

"""
This code imports the data that was scraped in the 02 script, creates 
pandas dataframes from that data, reorders some of the columns,
removes row entries which aren't actually aircraft (there were several
wikipedia pages which accidentally pointed to non-aircraft wiki pages),
and removes columns which don't have at least 2 entries.
"""

import pandas as pd
import numpy as np
import pickle


# Import data generated in 02_scrape_aircraft_data_off_wikipedia script
with open('Script_Data/02_1_aircraft_info.pkl','rb') as f:
    all_aircraft_info = pickle.load(f)

with open('Script_Data/02_2_infoboxes.pkl','rb') as f:
    infoboxes = pickle.load(f)
    
with open('Script_Data/02_3_titles.pkl','rb') as f:
    titles = pickle.load(f)
    
with open('Script_Data/02_4_aircraft_specs.pkl','rb') as f:
    aircraft_specs=pickle.load(f)

# create dataframes from infoboxes and specs
df_infoboxes = pd.DataFrame(infoboxes)
df_specs = pd.DataFrame(aircraft_specs)
df_specs['aircraft_wikipage_title'] = df_specs['aircraft_wikipage_title'].str.upper()

# Create titles dataframe with the wikipedia page title, and then all the 
# aircraft which were associated with that wikipedia page
titles2 = [[key,', '.join(value)] for key,value in titles.items()]
df_titles = pd.DataFrame(titles2,columns=['aircraft_wikipage_title','aircraft_linked_to_wikipage'])

df_infoboxes = df_infoboxes.merge(df_titles,how='left',on='aircraft_wikipage_title')

# Reorder columns
cols = list(df_infoboxes.columns)
cols.remove('aircraft_linked_to_wikipage')
cols.remove('parse_status')
cols.insert(2,'aircraft_linked_to_wikipage')
cols.insert(0,'parse_status')
df_infoboxes = df_infoboxes[cols]


categories = [row[3] for row in all_aircraft_info if len(row) == 9]
categories = [', '.join(row).upper() for row in categories]
all_aircraft_titles = [row[2] for row in all_aircraft_info if len(row)==9]

df_categories = pd.DataFrame(all_aircraft_titles, columns=['aircraft_wikipage_title'])
df_categories['categories'] = categories
df_categories['aircraft_wikipage_title'] = df_categories['aircraft_wikipage_title'].str.upper()

df_infoboxes = df_infoboxes.merge(df_categories,on='aircraft_wikipage_title')
categories = list(df_infoboxes['categories'])

# Include only entries which have at least one of the valid categories
valid_categories = ['AIRCRAFT','HELICOPTER','PLANE','GLIDER']
df_infoboxes = df_infoboxes[df_infoboxes['categories'].str.contains('|'.join(valid_categories))]

# Drop the columns which no longer have any entries
df_infoboxes = df_infoboxes.dropna(axis=1,how='all')

# Drop columns which don't have at least 2 entries
col_counts = df_infoboxes.count().sort_values(ascending=False)
col_counts = col_counts[col_counts > 1]
df_infoboxes = df_infoboxes[col_counts.index]

#==================================================

df_specs = df_specs.merge(df_titles,how='left',on='aircraft_wikipage_title')
df_specs = df_specs.merge(df_categories,how='left',on='aircraft_wikipage_title')

# Include only entries which have at least one of the valid categories
df_specs = df_specs[df_specs['categories'].str.contains('|'.join(valid_categories))]

# Drop columns which no longer have any entries
df_specs = df_specs.dropna(axis=1,how='all')

# Drop columns which don't have at least 2 entries
col_counts = df_specs.count().sort_values(ascending=False)
col_counts = col_counts[col_counts > 1]
df_specs = df_specs[col_counts.index]

#==================================================

# Save df_infoboxes and df_specs for use in next script
df_infoboxes.to_pickle('Script_Data/03_df_infoboxes.pkl')
df_specs.to_pickle('Script_Data/03_df_specs.pkl')














#df_infoboxes = df_infoboxes.loc[valid]
#valid = [False]*len(categories)
#for i,row in enumerate(categories):
#    for valid_cat in valid_categories:
#        if valid_cat in row:
#            valid[i]=True
#            break


#df_specs = df_specs.loc[valid]
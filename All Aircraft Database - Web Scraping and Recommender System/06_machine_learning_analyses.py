# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 17:07:02 2019

@author: thwhi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

#df_infoboxes = pd.read_pickle('Script_Data/04_df_infoboxes.pkl')
#df_specs = pd.read_pickle('Script_Data/04_df_specs.pkl')
#
#df_specs = df_specs.drop_duplicates()
#df_infoboxes = df_infoboxes.drop_duplicates()

df_specs_num = pd.read_pickle('Script_Data/05_df_specs_num.pkl')

scaler = StandardScaler()

#cols_to_use = ['wingspan_ft','length_ft','height_ft','empty_weight_lb',
#               'maximum_speed_kn']

cols_to_use = ['wingspan_ft','length_ft','height_ft','empty_weight_lb',
               'first_flight_date','number_built_qty']

df = df_specs_num[cols_to_use].dropna(how='any')
df['first_flight_date'] = df['first_flight_date'].astype(float)
df['number_built_qty'] = df['number_built_qty'].astype(float)

df1 = pd.DataFrame(scaler.fit_transform(df.iloc[:,:]),index=df.index)

distances = pairwise_distances(df1,metric='euclidean')
d1 = pd.DataFrame(distances)
d2 = [list(d1[row].sort_values().index)[1:6] for row in d1.index]
d3 = pd.DataFrame(d2)

d3 = d3.apply(lambda x: df1.index[x])
d3.index = [df1.index[x] for x in d3.index]

d4 = d3.applymap(lambda x: df_specs_num.iloc[x,0])
d4.index = [df_specs_num.iloc[x,0] for x in d4.index]





d2 = [list(sorted(distance)) for distance in distances]

d1 = pd.DataFrame(distances[:,0]).sort_values(0)

best_match = d1.index[1]

df_specs_num.loc[d1.index[0]]
df_specs_num.loc[best_match]



##df = df_specs_num[['wingspan_ft','length_ft']]
#df = df_specs_num[['length_ft','maximum_speed_kn']]
#df = df[df['maximum_speed_kn'] < 3000]
#df = df.dropna(how='any')
#
#df_scaled = scaler.fit_transform(df)
#
#kmeans_model = KMeans(n_clusters=2,random_state=1)
#
#kmeans_model.fit_transform(df_scaled)
#
#y_kmeans = kmeans_model.predict(df_scaled)
#
##unscaled_y_kmeans = scaler.inverse_transform(y_kmeans)
#
#fig,ax = plt.subplots()
#plt.scatter(df.iloc[:,0],df.iloc[:,1],c=y_kmeans)











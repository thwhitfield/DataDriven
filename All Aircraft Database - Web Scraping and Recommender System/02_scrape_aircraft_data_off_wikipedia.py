# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 17:13:28 2019

@author: thwhi
"""

import requests
import wikipedia
import pandas as pd
import numpy as np
import pickle
import bs4
import re

df_aircraft = pd.read_csv('Script_Data/01_1_wiki_aircraft_links.csv')
df_aircraft['title_mismatch'] = df_aircraft['title'] == df_aircraft['text']

aircraft_names = list(df_aircraft['title'])

# Grabs the infobox that appears on the top right side of each wiki article
def get_infobox(wiki_html,title):
    soup = bs4.BeautifulSoup(wiki_html)
    info_table_data = {'aircraft_wikipage_title':title,
                       'parse_status':'Parsed Successfully'}
     
    info_table = soup.find('table',attrs={'class':'infobox'})
    if info_table == None:
        info_table_data['parse_status'] = 'no infobox'
        return(info_table_data)
        
    # Replace break lines with commas to deal with multiple values in infobox
    if info_table.findAll('br') != []:
        for br in info_table.findAll('br'):
            br.replace_with(', ')
        
    # Get each row, then get the header and data element for each row and
    # add those as the field and field_entry to my info_table_data variable, 
    rows = info_table.findAll('tr')
    for row in rows:
        if row.find('th') is not None and row.find('td') is not None:
            field = row.find('th').text.strip().lower()
            field_entry = row.find('td').text.strip().upper()
            info_table_data[field] = field_entry
    return(info_table_data)  

# Grab the rest of the data not already grabbed by the other two functions
def parse_aircraft(name,page):
    title = page.title
    
    try:
        categories = page.categories
    except:
        categories = []
        print(name,' category links failed')
    
    try:
        image_links = page.images
    except:
        print(name,' image links failed')
        image_links = []
    
    try:
        links = page.links
    except:
        print(name,' general links failed')
        links = []
        
    try:
        references = page.references
    except:
        print(name,' reference links failed')
        references = []
    
    summary = page.summary
    url = page.url
    parse_status = 'Successful'
    aircraft_info = [name,parse_status,title,categories,image_links,links,
                     references,summary,url]
    return(aircraft_info)


field_names = ['aircraft_wikipage_title', 'Import Status', 'Summary']

# Grab the specifications listed in the body of each wikipage   
def save_specs(wiki_page, title):
    
    spec_regex = re.compile(r'== Specifications.*? ==(.*?)==', re.DOTALL)    
    wiki_page_specs = spec_regex.search(wiki_page.content)    
    if wiki_page_specs == None:
        return({'aircraft_wikipage_title': wiki_page.title, 'Summary':wiki_page.summary, 'Import Status':'regex search error'})
    mySpecs = wiki_page_specs.group().split('\n')    
    mySpecs2 = [['aircraft_wikipage_title', wiki_page.title]]

    for i in range(len(mySpecs)):
        if ':' in mySpecs[i]:
            if len(re.findall(':', mySpecs[i])) < 2:
                mySpecs2.append([x.strip().title() for x in mySpecs[i].split(':')])
                if mySpecs2[-1][0].strip().title() not in field_names:
                    field_names.append(mySpecs2[-1][0].strip().title())
    myDict = dict(mySpecs2)

    return(myDict)




all_aircraft_info = []
titles = {}

aircraft_fails = []
infoboxes = []

aircraft_specs = []
aircraft_spec_fails = [] 

i = 0

#for name in m_aircraft_names:

for name in aircraft_names[:10]:
    i += 1
    print(i, name)
    
    try:
        page = wikipedia.page(name)
        wiki_html = page.html()
    except:
        print(name,' wiki call failed')
        aircraft_info = [name,'wiki call failed']
        all_aircraft_info.append(aircraft_info)
    
    name = name.upper()
    title = page.title.upper()
    if title in titles:
        titles[title].append(name)
        print(name, ' matches other wikipage')
        continue
    else:
        titles[title] = [name]
    
    try:
        aircraft_info = parse_aircraft(name,page)
        all_aircraft_info.append(aircraft_info)
    except:
        print(name, ' failed aircraft parsing')
        
    
    try:        
        infobox = get_infobox(wiki_html,title)
        infoboxes.append(infobox)
    except:
        aircraft_fails.append(name)
        print(name, ' failed infobox parsing.')
        
    try:
        aircraft_spec = save_specs(page,title)
        aircraft_specs.append(aircraft_spec)
    except:
        aircraft_spec_fails.append(name)
        print(name, ' failed wiki spec import')
        
    # Download all text and html from those wikipages
    try:
        with open('Aircraft_wiki_data/' + name + '.txt',
                  'w', encoding='utf-8') as f:
            f.write(page.content)
        with open('Aircraft_wiki_data/' + name + '.html',
                  'w', encoding='utf-8') as f:  
            f.write(wiki_html)
    except:
        try:
            name2 = ''.join(x for x in name if x.isalnum())
            with open('Aircraft_wiki_data/' + name2 + '.txt',
                      'w', encoding='utf-8') as f:
                f.write(page.content)
            with open('Aircraft_wiki_data/' + name2 + '.html',
                      'w', encoding='utf-8') as f:  
                f.write(wiki_html)
        except:
            print(name, ' failed to save wiki_html & content')
        
        
# Save all the information scraped in this section as pickles, mainly
# due to the files not all being easily saved as csvs

with open('Script_Data/02_1_aircraft_info.pkl','wb') as f:
    pickle.dump(all_aircraft_info,f)

with open('Script_Data/02_2_infoboxes.pkl','wb') as f:
    pickle.dump(infoboxes,f)
    
with open('Script_Data/02_3_titles.pkl','wb') as f:
    pickle.dump(titles,f)
    
with open('Script_Data/02_4_aircraft_specs.pkl','wb') as f:
    pickle.dump(aircraft_specs,f)

# ======================================
## Save list to a variable so I don't have to worry about formatting it for now
#with open('aircraft_info.pkl','wb') as f:
#    pickle.dump(all_aircraft_info,f)
#
## Code to load the pickle back into data:
#with open('aircraft_info.pkl','rb') as f:
#    all_aircraft_info = pickle.load(f)
# ======================================


## Scrape the aircraft from the M letter that was missed during initial
## scraping. This was added on 8/17/2019. This part won't be needed in future
## runs because 01_scrape... file was updated
#
#df_m_aircraft = pd.read_csv('01_3_m_wiki_aircraft_links.csv')
#
#m_aircraft_names = list(df_m_aircraft['title'])
#
#
#with open('02_5_m_aircraft_info.pkl','wb') as f:
#    pickle.dump(all_aircraft_info,f)
#
#with open('02_6_m_infoboxes.pkl','wb') as f:
#    pickle.dump(infoboxes,f)
#    
#with open('02_7_m_titles.pkl','wb') as f:
#    pickle.dump(titles,f)
#    
#with open('02_8_m_aircraft_specs.pkl','wb') as f:
#    pickle.dump(aircraft_specs,f)
#
#
#with open('02_5_m_aircraft_info.pkl','rb') as f:
#    m_all_aircraft_info = pickle.load(f)
#
#with open('02_6_m_infoboxes.pkl','rb') as f:
#    m_infoboxes = pickle.load(f)
#    
#with open('02_7_m_titles.pkl','rb') as f:
#    m_titles = pickle.load(f)
#    
#with open('02_8_m_aircraft_specs.pkl','rb') as f:
#    m_aircraft_specs=pickle.load(f)
#    
#aircraft_specs += m_aircraft_specs
#titles.update(m_titles)
#infoboxes += m_infoboxes
#all_aircraft_info += m_all_aircraft_info

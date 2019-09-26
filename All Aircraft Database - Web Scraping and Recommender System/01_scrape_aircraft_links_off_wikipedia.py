# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 10:43:07 2019

@author: thwhi
"""

"""
This code scrapes wikipedia for all the aircraft links listed in the "lists
of aircraft" pages. It starts by scraping all of the different "lists of
aircraft", then it goes through each of the differents pages (73 in total)
and grabs the aircraft name, "title", and wikipedia url. Lots of the aircraft
did not have a wikipedia page even though they're listed here, so I gathered
those into a second csv file.
"""



import wikipedia
import bs4
import requests
import pandas as pd

wikipedia.set_rate_limiting(True)
wiki_start_link = r'https://en.wikipedia.org'

# Grab the links to the lists of aircraft
def get_aircraft_list_links():
    page = wikipedia.page('List of aircraft (0–Ah)')
    html = page.html()
    soup = bs4.BeautifulSoup(html)
    
    table = soup.find('div',attrs={'class':'hlist'})
    tag_list = table.findAll('a',href=True)
    aircraft_list_links = [wiki_start_link + tag['href'] for tag in tag_list]
    aircraft_list_links.insert(0,r'https://en.wikipedia.org/wiki/List_of_aircraft_(0%E2%80%93Ah)')

    return(aircraft_list_links)    


aircraft_list_links = get_aircraft_list_links()
# There were multiple pages for letters S & T, so those are dropped here
# and the links to the subpages (Sa, Sb, etc.) are added below
aircraft_list_links.remove(r'https://en.wikipedia.org/wiki/List_of_aircraft_(S)')
aircraft_list_links.remove(r'https://en.wikipedia.org/wiki/List_of_aircraft_(T)')

# Code to grab lists of aircraft starting with Sa, Sb, Ta, Tb, etc.
def get_letter_links(link):
    html = requests.get(link).text
    soup = bs4.BeautifulSoup(html)
    table = soup.find('div',attrs={'id':'toc'})
    tag_list = table.findAll('a',href=True)
    links = [wiki_start_link + tag['href'] for tag in tag_list]
    return(links)


# Add S, T, & M links to the whole list of lists
s_links = get_letter_links(r'https://en.wikipedia.org/wiki/List_of_aircraft_(S)')
aircraft_list_links += s_links
t_links = get_letter_links(r'https://en.wikipedia.org/wiki/List_of_aircraft_(T)')
aircraft_list_links += t_links
m_links = get_letter_links(r'https://en.wikipedia.org/wiki/List_of_aircraft_(M)')
aircraft_list_links += m_links

# Grab the title, displayed title, and url for each aircraft in the lists of
# aircraft that I found. This should be most of the aircraft found on wikipedia
def get_aircraft_titles(link):

    html = requests.get(link).text
    soup = bs4.BeautifulSoup(html)
    
    # Grab the first header of the page
    first_header = soup.find('span',attrs={'class':'mw-headline'})
    # Grab the last header of the page
    last_header = first_header.findNext('table',attrs={'class':'vertical-navbox nowraplinks plainlist'})
    # If statement accounts for differences between some of the pages
    if last_header == None:
        last_header = soup.find('span',attrs={'id':'References'})
        last_li = last_header.findPrevious('li')
    else:
        last_li = last_header.findNext('li')
    
    # Aircraft links were all in unordered bullets, so I grab the 'li' bullets
    # Stopping at where I believe the last entry is (because there are lots
    # of misc. bullets on the whole page.)
    li_list = first_header.findAllNext('li')
    last_index = li_list.index(last_li)
    li_list = li_list[:last_index]
    
    aircraft_titles = []
    aircraft_titles_no_link = []
    
    for li in li_list:
        tag = li.find('a',href=True)
        if tag == None:
            continue
        try:
            title = tag['title']
        except:
            continue
        text = tag.get_text()
        url = tag['href']
        if 'page does not exist' in title:
            aircraft_titles_no_link.append((title,text))
            continue
        else:
            aircraft_titles.append((title,text,url))
    
    return(aircraft_titles,aircraft_titles_no_link)
    
    
aircraft_titles = [('title','text','url')]
aircraft_titles_no_link = [('title','text','url')]

# Main loop grabbing all the individual links
for link in aircraft_list_links:
    a, b = get_aircraft_titles(link)
    aircraft_titles += a
    aircraft_titles_no_link += b

# Save the two csv files
df_aircraft = pd.DataFrame(aircraft_titles)
df_aircraft.columns = df_aircraft.iloc[0,:]
df_aircraft.drop(0,axis=0,inplace=True)
df_aircraft.to_csv('Script_Data/01_1_wiki_aircraft_links.csv',index=False)

df_aircraft_no_links = pd.DataFrame(aircraft_titles_no_link)
df_aircraft_no_links.columns = df_aircraft_no_links.iloc[0,:]
df_aircraft_no_links.drop(0,axis=0,inplace=True)
df_aircraft_no_links.to_csv('Script_Data/01_2_wiki_aircraft_titles_no_links.csv',index=False)


# Grab the aircraft titles from the M letter that was missed during initial
# scraping. This was added on 8/17/2019, but the above code has been updated
# to not need to run this section separately.

#m_links = get_letter_links(r'https://en.wikipedia.org/wiki/List_of_aircraft_(M)')
#m_aircraft_titles = [('title','text','url')]
#m_aircraft_titles_no_link = [('title','text','url')]
#
#for link in m_links:
#    a,b = get_aircraft_titles(link)
#    m_aircraft_titles += a
#    m_aircraft_titles_no_link += b
#    
#df_m_aircraft = pd.DataFrame(m_aircraft_titles)
#df_m_aircraft.columns = df_m_aircraft.iloc[0,:]
#df_m_aircraft.drop(0,axis=0,inplace=True)
#df_m_aircraft.to_csv('01_3_m_wiki_aircraft_links.csv')
#
#df_m_aircraft_no_links = pd.DataFrame(m_aircraft_titles_no_link)
#df_m_aircraft_no_links.columns = df_m_aircraft_no_links.iloc[0,:]
#df_m_aircraft_no_links.drop(0,axis=0,inplace=True)
#df_m_aircraft_no_links.to_csv('01_4_m_wiki_aircraft_titles_no_links.csv',index=False)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
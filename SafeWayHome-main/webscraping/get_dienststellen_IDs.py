
# import packages
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd

# define URLs
URL_main = 'https://www.presseportal.de/blaulicht/'

# list of all dieststellen
URL_dienststellen = URL_main + 'dienststellen'
URL_dienststellen

# function which first reads out all links on a given website and them extracts the ID within the URLs
def get_ids(df, website, pattern):
    request = requests.get(website)
    soup = BeautifulSoup(request.text, 'html.parser')
    
    # find all links on the website
    for tag in soup.findAll("a", href=True):
            if (pattern) in tag.get("href"):
                df = df.append({'URL': tag.get("href"), 'Headline': tag.text}, ignore_index=True) 
            else:
                next
    
    return df

# Scrape list of all available Dienststellen 
dienststellen = pd.DataFrame(columns =['Headline','ID', 'URL'])
dienststellen = get_ids(df = dienststellen,
                        website = URL_dienststellen, 
                        pattern = "/blaulicht/nr/")
#  split ID from URL
dienststellen[['URL','ID']] = dienststellen['URL'].str.rsplit("/", 1, expand = True)
dienststellen.head()


# add type of Dienstststelle
dienststellen['Roomtitle'] = ""
i = 0
for d in dienststellen['ID']:
    request = requests.get(URL_main + 'nr/' + d)
    soup = BeautifulSoup(request.text, 'html.parser')
    dienststellen.loc[i]['Roomtitle'] = soup.find('h1', class_='newsroom-title').text.strip()
    i = i + 1
    time.sleep(0.5)

dienststellen.head()
    
# save as .csv file
dienststellen.to_csv("data/dienststellen.csv")
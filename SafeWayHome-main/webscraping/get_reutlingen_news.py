# load packages
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import time

# define city for training data
city = 'Reutlingen'

# import Dienststellen IDs
dienststellen = pd.read_csv('dienststellen.csv')
dienststellen.dtypes # check types

# change type of id as it must be string
dienststellen['id'] = dienststellen['id'].astype("string")
dienststellen.dtypes

# define URL Reutlingen
URL_main = 'https://www.presseportal.de/blaulicht/'
URL_rt = URL_main + 'nr/' + dienststellen[dienststellen['text'].str.match(city, na = False)]['id'].item()
URL_rt

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

# preallocate empty data base for training articles
articles = pd.DataFrame(columns =['Preasidium', 'ID_preasidium', 'Headline','ID', 'URL', 'Date', 'Article', 'Keywords_location', 'Keywords_topic'])

# loop over all pages of URL_rt and save ID into data frame
maxpage = 60

for page in range(0, maxpage, 30):
    page_str = str(page)  # must be string for URL 
    
    articles = get_ids(df = articles,
                        website = URL_rt + "/" + page_str, 
                        pattern = URL_main + "pm")
    time.sleep(1)

    
# split ID from URL
articles[['URL','ID_preasidium', 'ID']] = articles['URL'].str.rsplit("/", 2, expand = True)
articles['Preasidium'] = city

# scrape title, articles and keywords using the URL
i = 0
for ID in articles['ID'][:5]:
    request = requests.get(URL_main + 'pm/' + articles.loc[i]['ID_preasidium'] + '/' + ID)
    soup = BeautifulSoup(request.text, 'html.parser')
    
    articles.loc[i]['Date'] = soup.find('p', class_='date').text.strip()
    articles.loc[i]['Article'] = soup.find('article').get_text(separator=' ')
    articles.loc[i]['Keywords_location'] = soup.findAll('ul', class_="tags")[0].get_text(separator=',')
    articles.loc[i]['Keywords_topic'] = soup.findAll('ul', class_="tags")[1].get_text(separator=',')
    i = i + 1
    time.sleep(1)
    
# save as .csv file
articles.to_csv("data/reutlingen.csv")
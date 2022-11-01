# import packages
from bs4 import BeautifulSoup
import re
import requests
import time

sleep_time = 0.5


################################################################################################
### -- Check robots.txt -------------------------------------------------------------------- ###
################################################################################################

class RobotsTxt():

    # -- read robots.txt file and store content as dict
    def __init__(self, url):
        # check url
        if url.endswith("/"):
            url = url[:-1]
        root_url = "https://" + url.replace("https://", "").replace("http://", "").split("/")[0]
        # request robots.txt
        try:
            robots = requests.get(root_url + "/robots.txt")
        except requests.exceptions.RequestException as e:
            raise e
        # convert text to lower
        robots_txt = robots.text.lower()
        # split text string by user-agent
        robots_txt = [x for x in robots_txt.split("user-agent:") if len(x) > 0]
        # for each user-agent, store all allow and disallow links in a separate list
        robots_dict = {x.splitlines()[0].strip(): {"Allow": [y.replace("allow:", "").strip() for y in x.splitlines()[1:] if "allow" in y and not "disallow" in y],
                                           "Disallow": [z.replace("disallow:", "").strip() for z in x.splitlines()[1:] if "disallow" in z]} for x in robots_txt}

        self.text = robots_dict
        self.url = root_url


    # -- check if url can be scraped
    def check_scrape_permission(self, fetch_url, user_agent="*"):
        # check if fetch_url contains any disallow link
        for x in self.text[user_agent]["Disallow"]:
            if "*" in x:
                x = [f"({re.escape(x)})" for x in x.split("*")]
                match = re.search(".*".join(x), fetch_url)
            else:
                match = re.search(f"({re.escape(x)})", fetch_url)

            if match:
                return not match
        return True



################################################################################################
### -- Check robots.txt -------------------------------------------------------------------- ###
################################################################################################

class PresseportalScraper():

    def __init__(self):
        # define base URL
        self.URL_main = 'https://www.presseportal.de/blaulicht/'
        # url for dienststellen
        self.URL_headquarters = self.URL_main + 'dienststellen'
        # matching url pattern to filter links
        self.hq_pattern = "blaulicht/nr/"
        self.article_pattern = "blaulicht/pm/"
        # only include listed headquarter types
        self.headquarter_types = ["Polizeipräsidium"]
        # read robots.txt
        self.robots = RobotsTxt(self.URL_main)

    def get_police_headquarters(self):
        headquarters = list()
        request = requests.get(self.URL_headquarters)
        soup = BeautifulSoup(request.text, 'html.parser')
        # find all links on the website
        for tag in soup.findAll("a", href=True):
            if (self.hq_pattern in tag.get("href")) and any(
                    type in tag.get("title") for type in self.headquarter_types):
                url, id = tag.get("href").rsplit("/", 1)
                title = re.search(r'[A-Z].*', tag.get("title")).group()
                headquarters.append({'ID': str(id), 'URL': url, 'Name': title})
            else:
                next

        return headquarters

    def get_articles(self, hq_data):
        URL_hq_newsroom = self.URL_main + 'nr/' + hq_data["ID"]
        articles = list()

        request = requests.get(URL_hq_newsroom)
        soup = BeautifulSoup(request.text, 'html.parser')
        # find all links on the website
        for tag in soup.findAll("a", href=True):
            if self.article_pattern in tag.get("href"):
                url, _, id = tag.get("href").rsplit("/", 2)
                title = tag.get("title")
                print(self.URL_main + 'pm/' + hq_data['ID'] + '/' + str(id))
                date, text, kw_location, kw_topic = self.scrape_article(
                    self.URL_main + 'pm/' + hq_data['ID'] + '/' + str(id))
                articles.append({'Preasidium': hq_data['Name'],
                                 'ID_preasidium': hq_data['ID'],
                                 'Headline': title,
                                 'ID': id,
                                 'URL': url,
                                 'Date': date,
                                 'Article': text,
                                 'Keywords_location': kw_location,
                                 'Keywords_topic': kw_topic})
            else:
                next

        return articles

    def scrape_article(self, article_url):
        request = requests.get(article_url)
        soup = BeautifulSoup(request.text, 'html.parser')

        date = soup.find('p', class_='date').text.strip()
        text = soup.find('article').get_text(separator=' ')
        kw_location = soup.findAll('ul', class_="tags")[0].get_text(separator=',')
        kw_topic = soup.findAll('ul', class_="tags")[1].get_text(separator=',')
        time.sleep(sleep_time)
        return date, text, kw_location, kw_topic


'''
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
'''

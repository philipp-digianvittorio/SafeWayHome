
# import packages
from bs4 import BeautifulSoup
import re
import requests
import time
import numpy as np

sleep_time = 1.6


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
### -- Presseportal Scraper ---------------------------------------------------------------- ###
################################################################################################

class PresseportalScraper():

    def __init__(self):
        # define base URL
        self.URL_main = 'https://www.presseportal.de/blaulicht/'
        # url for headquarters
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
        if self.robots.check_scrape_permission(self.URL_headquarters):
            request = requests.get(self.URL_headquarters)
            soup = BeautifulSoup(request.text, 'html.parser')
            # find all links on the website
            for tag in soup.findAll("a", href=True):
                if (self.hq_pattern in tag.get("href")) and any(
                        type in tag.get("title") for type in self.headquarter_types):
                    url, id = tag.get("href").rsplit("/", 1)
                    title = re.search(r'[A-Z].*', tag.get("title")).group()
                    headquarters.append({'id': str(id), 'url': url, 'name': title})
                else:
                    next

            return headquarters
        else:
            print("Scraping not allowed according to robots.txt")
            return None


    def get_articles(self, hq_data, max_articles, stop_ids=None, city_names=[]):
        URL_hq_newsroom = self.URL_main + 'nr/' + hq_data["id"]
        if self.robots.check_scrape_permission(URL_hq_newsroom):
            self.articles = list()
            try:
                for i in range(0,max_articles,30):
                    print(str(i) + "/" + str(max_articles))
                    time.sleep(sleep_time)
                    if i == 0:
                        request = requests.get(URL_hq_newsroom)
                    else:
                        request = requests.get(URL_hq_newsroom + f"/{i}")
                    soup = BeautifulSoup(request.text, 'html.parser')
                    # find all links on the website
                    article_urls = [tag for tag in soup.findAll("a", href=True) if self.article_pattern in tag.get("href")]
                    if len(article_urls) > 0:
                        for tag in soup.findAll("a", href=True):
                            if self.article_pattern in tag.get("href"):
                                url, _, id = tag.get("href").rsplit("/", 2)

                                # -- check if stop condition fulfilled
                                if stop_ids and hq_data['id'] + "#" + id in stop_ids:
                                    return articles

                                title = tag.get("title")
                                a = self.scrape_article(self.URL_main + 'pm/' + hq_data['id'] + '/' + str(id), city_names)
                                if a:
                                    articles, date, cities, kw_location, kw_topic = a
                                    for i in range(len(articles)):
                                        self.articles.append({'hq_name': hq_data['name'],
                                                              'hq_id': hq_data['id'],
                                                              'country': 'Deutschland',
                                                              'city': cities[i],
                                                              'headline': articles[i][0],
                                                              'id': id,
                                                              'url': url,
                                                              'date': date,
                                                              'article': articles[i][1],
                                                              'kw_location': kw_location,
                                                              'kw_topic': kw_topic})
                                        print("ok")
                                else:
                                    pass
                            else:
                                pass
                    else:
                        break
            except:
                pass

            return self.articles

        else:
            print("Scraping not allowed according to robots.txt")
            return None


    def scrape_article(self, article_url, city_names=[]):
        if self.robots.check_scrape_permission(article_url):
            request = requests.get(article_url)
            soup = BeautifulSoup(request.text, 'html.parser')

            text = soup.find('article')
            tags = text.find_all("p", {"class": False})
            title = text.find("h1").get_text()

            articles = [(tags[i].get_text(), tags[i + 1].get_text()) for i in range(len(tags) - 1) if
                        (len(tags[i].get_text()) < 100) and (len(tags[i + 1].get_text()) > 300) and not (
                                    "(ots)" in tags[i].get_text()) and (len(tags[i].get_text().strip()))]

            if not articles:
                articles = [(title, " ".join([t.get_text() for t in tags if
                                             not ("(ots)" in t.get_text()) and (len(t.get_text().strip())) > 100]))]
            print(articles)
            '''
            else:
                for a in articles:
                    header = a[0]
                    if any(c in header for c in [": ", " - "]) and not (re.search("^A[0-9]{1,2}", header)):
                        city = header.split(": ")[0].split(" - ")[0].split("(")[0].split("/")[0]
                        print(city, header)
                    else:
                        print("None", header)
            '''
            '''
            text = ""
            for tag in soup.find_all('article')[0]:
                #print(tag)
                for div in tag.find_all("div")[0]:
                    for p in div.find_all("p"):
                        txt = p.get_text(separator=" ")
                        text = text + "#" + txt
            '''
            cities = np.array([None]*len(articles))
            print(cities)
            for city in city_names:
                print(city)
                city_idx = np.where(np.array([city.lower() in a[0].lower() for a in articles]))[0]
                print(city_idx)
                if len(city_idx):
                    cities[city_idx] = city
            #text = soup.find('article').get_text(separator='#')
            date = soup.find('p', class_='date').text.strip()
            kw_location = soup.findAll('ul', class_="tags")[0].get_text(separator=',')
            kw_topic = soup.findAll('ul', class_="tags")[1].get_text(separator=',')
            time.sleep(sleep_time)
            print(articles, date, cities, kw_location, kw_topic)
            return articles, date, cities, kw_location, kw_topic
        else:
            print("Scraping not allowed according to robots.txt")
            return None







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



article_url = "https://www.presseportal.de/blaulicht/pm/4970/5418644"
article_url2 = "https://www.presseportal.de/blaulicht/pm/110976/2867731"
article_url3 = "https://www.presseportal.de/blaulicht/pm/110969/5418702"

request = requests.get(article_url)
soup = BeautifulSoup(request.text, 'html.parser')

date = soup.find('p', class_='date').text.strip()

text = ""
for tag in soup.find_all('article')[0]:
    #print(tag)
    for div in tag.find_all("div")[0]:
        for p in div.find_all("p"):
            txt = p.get_text(separator=" ")
            text = text + "#" + txt


text = soup.find('article')
tags = text.find_all("p", {"class": False})

#[len(t.get_text()) for t in tags if not "(ots)" in t.get_text() and len(t.get_text().strip())]
#[t.get_text() for t in tags if not "(ots)" in t.get_text() and len(t.get_text().strip())]

articles = [(tags[i].get_text(), tags[i+1].get_text()) for i in range(len(tags)-1) if (len(tags[i].get_text()) < 100) and (len(tags[i+1].get_text())>300) and not ("(ots)" in tags[i].get_text()) and (len(tags[i].get_text().strip()))]
if not articles:
    articles = [(None, " ".join([t.get_text() for t in tags if not ("(ots)" in t.get_text()) and (len(t.get_text().strip())) > 100]))]
    print("no city: ")
    print(articles)
else:
    for a in articles:
        header = a[0]
        if any(c in header for c in [": ", " - "]) and not (re.search("^A[0-9]{1,2}", header)):
            city = header.split(": ")[0].split(" - ")[0].split("(")[0].split("/")[0]
            print(city)
        else:
            print("None")





sc = PresseportalScraper()

# -- update headquarter data
headquarters = sc.get_police_headquarters()
articles = []

for hq in headquarters[:3]:
    articles += sc.get_articles(hq, max_articles=30)
#Nachtrag, Pressemitteilung
fra = [x for x in headquarters if "Frankfurt" in x["name"]][0]
articles = sc.get_articles(fra, max_articles=210)
'''



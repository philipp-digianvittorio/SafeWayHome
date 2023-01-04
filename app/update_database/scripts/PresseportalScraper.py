# import packages
from bs4 import BeautifulSoup
import re
import requests
import time

sleep_time = 2


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


    def get_articles(self, hq_data, max_articles, stop_ids=None):
        URL_hq_newsroom = self.URL_main + 'nr/' + hq_data["id"]
        if self.robots.check_scrape_permission(URL_hq_newsroom):
            articles = list()
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
                                a = self.scrape_article(self.URL_main + 'pm/' + hq_data['id'] + '/' + str(id))
                                if a:
                                    date, text, kw_location, kw_topic = a
                                    articles.append({'hq_name': hq_data['name'],
                                                     'hq_id': hq_data['id'],
                                                     'headline': title,
                                                     'id': id,
                                                     'url': url,
                                                     'date': date,
                                                     'article': text,
                                                     'kw_location': kw_location,
                                                     'kw_topic': kw_topic})
                                else:
                                    pass
                            else:
                                next
                    else:
                        break
            except:
                pass

            return articles

        else:
            print("Scraping not allowed according to robots.txt")
            return None


    def scrape_article(self, article_url):
        if self.robots.check_scrape_permission(article_url):
            request = requests.get(article_url)
            soup = BeautifulSoup(request.text, 'html.parser')

            date = soup.find('p', class_='date').text.strip()
            '''
            text = ""
            for tag in soup.find_all('article')[0]:
                #print(tag)
                for div in tag.find_all("div")[0]:
                    for p in div.find_all("p"):
                        txt = p.get_text(separator=" ")
                        text = text + "#" + txt
            '''
            text = soup.find('article').get_text(separator='#')
            kw_location = soup.findAll('ul', class_="tags")[0].get_text(separator=',')
            kw_topic = soup.findAll('ul', class_="tags")[1].get_text(separator=',')
            time.sleep(sleep_time)
            return date, text, kw_location, kw_topic
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
'''

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import numpy as np
import webbrowser
import time
import overpy
from geopy.geocoders import Nominatim
from PIL import Image, ImageGrab
import io
import base64

driver_path = r"update_database\drivers\geckodriver.exe"
firefox_binary = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"

class StreetviewScraper():


    def __init__(self, driver_path=driver_path, wait_seconds=10, download_path=None, headless=False, firefox_binary=None):

        self.driver_path = driver_path
        self.wait_seconds = wait_seconds
        self.download_path = download_path
        self.headless = headless

        if "chromedriver" in driver_path:
            self.options = ChromeOptions()
            self.options.headless = headless  # if true, run browser without window
            self.prefs = {
                'download.default_directory': self.download_path,
                'download.prompt_for_download': False,
                'download.extensions_to_open': 'xml',
                'safebrowsing.enabled': True
            }
            self.options.add_experimental_option('prefs', self.prefs)
            self.options.add_argument("--disable-extensions")
            self.options.add_argument("--safebrowsing-disable-download-protection")
            self.options.add_argument("safebrowsing-disable-extension-blacklist")

        elif "geckodriver" in driver_path:
            self.options = FirefoxOptions()
            self.options.headless = headless  #if true, run browser without window
            self.options.set_preference("browser.download.manager.showAlertOnComplete", False)
            self.options.set_preference("browser.download.alwaysOpenPanel", False)

            if self.download_path:
                self.options.set_preference("browser.download.dir", self.download_path)
                self.options.set_preference("browser.download.folderList", 2)

            if firefox_binary:
                self.options.binary_location = firefox_binary

        elif "msedgedriver" in driver_path:
            self.options = EdgeOptions()
            self.options.headless = headless  # if true, run browser without window

        else:
            print("specified driver not implemented, please use one of the following: 'chromedriver', 'geckodriver', 'msedgedriver'")


    def get_street_names(self, country, city):
        api = overpy.Overpass()

        # Define the query
        query = f'''
                area[name="{city}"];
                way(area)[highway][name];
                out;'''

        # Call the API
        res = api.query(query)

        if res:
            street_names = list(set([way.tags["name"] for way in res.ways]))
            return street_names
        else:
            return []


    def get_lat_lon(self, country, city, street):
        # get coordinates of streets
        try:
            geolocator = Nominatim(user_agent="tutorial")
            location = geolocator.geocode(", ".join([country, city, street]), timeout=3).raw
        except:
            return None, None

        return location["lat"], location["lon"], location['display_name'].split(', ')[-5:-4][0]


    def get_streetview_image(self, latitude, longitude):

        # -- specify driver --------------------------------------------------------------------
        if "chromedriver" in self.driver_path:
            self.service = ChromeService(executable_path=self.driver_path)
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
        elif "geckodriver" in self.driver_path:
            self.service = FirefoxService(executable_path=self.driver_path)
            self.driver = webdriver.Firefox(service=self.service, options=self.options)
        elif "msedgedriver" in self.driver_path:
            self.service = EdgeService(executable_path=self.driver_path)
            self.driver = webdriver.Edge(service=self.service, options=self.options)

        if self.headless:
            self.driver.set_window_size(1920, 1080)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(30)

        self.wait = WebDriverWait(self.driver, self.wait_seconds)

        self.url = f'http://maps.google.com/maps?q=&layer=c&cbll={str(latitude)},{str(longitude)}&cbp=11,0,0,0,0'

        try:
            self.driver.get(self.url)

            link = self.driver.find_elements(By.XPATH, "//span[text()='Alle akzeptieren']")
            print("link", len(link))
            print(self.driver.current_url)

            if len(link) > 0:
                counter = 0
                consent_url = self.driver.current_url
                print("1: ", self.driver.current_url)

                cookie_selection = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Alle akzeptieren']")))
                self.driver.execute_script('arguments[0].click()', cookie_selection)
                _ = self.wait.until(EC.url_changes(consent_url))

                #self.driver.execute_script("window.open('')")
                #self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(self.url)

            _ = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//canvas")))
            time.sleep(10)
            print(_)

            with Image.open(io.BytesIO(base64.b64decode(self.driver.get_screenshot_as_base64()))) as img:
                area = (int(0.2*img.width), # left
                        int(0.2*img.height), # upper
                        int(0.88*img.width), # right
                        int(0.88*img.height)) # lower
                cropped_img = img.crop(area).convert("RGB")
                # -> RGBA to RGB

            blackPxNum = np.count_nonzero([np.asarray(cropped_img) <= 30])/np.asarray(cropped_img).size
            print(blackPxNum)

            time.sleep(1)
            self.driver.close()
            self.driver.quit()

            if blackPxNum > 0.6:
                return None
            else:
                return cropped_img

        except:
            self.driver.close()
            self.driver.quit()
            return None

        # open webbrowser which redirects you to different URL (takes some seconds)
        #webbrowser.open(url)
        #time.sleep(10)

        # take screenshot
        #img = ImageGrab.grab()

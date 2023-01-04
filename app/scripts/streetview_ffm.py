# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 13:08:39 2022
@author: m-bau
"""


import webbrowser
import pandas as pd
import numpy as np
import time
from geopy.geocoders import Nominatim
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from PIL import ImageGrab, Image
import os.path
import math
#%%
path = "C:\\Users\\m-bau\\Dokumente\\Studium\\Master\\3. Semester\\Data Science Project\\webscraping\\"
#%%

# get street names of FFM
url = 'https://www.offenedaten.frankfurt.de/dataset/strassenverzeichnis-der-stadt-frankfurt-am-main/resource/be5982fe-ed79-42f4-acdc-57ca4737fb7a/download/strassenverzeichnis2022.csv'
streetnames = pd.read_csv(url, sep=";", encoding='latin1')
streetnames.shape

# remove duplicate street names
streetnames = streetnames.drop_duplicates(subset=['Straßenname', 'Postleitzahl'], keep='first')
streetnames.index = range(len(streetnames.index))
streetnames.shape

streetnames['Straßenname'] = streetnames['Straßenname'].str.replace('*', '')
streetnames['Address'] = streetnames['Straßenname'] + ' ' + streetnames['Postleitzahl'].astype(str) + ' ' + 'Frankfurt'

# get coordinates of streets
geolocator = Nominatim(user_agent="tutorial")
location = geolocator.geocode(streetnames['Address'][3], timeout=3).raw

#%%
# get coordiantes of street from open street view
df = pd.DataFrame(columns=['Address', 'Latitude', 'Longitude', 'Class', 'Type'])
for a in streetnames['Address']:
    print(a)
    location = geolocator.geocode(a, timeout=3)
    if location is not None:
        df = df.append({'Address': a, 'Latitude': location.latitude, 'Longitude': location.longitude}, ignore_index=True)
    else:
        next

#%%

# merge datas
df = pd.merge(df, streetnames, how='inner', on='Address')



# save data
df.to_csv(path + "ffm.csv", index= False)

#%%
df = pd.read_csv(path + "ffm.csv")
# create subset 

np.random.seed(42)
df = df.sample(frac=1)

survey_streets = pd.DataFrame.sample(df, n=250)
survey_streets['Ortsbezirk'].unique()
survey_streets.index = range(len(survey_streets.index))
#%%
# Scrape pics from Street view
for i in survey_streets.index[100:]:
    # define URL 
    url = 'http://maps.google.com/maps?q=&layer=c&cbll=' + survey_streets.loc[i]['Latitude'].astype(str) + ',' + survey_streets.loc[i]['Longitude'].astype(str) + '&cbp=11,0,0,0,0' 

    # open webbrowser which redirects you to different URL (takes some seconds)
    webbrowser.open(url)
    time.sleep(10)

    # take screenshot and save it
    snapshot = ImageGrab.grab()
    save_path = path + "pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg'
    snapshot.save(save_path)
    

#%%
# Crop screenshots
for i in survey_streets.index[:100]:
    img = Image.open(path + "\\pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg')
    if len(img.fp.read()) > 100000:
        area = (200, # rigth
                350, # upper
                1600, # left
                1200) # lower
        cropped_img = img.crop(area)
        cropped_img.show() 
        save_path = path +"survey_pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg'
        cropped_img.save(save_path)
    else:
            next
            
            
#%%
# manually sort blurred pics

survey_streets['survey'] = 0

for i in survey_streets.index[:100]:
    file = path + "survey_pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg'
    if os.path.isfile(file) is True:
        os.path.isfile(file)
        survey_streets.loc[i,'survey'] = 1

survey_streets_test = survey_streets.loc[survey_streets['survey'] == 1]


# split pics in training and test data
train_data = survey_streets_test.sample(frac=0.6, random_state=25)
test_data = survey_streets_test.drop(train_data.index)
#%%
survey_streets_test['subsample'] = "training"
for i in survey_streets_test.index:
    if i in test_data.index:
        survey_streets_test.loc[i, 'subsample'] = "test"
        img = Image.open(path + "survey_pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg')
        img.save(path + "test\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg')
    else:
        img = Image.open(path + "survey_pics\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg')
        img.save(path + "training\\" + survey_streets.loc[i]['Straßenname'] + '_' + survey_streets.loc[i]['Postleitzahl'].astype(str) + '.jpeg')
  
#%%
# Add street types and classes from OSM
geolocator = Nominatim(user_agent="project", timeout=10)

i = 0
for a in df['Address']:
    location = geolocator.geocode(a, timeout=3)
    if location is not None:
        df.loc[i, 'class'] = location.raw['class']
        df.loc[i, 'type'] = location.raw['osm_type']
    else:
        next
    i = i + 1

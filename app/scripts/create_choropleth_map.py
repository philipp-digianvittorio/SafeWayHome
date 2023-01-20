# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 14:17:37 2023

@author: stell
"""

import webbrowser
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#%%
path = "C:/Users/stell/Documents/Uni/DataScienceProject/SafeWayHome - tryout/webscraping/"
#%%

#%%
df = pd.read_csv(path + "ffm.csv")
df["STTLNAME"] = df["Stadtteil Name"]

import folium
import pandas as pd

# set map zoom to Frankfurt (later replace with location)
osm = folium.Map(location=[50.110446, 8.681968], zoom_start=11)

# colour according to Polizeirevier No. (append Creepinessscore of Stadtteil)
osm.choropleth(
    geo_data = open(path + 'stadtteileFM.geojson').read(),
    data = df,
    columns = ['STTLNAME', 'Polizeirevier'],
    key_on = 'feature.properties.STTLNAME',
    fill_color = 'RdYlGn',
    fill_opacity = 0.3,
)

osm

osm.save("choropleth.html")
webbrowser.open("choropleth.html")

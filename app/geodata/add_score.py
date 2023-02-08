import numpy as np
import pandas as pd
import osmnx as ox
from geopy.geocoders import Nominatim
import geopy.distance
import geopandas as gpd
from shapely.geometry import Point, Polygon

G = ox.graph_from_place('Frankfurt', network_type = 'walk') # download raw geopatial data from OSM

ffm_geojson = gpd.read_file('geodata/stadtteileFM.geojson') # import polygons of districs
parks = gpd.read_file('geodata/parks.json') # import polygons of parks
industrial = gpd.read_file('geodata/industrial.json') # import polygons of industrial areas

# get creeepines score from database


# 
def get_creepiness_score(a, b):
    try:
        creepiness_score = np.mean(db_streets["score_neutral"].loc[db_streets["Straßenname"] == G.edges[(nodea, nodeb, 0)]["name"]])

    # for edges without street name
    except Exception:
        for j, polygon in enumerate(ffm_geojson["geometry"]):
            point = Point(G.nodes[nodea]['x'], G.nodes[nodea]['y'])
            if point.within(polygon):
                creepiness_score = db_district["score_neutral"].loc[ffm_geojson["name"].iloc[j]]

    # for edges with street name not in database
    if pd.isna(creepiness_score):
        for j, polygon in enumerate(ffm_geojson["geometry"]):
            point = Point(G.nodes[nodea]['x'], G.nodes[nodea]['y'])
            if point.within(polygon):
                creepiness_score = db_district["score_neutral"].loc[ffm_geojson["name"].iloc[j]]
    # is edges has still no score            
    if pd.isna(creepiness_score):
        for j, polygon in enumerate(ffm_geojson["geometry"]):
            point = Point(G.nodes[nodeb]['x'], G.nodes[nodeb]['y'])
            dist = polygon.distance(point)
            if point.within(polygon):
                creepiness_score = db_district["score_neutral"].loc[ffm_geojson["name"].iloc[j]]
   
                
    # check whether edge is within a park
    for j, polygon in enumerate(parks["geometry"]):
            point = Point(G.nodes[nodea]['x'], G.nodes[nodea]['y'])
            if point.within(polygon):
                creepiness_score = creepiness_score + 1
   # check whether edge is within a industrial area
    for j, polygon in enumerate(industrial["geometry"]):
            point = Point(G.nodes[nodea]['x'], G.nodes[nodea]['y'])
            if point.within(polygon):
                creepiness_score = creepiness_score + 1

    
    return creepiness_score


n_edges = len(list(G.edges(data=True))) 

# loop over all edges 
for i in range(n_edges):
    
    nodea, nodeb = list(G.edges(data=True))[i][0:2]
    creepiness_score = get_creepiness_score(nodea, nodeb)   
    G.edges[(nodea, nodeb, 0)]["score"] = creepiness_score
    

ox.save_graphml(G, 'geodata/frankfurt_weighted.osm')
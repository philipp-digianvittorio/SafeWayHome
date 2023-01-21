import pandas as pd
import numpy as np
import mapclassify as mc
import matplotlib.pyplot as plt

from pyrosm.data import sources
from pyrosm import OSM, get_data
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.lines import Line2D

import osmnx as ox
import networkx as nx
import plotly.graph_objects as go

import taxicab as tc
import geopy.distance

import random

# define origin and destination
orig = (50.110446, 8.681968) # Römer
dest = (50.115452, 8.671515) # Oper

# compute middle and distance to origin
m = np.mean([orig,dest], axis = 0)

# compute distance in kilometers
radius = geopy.distance.geodesic(orig,m).m + 500  # add 500m 

# get geospatial data for area of route
G = ox.graph_from_point(orig, dist=radius, network_type='walk')
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

# compute shortest path with respect to distance
route_short = tc.shortest_path(G, orig, dest)

## Weight length of nodes
# G consist of edges and nodes. We need to multiply the length of each edge with the creepiness core of the respective street. Edges without a street names are skipped (for now). Computation takes some time.

path = "C:\\Users\\m-bau\\Dokumente\\Studium\\Master\\3. Semester\\Data Science Project\\webscraping\\"
streets = pd.read_csv(path + "ffm.csv")

# create random score to test code to test code -> has to be replaced by true creepinessscore
streets['score'] = np.random.randint(1, 6, streets.shape[0]) 


# get number of edges within radius
n_edges = len(list(G.edges(data=True)))

# loop over all edges 
for i in range(0,n_edges):
    nodea = list(G.edges(data=True))[i][0] # get start node
    nodeb = list(G.edges(data=True))[i][1] # get end node
    
    
    try:
        #print(i)
        #print(G.edges[(nodea, nodeb, 0)]["name"])
        name = G.edges[(nodea, nodeb, 0)]["name"]
        creepiness_score = streets["score"].loc[streets["Straßenname"] == G.edges[(nodea, nodeb, 0)]["name"]]
        
        # in case of duplicates choose first element
        #G.edges[(nodea, nodeb, 0)]["score"] = G.edges[(nodea, nodeb, 0)]["length"] * creepiness_score.iloc[0]
        G.edges[(nodea, nodeb, 0)]["score"] = creepiness_score.iloc[0]
        G.edges[(nodea, nodeb, 0)]["length"] = G.edges[(nodea, nodeb, 0)]["length"] * creepiness_score.iloc[0]
        
    except Exception:
        pass
    
# compute shortest path with respect to safety with manipulated data
route_safe = tc.shortest_path(G, orig, dest)


# check whether routes are indentical
route_safe == route_short


# Plot routes using plot_path function
# extend plot_path fucntion such that is plots two route instead of one
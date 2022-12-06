'''
This file plots a map showing the shortest and safest route from a start node 
to a destination node
'''
import numpy as np
import osmnx as ox
import taxicab as tc
import networkx as nx
import plotly.graph_objects as go
import plotly.io as io
io.renderers.default='browser'

# define start and destination
# optimally taken from website
start = (50.110446, 8.681968) # Römer #{{}}
destination = (50.115452, 8.671515) # Oper #{{}}

# get OSM data around the start point
G = ox.graph_from_point(start, dist=3000, network_type='walk')
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

# calculate shortest route using taxicab package
route = tc.distance.shortest_path(G, start, destination)

# remove distance from route
route_nodes = list(route)
route_nodes = route_nodes[1]

# function that Given a list of latitudes and longitudes, origin and destination point, plots a path on a map
def plot_route(lat, long, origin_node, destination_node):
    
    # adding the lines joining the nodes on the shortest way
    fig = go.Figure(go.Scattermapbox(
        name = "Schnellster Weg",
        mode = "lines",
        lon = long,
        lat = lat,
        marker = {'size': 10},
        line = dict(width = 4.5, color = '#FB607F')))
    
    # adding marker for starting node
    fig.add_trace(go.Scattermapbox(
        name = "Start",
        mode = "markers",
        lon = [origin_node[1]],
        lat = [origin_node[0]],
        marker = {'size': 12, 'color':"red"}))
     
    # adding marker for destination node
    fig.add_trace(go.Scattermapbox(
        name = "Ziel",
        mode = "markers",
        lon = [destination_node[1]],
        lat = [destination_node[0]],
        marker = {'size': 12, 'color':'#E4717A'}))
    
    # getting center for plots:
    lat_center = np.mean(lat)
    long_center = np.mean(long)
    
    # defining the layout using mapbox_style
    fig.update_layout(mapbox_style="stamen-terrain",
        mapbox_center_lat = 30, mapbox_center_lon=-80,
        width=1000, height=500)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      mapbox = {
                          'center': {'lat': lat_center, 
                          'lon': long_center},
                          'zoom': 13})
    fig.show() # function return a map

# function returning the route as lines connecting the list of nodes 
def node_list_to_path_short(G, node_list):
    
    # firste element contain all but the last node, second one contains all but first node
    edge_nodes = list(zip(node_list[:-1], node_list[1:])) 
    
    lines = []
    for u, v in edge_nodes:
        # if there are parallel edges, select the shortest in length
        data = min(G.get_edge_data(u, v).values(), 
                   key=lambda x: x['length'])
        # if it has a geometry attribute
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute,
            # then the edge is a straight line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)
    return lines

# getting the list of coordinates from the route 
lines = node_list_to_path_short(G, route_nodes)
long2 = []
lat2 = []
for i in range(len(lines)):
    z = list(lines[i])
    l1 = list(list(zip(*z))[0])
    l2 = list(list(zip(*z))[1])
    for j in range(len(l1)):
        long2.append(l1[j])
        lat2.append(l2[j])


plot_route(lat2, long2, start, destination)

io.renderers.default='svg'
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
import json
import plotly
import plotly.express as px
    #io.renderers.default='browser'

    #define start and destination
    #optimally taken from website
#start = (50.110446, 8.681968) # Römer #{{}}
#destination = (50.115452, 8.671515) # Oper #{{}}

    # get OSM data around the start point
#G = ox.graph_from_point(start, dist=3000, network_type='walk')
#G = ox.speed.add_edge_speeds(G)
#G = ox.speed.add_edge_travel_times(G)

    # calculate shortest route using taxicab package
#route = tc.distance.shortest_path(G, start, destination)

    # remove distance from route
#route_nodes = list(route)
#route_nodes = route_nodes[1]

    # function that Given a list of latitudes and longitudes, origin and destination point, plots a path on a map

# Use compute_line_string(), get_edge_geometry() and compute_taxi_length() from https://github.com/nathanrooy/taxicab.
# Then, rewrite shortest_path() function to get_best_path() function.
def compute_linestring_length(ls):
    '''
    Computes the length of a partial edge (shapely linesting)

    Parameters
    ----------
    ls : shapely.geometry.linestring.LineString
    Returns
    -------
    float : partial edge length distance in meters
    '''
    from shapely.geometry import LineString

    if type(ls) == LineString:
        x, y = zip(*ls.coords)

        dist = 0
        for i in range(0, len(x) - 1):
            dist += ox.distance.great_circle_vec(y[i], x[i], y[i + 1], x[i + 1])
        return dist
    else:
        return None


def get_edge_geometry(G, edge):
    '''
    Retrieve the points that make up a given edge.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    edge : tuple
        graph edge unique identifier as a tuple: (u, v, key)

    Returns
    -------
    list :
        ordered list of (lng, lat) points.

    Notes
    -----
    In the event that the 'geometry' key does not exist within the
    OSM graph for the edge in question, it is assumed then that
    the current edge is just a straight line. This results in an
    automatic assignment of edge end points.
    '''
    from shapely.geometry import LineString

    if G.edges.get(edge, 0):
        if G.edges[edge].get('geometry', 0):
            return G.edges[edge]['geometry']

    if G.edges.get((edge[1], edge[0], 0), 0):
        if G.edges[(edge[1], edge[0], 0)].get('geometry', 0):
            return G.edges[(edge[1], edge[0], 0)]['geometry']

    return LineString([
        (G.nodes[edge[0]]['x'], G.nodes[edge[0]]['y']),
        (G.nodes[edge[1]]['x'], G.nodes[edge[1]]['y'])])


def compute_taxi_length(G, nx_route, orig_partial_edge, dest_partial_edge):
    '''
    Computes the route complete taxi route length
    '''
    from osmnx.utils_graph import get_route_edge_attributes

    dist = 0
    if nx_route:
        dist += sum(get_route_edge_attributes(G, nx_route, 'length'))
    if orig_partial_edge:
        dist += compute_linestring_length(orig_partial_edge)
    if dest_partial_edge:
        dist += compute_linestring_length(dest_partial_edge)
    return dist


def get_best_path(G, orig_yx, dest_yx, weight, orig_edge=None, dest_edge=None):
    '''
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    orig_yx : tuple
        the (lat, lng) or (y, x) point representing the origin of the path
    dest_yx : tuple
        the (lat, lng) or (y, x) point representing the destination of the path

    Returns
    -------
    tuple
        (route_dist, route, orig_edge_p, dest_edge_p)
    '''
    import networkx as nx
    from shapely.geometry import Point
    from shapely.geometry import LineString
    from shapely.ops import substring
    from osmnx import nearest_edges


    # determine nearest edges
    if not orig_edge: orig_edge = ox.nearest_edges(G, orig_yx[1], orig_yx[0])
    if not dest_edge: dest_edge = ox.nearest_edges(G, dest_yx[1], dest_yx[0])


    # routing along same edge
    if orig_edge == dest_edge:
        p_o, p_d = Point(orig_yx[::-1]), Point(dest_yx[::-1])
        edge_geo = G.edges[orig_edge]['geometry']
        orig_clip = edge_geo.project(p_o, normalized=True)
        dest_clip = edge_geo.project(p_d, normalized=True)
        orig_partial_edge = substring(edge_geo, orig_clip, dest_clip, normalized=True)
        dest_partial_edge = []
        nx_route = []

    # routing across multiple edges
    else:
        nx_route = nx.shortest_path(G, orig_edge[0], dest_edge[0], weight)
        p_o, p_d = Point(orig_yx[::-1]), Point(dest_yx[::-1])
        orig_geo = get_edge_geometry(G, orig_edge)
        dest_geo = get_edge_geometry(G, dest_edge)

        orig_clip = orig_geo.project(p_o, normalized=True)
        dest_clip = dest_geo.project(p_d, normalized=True)

        orig_partial_edge_1 = substring(orig_geo, orig_clip, 1, normalized=True)
        orig_partial_edge_2 = substring(orig_geo, 0, orig_clip, normalized=True)
        dest_partial_edge_1 = substring(dest_geo, dest_clip, 1, normalized=True)
        dest_partial_edge_2 = substring(dest_geo, 0, dest_clip, normalized=True)

        # when the nx route is just a single node, this is a bit of an edge case
        if len(nx_route) <= 2:
            nx_route = []
            if orig_partial_edge_1.intersects(dest_partial_edge_1):
                orig_partial_edge = orig_partial_edge_1
                dest_partial_edge = dest_partial_edge_1

            if orig_partial_edge_1.intersects(dest_partial_edge_2):
                orig_partial_edge = orig_partial_edge_1
                dest_partial_edge = dest_partial_edge_2

            if orig_partial_edge_2.intersects(dest_partial_edge_1):
                orig_partial_edge = orig_partial_edge_2
                dest_partial_edge = dest_partial_edge_1

            if orig_partial_edge_2.intersects(dest_partial_edge_2):
                orig_partial_edge = orig_partial_edge_2
                dest_partial_edge = dest_partial_edge_2

        # when routing across two or more edges
        if len(nx_route) >= 3:

            ### resolve origin

            # check overlap with first route edge
            route_orig_edge = get_edge_geometry(G, (nx_route[0], nx_route[1], 0))
            if route_orig_edge.intersects(orig_partial_edge_1) and route_orig_edge.intersects(orig_partial_edge_2):
                nx_route = nx_route[1:]

            # determine which origin partial edge to use
            route_orig_edge = get_edge_geometry(G, (nx_route[0], nx_route[1], 0))
            if route_orig_edge.intersects(orig_partial_edge_1):
                orig_partial_edge = orig_partial_edge_1
            else:
                orig_partial_edge = orig_partial_edge_2

            ### resolve destination

            # check overlap with last route edge
            route_dest_edge = get_edge_geometry(G, (nx_route[-2], nx_route[-1], 0))
            if route_dest_edge.intersects(dest_partial_edge_1) and route_dest_edge.intersects(dest_partial_edge_2):
                nx_route = nx_route[:-1]

            # determine which destination partial edge to use
            route_dest_edge = get_edge_geometry(G, (nx_route[-2], nx_route[-1], 0))
            if route_dest_edge.intersects(dest_partial_edge_1):
                dest_partial_edge = dest_partial_edge_1
            else:
                dest_partial_edge = dest_partial_edge_2

    # final check
    if orig_partial_edge:
        if len(orig_partial_edge.coords) <= 1:
            orig_partial_edge = []
    if dest_partial_edge:
        if len(dest_partial_edge.coords) <= 1:
            dest_partial_edge = []

    # compute total path length
    route_dist = compute_taxi_length(G, nx_route, orig_partial_edge, dest_partial_edge)

    return route_dist, nx_route, orig_partial_edge, dest_partial_edge

def plot_path(lat1, lon1, lat2, lon2):
    """
    Given a list of latitudes and longitudes, origin
    and destination point, plots a path on a map

    Parameters
    ----------
    lat1, long1: list of latitudes and longitudes for shortest path
    lat2, long2: list of latitudes and longitudes for safest path
    origin_point, destination_point: co-ordinates of origin
    and destination
    Returns
    -------
    Nothing. Only shows the map.
    """

    # add the lines joining the nodes for the shortest path
    fig = go.Figure(go.Scattermapbox(
        name="Shortest Route",
        mode="lines",
        lon=lon1,
        lat=lat1,
        marker={'size': 10},
        line=dict(width=2, color='#e62020')))

    # add the lines joining the nodes for the safest path
    fig.add_trace(go.Scattermapbox(
        name="Safest Route",
        mode="lines",
        lon=lon2,
        lat=lat2,
        marker={'size': 10},
        line=dict(width=2, color='#000080')))

    # adding destination marker
    fig.add_trace(go.Scattermapbox(
        name="Destination",
        mode="markers",
        lon=[lon1[-1]],
        lat=[lat1[-1]],
        marker={'size': 12, 'color': 'red'}))

    # adding source marker
    fig.add_trace(go.Scattermapbox(
        name="Start",
        mode="markers",
        lon=[lon1[0]],
        lat=[lat1[0]],
        marker={'size': 12, 'color': "#2F4F4F"}))

    # define hover
    hovertemp = "<b>Creepiness Score: </b> coming soon <br>"
    hovertemp += "<b>Distance: </b> coming soo too <br>"
    fig.update_traces(hovertemplate=hovertemp)

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=13
        )
    )

    # getting center for plots:
    lat_center = np.mean(lat1)
    long_center = np.mean(lon1)

    # defining the layout using mapbox_style
    fig.update_layout(mapbox_style="open-street-map",
                      mapbox_center_lat=30, mapbox_center_lon=-80,
                      width=1000, height=500)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox={
                          'center': {'lat': lat_center,
                                     'lon': long_center},
                          'zoom': 14})
    fig.update_layout(legend_traceorder="reversed")
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        orientation="h",
        bgcolor='rgba(255,250,250,0.7)'))
    fig.show()

    return fig
    # plot_route(lat2, long2, start, destination)

    # function returning the route as lines connecting the list of nodes 
def node_list_to_path(G, route):
    """
    Given a route containing a list of nodes, this function creates
    a list of longitude and latitude which can be plotted.

    Parameters
    ----------
    G: geospatial data
    route: taxicab route containing list of nodes and partial edges

    Returns
    -------
    Two list of longitude and latitude
    """

    node_list = route[1]

    edge_nodes = list(zip(node_list[:-1], node_list[
                                          1:]))  # first element contain all but the last node, second one contains all but first node
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

    # extract partial edges at start and destination
    try:
        x1, y1 = zip(*route[2].coords)
        x2, y2 = zip(*route[3].coords)
    except Exception:
        pass

    lon = []
    lat = []
    # add partial edge at start
    lon.append(x1[-1])
    lat.append(y1[-1])

    # add route
    for i in range(len(lines)):
        z = list(lines[i])
        l1 = list(list(zip(*z))[0])
        l2 = list(list(zip(*z))[1])
        for j in range(len(l1)):
            lon.append(l1[j])
            lat.append(l2[j])
    # add partial edge at destination
    lon.append(x2[0])
    lat.append(y2[0])

    return lon, lat

    # getting the list of coordinates from the route 
#lines = node_list_to_path_short(G, route_nodes)
#long2 = []
#lat2 = []
#for i in range(len(lines)):
#        z = list(lines[i])
#        l1 = list(list(zip(*z))[0])
#        l2 = list(list(zip(*z))[1])
#        for j in range(len(l1)):
#            long2.append(l1[j])
#            lat2.append(l2[j])


    #plot_route(lat2, long2, start, destination)
    
    #io.renderers.default='svg'
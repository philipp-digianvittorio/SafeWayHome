
# pip install flask==2.1.3
# pip install -U werkzeug==2.2.2
# pip install flask-reuploaded
# pip install flask-wtf
# pip install wtforms

# pip install flask-sqlalchemy
# pip install sqlalchemy

# -- import flask modules
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import SubmitField


# -- import database modules
from sqlalchemy import inspect, or_, and_
from scripts.FlaskDataBase import db, initialize_database, create_database_mysql, db_select, db_insert, Headquarters, Nodes, Edges, drop_database_mysql, mysql_pw

# -- import additional scripts
from settings import DATABASE_URL
from update_database.scripts.PresseportalScraper import PresseportalScraper

# -- import plot modules
import json
#import plotly
import osmnx as ox
import numpy as np
import pandas as pd
#import taxicab as tc
#from scripts.OSMConnection import get_police_coords

#from scripts.compute_plot_route import plot_route, node_list_to_path_short
#io.renderers.default='browser'


from geopy.geocoders import Nominatim
import geopy.distance
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely import wkt

from scripts.compute_plot_route import compute_linestring_length, get_edge_geometry, compute_taxi_length, \
    get_best_path, plot_path, node_list_to_path, get_creepiness_score


def get_lat_lon(address):
    # get coordinates of streets
    try:
        geolocator = Nominatim(user_agent="tutorial")
        location = geolocator.geocode(address, timeout=3).raw
    except:
        return None, None, None

    return location["lat"], location["lon"], location['display_name'].split(', ')[-5:-4][0]


# -- Initialize App ----------------------------------------------------------------------------
app = Flask(__name__)


# -- Add Database Connection -------------------------------------------------------------------
#db_name = "db_name"  # "mysql_db"
db_name = "mysql_db"
# -- initialize sqlite database
#initialize_database(app=app, db_uri=DATABASE_URL)

# -- initialize mysql database
#drop_database_mysql(db_name, host="localhost", user="root", pw=mysql_pw)
create_database_mysql(name=db_name)  # mysql
initialize_database(app=app, db_uri=DATABASE_URL)  # mysql

print(inspect(db.engine).get_table_names())


# -- Configure App -----------------------------------------------------------------------------
app.config["SECRET_KEY"] = "slafnlanlskjfkjafkjebfkjjkebfpqfeh3737664aiq4893hckcqb"


################################################################################################
### -- Define FlaskForms ------------------------------------------------------------------- ###
################################################################################################

# -- Database Form -----------------------------------------------------------------------------
class DataBaseForm(FlaskForm):

	submit = SubmitField("Load Database Data")




################################################################################################
### -- Define App Routes ------------------------------------------------------------------- ###
################################################################################################


# -- Home Route --------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def my_func():
    if request.method == "POST":

        print(request.form)

        start_coords, dest_coords = None, None
        # -- get destination coordinates
        if request.form["destination_loc"] != "":
            print(request.form["destination_loc"])
            dest_coords = [float(x) for x in get_lat_lon(request.form["destination_loc"])[:2]]

        # -- get start coordinates
        if (request.form["start_loc"] == "Mein Standort") and (request.form["user_position"] != ""):
            start_coords = [float(x) for x in request.form["user_position"].split(",")]
        elif (request.form["start_loc"] != "Mein Standort") and (request.form["start_loc"] != ""):
            start_coords =[float(x) for x in get_lat_lon(request.form["start_loc"])[:2]]

        if start_coords and dest_coords:
            valid_coords = True
        else:
            valid_coords = False

        route = {"start_coords": start_coords,
                 "dest_coords": dest_coords,
                 "valid_coords": valid_coords}

        route = json.dumps(route)
        grid = json.dumps({})

        # -- nodes and edges -----------------------------------------------------
        pad = 0.000005
        nodes_filters = (Nodes.y <= max(start_coords[0], dest_coords[0]) + pad,
                         Nodes.y >= min(start_coords[0], dest_coords[0]) - pad,
                         Nodes.x <= max(start_coords[1], dest_coords[1]) + pad,
                         Nodes.x >= min(start_coords[1], dest_coords[1]) - pad,
                         )

        db_nodes = db_select("Nodes", filters=nodes_filters)
        nodes = gpd.GeoDataFrame(db_nodes).set_index(["osmid"])

        edges_filters = (Edges.u.in_(nodes.index.unique().values.tolist()) & Edges.v.in_(nodes.index.unique().values.tolist()),
                         )

        db_edges = db_select("Edges", filters=edges_filters)

        edges = gpd.GeoDataFrame(db_edges).set_index(["u", "v", "key"])
        edges["geometry"] = edges["geometry"].apply(lambda x: wkt.loads(x))
        edges = gpd.GeoDataFrame(edges).set_crs("epsg:4326")

        G = ox.graph_from_gdfs(nodes, edges)

        start_edge = ox.nearest_edges(G, start_coords[1], start_coords[0])
        dest_edge = ox.nearest_edges(G, dest_coords[1], dest_coords[0])

        path_safe = nx.shortest_path(G, start_edge[0], dest_edge[0], weight='weight_neutral')
        path_short = nx.shortest_path(G, start_edge[0], dest_edge[0], weight='length')

        edge_nodes_safe = list(zip(path_safe[:-1], path_safe[1:], [0]*(len(path_safe)-1)))
        edge_nodes_short = list(zip(path_short[:-1], path_short[1:], [0] * (len(path_short) - 1)))

        lat_long_safe = [i for li in edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_safe, "lat_long"].apply(lambda x: [(float(y.split(" ")[0]), float(y.split(" ")[1])) for y in x.split(", ")]).values.tolist() for i in li[:-1]]
        lat_long_short = [i for li in edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_short, "lat_long"].apply(lambda x: [(float(y.split(" ")[0]), float(y.split(" ")[1])) for y in x.split(", ")]).values.tolist() for i in li[:-1]]

        lat_long_safe.insert(0, start_coords)
        lat_long_safe.append(dest_coords)

        lat_long_short.insert(0, start_coords)
        lat_long_short.append(dest_coords)

        print(lat_long_safe)
        print(lat_long_short)

        return render_template('index.html', valid_coords=valid_coords, route=route, grid=grid, safe_route=json.dumps(lat_long_safe), short_route=json.dumps(lat_long_short))

    else:
        route = json.dumps({"start_coords": "NA",
                             "dest_coords": "NA",
                             "valid_coords": False})
        grid = json.dumps({})
        valid_coords = False

        # Render the input form
        return render_template('index.html', valid_coords=valid_coords, route=route, grid=grid, safe_route=json.dumps([]), short_route=json.dumps([]))

'''
# -- Plotly Testpage ------------------------------------------------------------------------
@app.route("/map", methods=["GET", "POST"])
def plotly_plot():
    # Include plot
    orig = (50.110446, 8.681968) # Römer #{{}}
    dest = (50.115452, 8.671515) # Oper #{{}}

    # compute middle and distance to origin
    m = np.mean([orig, dest], axis=0)

    # compute distance in kilometers
    radius = geopy.distance.geodesic(orig, m).m + 100  # add 100m

    # get OSM data around the start point
    G = ox.graph_from_point(m, dist=radius, network_type='walk')

    # get number of edges within radius
    n_edges = len(list(G.edges(data=True)))

    # get street from database
    db_streets = pd.DataFrame(db_select("Streets"))
    db_district = db_streets.groupby(['district']).agg("mean")

    # read in json file for district allocation
    ffm_geojson = gpd.read_file('geodata/districts.json')
    list(G.edges(data=True))[0][0:2]
    # loop over all edges
    for i in range(0, n_edges):
        nodea, nodeb = list(G.edges(data=True))[i][0:2]
        # may cause problems with districts as they are not yet in database
        creepiness_score = get_creepiness_score(nodea, nodeb)
        G.edges[(nodea, nodeb, 0)]["score"] = creepiness_score

    route_short = get_best_path(G, orig, dest, 'length')
    route_safe = get_best_path(G, orig, dest, 'score')

    lon_short, lat_short = node_list_to_path(G, route_short)
    lon_safe, lat_safe = node_list_to_path(G, route_safe)

    fig = plot_path(lat_short, lon_short, lat_safe, lon_safe)

    #fig = plot_route(lat2, long2, start, destination)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON=graphJSON)

'''
# -- Database Route ----------------------------------------------------------------------------
@app.route("/database", methods=["GET", "POST"])
def upload():
	if request.method == "POST":
		pass
	########################################################################################
	### -- Update Database ------------------------------------------------------------- ###
	########################################################################################

	else:
		pass
	# code here
	if len(db_select("Articles")) == 0:
		sc = PresseportalScraper()
		hq = sc.get_police_headquarters()
		articles = sc.get_articles(hq[89], max_articles=30)
		res = db_insert("Headquarters", hq)
		res = db_insert("Articles", articles)
		flash("Data scraped successfully", "info")
	db_articles = db_select("Articles")
	#db_articles = [{"title": "title 1", "text": "blad ajdnfa wjf weonf oawefw o "}, {"title": "title 2", "text": "blad ajdnfa wjf weonf oawefw o "}]
	return render_template("database.html", db_articles = db_articles)


# -- About Route -------------------------------------------------------------------------------
@app.route("/about", methods=["GET", "POST"])
def about():
	#form=DatabaseForm()
	form = None
	return render_template("about.html", form=form)


# -- Code Route --------------------------------------------------------------------------------
@app.route("/code", methods=["GET", "POST"])
def getcode():
	#form=DatabaseForm()
	form = None
	return render_template("getcode.html", form=form)


# -- Imprint Route -----------------------------------------------------------------------------
@app.route("/imprint", methods=["GET", "POST"])
def imprint():
	#form=DatabaseForm()
	form = None
	return render_template("imprint.html", form=form)

################################################################################################
### -- Run the App ------------------------------------------------------------------------- ###
################################################################################################
if __name__ == "__main__":
    app.run(debug=False)









'''

        # -- grid for crime rectangles ------------------------------------------------
        db_streets = db_select("Streets")

        streets_df = pd.DataFrame({"id": [s["id"] for s in db_streets],
                                   "city": [s["city"] for s in db_streets],
                                   "street": [s["street"] for s in db_streets],
                                   "lat": [float(s["lat"]) for s in db_streets],
                                   "long": [float(s["long"]) for s in db_streets]})

        grid_size = 20
        pad_size = 0.00000001

        lat_grid = np.linspace(streets_df["lat"].min() - pad_size, streets_df["lat"].max() + pad_size, grid_size + 1)
        lat_diff = ((lat_grid.reshape(1, -1) - streets_df["lat"].values.reshape(-1, 1)) < 0).astype(int)
        lat_grid_idx = np.where(lat_diff[:, :-1] - lat_diff[:, 1:])[1]

        long_grid = np.linspace(streets_df["long"].min() - pad_size, streets_df["long"].max() + pad_size, grid_size + 1)
        long_diff = ((long_grid.reshape(1, -1) - streets_df["long"].values.reshape(-1, 1)) < 0).astype(int)
        long_grid_idx = np.where(long_diff[:, :-1] - long_diff[:, 1:])[1]

        streets_df["lat_grid_idx"], streets_df["long_grid_idx"] = lat_grid_idx, long_grid_idx
        streets_df["crime_deviation"] = np.random.uniform(0, 5, len(streets_df))
        streets_df["crime_score"] = 0.0

        def create_color_gradient(c1, c2, n):
            r = np.linspace(c1[0], c2[0], n).astype(int)
            g = np.linspace(c1[1], c2[1], n).astype(int)
            b = np.linspace(c1[2], c2[2], n).astype(int)
            return list(zip(r, g, b))

        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)

        c1 = (179, 253, 255)  # light blue
        c2 = (135, 23, 23)  # red
        n = 51

        color_gradients = [rgb_to_hex(*c) for c in create_color_gradient(c1, c2, n)]
        color_mapper = dict(zip(np.arange(0.0, 5.1, 0.1).round(1), color_gradients))

        window_size = 3
        padding = 1
        crime_grid = np.zeros((grid_size, grid_size))

        grid_lines = list()

        for lat_idx in range(grid_size):
            for long_idx in range(grid_size):
                in_lat = ((streets_df["lat_grid_idx"] >= lat_idx - 1) * (
                            streets_df["lat_grid_idx"] <= lat_idx + 1)).astype(bool)
                in_long = ((streets_df["long_grid_idx"] >= long_idx - 1) * (
                            streets_df["long_grid_idx"] <= long_idx + 1)).astype(bool)
                crime_score = round(streets_df[(in_lat) & (in_long)]["crime_deviation"].mean(), 1)
                if pd.isnull(crime_score):
                    crime_score = 0.0
                color = color_mapper[crime_score]
                crime_grid[lat_idx, long_idx] = crime_score
                streets_df.loc[(streets_df["lat_grid_idx"] == lat_idx) & (
                            streets_df["long_grid_idx"] == long_idx), "crime_score"] = crime_score
                streets_df.loc[(streets_df["lat_grid_idx"] == lat_idx) & (
                            streets_df["long_grid_idx"] == long_idx), "color"] = color
                grid_lines.append(
                    {"lat_min": lat_grid[lat_idx],
                     "lat_max": lat_grid[lat_idx + 1],
                     "long_min": long_grid[long_idx],
                     "long_max": long_grid[long_idx + 1],
                     "crime_score": crime_score,
                     "color": color})








# -- Home Route --------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def my_func():
    if request.method == "POST":
        print(request.form)
        # Get shops data from OpenStreetMap
        polices = get_police_coords(request.form["lat"], request.form["lon"])

        # Initialize variables
        id_counter = 0
        markers = ''
        for node in polices.nodes:

            # Create unique ID for each marker
            idd = 'pol' + str(id_counter)
            id_counter += 1


            # Create the marker and its pop-up for each shop
            markers += "var {idd} = L.marker([{latitude}, {longitude}]);\
                        {idd}.addTo(map);".format(idd=idd, latitude=node.lat,\
                                                                                     longitude=node.lon)



        return render_template('results.html', markers=markers, lat=request.form["lat"], lon=request.form["lon"])

    else:
          
        # Render the input form
        return render_template('index.html')

'''
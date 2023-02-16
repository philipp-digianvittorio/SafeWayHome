
# pip install flask==2.1.3
# pip install -U werkzeug==2.2.2
# pip install flask-reuploaded
# pip install flask-wtf
# pip install wtforms

# pip install flask-sqlalchemy
# pip install sqlalchemy

# -- import flask modules
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField

# -- import database modules
from sqlalchemy import inspect
from scripts.FlaskDataBase import db, drop_database_mysql, initialize_database, create_database_mysql, db_select, db_update, Nodes, Edges

# -- import additional scripts
from settings import DATABASE_URL
from scripts.GeoDataProcessing import get_lat_lon, db_to_graph, get_creepiness_score


# -- import plot modules
import json
import plotly
import numpy as np
import pandas as pd

import geopy.distance
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely import wkt


# -- Initialize App ----------------------------------------------------------------------------
app = Flask(__name__)


# -- Add Database Connection -------------------------------------------------------------------
#db_name = "db_name"  # "mysql_db"
db_name = "mysql_db"
# -- initialize sqlite database
#initialize_database(app=app, db_uri=DATABASE_URL)

# -- initialize mysql database
#drop_database_mysql(db_name, host="localhost", user="root", pw="celestial09#")
create_database_mysql(name=db_name)  # mysql
initialize_database(app=app, db_uri=DATABASE_URL)  # mysql

print(inspect(db.engine).get_table_names())


# -- Configure App -----------------------------------------------------------------------------
app.config["SECRET_KEY"] = "slafnlanlskjfkjafkjebfkjjkebfpqfeh3737664aiq4893hckcqb"


################################################################################################
### -- Define Global Variables ------------------------------------------------------------- ###
################################################################################################
PERCEPTION_WEIGHT = (1/3)
INCLUDE_PARK = True
INCLUDE_INDUSTRIAL = True


################################################################################################
### -- Define App Routes ------------------------------------------------------------------- ###
################################################################################################


# -- Home Route --------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def render_home():
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

        # -- grid lines ----------------------------------------------------------


        # -- nodes and edges -----------------------------------------------------

        m = np.mean([start_coords, dest_coords], axis=0)
        radius = abs(start_coords - m).max()
        pad = 0.001
        max_coords, min_coords = m + radius + pad, m - radius - pad

        nodes_filters = (Nodes.y <= max_coords[0],
                         Nodes.y >= min_coords[0],
                         Nodes.x <= max_coords[1],
                         Nodes.x >= min_coords[1],
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

        path_safe = ox.shortest_path(G, start_edge[0], dest_edge[1], weight='weight_neutral')
        path_short = ox.shortest_path(G, start_edge[0], dest_edge[1], weight='length')

        edge_nodes_safe = list(zip(path_safe[:-1], path_safe[1:], [0]*(len(path_safe)-1)))
        edge_nodes_short = list(zip(path_short[:-1], path_short[1:], [0] * (len(path_short) - 1)))

        lat_long_safe = [i for li in edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_safe, "lat_long"].apply(lambda x: [(float(y.split(" ")[0]), float(y.split(" ")[1])) for y in x.split(", ")]).values.tolist() for i in li[:-1]]
        lat_long_short = [i for li in edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_short, "lat_long"].apply(lambda x: [(float(y.split(" ")[0]), float(y.split(" ")[1])) for y in x.split(", ")]).values.tolist() for i in li[:-1]]

        lat_long_safe.insert(0, start_coords)
        lat_long_safe.append(dest_coords)

        lat_long_short.insert(0, start_coords)
        lat_long_short.append(dest_coords)

        short_length = edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_short, "length"].sum()
        safe_length = edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_safe, "length"].sum()

        short_score = edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_short, "weight_neutral"].sum()/short_length
        safe_score = edges[~edges.index.duplicated(keep='first')].loc[edge_nodes_safe, "weight_neutral"].sum()/safe_length

        params = {"short_length": round(short_length/1000,1),
                  "short_duration": int(round(((short_length/1000)/3)*60,0)),
                  "short_score": round(short_score,1),
                  "safe_length": round(safe_length/1000,1),
                  "safe_duration": int(round(((safe_length/1000)/3)*60,0)),
                  "safe_score": round(safe_score,1)}


        # -- compute mean crime score per grid ----------------------------------------------------
        edges["lat_long"] = edges["lat_long"].apply(lambda x: np.round(
            np.array([[float(y.split(" ")[0]), float(y.split(" ")[1])] for y in x.split(", ")]).mean(axis=0), 7))
        edges.loc[:, ["lat", "long"]] = np.array(edges["lat_long"].values.tolist())

        grid_size = 30
        pad_size = 0.00000001

        lat_grid = np.linspace(edges["lat"].min() - pad_size, edges["lat"].max() + pad_size, grid_size + 1)
        lat_diff = ((lat_grid.reshape(1, -1) - edges["lat"].values.reshape(-1, 1)) < 0).astype(int)
        lat_grid_idx = np.where(lat_diff[:, :-1] - lat_diff[:, 1:])[1]

        long_grid = np.linspace(edges["long"].min() - pad_size, edges["long"].max() + pad_size, grid_size + 1)
        long_diff = ((long_grid.reshape(1, -1) - edges["long"].values.reshape(-1, 1)) < 0).astype(int)
        long_grid_idx = np.where(long_diff[:, :-1] - long_diff[:, 1:])[1]

        edges["lat_grid_idx"], edges["long_grid_idx"] = lat_grid_idx, long_grid_idx

        def create_color_gradient(c1, c2, n):
            r = np.linspace(c1[0], c2[0], n).astype(int)
            g = np.linspace(c1[1], c2[1], n).astype(int)
            b = np.linspace(c1[2], c2[2], n).astype(int)
            return list(zip(r, g, b))

        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)

        c1 = (77, 216, 219)  # light blue
        c2 = (223, 32, 32)  # red
        n = 101

        color_gradients = [rgb_to_hex(*c) for c in create_color_gradient(c1, c2, n)]
        color_mapper = dict(zip(np.arange(0.0, 10.1, 0.1).round(1), color_gradients))

        kernel_size = 3
        padding = 1
        crime_grid = np.zeros((grid_size, grid_size))

        grid_lines = list()
        scores = edges["weight_neutral"]/edges["length"]
        print(scores)
        for lat_idx in range(grid_size):
            for long_idx in range(grid_size):
                in_lat = ((edges["lat_grid_idx"] >= lat_idx - 1) * (edges["lat_grid_idx"] <= lat_idx + 1)).astype(
                    bool)
                in_long = ((edges["long_grid_idx"] >= long_idx - 1) * (
                            edges["long_grid_idx"] <= long_idx + 1)).astype(bool)
                score = round(scores[(in_lat) & (in_long)].mean(), 1)
                if pd.isnull(score):
                    score = 0.0
                color = color_mapper[score]
                opacity = min(1,max(0,(score - 3)/5)**2)
                crime_grid[lat_idx, long_idx] = score
                # edges_df.loc[(edges_df["lat_grid_idx"] == lat_idx) & (edges_df["long_grid_idx"] == long_idx), "score"] = score
                # edges_df.loc[(edges_df["lat_grid_idx"] == lat_idx) & (edges_df["long_grid_idx"] == long_idx), "color"] = color
                grid_lines.append(
                    {"lat_min": lat_grid[lat_idx],
                     "lat_max": lat_grid[lat_idx + 1],
                     "long_min": long_grid[long_idx],
                     "long_max": long_grid[long_idx + 1],
                     "crime_score": score,
                     "color": color,
                     "opacity": opacity}
                )

        return render_template('index.html', valid_coords=valid_coords, route=route, grid=json.dumps(grid_lines), safe_route=json.dumps(lat_long_safe), short_route=json.dumps(lat_long_short), params=params)

    else:
        route = json.dumps({"start_coords": "NA",
                             "dest_coords": "NA",
                             "valid_coords": False})
        grid = json.dumps({})
        valid_coords = False

        # Render the input form
        return render_template('index.html', valid_coords=valid_coords, route=route, grid=grid, safe_route=json.dumps([]), short_route=json.dumps([]), params=json.dumps([]))


# -- Database Route ----------------------------------------------------------------------------
@app.route("/about", methods=["GET", "POST"])
def render_about():
    return render_template("about.html")


# -- Database Route ----------------------------------------------------------------------------
@app.route("/database", methods=["GET", "POST"])
def render_database():
	if request.method == "POST":
	    return render_template("database.html")


# -- Settings Route ----------------------------------------------------------------------------
@app.route("/settings", methods=["GET", "POST"])
def render_settings():
    if request.method == "POST":
        print(request.form)
        PERCEPTION_WEIGHT = float(request.form["perception_weight"])
        INCLUDE_PARK = True if request.form.get("include_park") == "on" else False
        INCLUDE_INDUSTRIAL = True if request.form.get("include_industrial") == "on" else False
        db_edges = db_select("Edges")
        db_edges = get_creepiness_score(db_edges, PERCEPTION_WEIGHT, INCLUDE_PARK, INCLUDE_INDUSTRIAL)
        res = db_update("Edges", db_edges, bulk_update=True)
        return redirect(url_for("render_home"))
    else:
        return render_template("settings.html")


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

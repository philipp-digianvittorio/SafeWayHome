
import osmnx as ox
from update_database.scripts.PresseportalScraper import PresseportalScraper
from update_database.scripts.SQLAlchemyDB import db_select, db_insert, db_update
from update_database.scripts.GeoDataProcessing import geodata_to_df, get_district_park_industrial, get_image_scores, get_creepiness_score, db_to_graph
from update_database.scripts.TextClassification import article_to_crime_data
import shapely

# -- insert new cities
'''
res = db_insert("Cities", {"hq_id": [x["id"] for x in db_headquarters if "Frankfurt" in x["name"]][0],
                           "country": "Deutschland",
                           "city": "Frankfurt",
                           "full_name": "Frankfurt am Main"})
'''
################################################################################################
### -- Get Database Data ------------------------------------------------------------------- ###
################################################################################################

db_headquarters = db_select("Headquarters")
db_hq_ids = [hq["id"] for hq in db_headquarters]

db_articles = db_select("Articles")
db_article_ids = [a["hq_id"] + "#" + a["id"] for a in db_articles]

db_crimes = db_select("Crimes")

db_nodes = db_select("Nodes")
db_edges = db_select("Edges")

db_cities = db_select("Cities")
db_city_ids = list(set([c["country"] + "#" + (c["full_name"] or c["city"]) for c in db_cities]))

new_cities = [x.split("#") for x in set([e["country"] + "#" + e["city"] for e in db_edges]).symmetric_difference(db_city_ids)]

################################################################################################
### -- Scrape Presseportal Data & Update Database ------------------------------------------ ###
################################################################################################
sc = PresseportalScraper()

# -- update headquarter data -------------------------------------------------------------------
headquarters = sc.get_police_headquarters()
new_headquarters = [hq for hq in headquarters if not hq["id"] in db_hq_ids]
if new_headquarters:
    res = db_insert("Headquarters", new_headquarters)

# -- update articles and crimes for each headquarter -------------------------------------------
db_headquarters = db_select("Headquarters")

for hq in db_headquarters:
    #hq = [x for x in db_headquarters if "Frankfurt" in x["name"]][0]
    city_names = list(set([c["city"] for c in db_cities if c["hq_id"] == hq["id"]]))
    full_city_names = list(set([c["full_name"] or c["city"] for c in db_cities if c["hq_id"] == hq["id"]]))
    articles = sc.get_articles(hq, max_articles=60, stop_ids=db_article_ids, city_names=city_names)
    articles = [a for a in articles if a["city"]]

    if articles:
        res = db_insert("Articles", articles)

        crimes = list()
        G = db_to_graph([n for n in db_nodes if n["city"] in full_city_names], [e for e in db_edges if e["city"] in full_city_names])
        for article in db_articles[3500:5000]:
            try:
                c = article_to_crime_data(article)
                print(c)
                if c:
                    u, v, key = ox.nearest_edges(G, float(c["long"]), float(c["lat"]))
                    c["u"], c["v"], c["key"] = u, v, key
                    c["district"] = "None"
                    try:
                        res = db_insert("Crimes", c)
                    except:
                        print("database error")
            except:
                print("unknown error")
                next
                crimes.append(c)
        if crimes:
            res = db_insert("Crimes", crimes)


################################################################################################
### -- Load geo-data, scrape Streetview data & update database ----------------------------- ###
################################################################################################

for (country, city) in new_cities:
    # -- convert geodata to database format ----------------------------------------------------
    nodes, edges = geodata_to_df(country, city)
    db_nodes = nodes.reset_index().to_dict('records')
    db_edges = edges.reset_index().to_dict('records')

    # -- get districts for each edge -----------------------------------------------------------
    db_edges = get_district_park_industrial(db_edges)

    # -- update database -----------------------------------------------------------------------
    res = db_insert("Nodes", db_nodes)
    res = db_insert("Edges", db_edges)

    # -- get image scores for streets in geodata -----------------------------------------------
    db_edges = db_select("Edges")
    db_edges = get_image_scores(db_edges, step=160)

    # -- compute creepiness score --------------------------------------------------------------
    db_edges = get_creepiness_score(db_edges)

    # -- update database -----------------------------------------------------------------------
    db_update("Edges", db_edges, bulk_update=True)







'''
from shapely.ops import unary_union, polygonize
from shapely import wkt
from osmnx.geometries import MultiPolygon
import re
import pandas as pd
import geopandas as gpd

G = db_to_graph(db_nodes, db_edges)
ped = ox.graph_to_gdfs(G, nodes = False)
multi_line = ped.geometry.values
border_lines = unary_union(multi_line)
result = MultiPolygon(polygonize(border_lines))
bounds = gpd.GeoDataFrame(result)
bounds = bounds.rename({0: "geometry"}, axis=1)
bounds = gpd.GeoDataFrame(bounds).set_crs("epsg:4326")
edges = gpd.GeoDataFrame(db_edges).set_index(["u", "v", "key"])
edges["geometry"] = edges["geometry"].apply(lambda x: wkt.loads(x))
edges = gpd.GeoDataFrame(edges).set_crs("epsg:4326")

edges_bounds = edges.sjoin(bounds, how="left", predicate="intersects")
y = pd.DataFrame(edges_bounds)
boundaries = pd.Series([list(zip(r.exterior.coords.xy[0], r.exterior.coords.xy[1])) for r in list(result)])
b = dict()
for i in range(len(boundaries)):
    b[i] = pd.DataFrame({"idx": i,
                         "x": [x[0] for x in boundaries[i]],
                         "y": [x[1] for x in boundaries[i]]})

bounds = pd.concat(b.values())
edges = pd.DataFrame(db_edges)
edges["geometry"].apply(lambda x: wkt.loads(x).xy)
for i in range(len(bounds)):
    if str(bounds["x"][i]) + " " + str(bounds["y"][i])
    b[i] = pd.DataFrame({"idx": i,
                         "x": [x[0] for x in edges[i]],
                         "y": [x[1] for x in boundaries[i]]})
nodes = pd.DataFrame(db_nodes)
nodes_bounds = pd.merge(nodes, bounds,
                         how="left",
                         on=["x", "y"])

nodes_list = list(zip(nodes["x"], nodes["y"]))
boundaries.apply(lambda x: any(n in x for n in nodes_list))




import numpy as np
import pandas as pd
from update_database.scripts.SQLAlchemyDB import db_select, db_insert, db_update, db_delete

RELEVANT_CRIMES = ["tötungsdelikt", "sexualdelikt", "körperverletzung", "raub", "diebstahl", "drogendelikt"]

# -- compute crime score ---------------------------------------------------------------------------
db_edges = db_select("Edges")
db_crimes = db_select("Crimes")

edges_df = pd.DataFrame(db_edges)[["u", "v", "key", "lat_long", "weight_neutral"]]
crimes_df = pd.DataFrame(db_crimes).groupby(["u", "v", "key"]).count().reset_index()

edges_crimes = pd.merge(edges_df, crimes_df,
                          how="left",
                          on=["u", "v", "key"]).fillna(0)

edges_crimes[RELEVANT_CRIMES] = edges_crimes[RELEVANT_CRIMES] / edges_crimes.groupby(["country", "city"])[RELEVANT_CRIMES].transform("mean")
edges_crimes[RELEVANT_CRIMES[:3]] = edges_crimes[RELEVANT_CRIMES[:3]]*2
edges_crimes["crime_score"] = edges_crimes[RELEVANT_CRIMES].mean(axis=1)

# -- compute mean crime score per grid ----------------------------------------------------
edges_df["lat_long"] = edges_df["lat_long"].apply(lambda x: np.round(np.array([[float(y.split(" ")[0]), float(y.split(" ")[1])] for y in x.split(", ")]).mean(axis=0),7))
edges_df.loc[:, ["lat", "long"]] = np.array(edges_df["lat_long"].values.tolist())

grid_size = 20
pad_size = 0.00000001

lat_grid = np.linspace(edges_df["lat"].min()-pad_size, edges_df["lat"].max()+pad_size, grid_size+1)
lat_diff = ((lat_grid.reshape(1, -1) - edges_df["lat"].values.reshape(-1,1)) < 0).astype(int)
lat_grid_idx = np.where(lat_diff[:, :-1] - lat_diff[:, 1:])[1]

long_grid = np.linspace(edges_df["long"].min()-pad_size, edges_df["long"].max()+pad_size, grid_size+1)
long_diff = ((long_grid.reshape(1, -1) - edges_df["long"].values.reshape(-1,1)) < 0).astype(int)
long_grid_idx = np.where(long_diff[:, :-1] - long_diff[:, 1:])[1]

edges_df["lat_grid_idx"], edges_df["long_grid_idx"] = lat_grid_idx, long_grid_idx


def create_color_gradient(c1, c2, n):
    r = np.linspace(c1[0], c2[0], n).astype(int)
    g = np.linspace(c1[1], c2[1], n).astype(int)
    b = np.linspace(c1[2], c2[2], n).astype(int)
    return list(zip(r,g,b))

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


c1 = (77, 216, 219) # light blue
c2 = (223, 32, 32) # red
n = 51

color_gradients = [rgb_to_hex(*c) for c in create_color_gradient(c1, c2, n)]
color_mapper = dict(zip(np.arange(0.0, 5.1, 0.1).round(1), color_gradients))

kernel_size = 3
padding = 1
crime_grid = np.zeros((grid_size,grid_size))

grid_lines = list()

for lat_idx in range(grid_size):
    for long_idx in range(grid_size):
        in_lat = ((edges_df["lat_grid_idx"] >= lat_idx-1)*(edges_df["lat_grid_idx"] <= lat_idx+1)).astype(bool)
        in_long = ((edges_df["long_grid_idx"] >= long_idx-1)*(edges_df["long_grid_idx"] <= long_idx+1)).astype(bool)
        score = round(edges_df[(in_lat) & (in_long)]["weight_neutral"].mean(),1)
        if pd.isnull(score):
            score = 0.0
        #color = color_mapper[score]
        crime_grid[lat_idx,long_idx] = score
        #edges_df.loc[(edges_df["lat_grid_idx"] == lat_idx) & (edges_df["long_grid_idx"] == long_idx), "score"] = score
        #edges_df.loc[(edges_df["lat_grid_idx"] == lat_idx) & (edges_df["long_grid_idx"] == long_idx), "color"] = color
        grid_lines.append([lat_grid[lat_idx], lat_grid[lat_idx+1], long_grid[long_idx], long_grid[long_idx+1], score])

#grid_df = pd.DataFrame(np.array(grid_lines), columns=["lat_min", "lat_max", "long_min", "long_max", "score", "color"])

'''
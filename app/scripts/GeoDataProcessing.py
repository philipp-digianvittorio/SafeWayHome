
import re
import osmnx as ox
from shapely import wkt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderQuotaExceeded, GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable

from scripts.FlaskDataBase import db_select, db_insert, db_update, db_delete, Edges, Nodes
from scripts.StreetviewScraper import StreetviewScraper, firefox_binary
from scripts.ImageClassification import score_image


def geodata_to_df(country, city):

    G = ox.graph_from_place(city, network_type='walk')  # download raw geospatial data from OSM

    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
    nodes["city"], edges["city"] = city, city
    nodes["country"], edges["country"] = country, country

    edges["lat_long"] = edges["geometry"].apply(lambda x: re.sub(r'[^0-9., ]', "", str([re.sub(r'[^0-9. ]', '', str(i)) for i in list(zip(x.xy[1], x.xy[0]))])))
    edges["geometry"] = edges["geometry"].apply(lambda x: wkt.dumps(x))

    edges["district_u"] = None
    edges["district_v"] = None

    edges["score_neutral"] = None
    edges["score_positive"] = None
    edges["score_very_positive"] = None
    edges["score_negative"] = None
    edges["score_very_negative"] = None

    edges["weight_neutral"] = 0.0
    edges["weight_positive"] = 0.0
    edges["weight_very_positive"] = 0.0
    edges["weight_negative"] = 0.0
    edges["weight_very_negative"] = 0.0

    edges["park_flag"] = False
    edges["industrial_flag"] = False

    edges_cols = [col for col in edges.columns if col in Edges._get_columns()]
    nodes_cols = [col for col in nodes.columns if col in Nodes._get_columns()]
    edges, nodes = edges[edges_cols], nodes[nodes_cols]

    edges["highway"] = edges["highway"].apply(lambda x: ", ".join(x) if x.__class__.__name__=="list" else x)
    edges["name"] = edges["name"].apply(lambda x: ", ".join(x) if x.__class__.__name__=="list" else x)
    edges["maxspeed"] = edges["maxspeed"].apply(lambda x: ", ".join(x) if x.__class__.__name__ == "list" else x)
    edges["ref"] = edges["ref"].apply(lambda x: ", ".join(x) if x.__class__.__name__ == "list" else x)

    edges["reversed"] = edges["reversed"].apply(lambda x: x[0] if x.__class__.__name__ == "list" else x)
    edges["oneway"] = edges["oneway"].apply(lambda x: x[0] if x.__class__.__name__ == "list" else x)

    edges.fillna(-99, inplace=True)
    nodes.fillna(-99, inplace=True)
    edges["name"] = edges["name"].astype(str).replace("-99", None)

    return nodes, edges

def get_district(node, district_polygons):
    point = Point(float(node[1]), float(node[0]))
    polygon_index = district_polygons["geometry"].apply(point.within)
    try:
        return district_polygons['name'][polygon_index].iloc[0]
    except Exception:
        closest_polygon = None
        closest_distance = float("inf")
        for j, polygon in enumerate(district_polygons["geometry"]):
            distance = point.distance(polygon)
            closest_polygon = district_polygons['name'].iloc[j] if distance < closest_distance else closest_polygon
            closest_distance = min(distance, closest_distance)
        return closest_polygon
    
def is_within_any_polygon(edge, polygons):
    start_point = Point(float(edge.split(", ")[0].split(" ")[1]), float(edge.split(", ")[0].split(" ")[0]))
    end_point = Point(float(edge.split(", ")[1].split(" ")[1]), float(edge.split(", ")[1].split(" ")[0]))
    polygon_index = polygons["geometry"].apply(lambda x: start_point.within(x) or end_point.within(x))
    return any(polygon_index) 

def get_district_park_industrial(db_edges):

    edges = pd.DataFrame(db_edges)

    for city in edges["city"].unique():

        districts = ox.geometries.geometries_from_place(city, {'place': 'suburb'})

        for i in range(len(districts)):

            try:
                gdf = ox.geocode_to_gdf(city + ", " + districts['name'][i])
            except:
                try:
                    gdf = ox.geocode_to_gdf(city.split(" ")[0] + ", " + districts['name'][i])
                except:
                    gdf = ox.geocode_to_gdf(districts['name'][i])

            gdf['name'] = districts['name'][i]  # add district name as separate element
            if i == 0:
                district_polygons = gdf
            else:
                district_polygons = pd.concat([district_polygons, gdf])

        # 1) Parks
        parks = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'leisure': 'park'})
        parks_save = parks.applymap(lambda x: str(x) if isinstance(x, list) else x)
        parks_final = gpd.clip(parks_save, gdf)

        # 2) Industrial areas
        industrial = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'landuse': 'industrial'})
        industrial_save = industrial.applymap(lambda x: str(x) if isinstance(x, list) else x)
        industrial_final = gpd.clip(industrial_save, gdf)

        edges.loc[edges["city"] == city, "district_u"] = edges.loc[edges["city"] == city, "lat_long"].apply(lambda x: get_district(x.split(", ")[0].split(" "), district_polygons))
        edges.loc[edges["city"] == city, "district_v"] = edges.loc[edges["city"] == city, "lat_long"].apply(lambda x: get_district(x.split(", ")[-1].split(" "), district_polygons))

        edges.loc[edges["city"] == city, "park_flag"] = edges.loc[edges["city"] == city, "lat_long"].apply(lambda x: is_within_any_polygon(x, parks_final))
        edges.loc[edges["city"] == city, "industrial_flag"] = edges.loc[edges["city"] == city, "lat_long"].apply(lambda x: is_within_any_polygon(x, industrial_final))

    db_edges = edges.to_dict('records')

    return db_edges


def get_image_scores(db_edges, step=1):

    sc = StreetviewScraper(headless=True, firefox_binary=firefox_binary)

    for edge in db_edges[::step]:

        edge["score_neutral"], edge["score_positive"], edge["score_very_positive"], edge["score_negative"], edge["score_very_negative"] = [-99.0]*5

        lat_longs = [(float(x.split(" ")[0]), float(x.split(" ")[1])) for x in edge["lat_long"].split(", ")]
        for (lat, long) in lat_longs:
            img = sc.get_streetview_image(lat, long)
            if img:
                edge["score_neutral"], edge["score_positive"], edge["score_very_positive"], edge["score_negative"], edge["score_very_negative"] = score_image(img)
                break
            else:
                pass

    return db_edges


def get_creepiness_score(db_edges, perception_weight=0.3, include_park=True, include_industrial=True):
    # -- convert list of dicts to dataframe for vector operations -------------------------------------------
    edges = pd.DataFrame(db_edges)
    edges2 = edges.copy()

    # compute district scores for edges without street scores -----------------------------------------------
    d = dict()
    for cls in ["neutral", "positive", "negative", "very_positive", "very_negative"]:
        edges2[f"score_{cls}"] = edges2[f"score_{cls}"].replace(-99.0, np.nan)
        d[f"score_{cls}"] = edges[f"score_{cls}"].replace(-99.0, np.nan)
        district_u_score = edges2.groupby(["country", "city", "district_u"])[f"score_{cls}"].transform("mean")
        district_v_score = edges2.groupby(["country", "city", "district_v"])[f"score_{cls}"].transform("mean")
        d[f"score_{cls}"].loc[d[f"score_{cls}"].isnull()] = (1 / 2) * district_u_score + (1 / 2) * district_v_score
        d[f"score_{cls}"].loc[d[f"score_{cls}"].isnull()] = d[f"score_{cls}"].mean()
        # -- normalize streetview scores (range 0 - 10)
        # d[f"score_{cls}"] = ((d[f"score_{cls}"] - d[f"score_{cls}"].max()) / (d[f"score_{cls}"].min() - d[f"score_{cls}"].max()))
        d[f"score_{cls}"] = (
                    (d[f"score_{cls}"] - d[f"score_{cls}"].min()) / (d[f"score_{cls}"].max() - d[f"score_{cls}"].min()))
        d[f"score_{cls}"] = ((1 - d[f"score_{cls}"]) * 9) + 1

    # -- compute crime scores -------------------------------------------------------------------------------
    RELEVANT_CRIMES = ["tötungsdelikt", "sexualdelikt", "körperverletzung", "raub", "diebstahl", "drogendelikt"]

    db_crimes = db_select("Crimes")
    crimes_df = pd.DataFrame(db_crimes).groupby(["country", "city", "u", "v", "key"]).count().reset_index()

    edges_crimes = pd.merge(edges[["country", "city", "u", "v", "key", "lat_long"]],
                            crimes_df[["u", "v", "key"] + RELEVANT_CRIMES],
                            how="left",
                            on=["u", "v", "key"]).drop_duplicates(subset=["country", "city", "u", "v", "key", "lat_long"]).fillna(0).reset_index(drop=True)

    edges_crimes[RELEVANT_CRIMES] = edges_crimes[RELEVANT_CRIMES] / edges_crimes.groupby(["country", "city"])[
        RELEVANT_CRIMES].transform("mean")
    edges_crimes[RELEVANT_CRIMES[:3]] = edges_crimes[RELEVANT_CRIMES[:3]] * 2
    crime_score = edges_crimes[RELEVANT_CRIMES].sum(axis=1) / 9

    # -- compute mean crime score per grid ----------------------------------------------------
    edges2["lat_long"] = edges2["lat_long"].apply(lambda x: np.round(
        np.array([[float(y.split(" ")[0]), float(y.split(" ")[1])] for y in x.split(", ")]).mean(axis=0), 7))
    edges2.loc[:, ["lat", "long"]] = np.array(edges2["lat_long"].values.tolist())

    grid_size = 60
    pad_size = 0.00000001

    lat_grid = np.linspace(edges2["lat"].min() - pad_size, edges2["lat"].max() + pad_size, grid_size + 1)
    lat_diff = ((lat_grid.reshape(1, -1) - edges2["lat"].values.reshape(-1, 1)) < 0).astype(int)
    lat_grid_idx = np.where(lat_diff[:, :-1] - lat_diff[:, 1:])[1]

    long_grid = np.linspace(edges2["long"].min() - pad_size, edges2["long"].max() + pad_size, grid_size + 1)
    long_diff = ((long_grid.reshape(1, -1) - edges2["long"].values.reshape(-1, 1)) < 0).astype(int)
    long_grid_idx = np.where(long_diff[:, :-1] - long_diff[:, 1:])[1]

    edges2["lat_grid_idx"], edges2["long_grid_idx"] = lat_grid_idx, long_grid_idx

    kernel_size = 5
    crime_grid = np.zeros((grid_size, grid_size))

    edges2["score"] = crime_score

    grid_lines = list()
    for lat_idx in range(grid_size):
        for long_idx in range(grid_size):
            in_lat = ((edges2["lat_grid_idx"] >= lat_idx - 2) * (edges2["lat_grid_idx"] <= lat_idx + 2)).astype(
                bool)
            in_long = ((edges2["long_grid_idx"] >= long_idx - 2) * (
                    edges2["long_grid_idx"] <= long_idx + 2)).astype(bool)
            score = round(crime_score[(in_lat) & (in_long)].mean(), 1)
            if pd.isnull(score):
                score = 0.0
            edges2.loc[(edges2["lat_grid_idx"] == lat_idx) & (edges2["long_grid_idx"] == long_idx), "score"] = score

    crime_score = edges2["score"].copy()

    # -- normalize crime scores (range 0 - 10)
    norm_crime_score = (((crime_score - crime_score.min()) / (crime_score.max() - crime_score.min())) * 9) + 1

    # -- compute final weights ------------------------------------------------------------------------------
    for cls in ["neutral", "positive", "negative", "very_positive", "very_negative"]:
        # edges[f"weight_{cls}"] = edges["length"] * ( (1/3)*d[f"score_{cls}"] + (2/3)*crime_score - edges["park_flag"].astype(int) - edges["industrial_flag"].astype(int) )
        # edges[f"weight_{cls}"] = edges["length"] * min(10, crime_score + (1/3)*(d[f"score_{cls}"]) + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )
        edges[f"weight_{cls}"] = edges["length"] * (
                    (1 - perception_weight) * norm_crime_score + perception_weight * d[f"score_{cls}"] - int(
                include_park) * edges["park_flag"].astype(int) - int(include_industrial) * edges[
                        "industrial_flag"].astype(int)).apply(lambda x: min(10, x))
        # edges[f"weight_{cls}"].loc[edges[f"weight_{cls}"] .isnull()] = edges[f"weight_{cls}"].mean()
    # -- convert dataframe to list of dicts -----------------------------------------------------------------
    db_edges = edges.to_dict('records')

    return db_edges


def db_to_graph(db_nodes, db_edges):
    nodes = gpd.GeoDataFrame(db_nodes).set_index(["osmid"])
    edges = gpd.GeoDataFrame(db_edges).set_index(["u", "v", "key"])
    edges["geometry"] = edges["geometry"].apply(lambda x: wkt.loads(x))
    edges = gpd.GeoDataFrame(edges).set_crs("epsg:4326")
    G = ox.graph_from_gdfs(nodes, edges)
    return G


def get_lat_lon(address):
    # get coordinates of streets
    try:
        geolocator = Nominatim(user_agent="safewayhome")
        location = geolocator.geocode(address, timeout=3).raw
    except (GeocoderQuotaExceeded, GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable) as e:
        print(e)
        return None, None

    return location["lat"], location["lon"]
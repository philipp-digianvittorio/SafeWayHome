
import re
import osmnx as ox
from shapely import wkt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

from update_database.scripts.SQLAlchemyDB import db_select, db_insert, db_update, db_delete, Edges, Nodes
from update_database.scripts.StreetviewScraper import StreetviewScraper, firefox_binary
from update_database.scripts.ImageClassification import score_image


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
            gdf = ox.geocode_to_gdf(districts['name'][i] + "," + city)
            gdf['name'] = districts['name'][i]  # add district name as separate element
            if i == 0:
                district_polygons = gdf
            else:
                district_polygons = pd.concat([district_polygons, gdf])

        # edges[edges["city"] == city]["district_u"]...
        # edges[edges["city"] == city]["district_v"]...

        # 1) Parks
        parks = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'leisure': 'park'})
        parks_save = parks.applymap(lambda x: str(x) if isinstance(x, list) else x)
        parks_final = gpd.clip(parks_save, gdf)

        # 2) Industral areas
        industrial = ox.geometries.geometries_from_polygon(gdf['geometry'][0], {'landuse': 'industrial'})
        industrial_save = industrial.applymap(lambda x: str(x) if isinstance(x, list) else x)
        industrial_final = gpd.clip(industrial_save, gdf)

        edges["district_u"] = edges["lat_long"].apply(
            lambda x: get_district(x.split(", ")[0].split(" "), district_polygons))
        edges["district_v"] = edges["lat_long"].apply(
            lambda x: get_district(x.split(", ")[1].split(" "), district_polygons))

        edges["park_flag"] = edges["lat_long"].apply(lambda x: is_within_any_polygon(x, parks_final))
        edges["industrial_flag"] = edges["lat_long"].apply(lambda x: is_within_any_polygon(x, industrial_final))


def get_image_scores(db_edges, step=1):

    sc = StreetviewScraper(headless=True, firefox_binary=firefox_binary)

    for edge in db_edges[::step]:

        edge["score_neutral"], edge["score_positive"], edge["score_very_positive"], edge["score_negative"], edge["score_very_negative"] = [None]*5

        lat_longs = [(float(x.split(" ")[0]), float(x.split(" ")[1])) for x in edge["lat_long"].split(", ")]
        for (lat, long) in lat_longs:
            img = sc.get_streetview_image(lat, long)
            if img:
                edge["score_neutral"], edge["score_positive"], edge["score_very_positive"], edge["score_negative"], edge["score_very_negative"] = score_image(img)
                break
            else:
                pass

    return db_edges


def get_creepiness_score(db_edges):

    # -- convert list of dicts to dataframe for vector operations -------------------------------------------
    edges = pd.DataFrame(db_edges)


    # compute district scores for edges without street scores -----------------------------------------------
    for cls in ["neutral", "positive", "negative", "very_positive", "very_negative"]:
        district_score = edges.groupby(["country", "city", "district"])["score_neutral"].mean()
        edges.loc[edges["score_neutral"].isnull(), "score_neutral"] = district_score

    # -- compute crime scores -------------------------------------------------------------------------------
    crime_score = 1

    # -- compute final weights ------------------------------------------------------------------------------
    edges["weight_neutral"] = edges["length"] * ( (1/3)*edges["score_neutral"] + (2/3)*crime_score + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )
    edges["weight_positive"] = edges["length"] * ( (1/3)*edges["score_positive"] + (2/3)*crime_score + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )
    edges["weight_very_positive"] = edges["length"] * ( (1/3)*edges["score_very_positive"] + (2/3)*crime_score + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )
    edges["weight_negative"] = edges["length"] * ( (1/3)*edges["score_negative"] + (2/3)*crime_score + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )
    edges["weight_very_negative"] = edges["length"] * ( (1/3)*edges["score_very_negative"] + (2/3)*crime_score + edges["park_flag"].astype(int) + edges["industrial_flag"].astype(int) )

    # -- convert dataframe to list of dicts -----------------------------------------------------------------
    db_edges = edges.to_dict('records')

    return db_edges

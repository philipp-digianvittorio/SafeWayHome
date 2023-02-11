
from update_database.scripts.PresseportalScraper import PresseportalScraper
from update_database.scripts.SQLAlchemyDB import db_select, db_insert, db_update
from update_database.scripts.GeoDataProcessing import geodata_to_df, get_district_park_industrial, get_image_scores, get_creepiness_score
#from update_database.scripts.TextClassification import article_to_crime_data


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

db_nodes = db_select("Nodes")
db_edges = db_select("Edges")

db_cities = db_select("Cities")
db_city_ids = list(set([c["country"] + "#" + (c["full_name"] or c["city"]) for c in db_cities]))

new_cities = [x.split("#") for x in set([e["country"] + "#" + e["city"] for e in db_edges]).symmetric_difference(db_city_ids)]

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
    db_edges = get_image_scores(db_edges, step=20)

    # -- compute creepiness score --------------------------------------------------------------
    db_edges = get_creepiness_score(db_edges)

    # -- update database -----------------------------------------------------------------------
    db_update("Edges", db_edges, bulk_update=True)







'''


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
    city_names = list(set([c["city"] for c in db_cities if c["hq_id"] == hq["id"]]))
    articles = sc.get_articles(hq, max_articles=200, stop_ids=db_article_ids, city_names=city_names)
    articles = [a for a in articles if a["city"]]
    if articles:
        res = db_insert("Articles", articles)

        crimes = list()
        for article in articles:
            c = article_to_crime_data(article)
            print(c)
            if c:
                crimes.append(c)
        if crimes:
            res = db_insert("Crimes", crimes)









import numpy as np
import pandas as pd
from update_database.scripts.SQLAlchemyDB import db_select, db_insert, db_update, db_delete

RELEVANT_CRIMES = ["tötungsdelikt", "sexualdelikt", "körperverletzung", "raub", "diebstahl", "drogendelikt"]

db_streets = db_select("Streets")
db_crimes = db_select("Crimes")

streets_df = pd.DataFrame(db_streets)
crimes_df = pd.DataFrame(db_crimes).groupby(["lat", "long"]).count().reset_index()
crimes_df[RELEVANT_CRIMES] = crimes_df[RELEVANT_CRIMES] / crimes_df.groupby(["country", "city"])[RELEVANT_CRIMES].transform("mean")

streets_crimes = pd.merge(streets_df, crimes_df,
                          how="left",
                          on=["lat", "long"])

streets_crimes = streets_crimes.fillna(0)

streets_crimes[RELEVANT_CRIMES] = streets_crimes[RELEVANT_CRIMES] / streets_crimes.groupby(["country", "city"])[RELEVANT_CRIMES].transform("mean")
streets_crimes[RELEVANT_CRIMES[:3]] = streets_crimes[RELEVANT_CRIMES[:3]]*2
street_crimes["crime_score"] = streets_crimes[RELEVANT_CRIMES].mean(axis=1)


grid_size = 10
pad_size = 0.00000001

lat_grid = np.linspace(streets_df["lat"].min()-pad_size, streets_df["lat"].max()+pad_size, grid_size+1)
lat_diff = ((lat_grid.reshape(1, -1) - streets_df["lat"].values.reshape(-1,1)) < 0).astype(int)
lat_grid_idx = np.where(lat_diff[:, :-1] - lat_diff[:, 1:])[1]

long_grid = np.linspace(streets_df["long"].min()-pad_size, streets_df["long"].max()+pad_size, grid_size+1)
long_diff = ((long_grid.reshape(1, -1) - streets_df["long"].values.reshape(-1,1)) < 0).astype(int)
long_grid_idx = np.where(long_diff[:, :-1] - long_diff[:, 1:])[1]

streets_df["lat_grid_idx"], streets_df["long_grid_idx"] = lat_grid_idx, long_grid_idx
streets_df["crime_deviation"] = np.random.uniform(0,3,len(streets_df))
streets_df["crime_score"] = 0.0

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

window_size = 3
padding = 1
crime_grid = np.zeros((grid_size,grid_size))

grid_lines = list()

for lat_idx in range(grid_size):
    for long_idx in range(grid_size):
        in_lat = ((streets_df["lat_grid_idx"] >= lat_idx-1)*(streets_df["lat_grid_idx"] <= lat_idx+1)).astype(bool)
        in_long = ((streets_df["long_grid_idx"] >= long_idx-1)*(streets_df["long_grid_idx"] <= long_idx+1)).astype(bool)
        crime_score = round(streets_df[(in_lat) & (in_long)]["crime_deviation"].mean(),1)
        if pd.isnull(crime_score):
            crime_score = 0.0
        color = color_mapper[crime_score]
        crime_grid[lat_idx,long_idx] = crime_score
        streets_df.loc[(streets_df["lat_grid_idx"] == lat_idx) & (streets_df["long_grid_idx"] == long_idx), "crime_score"] = crime_score
        streets_df.loc[(streets_df["lat_grid_idx"] == lat_idx) & (streets_df["long_grid_idx"] == long_idx), "color"] = color
        grid_lines.append([lat_grid[lat_idx], lat_grid[lat_idx+1], long_grid[long_idx], long_grid[long_idx+1], crime_score, color])

grid_df = pd.DataFrame(np.array(grid_lines),
                       columns=["lat_min", "lat_max", "long_min", "long_max", "score", "color"])

'''
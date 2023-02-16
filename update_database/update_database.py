
import osmnx as ox
from scripts.PresseportalScraper import PresseportalScraper
from scripts.SQLAlchemyDB import db_select, db_insert, db_update
from scripts.GeoDataProcessing import geodata_to_df, get_district_park_industrial, get_image_scores, get_creepiness_score, db_to_graph
from scripts.TextClassification import article_to_crime_data


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
        for article in articles:
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

    # -- update database -----------------------------------------------------------------------
    db_update("Edges", db_edges, bulk_update=True)


################################################################################################
### -- Update Creepiness Score ------------------------------------------------------------- ###
################################################################################################
db_edges = db_select("Edges")
# -- compute creepiness score --------------------------------------------------------------
db_edges = get_creepiness_score(db_edges)

# -- update database -----------------------------------------------------------------------
db_update("Edges", db_edges, bulk_update=True)







'''
edges = pd.DataFrame(db_edges)
articles = pd.read_excel("gpt_output_clean_new.xlsx")
articles_edges = pd.merge(articles, edges,
                          how="inner",
                          left_on=["location"],
                          right_on=["name"]).drop_duplicates(subset=["article_id", "location", "article"])
articles_edges["lat"] = articles_edges["lat_long"].apply(lambda x: x.split(", ")[0].split(" ")[0])
articles_edges["long"] = articles_edges["lat_long"].apply(lambda x: x.split(", ")[0].split(" ")[1])
articles_edges["crime"] = articles_edges["crime"].apply(lambda x: eval(x)[0])
articles_edges = articles_edges[articles_edges["crime"].isin(["Tötungsdelikt", "Sexualdelikt", "Körperverletzung", "Raub", "Diebstahl", "Drogendelikt"])].reset_index(drop=True)
articles_edges[['tötungsdelikt', 'sexualdelikt', 'körperverletzung', 'raub', 'diebstahl', 'drogendelikt']] = False
for col in ['tötungsdelikt', 'sexualdelikt', 'körperverletzung', 'raub', 'diebstahl', 'drogendelikt']:
    articles_edges.loc[articles_edges["crime"].str.lower().str.contains(col), col] = True

db_crimes = articles_edges[['u', 'v', 'key', 'country', 'city', 'street', 'district', 'lat', 'long', 'tötungsdelikt', 'sexualdelikt', 'körperverletzung', 'raub', 'diebstahl', 'drogendelikt']].to_dict("records")
db_insert("Crimes", db_crimes)

'''
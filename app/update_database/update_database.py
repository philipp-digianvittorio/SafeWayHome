
from update_database.scripts.PresseportalScraper import PresseportalScraper
from update_database.scripts.StreetviewScraper import StreetviewScraper, firefox_binary
from update_database.scripts.SQLAlchemyDB import db_select, db_insert
from update_database.scripts.TextClassification import classify_articles
from update_database.scripts.ImageClassification import score_image


################################################################################################
### -- Get Database Data ------------------------------------------------------------------- ###
################################################################################################

db_headquarters = db_select("Headquarters")
db_hq_ids = [hq["id"] for hq in db_headquarters]

db_articles = db_select("Articles")
db_article_ids = [a["hq_id"] + "#" + a["id"] for a in db_articles]

db_streets = db_select("Streets")
db_street_ids = [s["country"] + "#" + s["city"] + "#" + s["street"] for s in db_streets]

db_cities = db_select("Cities")
db_city_ids = list(set([c["country"] + "#" + c["city"] for c in db_cities]))

################################################################################################
### -- Scrape Presseportal Data & Update Database ------------------------------------------ ###
################################################################################################

sc = PresseportalScraper()

# -- update headquarter data
headquarters = sc.get_police_headquarters()
new_headquarters = [hq for hq in headquarters if not hq["id"] in db_hq_ids]
if new_headquarters:
    res = db_insert("Headquarters", new_headquarters)

# -- update articles and crimes for each headquarter
db_headquarters = db_select("Headquarters")
for hq in db_headquarters:
    articles = sc.get_articles(hq, max_articles=30, stop_ids=db_article_ids)
    if articles:
        res = db_insert("Articles", articles)

        crimes = classify_articles(articles)
        res = db_insert("Crimes", crimes)


################################################################################################
### -- Scrape Streetview Data & Update Database -------------------------------------------- ###
################################################################################################

new_street_list = []

sc = StreetviewScraper(headless=True, firefox_binary=firefox_binary)
for id in db_city_ids:
    street_ids = [id + "#" + street_id for street_id in sc.get_street_names(*id.split("#"))]
    # -- get all streets that are not in the database
    new_street_ids = [street_id for street_id in street_ids if not street_id in db_street_ids]
    # -- try to scrape images for all new streets
    for street_id in new_street_ids:
        s = dict()

        s["country"], s["city"], s["street"] = street_id.split("#")
        s["lat"], s["long"] = sc.get_lat_lon(*street_id.split("#"))

        if (s["lat"] and s["long"]):
            img = sc.get_streetview_image(s["lat"], s["long"])

            if img:
                s["score_neutral"], s["score_positive"], s["score_very_positive"], s["score_negative"], s["score_very_negative"] = score_image(img)

            else:
                pass
        else:
            pass

        new_street_list.append(s)
        res = db_insert("Streets", s)

#if new_street_list:
 #   res = db_insert("Streets", new_street_list)


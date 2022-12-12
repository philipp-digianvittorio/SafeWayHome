from db_update.PresseportalScraper import PresseportalScraper
from db_update.SQLAlchemyDB import db_insert

sc = PresseportalScraper()

# -- update headquarter data
headquarters = sc.get_police_headquarters()
res = db_insert("Headquarters", headquarters)

# -- update articles for each headquarter
for hq in headquarters:
    articles = sc.get_articles(hq, max_articles=1000)
    res = db_insert("Articles", articles)
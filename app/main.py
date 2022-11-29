
# pip install flask==2.1.3
# pip install -U werkzeug==2.2.2
# pip install flask-reuploaded
# pip install flask-wtf
# pip install wtforms

# pip install flask-sqlalchemy
# pip install sqlalchemy

# -- import flask modules
from flask import Flask, render_template, send_from_directory, url_for, request, session, flash
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


# -- import database modules
from sqlalchemy import inspect
from FlaskDataBase import db, create_database_mysql, drop_database_mysql, initialize_database, db_select, db_insert, db_update, mysql_pw
from OSMConnection import get_police_coords

# -- import additional scripts
from PresseportalScraper import PresseportalScraper

# -- Initialize App ----------------------------------------------------------------------------
app = Flask(__name__)


# -- Add Database Connection -------------------------------------------------------------------
db_name = "db_name"  # "mysql_db"

# -- initialize sqlite database
initialize_database(app=app, db_uri=f"sqlite:///{db_name}.db")

# -- initialize mysql database
#create_database_mysql(name=db_name)  # mysql
#initialize_database(app=app, db_uri=f"mysql+pymysql://root:{mysql_pw}@localhost/{db_name}")  # mysql

print(inspect(db.engine).get_table_names())


# -- Configure App -----------------------------------------------------------------------------
app.config["SECRET_KEY"] = "slafnlanlskjfkjafkjebfkjjkebfpqfeh3737664aiq4893hckcqb"


################################################################################################
### -- Define FlaskForms ------------------------------------------------------------------- ###
################################################################################################

# -- Database Form --------------------------------------------------------------------------
class DataBaseForm(FlaskForm):

	submit = SubmitField("Load Database Data")

  
  

################################################################################################
### -- Define App Routes ------------------------------------------------------------------- ###
################################################################################################


# -- Home Route --------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def my_func():
    if request.method == "POST":
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

        # Render the page with the map
        return render_template('results.html', markers=markers, lat=request.form["lat"], lon=request.form["lon"])


    else:
        # Render the input form
        return render_template('index.html')


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
		articles = sc.get_articles(hq[89])
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
	app.run(debug=True)


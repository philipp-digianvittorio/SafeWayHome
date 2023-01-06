
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
from sqlalchemy import inspect
from scripts.FlaskDataBase import db, initialize_database, db_select, db_insert

# -- import additional scripts
from settings import DATABASE_URL
from update_database.scripts.PresseportalScraper import PresseportalScraper

# -- import plot modules
import json
import plotly
import osmnx as ox
import taxicab as tc
#from scripts.OSMConnection import get_police_coords
#from scripts.compute_plot_route import plot_route, node_list_to_path_short

#io.renderers.default='browser'


from geopy.geocoders import Nominatim


def get_lat_lon(address):
    # get coordinates of streets
    try:
        geolocator = Nominatim(user_agent="tutorial")
        location = geolocator.geocode(address, timeout=3).raw
    except:
        return None, None

    return location["lat"], location["lon"]


# -- Initialize App ----------------------------------------------------------------------------
app = Flask(__name__)


# -- Add Database Connection -------------------------------------------------------------------
db_name = "db_name"  # "mysql_db"

# -- initialize sqlite database
initialize_database(app=app, db_uri=DATABASE_URL)

# -- initialize mysql database
#create_database_mysql(name=db_name)  # mysql
#initialize_database(app=app, db_uri=f"mysql+pymysql://root:{mysql_pw}@localhost/{db_name}")  # mysql

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

        # -- get destination coordinates
        if request.form["destination_loc"] != "":
            print(request.form["destination_loc"])
            dest_coords = get_lat_lon(request.form["destination_loc"])

        # -- get start coordinates
        if (request.form["start_loc"] == "Mein Standort") and (request.form["user_position"] != ""):
            start_coords = request.form["user_position"].split(",")
        elif (request.form["start_loc"] != "Mein Standort") and (request.form["start_loc"] != ""):
            start_coords = get_lat_lon(request.form["start_loc"])

        route = {"start_coords": start_coords,
                 "dest_coords": dest_coords,
                 "valid_coords": True}

        route = json.dumps(route)

        return render_template('index.html', route=route)

    else:
        route = json.dumps({"start_coords": "NA",
                             "dest_coords": "NA",
                             "valid_coords": False})

        # Render the input form
        return render_template('index.html', route=route)


# -- Plotly Testpage ------------------------------------------------------------------------
@app.route("/map")
def plotly_plot():
    # Include plot
    start = (50.110446, 8.681968) # Römer #{{}}
    destination = (50.115452, 8.671515) # Oper #{{}}

    # get OSM data around the start point
    G = ox.graph_from_point(start, dist=3000, network_type='walk')
    G = ox.speed.add_edge_speeds(G)
    G = ox.speed.add_edge_travel_times(G)

    # calculate shortest route using taxicab package
    route = tc.distance.shortest_path(G, start, destination)

    # remove distance from route
    route_nodes = list(route)
    route_nodes = route_nodes[1]


    lines = node_list_to_path_short(G, route_nodes)
    long2 = []
    lat2 = []
    for i in range(len(lines)):
        z = list(lines[i])
        l1 = list(list(zip(*z))[0])
        l2 = list(list(zip(*z))[1])
        for j in range(len(l1)):
            long2.append(l1[j])
            lat2.append(l2[j])

    fig = plot_route(lat2, long2, start, destination)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON=graphJSON)


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
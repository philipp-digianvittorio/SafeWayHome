
# pip install flask==2.1.3
# pip install -U werkzeug==2.2.2
# pip install flask-reuploaded
# pip install flask-wtf
# pip install wtforms

# -- import flask modules
from flask import Flask, render_template, send_from_directory, url_for, request, session, flash
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


# -- import database modules
from sqlalchemy import inspect
from FlaskDataBase import db, create_database_mysql, drop_database_mysql, initialize_database, insert_data, update_data, mysql_pw


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
	form=DatabaseForm()

	if form.validate_on_submit():
    pass
    # code here
	else:
    pass
		# other code

	return render_template("index.html", form=form)


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

	return render_template("database.html", db_data = db_data)



################################################################################################
### -- Run the App ------------------------------------------------------------------------- ###
################################################################################################
if __name__ == "__main__":
	app.run(debug=True)


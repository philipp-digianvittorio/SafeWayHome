
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects import mysql
from datetime import datetime
import typing
import mysql.connector

# -- instantiate database engine
db = SQLAlchemy()  # use for SQL database

mysql_pw = "celestial09#"

################################################################################################
### -- Define Database Tables -------------------------------------------------------------- ###
################################################################################################



################################################################################################
### -- Initialize Database  ---------------------------------------------------------------- ###
################################################################################################

def initialize_database(app, db_uri):
    # -- add database ------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'poolclass': NullPool}  # disable pooling
    
    # -- initialize database -----------------------------------
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    
    # -- close the connection pool -----------------------------
    db.engine.dispose()


def create_database_mysql(name="mysql_db", host="localhost", user="root", pw=mysql_pw, overwrite=False):

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=pw
    )
    my_curser = mydb.cursor()
    # check if database already exists
    my_curser.execute("SHOW DATABASES")
    print(my_curser)
    db_exists = False
    for db in my_curser:
        if db[0] == name:
            db_exists = True
        print(db[0])

    # create new database if it doesn't exist
    if not db_exists:
        my_curser.execute(f"CREATE DATABASE {name}")

        # check if database was created successfully
        my_curser.execute("SHOW DATABASES")
        for db in my_curser:
            if db[0] == name:
                db_exists = True
            print(db[0])

        if db_exists == True:
            print(f"Database {name} created successfully!")
        else:
            print(f"Database {name} could not be created!")

    else:
        print(f"Database {name} already exists!")
    mydb.commit()
    my_curser.close()
    mydb.close()


def drop_database_mysql(name, host="localhost", user="root", pw=mysql_pw):

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=pw
    )
    my_curser = mydb.cursor()
    # check if database exists
    my_curser.execute("SHOW DATABASES")
    db_exists = False
    for db in my_curser:
        if db[0] == name:
            db_exists = True
        print(db[0])

    # drop database if it doesn't exist
    if db_exists:
        my_curser.execute(f"DROP DATABASE {name}")
        db_exists = False
        for db in my_curser:
            if db[0] == name:
                db_exists = True
        if not db_exists:
            print(f"Database {name} dropped successfully!")
        else:
            print(f"Database {name} could not be dropped!")
    else:
        print(f"Database {name} does not exist!")

    mydb.commit()
    my_curser.close()
    mydb.close()


################################################################################################
### -- Modify Database  -------------------------------------------------------------------- ###
################################################################################################

def insert_data(table_name, data):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        res = conn.execute(my_table.insert(), data)
        #new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
    #db.session.commit()
    #db.session.close()
    db.engine.dispose()  # close the connection pool
    return res.lastrowid


def update_data(table_name, data, **kwargs):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        res = conn.execute(my_table.update().filter_by(**kwargs), data).rowcount
        # new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
    #db.session.commit()
    #db.session.close()
    db.engine.dispose()  # close the connection pool
    return res


from flask_sqlalchemy import SQLAlchemy, inspect
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

class Headquarters(db.Model):

    # -- declare table name
    __tablename__ = 'Headquarters'

    # -- declare columns
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Articles(db.Model):

    # -- declare table name
    __tablename__ = 'Articles'

    # -- declare columns
    id = db.Column(db.String(100), primary_key=True)
    hq_id = db.Column(db.String(100), db.ForeignKey('Headquarters.id'), nullable=False)
    hq_name = db.Column(db.String(100), db.ForeignKey('Headquarters.name'), nullable=False)
    headline = db.Column(db.String(1000), nullable=False)
    article = db.Column(db.String(50000), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    kw_location = db.Column(db.String(1000))
    kw_topic = db.Column(db.String(1000))

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



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


def db_select(table_name, **filter_cols):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        res = conn.execute(my_table.select().filter_by(**filter_cols)).mappings().all()

    return res

def db_insert(table_name, data):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        res = conn.execute(my_table.insert(), data)
        #new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
    #db.session.commit()
    #db.session.close()
    db.engine.dispose()  # close the connection pool
    return res.lastrowid


def db_update(table_name, data, **filter_cols):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        res = conn.execute(my_table.update().filter_by(**filter_cols), data).rowcount
        # new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
    #db.session.commit()
    #db.session.close()
    db.engine.dispose()  # close the connection pool
    return res



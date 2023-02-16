
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects import mysql
from sqlalchemy_utils import get_mapper
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

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Cities(db.Model):

    # -- declare table name
    __tablename__ = 'Cities'

    # -- declare columns
    id = db.Column(db.Integer, primary_key=True)
    hq_id = db.Column(db.String(100), db.ForeignKey('Headquarters.id'), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(200), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Articles(db.Model):

    # -- declare table name
    __tablename__ = 'Articles'

    # -- declare columns
    id = db.Column(db.String(100), primary_key=True)
    hq_id = db.Column(db.String(100), db.ForeignKey('Headquarters.id'), nullable=False)
    hq_name = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(1000), nullable=False)
    article = db.Column(db.String(5000), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    kw_location = db.Column(db.String(1000))
    kw_topic = db.Column(db.String(1000))

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Crimes(db.Model):

    # -- declare table name
    __tablename__ = 'Crimes'

    # -- declare columns
    id = db.Column(db.Integer, primary_key=True)
    u = db.Column(db.BigInteger, nullable=False)
    v = db.Column(db.BigInteger, nullable=False)
    key = db.Column(db.BigInteger, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.String(100), nullable=False)
    long = db.Column(db.String(100), nullable=False)
    tötungsdelikt = db.Column(db.Boolean, nullable=False)
    sexualdelikt = db.Column(db.Boolean, nullable=False)
    körperverletzung = db.Column(db.Boolean, nullable=False)
    raub = db.Column(db.Boolean, nullable=False)
    diebstahl = db.Column(db.Boolean, nullable=False)
    drogendelikt = db.Column(db.Boolean, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Streets(db.Model):

    # -- declare table name
    __tablename__ = 'Streets'

    # -- declare columns
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.String(100), nullable=False)
    long = db.Column(db.String(100), nullable=False)
    score_neutral = db.Column(db.Float, nullable=False)
    score_positive = db.Column(db.Float, nullable=False)
    score_very_positive = db.Column(db.Float, nullable=False)
    score_negative = db.Column(db.Float, nullable=False)
    score_very_negative = db.Column(db.Float, nullable=False)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



class Nodes(db.Model):

    # -- declare table name
    __tablename__ = 'Nodes'
    # -- declare columns
    id = db.Column(db.Integer, primary_key=True)
    osmid = db.Column(db.BigInteger)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    y = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)
    highway = db.Column(db.String(100), nullable=True)
    street_count = db.Column(db.Integer, nullable=True)
    ref = db.Column(db.String(100), nullable=True)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



class Edges(db.Model):

    # -- declare table name
    __tablename__ = 'Edges'

    # -- declare columns
    id = db.Column(db.Integer, primary_key=True)
    u = db.Column(db.BigInteger, nullable=False)
    v = db.Column(db.BigInteger, nullable=False)
    key = db.Column(db.BigInteger, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    district_u = db.Column(db.String(100), nullable=True)
    district_v = db.Column(db.String(100), nullable=True)
    park_flag = db.Column(db.Boolean, nullable=True, default=False)
    industrial_flag = db.Column(db.Boolean, nullable=True, default=False)
    highway = db.Column(db.String(100), nullable=True)
    maxspeed = db.Column(db.String(100), nullable=True)
    oneway = db.Column(db.Boolean, nullable=True)
    reversed = db.Column(db.Boolean, nullable=True)
    length = db.Column(db.Float, nullable=True)
    ref = db.Column(db.String(100), nullable=True)
    geometry = db.Column(db.String(10000), nullable=False)
    lat_long = db.Column(db.String(5000), nullable=False)
    score_neutral = db.Column(db.Float, nullable=True)
    score_positive = db.Column(db.Float, nullable=True)
    score_very_positive = db.Column(db.Float, nullable=True)
    score_negative = db.Column(db.Float, nullable=True)
    score_very_negative = db.Column(db.Float, nullable=True)
    weight_neutral = db.Column(db.Float, nullable=False)
    weight_positive = db.Column(db.Float, nullable=False)
    weight_very_positive = db.Column(db.Float, nullable=False)
    weight_negative = db.Column(db.Float, nullable=False)
    weight_very_negative = db.Column(db.Float, nullable=False)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



################################################################################################
### -- Initialize Database  ---------------------------------------------------------------- ###
################################################################################################

def initialize_database(app, db_uri):
    # -- add database ------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    if not "mysql" in str(db_uri):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'poolclass': NullPool}  # disable pooling
    
    # -- initialize database -----------------------------------
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    
    # -- close the connection pool -----------------------------
    db.engine.dispose()


def create_database_mysql(name="instance/mysql_db", host="localhost", user="root", pw=mysql_pw, overwrite=False):

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


def db_select(table_name, filters=None):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        if filters:
            res = conn.execute(my_table.select().filter(*filters)).mappings().all()
        else:
            res = conn.execute(my_table.select()).mappings().all()
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


def db_update(table_name, data, filters=None, bulk_update=False):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        if filters:
            res = conn.execute(my_table.update().filter(*filters), data).rowcount
        elif bulk_update:
                res = db.session.bulk_update_mappings(get_mapper(my_table), data)
                db.session.commit()
        else:
            res = conn.execute(my_table.update(), data).rowcount
    db.engine.dispose()  # close the connection pool
    return res


def db_delete(table_name, data, filters=None):
    my_table = db.metadata.tables[table_name]
    with db.engine.connect() as conn:
        if filters:
            res = conn.execute(my_table.delete().filter(*filters), data).rowcount
        else:
            res = conn.execute(my_table.delete(), data).rowcount
    db.engine.dispose()  # close the connection pool
    return res
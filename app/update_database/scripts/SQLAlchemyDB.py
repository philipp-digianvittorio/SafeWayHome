from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import get_mapper
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, BigInteger
from datetime import datetime
from settings import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()


################################################################################################
### -- Define Database Tables -------------------------------------------------------------- ###
################################################################################################

class Headquarters(Base):

    # -- declare table name
    __tablename__ = 'Headquarters'

    # -- declare columns
    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(200), nullable=False)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Cities(Base):

    # -- declare table name
    __tablename__ = 'Cities'

    # -- declare columns
    id = Column(Integer, primary_key=True)
    hq_id = Column(String(100), ForeignKey('Headquarters.id'), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    zip_code = Column(String(200), nullable=True)
    full_name = Column(String(100), nullable=True)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Articles(Base):

    # -- declare table name
    __tablename__ = 'Articles'

    # -- declare columns
    id = Column(String(100), primary_key=True)
    hq_id = Column(String(100), ForeignKey('Headquarters.id'), nullable=False)
    hq_name = Column(String(100), nullable=False)
    headline = Column(String(1000), nullable=False)
    article = Column(String(5000), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    url = Column(String(200), nullable=False)
    date = Column(String(50), nullable=False)
    kw_location = Column(String(1000))
    kw_topic = Column(String(1000))

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Crimes(Base):

    # -- declare table name
    __tablename__ = 'Crimes'

    # -- declare columns
    id = Column(Integer, primary_key=True)
    u = Column(BigInteger, nullable=False)
    v = Column(BigInteger, nullable=False)
    key = Column(BigInteger, nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    zip_code = Column(String(100), nullable=True)
    street = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    lat = Column(String(100), nullable=False)
    long = Column(String(100), nullable=False)
    tötungsdelikt = Column(Boolean, nullable=False)
    sexualdelikt = Column(Boolean, nullable=False)
    körperverletzung = Column(Boolean, nullable=False)
    raub = Column(Boolean, nullable=False)
    diebstahl = Column(Boolean, nullable=False)
    drogendelikt = Column(Boolean, nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})


class Nodes(Base):

    # -- declare table name
    __tablename__ = 'Nodes'
    # -- declare columns
    id = Column(Integer, primary_key=True)
    osmid = Column(BigInteger)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    y = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    highway = Column(String(100), nullable=True)
    street_count = Column(Integer, nullable=True)
    ref = Column(String(100), nullable=True)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



class Edges(Base):

    # -- declare table name
    __tablename__ = 'Edges'

    # -- declare columns
    id = Column(Integer, primary_key=True)
    u = Column(BigInteger, nullable=False)
    v = Column(BigInteger, nullable=False)
    key = Column(BigInteger, nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)
    district_u = Column(String(100), nullable=True)
    district_v = Column(String(100), nullable=True)
    park_flag = Column(Boolean, nullable=True, default=False)
    industrial_flag = Column(Boolean, nullable=True, default=False)
    highway = Column(String(100), nullable=True)
    maxspeed = Column(String(100), nullable=True)
    oneway = Column(Boolean, nullable=True)
    reversed = Column(Boolean, nullable=True)
    length = Column(Float, nullable=True)
    ref = Column(String(100), nullable=True)
    geometry = Column(String(10000), nullable=False)
    lat_long = Column(String(5000), nullable=False)
    score_neutral = Column(Float, nullable=True)
    score_positive = Column(Float, nullable=True)
    score_very_positive = Column(Float, nullable=True)
    score_negative = Column(Float, nullable=True)
    score_very_negative = Column(Float, nullable=True)
    weight_neutral = Column(Float, nullable=False)
    weight_positive = Column(Float, nullable=False)
    weight_very_positive = Column(Float, nullable=False)
    weight_negative = Column(Float, nullable=False)
    weight_very_negative = Column(Float, nullable=False)

    # -- return a list of table column names
    @classmethod
    def _get_columns(cls):
        return [key for key, val in vars(cls).items() if not key.startswith("_")]

    # -- define print format
    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, {key: val for key, val in self.__dict__.items() if key != "_sa_instance_state"})



################################################################################################
### -- Declare Schema and Session  --------------------------------------------------------- ###
################################################################################################

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


################################################################################################
### -- Modify Database  -------------------------------------------------------------------- ###
################################################################################################


def db_select(table_name, filters=None):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        if filters:
            res = session.execute(my_table.select().filter(*filters)).mappings().all()
        else:
            res = session.execute(my_table.select()).mappings().all()
    res = [dict(x) for x in res]
    return res


def db_insert(table_name, data):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        res = session.execute(my_table.insert(), data)
        #new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
        session.commit()
    return res.lastrowid


def db_update(table_name, data, filters=None, bulk_update=False):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        if filters:
            res = session.execute(my_table.update().filter(*filters), data).rowcount
        elif bulk_update:
            res = session.bulk_update_mappings(get_mapper(my_table), data)
        else:
            res = session.execute(my_table.update(), data).rowcount
        # new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
        session.commit()

    return res


def db_delete(table_name, data, filters=None):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        if filters:
            res = session.execute(my_table.delete().filter(*filters), data).rowcount
        else:
            res = session.execute(my_table.delete(), data).rowcount
        # new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
        session.commit()

    return res


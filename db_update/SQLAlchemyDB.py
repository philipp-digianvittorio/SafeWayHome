from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from datetime import datetime


db_name = "db"  # "mysql_db"
engine = create_engine(f"sqlite:///app/instance/{db_name}.db", echo=False)
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


class Articles(Base):

    # -- declare table name
    __tablename__ = 'Articles'

    # -- declare columns
    id = Column(String(100), primary_key=True)
    hq_id = Column(String(100), ForeignKey('Headquarters.id'), nullable=False)
    hq_name = Column(String(100), ForeignKey('Headquarters.name'), nullable=False)
    headline = Column(String(1000), nullable=False)
    article = Column(String(50000), nullable=False)
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


################################################################################################
### -- Declare Schema and Session  --------------------------------------------------------- ###
################################################################################################

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


################################################################################################
### -- Modify Database  -------------------------------------------------------------------- ###
################################################################################################


def db_select(table_name, filters):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        res = session.execute(my_table.select().filter(*filters)).mappings().all()
    res = [dict(x) for x in res]
    return res


def db_insert(table_name, data):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        res = session.execute(my_table.insert(), data)
        #new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
        session.commit()
    return res.lastrowid


def db_update(table_name, data, filters):
    my_table = Base.metadata.tables[table_name]
    with Session() as session:
        res = session.execute(my_table.update().filter(*filters), data).rowcount
        # new_entry = conn.execute(my_table.insert().returning(my_table), data).fetchall() # return inserted row, not supported by sqlite
        session.commit()

    return res


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from .app import Newgrace as app


Base = declarative_base()

class Thredds(Base):
    '''
    Thredds SQLAlchemy DB Model
    '''
    __tablename__ = 'thredds'

    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    username = Column(String)
    password = Column(String)

    def __init__(self, name, url, username, password):
        self.name = name
        self.url = url
        self.username = username
        self.password = password

class Region(Base):
    '''
    Region SQLAlchemy DB Model
    '''

    __tablename__ = 'region'

    # Table Columns

    id = Column(Integer, primary_key=True)
    thredds_id = Column(Integer, ForeignKey('thredds.id'))
    display_name = Column(String)
    latlon_bbox = Column(String)
    reg_area = Column(Float)


    def __init__(self, thredds_id,display_name,latlon_bbox,reg_area):
        """
        Constructor for the table
        """
        self.thredds_id = thredds_id
        self.display_name = display_name
        self.latlon_bbox = latlon_bbox
        self.reg_area = reg_area

def init_grace_db(engine,first_time):
    Base.metadata.create_all(engine)
    # if first_time:
    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()
    session.close()

def init_gracefo_db(engine,first_time):
    Base.metadata.create_all(engine)
    # if first_time:
    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()
    session.close()

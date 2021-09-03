from geoalchemy2 import Geometry
from sqlalchemy import (Column,
                        Integer,
                        Boolean,
                        Float,
                        String,
                        UniqueConstraint,
                        JSON,
                        ForeignKey,
                        Index,
                        Sequence)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (sessionmaker,
                            relationship,
                            backref)

Base = declarative_base()

AQUIFER_ID_SEQ = Sequence('aquifer_id_seq')
WELL_ID_SEQ = Sequence('well_id_seq')


# SQLAlchemy ORM definition for the Regions Table
class Region(Base):
    """
    SQLAlchemy GW Database table
    """
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    region_name = Column(String)
    geometry = Column(Geometry('GEOMETRY', srid=4326))

    def __init__(self, region_name, geometry):
        """
        Constructor
        """

        self.region_name = region_name
        self.geometry = 'SRID=4326;{0}'.format(geometry)


class Aquifer(Base):
    """
    SQLAlchemy Aquifer Database table
    """
    __tablename__ = 'aquifer'

    id = Column(Integer, AQUIFER_ID_SEQ, primary_key=True, server_default=AQUIFER_ID_SEQ.next_value())
    aquifer_id = Column(String)
    region_id = Column(Integer, ForeignKey('region.id'))
    aquifer_name = Column(String)
    geometry = Column(Geometry('GEOMETRY', srid=4326))
    aq_index = Index('aq_index', "id", "aquifer_id")

    region = relationship(Region,
                          primaryjoin='Region.id==Aquifer.region_id',
                          backref=backref('regions',
                                          cascade='delete,all'))
    
    __table_args__ = (UniqueConstraint('region_id', 'aquifer_id', name='_aquifer_uc'),)

    def __init__(self, region_id, aquifer_name, aquifer_id, geometry):
        """
        Constructor
        """
        self.region_id = region_id
        self.aquifer_name = aquifer_name
        self.aquifer_id = aquifer_id
        self.geometry = 'SRID=4326;{0}'.format(geometry)


class Well(Base):
    """
    SQLAlchemy Variable Database table
    """

    __tablename__ = 'well'
    id = Column(Integer, WELL_ID_SEQ, primary_key=True, server_default=WELL_ID_SEQ.next_value())
    aquifer_id = Column(Integer, ForeignKey('aquifer.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    geometry = Column(Geometry('POINT', srid=4326))
    well_id = Column(String)
    well_name = Column(String)
    gse = Column(Float)
    outlier = Column(Boolean)
    attr_dict = Column(JSON)

    well_index = Index('well_index', "well_id", "id")

    __table_args__ = (UniqueConstraint('aquifer_id', 'well_id', name='_well_uc'),)
    aquifer = relationship(Aquifer,
                           primaryjoin='Well.aquifer_id==Aquifer.id',
                           backref=backref('aquifers',
                                           cascade='delete,all'))

    def __init__(self, aquifer_id, latitude, longitude, well_id, well_name, gse, outlier, attr_dict):
        self.aquifer_id = aquifer_id
        self.latitude = latitude
        self.longitude = longitude
        self.well_id = well_id
        self.well_name = well_name
        self.gse = gse
        self.attr_dict = attr_dict
        self.outlier = outlier
        self.geometry = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)


class Measurement(Base):

    __tablename__ = 'measurement'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('well.id'))
    variable_id = Column(Integer, ForeignKey('variable.id'))
    ts_time = Column(String)
    ts_value = Column(Float)
    ts_format = Column(String)
    ts_index = Index('ts_index', "well_id", "variable_id")

    well = relationship(Well,
                        primaryjoin='Well.id==Measurement.well_id',
                        backref=backref('wells',
                                        cascade='delete,all'))

    def __init__(self, well_id, variable_id, ts_time, ts_value, ts_format):
        self.well_id = well_id
        self.variable_id = variable_id
        self.ts_time = ts_time
        self.ts_value = ts_value
        self.ts_format = ts_format


class Variable(Base):
    """
    SQLAlchemy Variable Database table
    """

    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    units = Column(String)
    description = Column(String)

    def __init__(self, name, units, description):
        self.name = name
        self.units = units
        self.description = description


def init_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Create all the tables
    Base.metadata.create_all(engine)

    # Add data
    if first_time:
        # Make session
        Session = sessionmaker(bind=engine)
        session = Session()
        session.commit()
        session.close()

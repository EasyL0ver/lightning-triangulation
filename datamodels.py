from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATE, TIME, FLOAT, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship
import common
import numpy as np
import geopy as gp
import converter
Base = declarative_base()


class File(Base):
    def __init__(self):
        self.dataarr = [None] * 4
        self.dataloaded = False
        self.cachedatamodified = False

    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    headerHash = Column(BLOB(64), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    date = Column(DATE, nullable=False)
    time = Column(TIME, nullable=False)
    fsample = Column(Integer, nullable=False)
    expectedlen = Column(Integer, nullable=False)
    eventscreated = Column(Integer, nullable=False)
    mid_adc = Column(FLOAT, nullable=False)
    conv_fac = Column(FLOAT, nullable=False)
    filepath = Column(String(64), nullable=True)
    filename = Column(String(64), nullable=True)

    location = relationship("Location")

    dat1type = Column(String(64), nullable=True)
    dat1 = deferred(Column(BLOB(250000), nullable=True))

    dat2type = Column(String(64), nullable=True)
    dat2 = deferred(Column(BLOB(250000), nullable=True))



    def getdataarr(self):
        if not self.dataloaded:
            if self.dat1:
                self.dataarr[0] = common.binarytonp(self.dat1, self.mid_adc, self.conv_fac)
                self.dataloaded = True
            if self.dat2:
                self.dataarr[1] = common.binarytonp(self.dat2, self.mid_adc, self.conv_fac)
                self.dataloaded = True
            if not self.dat1 and not self.dat2 and filepath and filename:
                #try load from txt file
                try:
                    d_file = open(self.filepath + "/" + self.filename, mode='rb')
                    file = d_file.read()
                    matrix = (converter.readrawdata(file).astype(np.float64) - self.mid_adc) / self.conv_fac
                    self.dataarr[0] = matrix[0,]
                    self.dataarr[1] = matrix[1,]
                    self.dataloaded = True
                except IOError as e:
                    print("DB from txt load failure")

            self.cachedatamodified = False
        return self.dataarr


class Observation(Base):
    __tablename__ = 'observation'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=True)
    file_id = Column(Integer, ForeignKey("file.id"), nullable=True)
    sample = Column(Integer, nullable=False)
    firstsample = Column(Integer, nullable=False)
    samplelen = Column(Integer, nullable=False)
    assigned_event_id = Column(Integer, ForeignKey("event.id"), nullable=True)
    sn_max_value = Column(FLOAT, nullable=False)
    ew_max_value = Column(FLOAT, nullable=False)



    file = relationship("File")
    assigned_event = relationship("Event", foreign_keys=assigned_event_id)

    def getpwr(self):
        return np.sqrt(np.power(self.sn_max_value, 2) + np.power(self.ew_max_value, 2))


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    time_zone = Column(Integer, nullable=False)
    longitude = Column(FLOAT, nullable=True)
    latitude = Column(FLOAT, nullable=True)
    reqionfreq = Column(Integer, nullable=True)

    def getpoint(self):
        return gp.Point(longitude=self.longitude, latitude=self.latitude)


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)

    obs1_id = Column(Integer, ForeignKey("observation.id"))
    obs2_id = Column(Integer, ForeignKey("observation.id"))
    obs3_id = Column(Integer, ForeignKey("observation.id"))

    ob1_angle = Column(FLOAT, nullable=True)
    ob2_angle = Column(FLOAT, nullable=True)
    ob3_angle = Column(FLOAT, nullable=True)

    #positive polarity lolcations
    pos_loc_lat = Column(FLOAT, nullable=True)
    pos_loc_lon = Column(FLOAT, nullable=True)

    #negative polarity locations
    neg_loc_lat = Column(FLOAT, nullable=True)
    neg_loc_lon = Column(FLOAT, nullable=True)

    obs1 = relationship("Observation", foreign_keys=[obs1_id])
    obs2 = relationship("Observation", foreign_keys=[obs2_id])
    obs3 = relationship("Observation", foreign_keys=[obs3_id])

    polarity = Column(Integer, nullable=True)

    #tutaj wchodza wszystkei dane z triangularyzacji
    def getobsarr(self):
        obsarr=[3];
        obsarr[0] = self.obs1_id;
        obsarr[1] = self.obs2_id;
        obsarr[2] = self.obs3_id;
        return obsarr




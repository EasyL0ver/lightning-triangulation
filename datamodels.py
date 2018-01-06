from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATE, TIME, FLOAT, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship
import common
import numpy as np
import geopy as gp
import converter
from Modules.linelement import DataBus
Base = declarative_base()


class File(Base):
    def __deepcopy__(self, memodict={}):
        return self

    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    headerHash = Column(BLOB(64), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    date = Column(DATE, nullable=False)
    time = Column(TIME, nullable=False)
    fsample = Column(FLOAT, nullable=False)
    expectedlen = Column(Integer, nullable=False)
    eventscreated = Column(Integer, nullable=False)
    mid_adc = Column(FLOAT, nullable=False)
    conv_fac = Column(FLOAT, nullable=False)
    filepath = Column(String(128), nullable=True)
    filename = Column(String(128), nullable=True)

    location = relationship("Location")

    dat1type = Column(String(64), nullable=True)
    dat1 = deferred(Column(BLOB(250000), nullable=True))

    dat2type = Column(String(64), nullable=True)
    dat2 = deferred(Column(BLOB(250000), nullable=True))

    def load_data(self):
        databus = DataBus()
        #lazy loading
        loaded_dat1 = self.dat1
        loaded_dat2 = self.dat2
        if loaded_dat1 is None or loaded_dat2 is None:
            #try to load data
            try:
                d_file = open(self.filepath + "/" + self.filename, mode='rb')
            except IOError as e:
                common.conversionLog.reportFailure(e.strerror)
                return

            loaded_file = d_file.read()
            output_matrix = converter.read_raw_data(loaded_file)

            if output_matrix[0, -1] == 0:
                output_matrix = output_matrix[0:2, 0:self.expectedwidth - 1]

            # TODO THESE ARE TO BE SWITCHED
            databus.data['sn'] = (output_matrix[0, ] - self.mid_adc)/self.conv_fac
            databus.data['ew'] = (output_matrix[1, ] - self.mid_adc)/self.conv_fac
        else:
            databus.data['sn'] = common.binarytonp(loaded_dat1, self.mid_adc, self.conv_fac)
            databus.data['ew'] = common.binarytonp(loaded_dat2, self.mid_adc, self.conv_fac)
        databus.data['file'] = self
        return databus


class Observation(Base):
    __tablename__ = 'observation'
    id = Column(Integer, primary_key=True)
    certain = Column(FLOAT, nullable=True)
    event_type = Column(String(64), nullable=True)
    file_id = Column(Integer, ForeignKey("file.id"), nullable=True)
    sample = Column(Integer, nullable=False)
    firstsample = Column(Integer, nullable=False)
    samplelen = Column(Integer, nullable=False)
    assigned_event_id = Column(Integer, ForeignKey("event.id"), nullable=True)
    sn_max_value = Column(FLOAT, nullable=False)
    ew_max_value = Column(FLOAT, nullable=False)

    file = relationship("File")
    assigned_event = relationship("Event", foreign_keys=assigned_event_id, post_update=True)

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

    def __deepcopy__(self, memodict={}):
        return self

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

    loc_lat = Column(FLOAT, nullable=True)
    loc_lon = Column(FLOAT, nullable=True)

    obs1 = relationship("Observation", foreign_keys=[obs1_id])
    obs2 = relationship("Observation", foreign_keys=[obs2_id])
    obs3 = relationship("Observation", foreign_keys=[obs3_id])

    def get_angles_locations(self):
        arr = []
        if self.ob1_angle:
            obs = self.obs1
            ang = self.ob1_angle
            arr.append({'obs': obs, 'ang': ang})
        if self.ob2_angle:
            obs = self.obs2
            ang = self.ob2_angle
            arr.append({'obs': obs, 'ang': ang})
        if self.ob3_angle:
            obs = self.obs3
            ang = self.ob3_angle
            arr.append({'obs': obs, 'ang': ang})
        return arr





import math

import geopy as gp
import numpy as np
from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATE, TIME, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.ext.hybrid import hybrid_property

import common
import converter
import datetime
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

    def get_datetime(self):
        return common.cmbdt(self.date, self.time)

    def load_data(self):
        data_bus = DataBus()
        # invoke lazy loading
        loaded_dat1 = self.dat1
        loaded_dat2 = self.dat2
        if loaded_dat1 is None or loaded_dat2 is None:
            # load from stored file path
            try:
                d_file = open(self.filepath + "/" + self.filename, mode='rb')
            except IOError as e:
                common.conversionLog.reportFailure(e.strerror)
                return

            loaded_file = d_file.read()
            output_matrix = converter.read_raw_data(loaded_file)

            if output_matrix[0, -1] == 0:
                output_matrix = output_matrix[0:2, 0:self.expectedwidth - 1]

            data_bus.data['sn'] = (output_matrix[0, ] - self.mid_adc)/self.conv_fac
            data_bus.data['ew'] = (output_matrix[1, ] - self.mid_adc)/self.conv_fac
        else:
            # load from db blob
            data_bus.data['sn'] = common.binarytonp(loaded_dat1, self.mid_adc, self.conv_fac)
            data_bus.data['ew'] = common.binarytonp(loaded_dat2, self.mid_adc, self.conv_fac)
        data_bus.data['file'] = self
        return data_bus

    def load_range(self, start_time, stop_time):
        bus = self.load_data()
        start_delta = start_time - common.cmbdt(self.date, self.time)
        var = start_delta.total_seconds()
        start_index = int(math.ceil(start_delta.total_seconds() * self.fsample))
        end_delta = stop_time - common.cmbdt(self.date, self.time)
        end_index = int(math.ceil(end_delta.total_seconds() * self.fsample))

        if start_index < 0:
            start_index = 0
        if end_index > len(bus['sn']) - 1:
            end_index = len(bus['sn']) - 1

        cropped_bus = DataBus()
        # crop
        sn_array = bus['sn']
        ew_array = bus['ew']
        cropped_bus['sn'] = sn_array[start_index:end_index]
        cropped_bus['ew'] = ew_array[start_index:end_index]
        cropped_bus['file'] = bus['file']

        return cropped_bus


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

    def get_start_time(self):
        return common.cmbdt(self.file.date, self.file.time) + datetime.timedelta(seconds=(float(self.firstsample) / self.file.fsample))

    def get_data(self):
        data_bus = DataBus()
        file_bus = self.file.load_data()
        data_bus['sn'] = file_bus['sn'][self.firstsample:self.firstsample + self.samplelen]
        data_bus['ew'] = file_bus['ew'][self.firstsample:self.firstsample + self.samplelen]
        data_bus.data['file'] = self.file
        data_bus['obs_single'] = self
        return data_bus


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

    index_date = Column(DATE, nullable=False)
    index_time = Column(TIME, nullable=False)

    def get_data(self):
        data_bus = DataBus()
        data_bus['ev_single'] = self
        return data_bus


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





from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATE, TIME, DECIMAL, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship
import common
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

    location = relationship("Location")

    dat1type = Column(String(64), nullable=True)
    dat1 = deferred(Column(BLOB(250000), nullable=True))

    dat2type = Column(String(64), nullable=True)
    dat2 = deferred(Column(BLOB(250000), nullable=True))

    dat3type = Column(String(64), nullable=True)
    dat3 = deferred(Column(BLOB(250000), nullable=True))

    dat4type = Column(String(64), nullable=True)
    dat4 = deferred(Column(BLOB(250000), nullable=True))

    def getdataarr(self):
        if not self.dataloaded:
            if self.dat1:
                self.dataarr[0] = common.binarytonp(self.dat1)
            if self.dat2:
                self.dataarr[1] = common.binarytonp(self.dat2)
            if self.dat3:
                self.dataarr[2] = common.binarytonp(self.dat3)
            if self.dat4:
                self.dataarr[3] = common.binarytonp(self.dat4)
            self.dataloaded = True
            self.cachedatamodified = False
        return self.dataarr


class Observation(Base):
    __tablename__ = 'observation'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=True)
    file_id = Column(Integer, ForeignKey("file.id"))
    sample = Column(Integer, nullable=False)
    firstsample = Column(Integer, nullable=False)
    samplelen = Column(Integer, nullable=False)
    is_assigned = Column(Integer, nullable=False)

    file = relationship("File")


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    time_zone = Column(Integer, nullable=False)
    xcords = Column(Integer, nullable=True)
    ycords = Column(Integer, nullable=True)


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)

    obs1_id = Column(Integer, ForeignKey("observation.id"))
    obs2_id = Column(Integer, ForeignKey("observation.id"))
    obs3_id = Column(Integer, ForeignKey("observation.id"))

    obs1 = relationship("Observation", foreign_keys=[obs1_id])
    obs2 = relationship("Observation", foreign_keys=[obs2_id])
    obs3 = relationship("Observation", foreign_keys=[obs3_id])

    #tutaj wchodza wszystkei dane z triangularyzacji



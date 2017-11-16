from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATE, TIME, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred
import datetime as dt
Base = declarative_base()

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    headerHash = Column(BLOB(64), nullable=False)
    #foreign key dla lokacji ?
    location = Column(String(64), nullable=False)
    timezone = Column(Integer, nullable=False)
    date = Column(DATE, nullable=False)
    time = Column(TIME, nullable=False)
    fsample = Column(Integer, nullable=False)
    expectedlen = Column(Integer, nullable=False)

    dat1type = Column(String(64), nullable=True)
    dat1 = deferred(Column(BLOB(250000), nullable=True))

    dat2type = Column(String(64), nullable=True)
    dat2 = deferred(Column(BLOB(250000), nullable=True))

    dat3type = Column(String(64), nullable=True)
    dat3 = deferred(Column(BLOB(250000), nullable=True))

    dat4type = Column(String(64), nullable=True)
    dat4 = deferred(Column(BLOB(250000), nullable=True))





#class Data(Base):
#    __tablename__ = 'data'
#    id = Column(Integer, primary_key=True)
#    fsample = Column(Integer, primary_key=True)
#    type = Column(String(100), nullable=False)
#    #tutaj dane
#   file_id = Column(Integer, ForeignKey('file.id'))

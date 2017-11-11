from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred
Base = declarative_base()

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    headerHash = Column(BLOB(64), nullable=False)
    location = Column(String(64), nullable=False)
    date = Column(String(64), nullable=False)
    time = Column(String(64), nullable=False)
    exacttime = Column(Integer, nullable=False)
    extactlen = Column(Integer, nullable=False)
    dat1 = deferred(Column(String(250000), nullable=True))
    dat2 = deferred(Column(String(250000), nullable=True))






    #data = relationship('Data', backref='file')


#class Data(Base):
#    __tablename__ = 'data'
#    id = Column(Integer, primary_key=True)
#    fsample = Column(Integer, primary_key=True)
#    type = Column(String(100), nullable=False)
#    #tutaj dane
#   file_id = Column(Integer, ForeignKey('file.id'))

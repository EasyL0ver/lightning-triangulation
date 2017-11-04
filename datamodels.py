from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    headerHash = Column(String(64), nullable=False)
    location = Column(String(64), nullable=False)
    date = Column(String(64), nullable=False)
    time = Column(String(64), nullable=False)
    exacttime = Column(Integer, nullable=False)
    extactlen = Column(Integer, nullable=False)
    dat1 = Column(String(250000), nullable=False)
    dat2 = Column(String(250000), nullable=False)


def mapstructtofile(datastruct):
    file = File()
    file.headerHash = datastruct.headerhash
    file.location = datastruct.location
    file.date = datastruct.date
    file.time = datastruct.time
    file.exacttime = datastruct.initTime
    file.extactlen = datastruct.timelen
    file.dat1 = "prusac"
    file.dat2 = "maly"


    return file;





    #data = relationship('Data', backref='file')


#class Data(Base):
#    __tablename__ = 'data'
#    id = Column(Integer, primary_key=True)
#    fsample = Column(Integer, primary_key=True)
#    type = Column(String(100), nullable=False)
#    #tutaj dane
#   file_id = Column(Integer, ForeignKey('file.id'))

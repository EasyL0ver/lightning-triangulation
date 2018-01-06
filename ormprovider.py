import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datamodels import Base
import datamodels as dm


class DataProvider(object):

    def __init__(self, createmodel):
        #for testing
        if createmodel and os.path.exists('test.db'):
            os.remove('test.db')

        #echo for logging, switch off in final version ?
        self.db = create_engine('sqlite:///test.db')
        self.active_session = None

        Base.metadata.create_all(self.db)

        if createmodel:
            self.initializefields()

    def get_session(self):
        if not self.active_session:
            DBSession = sessionmaker(bind=self.db)
            self.active_session = DBSession()
        return self.active_session



    def initializefields(self):
        stacjatest = dm.Location()
        stacjatest.name = "Hylaty"
        stacjatest.time_zone = 0
        stacjatest.latitude = 49.2035
        stacjatest.longitude = 22.54381
        stacjatest.reqionfreq = 50

        stacjatest2 = dm.Location()
        stacjatest2.name = "Patagonia"
        stacjatest2.time_zone = 0
        stacjatest2.latitude = -51.590
        stacjatest2.longitude = -69.3197
        stacjatest2.reqionfreq = 60

        stacjatest3 = dm.Location()
        stacjatest3.name = "Hugo"
        stacjatest3.time_zone = 0
        stacjatest3.latitude = 38.892
        stacjatest3.longitude = -103.406
        stacjatest3.reqionfreq = 60

        self.get_session().add(stacjatest)
        self.get_session().add(stacjatest2)
        self.get_session().add(stacjatest3)
        self.get_session().commit()




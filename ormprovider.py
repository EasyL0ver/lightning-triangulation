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
        self.activesession = None

        Base.metadata.create_all(self.db)

        if createmodel:
            self.initializefields()

    def getActiveSession(self):
        if not self.activesession:
            DBSession = sessionmaker(bind=self.db)
            self.activesession = DBSession()
        return self.activesession



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


        self.getActiveSession().add(stacjatest)
        self.getActiveSession().add(stacjatest2)
        self.getActiveSession().add(stacjatest3)
        self.getActiveSession().commit()




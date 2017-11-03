import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datamodels import Base


class DataProvider(object):

    def __init__(self):
        #for testing
        if os.path.exists('test.db'):
            os.remove('test.db')
        self.db = create_engine('sqlite:///test.db')

        Base.metadata.create_all(self.db)

    def getActiveSession(self):
        BDSesja = sessionmaker(bind=self.db)
        return BDSesja()





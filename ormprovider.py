import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datamodels import Base


class DataProvider(object):

    def __init__(self):
        #for testing
        if os.path.exists('test.db'):
           os.remove('test.db')

        #echo for logging, switch off in final version ?
        self.db = create_engine('sqlite:///test.db')
        self.activesession = None

        Base.metadata.create_all(self.db)

    def getActiveSession(self):
        if not self.activesession:
            DBSession = sessionmaker(bind=self.db)
            self.activesession = DBSession()
        return self.activesession






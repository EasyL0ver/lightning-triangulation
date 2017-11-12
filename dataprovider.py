import InputConverter as ic
import os
import common
import datamodels as dm
import datetime as dt

class DataProvider:
    def __init__(self,currentdbsession):
        self.datasources = []
        self.converter = ic.InputConverter(65536/2, 19.54)
        self.currentdbsession = currentdbsession
        self.loadeddata = []

    def loaddata(self):
        print("Loading data")
        print("Loading header hashes from DB")
        #todo try catch
        hashes = self.currentdbsession.query(dm.File.headerHash).all()
        for i in range(0, len(self.datasources)):
            files = os.listdir(self.datasources[i])
            print("Converting files in: " + self.datasources[i])
            converted = False
            for o in range(0, len(files)):
                if self.issupported(files[o]):
                    cl = common.ConversionError()
                    header = self.converter.readheader(self.datasources[i], files[o], cl)
                    if not contains(hashes, header.headerHash):
                        data = self.converter.convert(self.datasources[i], files[o], cl)
                        if cl.conversionSucces:
                            print("Conversion of: " + files[o] + " successful")
                            converted = True
                            self.currentdbsession.add(data)
                        else:
                            print("Conversion of: " + files[o] + " failed: " + cl.conversionErrorLog )

            #todo try catch block
            if converted:
                print("Flushing db changes")
                self.currentdbsession.commit()
            pass

    def issupported(self, fil):
        return fil.endswith('.dat')

    def populate(self):
        print("Loading data from db")
        self.loadeddata = self.currentdbsession.query(dm.File).all()

    def getfileswithrange(self, rangestart, sectimelen):
        print("Checking if data exist : " + rangestart + " with length: " + sectimelen)
        fileswithrange = []
        rangeend = rangestart + dt.timedelta(seconds=sectimelen)
        for data in self.loadeddata:
            filestart = data.date + data.time
            fileend = filestart + dt.timedelta(seconds=float(data.expectedlen)/data.fsample)
            if (filestart < rangestart < fileend) or (filestart < rangeend < fileend):
                fileswithrange.append(data)
        return fileswithrange

















def contains(collection, element):
    for e in collection:
        if e[0] == element:
            return True
    return False






import InputConverter as ic
import os
import common
import datamodels as dm
import datetime as dt
import numpy as np
import math

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

    def getfileswithrange(self, rangestart, rangeend):
        #print("Checking if data exist : " + rangestart + " with length: " + sectimelen)
        fileswithrange = []
        for data in self.loadeddata:
            filestart =dt.datetime.combine(data.date, data.time)
            fileend = filestart + dt.timedelta(seconds=float(data.expectedlen)/data.fsample)
            if (filestart < rangestart < fileend) or (filestart < rangeend < fileend) or (filestart >= rangestart and fileend <= rangeend):
                fileswithrange.append(data)
        return fileswithrange

    def getunique(self,filerange):
        uniquelocs=[]
        for file in filerange:
            if not file.location in uniquelocs:
                uniquelocs.append(file.location)
        return uniquelocs


    def getdata(self, rangestart, sectimelen):
        rangeend = rangestart + dt.timedelta(seconds=sectimelen)
        fileswithrange = self.getfileswithrange(rangestart,rangeend)
        uniquelocs = self.getunique(fileswithrange)


        data = []
        for loc in uniquelocs:
            fileswithloc = []
            for file in fileswithrange:
                if file.location == loc:
                    fileswithloc.append(file)

            fileswithloc.sort(key=lambda r: dt.datetime.combine(r.date, r.time))
            #actual glueing starts here
            glueddata1 = []
            glueddata2 = []

            for i in range(0, len(fileswithloc)):
                if i == 0:
                    timediff = dt.datetime.combine(fileswithloc[0].date, fileswithloc[0].time) - rangestart
                    nanvectorl = int(math.floor(timediff.total_seconds() * fileswithloc[0].fsample))
                else:
                    previous = fileswithloc[i-1]
                    current = fileswithloc[i]
                    prevtime = common.cmbdt(previous.date,previous.time) + dt.timedelta(seconds=float(previous.expectedlen)/previous.fsample)
                    timediff = prevtime - common.cmbdt(current.date,current.time)
                    nanvectorl = int(math.floor(timediff.total_seconds() * fileswithloc[i].fsample))

                #glueddata1 = glueddata1 + [np.nan] * nanvectorl
                #glueddata2 = glueddata2 + [np.nan] * nanvectorl
                glueddata1 = glueddata1 + common.binarytonp(fileswithloc[i].dat1).tolist()
                glueddata2 = glueddata2 + common.binarytonp(fileswithloc[i].dat2).tolist()

            current = fileswithloc[i]
            timediff = rangeend - common.cmbdt(current.date, current.time)
            nanvectorl = int(math.floor(timediff.total_seconds() * fileswithloc[i].fsample))
            glueddata1 = glueddata1 + [np.nan] * nanvectorl
            glueddata2 = glueddata2 + [np.nan] * nanvectorl

            data.append(dict(location=loc, dat1=glueddata1, dat2=glueddata2))

        return data



def contains(collection, element):
    for e in collection:
        if e[0] == element:
            return True
    return False






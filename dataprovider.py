import converter as ic
import os
import common
import datamodels as dm
import datetime as dt
import numpy as np
import math


class DataProvider:
    def __init__(self, currentdbsession):
        self.datasources = []
        self.currentdbsession = currentdbsession
        self.loadeddata = []


        #testing
        self.prepareTestDB()
        #

    def loaddata(self):
        print("Loading data")
        print("Loading header hashes from DB")
        #todo try catch
        hashes = self.currentdbsession.query(dm.File.headerHash).all()
        locations = self.currentdbsession.query(dm.Location).all()
        for i in range(0, len(self.datasources)):
            files = os.listdir(self.datasources[i]['filepath'])
            print("Converting files in: " + self.datasources[i]['filepath'])
            converted = False
            for o in range(0, len(files)):
                if self.issupported(files[o]):
                    cl = common.ConversionError()
                    header = ic.readheader(self.datasources[i]['filepath'], files[o], cl)
                    if not contains(hashes, header.headerHash):
                        #resolve location
                        thisloc = [x for x in locations if x.name == self.datasources[i]['locname']][0]
                        if not thisloc:
                            raise ValueError('No valid location in DB')
                        data = ic.convert(self.datasources[i]['filepath'], files[o], cl,
                                                      65536 / 2, 19.54, thisloc)
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
        #TODO DOUBLE CHECK FOR SAMPLING FREQUENCY ?
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
            currenttime = rangestart
            for i in range(0, len(fileswithloc)):
                previous = fileswithloc[i - 1]
                current = fileswithloc[i]
                if i == 0:
                    timediff = dt.datetime.combine(fileswithloc[0].date, fileswithloc[0].time) - rangestart
                else:
                    prevtime = common.cmbdt(previous.date, previous.time) + dt.timedelta(seconds=float(previous.expectedlen)/previous.fsample)
                    timediff = prevtime - common.cmbdt(current.date, current.time)

                dat1 = common.binarytonp(fileswithloc[i].dat1,
                                         fileswithloc[i].mid_adc, fileswithloc[i].conv_fac).tolist()
                dat2 = common.binarytonp(fileswithloc[i].dat2,
                                         fileswithloc[i].mid_adc, fileswithloc[i].conv_fac).tolist()

                nanvectorl = int(math.floor(timediff.total_seconds() * current.fsample))
                if timediff.total_seconds() >= 0:
                    glueddata1 = glueddata1 + [np.nan] * nanvectorl
                    glueddata2 = glueddata2 + [np.nan] * nanvectorl
                    currenttime += dt.timedelta(seconds=float(nanvectorl) * current.fsample)
                else:
                    dat1 = dat1[0 - nanvectorl:len(dat1)]
                    dat2 = dat2[0 - nanvectorl:len(dat2)]

                glueddata1 = glueddata1 + dat1
                glueddata2 = glueddata2 + dat2
                currenttime += dt.timedelta(seconds=float(len(dat1)) / current.fsample)

                if currenttime > rangeend:
                    #crop end
                    td = currenttime - rangeend
                    samples = int(math.floor(td.total_seconds() * current.fsample))
                    glueddata1 = glueddata1[0:len(glueddata1) - samples]
                    glueddata2 = glueddata2[0:len(glueddata2) - samples]
                else:
                    current = fileswithloc[i]
                    timediff = rangeend - common.cmbdt(current.date, current.time)
                    nanvectorl = int(math.floor(timediff.total_seconds() * fileswithloc[i].fsample))
                    glueddata1 = glueddata1 + [np.nan] * nanvectorl
                    glueddata2 = glueddata2 + [np.nan] * nanvectorl

            data.append(dict(location=loc, sn=glueddata1, ew=glueddata2, file=current))

        return data

    def prepareTestDB(self):
        stacjatest = dm.Location()
        stacjatest.name = "Stacja ELF ELA10"
        stacjatest.time_zone = -1
        stacjatest.latitude = 51
        stacjatest.longitude = 17

        stacjatest2 = dm.Location()
        stacjatest2.name = "Staaja ELF ELA10"
        stacjatest2.time_zone = -1
        stacjatest2.latitude = 52
        stacjatest2.longitude = 21


        self.currentdbsession.add(stacjatest)
        self.currentdbsession.add(stacjatest2)
        self.currentdbsession.commit()

def contains(collection, element):
    for e in collection:
        if e[0] == element:
            return True
    return False






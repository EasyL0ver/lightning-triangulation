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

    def loaddata(self, copy_raw):
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
                    data = ic.readheader(self.datasources[i]['filepath'], files[o], cl)
                    if not contains(hashes, data.headerHash):
                        #resolve location
                        thisloc = [x for x in locations if x.name == self.datasources[i]['locname']][0]
                        if not thisloc:
                            raise ValueError('No valid location in DB')
                        data = ic.convert(self.datasources[i]['filepath'],
                                          files[o], cl, 65536 / 2, 19.54, thisloc, unpack=copy_raw)
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

    def get_data(self, rangestart, sectimelen):
        range_end = rangestart + dt.timedelta(microseconds=sectimelen*1000000)
        fileswithrange = self.getfileswithrange(rangestart, range_end)
        uniquelocs = self.getunique(fileswithrange)

        data = []
        for loc in uniquelocs:
            fileswithloc = []
            for file in fileswithrange:
                if file.location == loc:
                    fileswithloc.append(file)

            fileswithloc.sort(key=lambda r: dt.datetime.combine(r.date, r.time))
            #actual glueing starts here
            glued_data_1 = []
            glued_data_2 = []
            current_time = rangestart
            for i in range(0, len(fileswithloc)):
                previous = fileswithloc[i - 1]
                current = fileswithloc[i]
                if i == 0:
                    time_diff = dt.datetime.combine(fileswithloc[0].date, fileswithloc[0].time) - rangestart
                else:
                    previous_time = common.cmbdt(previous.date, previous.time) + dt.timedelta(seconds=float(previous.expectedlen)/previous.fsample)
                    time_diff = previous_time - common.cmbdt(current.date, current.time)

                databus = fileswithloc[i].getbus()
                dat1 = databus.data['sn'].tolist()
                dat2 = databus.data['ew'].tolist()

                nan_vector_1 = int(math.floor(time_diff.total_seconds() * current.fsample))
                if time_diff.total_seconds() >= 0:
                    glued_data_1 = glued_data_1 + [np.nan] * nan_vector_1
                    glued_data_2 = glued_data_2 + [np.nan] * nan_vector_1
                    current_time += dt.timedelta(seconds=float(nan_vector_1) * current.fsample)
                else:
                    dat1 = dat1[0 - nan_vector_1:len(dat1)]
                    dat2 = dat2[0 - nan_vector_1:len(dat2)]

                glued_data_1 = glued_data_1 + dat1
                glued_data_2 = glued_data_2 + dat2
                current_time += dt.timedelta(seconds=float(len(dat1)) / current.fsample)

                if current_time > range_end:
                    #crop end
                    td = current_time - range_end
                    samples = int(math.floor(td.total_seconds() * current.fsample))
                    glued_data_1 = glued_data_1[0:len(glued_data_1) - samples]
                    glued_data_2 = glued_data_2[0:len(glued_data_2) - samples]
                else:
                    current = fileswithloc[i]
                    time_diff = range_end - common.cmbdt(current.date, current.time)
                    nan_vector_1 = int(math.floor(time_diff.total_seconds() * fileswithloc[i].fsample))
                    glued_data_1 = glued_data_1 + [np.nan] * nan_vector_1
                    glued_data_2 = glued_data_2 + [np.nan] * nan_vector_1

            data.append(dict(location=loc, sn=glued_data_1, ew=glued_data_2, file=current))

        return data


def contains(collection, element):
    for e in collection:
        if e[0] == element:
            return True
    return False






import converter as ic
import os
import common
import datamodels as dm
import datetime as dt
import numpy as np
import math


class DataProvider:
    def __init__(self, current_session):
        self.sources = []
        self.current_session = current_session
        self.loaded_data = []

    def load_data(self, copy_raw):
        print("Loading data")
        print("Loading header hashes from DB")
        #load locations and headers of existing data
        hashes = self.current_session.query(dm.File.headerHash).all()
        locations = self.current_session.query(dm.Location).all()
        for i in range(0, len(self.sources)):
            files = os.listdir(self.sources[i]['filepath'])
            print("Converting files in: " + self.sources[i]['filepath'])
            converted = False
            for o in range(0, len(files)):
                if self.issupported(files[o]):
                    cl = common.ConversionError()
                    data = ic.read_header(self.sources[i]['filepath'], files[o], cl)
                    if not contains(hashes, data.headerHash):
                        #resolve location
                        this_location = [x for x in locations if x.name == self.sources[i]['locname']][0]
                        if not this_location:
                            raise ValueError('No valid location in DB')
                        data = ic.convert(self.sources[i]['filepath'],
                                          files[o], cl, 65536 / 2, 19.54, this_location, unpack=copy_raw)
                        if cl.conversionSucces:
                            print("Conversion of: " + files[o] + " successful")
                            converted = True
                            self.current_session.add(data)
                        else:
                            print("Conversion of: " + files[o] + " failed: " + cl.conversionErrorLog )

            if converted:
                print("Flushing db changes")
                self.current_session.commit()
            pass

    def issupported(self, fil):
        return fil.endswith('.dat')

    def populate(self):
        print("Loading data from db")
        self.loaded_data = self.current_session.query(dm.File).all()

    def files_with_range(self, range_start, range_end):
        #print("Checking if data exist : " + rangestart + " with length: " + sectimelen)
        files_with_range = []
        for data in self.loaded_data:
            file_start = dt.datetime.combine(data.date, data.time)
            file_end = file_start + dt.timedelta(seconds=float(data.expectedlen)/data.fsample)
            if (file_start < range_start < file_end) or (file_start < range_end < file_end) or (file_start >= range_start and file_end <= range_end):
                files_with_range.append(data)
        return files_with_range

    def getunique(self, file_range):
        #TODO DOUBLE CHECK FOR SAMPLING FREQUENCY ?
        unique_locations = []
        for file in file_range:
            if not file.location in unique_locations:
                unique_locations.append(file.location)
        return unique_locations

    def get_data(self, range_start, second_time_length):
        range_end = range_start + dt.timedelta(microseconds=second_time_length * 1000000)
        files_in_range = self.files_with_range(range_start, range_end)
        unique_locations = self.getunique(files_in_range)

        data = []
        for loc in unique_locations:
            fileswithloc = []
            for file in files_in_range:
                if file.location == loc:
                    fileswithloc.append(file)

            fileswithloc.sort(key=lambda r: dt.datetime.combine(r.date, r.time))
            #actual glueing starts here
            glued_data_1 = []
            glued_data_2 = []
            current_time = range_start
            for i in range(0, len(fileswithloc)):
                previous = fileswithloc[i - 1]
                current = fileswithloc[i]
                if i == 0:
                    time_diff = dt.datetime.combine(fileswithloc[0].date, fileswithloc[0].time) - range_start
                else:
                    previous_time = common.cmbdt(previous.date, previous.time) + dt.timedelta(seconds=float(previous.expectedlen)/previous.fsample)
                    time_diff = previous_time - common.cmbdt(current.date, current.time)

                databus = fileswithloc[i].load_data()
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






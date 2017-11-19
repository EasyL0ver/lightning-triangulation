import struct
import numpy as np
import datamodels as dm
import datetime as dt
import io
import sqlite3
import common

class InputConverter:
    def __init__(self,midAdc,convFactor,locations):
        self.midAdc = midAdc
        self.convFactor = convFactor
        self.locations = locations

    def convert(self,filePath,fileName,conversionLog):
        try:
            d_file = open(filePath + "/" + fileName, mode='rb')
        except IOError as e:
            conversionLog.reportFailure(e.strerror)
            return
        file = d_file.read()
        datalen = len(file)
        datastruct = self.dcdheader(file[:64])
        expectedwidth = (datalen - 72)/4
        outputMatrix = np.zeros((2, expectedwidth))
        index = 0;
        for i in range(64, datalen-8, 4):
            e1, e2 = struct.unpack('>HH', file[i:i+4])
            outputMatrix[0, index] = (e1 - self.midAdc)/self.convFactor
            outputMatrix[1, index] = (e2 - self.midAdc)/self.convFactor
            index += 1

        datastruct.dat1 = common.nptobinary(outputMatrix[0, ])
        datastruct.dat2 = common.nptobinary(outputMatrix[1, ])
        datastruct.fsample = 800
        datastruct.expectedlen = expectedwidth

        return datastruct

    def readheader(self, filePath, fileName, conversionLog):
        try:
            d_file = open(filePath + "/" + fileName, mode='rb')
        except IOError as e:
            conversionLog.reportFailure(e.strerror)
            return
        return self.dcdheader(d_file.read(64))

    def dcdheader(self, header):
        thisloc = None
        for location in self.locations:
            if location.name == header[0:16]:
                thisloc = location

        timezone = thisloc.time_zone

        file = dm.File()
        datetime = dt.datetime.strptime(header[16:32], "%d.%m.%Y %H:%M")
        exacttime, = struct.unpack('>H', header[48:50])
        sectime = float(exacttime) / 625000
        datetime += dt.timedelta(seconds=sectime)

        normalizedtime = datetime - dt.timedelta(hours=timezone)
        file.date = normalizedtime.date()
        file.time = normalizedtime.time()

        file.location_id = thisloc.id
        file.headerHash = header[0:43]

        file.eventscreated = 0
        return file








import struct
import numpy as np
import common

class InputConverter:
    def __init__(self,midAdc,convFactor):
        self.midAdc = midAdc
        self.convFactor = convFactor

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
        datastruct.data = outputMatrix
        datastruct.timelen = expectedwidth

        return datastruct

    def readheader(self, filePath, fileName, conversionLog):
        try:
            d_file = open(filePath + "/" + fileName, mode='rb')
        except IOError as e:
            conversionLog.reportFailure(e.strerror)
            return
        return self.dcdheader(d_file.read(64))

    def dcdheader(self, header):
        initime, = struct.unpack('>H', header[48:50])
        date = header[16:26]
        time = header[26:32]
        location = header[0:16]

        return common.DataStruct(None, initime, None, 800, date, time, location, header)









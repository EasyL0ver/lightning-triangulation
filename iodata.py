import struct
import numpy as np
import common

class InputConverter:
    def __init__(self,midAdc,convFactor):
        self.midAdc = midAdc
        self.convFactor = convFactor

    def convert(self,filePath,fileName,conversionLog):
        try:
            d_file = open(filePath + "/" + fileName + ".dat", mode='rb')
        except IOError as e:
            conversionLog.reportFailure(e.strerror)
            return
        file = d_file.read()
        datalen = len(file)
        headerString = file[:43]
        initime, = struct.unpack('>H', file[48:50])
        expectedMatrixWidth = (datalen - 72)/4
        outputMatrix = np.zeros((2, expectedMatrixWidth))
        index = 0;
        for i in range(64, datalen-8, 4):
            e1, e2 = struct.unpack('>HH', file[i:i+4])
            outputMatrix[0, index] = (e1 - self.midAdc)/self.convFactor
            outputMatrix[1, index] = (e2 - self.midAdc)/self.convFactor
            index += 1

        return common.DataStruct(outputMatrix, initime, headerString)







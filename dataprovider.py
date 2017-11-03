import InputConverter as ic
import os
import common

class DataProvider:
    def __init__(self,currentdbsession):
        self.datasources = []
        self.converter = ic.InputConverter(65536/2,19.54)
        self.loadeddata = []
        self.currentdbsession = currentdbsession

    def loaddata(self):
        print("Loading data")
        #zaladuj hasze z db
        for i in range(0, len(self.datasources)):
            files = os.listdir(self.datasources[i])
            print("Converting files in: " + self.datasources[i])
            for o in range(0, len(files)):
                if self.issupported(files[o]):
                    cl = common.ConversionError()
                    #zczytaj naglowke i sprawdz hasz
                    data = self.converter.convert(self.datasources[i], files[o], cl)
                    if cl.conversionSucces:
                        print("Conversion of: " + files[o] + " successful")
                        self.loadeddata.append(data)
                    else:
                        print("Conversion of: " + files[o] + " failed: " + cl.conversionErrorLog )
            pass

    def issupported(self, fil):
        return fil.endswith('.dat')




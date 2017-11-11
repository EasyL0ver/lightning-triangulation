import InputConverter as ic
import os
import common
import datamodels as dm

class DataProvider:
    def __init__(self,currentdbsession):
        self.datasources = []
        self.converter = ic.InputConverter(65536/2,19.54)
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
            for o in range(0, len(files)):
                if self.issupported(files[o]):
                    cl = common.ConversionError()
                    header = self.converter.readheader(self.datasources[i], files[o], cl)
                    if not contains(hashes, header.headerHash):
                        data = self.converter.convert(self.datasources[i], files[o], cl)
                        if cl.conversionSucces:
                            print("Conversion of: " + files[o] + " successful")
                            self.loadeddata.append(data)
                            self.currentdbsession.add(data)
                        else:
                            print("Conversion of: " + files[o] + " failed: " + cl.conversionErrorLog )

            #todo try catch block
            print("Flushing db changes")
            self.currentdbsession.commit()
            pass

    def issupported(self, fil):
        return fil.endswith('.dat')





def contains(collection, element):
    for e in collection:
        if e[0] == element:
            return True
    return False






import baseprocessor
import numpy as np
import datamodels as dm


class EventToDbEndpoint(baseprocessor.FileProcessor):
    def __init__(self, orm):
        self.orm = orm
        self.children = None

    def process(self, events):
        for event in events:
            self.orm.getActiveSession().add(event)

    def flush(self):
        self.orm.getActiveSession().commit()


class LocalMaximumEventBlock(baseprocessor.FileProcessor):
    def __init__(self, prelen, postlen):
        self.children = []
        self.prelen = prelen
        self.postlen = postlen

    def process(self, infile):
        #przechodzi tylko rpzez jeden ciag danych, moze patrzec na wsyzstkie i wazyc wyniki ?
        data = infile.getdataarr()[0]
        #assert cluster data
        clusterdata = data["tcluster"]
        signal = data["dat"]

        arrevent = []
        for cluster in clusterdata:
            localmax = np.argmax(signal[cluster['start']:cluster['end']+1]) + cluster['start']
            evstart = localmax-self.prelen
            evend = localmax+self.postlen
            if evstart < 0:
                evstart = 0
            if evend > len(signal) - 1:
                evend = len(signal) - 1
            arrevent.append(dm.Event(firstsample=evstart, samplelen=evend-evstart, file_id=infile.id, event_type='basic_event'))

        #TODO TEN BUS DANYCH TRZEBA ZREFACTOROWAC QRWA ;/  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return arrevent


























import copy
import datetime as dt
import numpy as np

import common
import datamodels as dm
import vectorprocessor


class EntityToDbEndpoint(vectorprocessor.BaseProcessor):
    def __init__(self, orm):
        self.orm = orm
        self.children = None

    def process(self, events):
        for event in events:
            self.orm.getActiveSession().add(event)

    def flush(self):
        self.orm.getActiveSession().commit()


class LocalMaximumEventBlock(vectorprocessor.BaseProcessor):
    def __init__(self, prelen, postlen, ):
        self.children = []
        self.prelen = prelen
        self.postlen = postlen


    def process(self, infile):
        #przechodzi tylko rpzez jeden ciag danych, moze patrzec na wsyzstkie i wazyc wyniki ?
        data1 = infile.getdataarr()[0]
        data2 = infile.getdataarr()[1]

        #assert cluster data
        clusterdata = data1["tcluster"]
        signal = data1["dat"]
        signal2 = data2

        arrevent = []
        for cluster in clusterdata:
            localmax = np.argmax(signal[cluster['start']:cluster['end']+1]) + cluster['start']
            evstart = localmax-self.prelen
            evend = localmax+self.postlen
            if evstart < 0:
                evstart = 0
            if evend > len(signal) - 1:
                evend = len(signal) - 1
            arrevent.append(dm.Observation(firstsample=evstart, samplelen=evend-evstart,
                                           file_id=infile.id, event_type='basic_event',
                                           sample=localmax, sn_max_value=signal[localmax],
                                           ew_max_value=signal2[localmax]))

        #TODO TEN BUS DANYCH TRZEBA ZREFACTOROWAC QRWA ;/  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return arrevent


class TimeOffsetObservationConnectorBlock(vectorprocessor.BaseProcessor):
    def __init__(self, timedelta):
        self.children = []
        self.timedelta = timedelta

    def process(self, observations):
        #performance bottleneck here, crucial to optimize
        uniquelocs = set([observation.file.location.name for observation in observations])
        if len(uniquelocs) == 0:
            print("No Locations provided")
            return
        events = []
        for location in uniquelocs:
            for fobservation in observations:
                if fobservation.file.location.name == location:
                    locsleft = copy.deepcopy(uniquelocs)
                    locsleft.remove(location)
                    if not fobservation.assigned_event:
                        event = dm.Event(obs1_id=fobservation.id)
                        fobservation.assigned_event = event
                    else:
                        event = fobservation.assigned_event
                    fdatetime = common.cmbdt(fobservation.file.date, fobservation.file.time) + dt.timedelta(
                        seconds=float(fobservation.sample) / fobservation.file.fsample)
                    for sobservation in observations:
                        if sobservation.assigned_event:
                            continue
                        if len(locsleft) == 0:
                            break
                        if sobservation.file.location.name in locsleft:
                            #check if within timedelta
                            sdatetime = common.cmbdt(sobservation.file.date, sobservation.file.time) + dt.timedelta(seconds=float(sobservation.sample)/sobservation.file.fsample)
                            if fdatetime - self.timedelta < sdatetime < fdatetime + self.timedelta:
                                #append
                                if(event.obs2_id == None):
                                    event.obs2_id = sobservation.id
                                else:
                                    event.obs3_id = sobservation.id
                                sobservation.assigned_event = event;
                                #for optimization
                                locsleft.remove(sobservation.file.location.name)
                    events.append(event)
        return events































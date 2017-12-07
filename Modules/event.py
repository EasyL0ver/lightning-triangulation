import copy
import datetime as dt
import numpy as np

import common
import datamodels as dm
import linelement
from Modules import linelement as bsp


class EntityToDbEndpoint(linelement.BaseProcessor):
    def dbadd(self, events):
        for event in events:
            self.orm.getActiveSession().add(event)

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, orm, type):
        self.orm = orm
        self._children = None
        self._prcmodes = [bsp.ProcessingMode(self.dbadd, type)]

    def flush(self):
        self.orm.getActiveSession().commit()


class LocalMaximumEventBlock(linelement.BaseProcessor):
    def maxevent(self, clusterdata, signal, signal2, infile):
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

        return arrevent

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, prelen, postlen, ):
        self._children = []
        self.prelen = prelen
        self.postlen = postlen
        self._prcmodes = [bsp.ProcessingMode(self.maxevent, 'clstr_th', 'sn', 'ew', 'file', toname='obs')]





class TimeOffsetObservationConnectorBlock(linelement.BaseProcessor):
    def connect(self, observations):
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

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, timedelta):
        self._children = []
        self.timedelta = timedelta
        self._prcmodes = [bsp.ProcessingMode(self.connect, 'obs', toname='ev')]































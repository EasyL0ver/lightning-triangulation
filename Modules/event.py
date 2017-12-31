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
    def maxevent(self, clusterdata, signal, signal2, infile, pwrthresh):
        arrevent = []
        for cluster in clusterdata:
            localmax = np.argmax(pwrthresh[cluster['start']:cluster['end']+1]) + cluster['start']
            pwrmax = min((pwrthresh[localmax] / self.crttresh) * 100, 100)
            evstart = localmax-self.prelen
            evend = localmax+self.postlen
            if evstart < 0:
                evstart = 0
            if evend > len(signal) - 1:
                evend = len(signal) - 1
            #snmax = np.argmax(np.abs(signal[cluster['start']:cluster['end']+1])) + cluster['start']
            #ewmax = np.argmax(np.abs(signal2[cluster['start']:cluster['end'] + 1])) + cluster['start']
            arrevent.append(dm.Observation(firstsample=evstart, samplelen=evend-evstart,
                                           file_id=infile.id, event_type='basic_event',
                                           sample=localmax, sn_max_value=signal[localmax],
                                           ew_max_value=signal2[localmax], certain=pwrmax))
            infile.eventscreated = 1
        return arrevent

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, prelen, postlen, crttresh):
        self._children = []
        self.prelen = prelen
        self.postlen = postlen
        self.crttresh = crttresh
        self._prcmodes = [bsp.ProcessingMode(self.maxevent, 'clstr_th', 'sn', 'ew', 'file', 'pwr_th', toname='obs')]


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
                if fobservation.assigned_event:
                    continue
                if fobservation.file.location.name == location:
                    if fobservation.certain < self.crttresh:
                        continue
                    locsleft = copy.deepcopy(uniquelocs)
                    locsleft.remove(location)
                    event = dm.Event(obs1_id=fobservation.id)
                    fobservation.assigned_event = event
                    fdatetime = common.cmbdt(fobservation.file.date, fobservation.file.time) + dt.timedelta(
                        seconds=float(fobservation.sample) / fobservation.file.fsample)
                    posdict = dict()
                    for locleft in locsleft:
                        posdict[locleft] = []
                    for sobservation in observations:
                        if sobservation.assigned_event:
                            continue
                        if len(locsleft) == 0:
                            break
                        if sobservation.file.location.name in locsleft:
                            #check if within timedelta
                            sdatetime = common.cmbdt(sobservation.file.date, sobservation.file.time) + \
                                        dt.timedelta(seconds=float(sobservation.sample)/sobservation.file.fsample)
                            if fdatetime - self.timedelta < sdatetime < fdatetime + self.timedelta:
                                posdict[sobservation.file.location.name].append(sobservation)
                    #append
                    for key in posdict:
                        arr = posdict[key]
                        maxcert = 0
                        output = None
                        for obs in arr:
                            if obs.certain > maxcert:
                                maxcert = obs.certain
                                output = obs
                        if output is not None:
                            if event.obs2 is None:
                                event.obs2 = output
                                output.assigned_event = event
                            else:
                                event.obs3 = output
                                output.assigned_event = event


                    events.append(event)
        return events

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, timedelta, crttresh):
        self._children = []
        self.timedelta = timedelta
        self.crttresh = crttresh
        self._prcmodes = [bsp.ProcessingMode(self.connect, 'obs', toname='ev')]































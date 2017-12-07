import linelement as bsp
import scipy.signal as signal
import numpy as np


class ThresholdBlock(bsp.BaseProcessor):
    def pwrtresh(self, d1, d2):
        if len(d1) != len(d2):
            print(self.tostring() + " vector lenghts don't match")
            return
        outputvalues = np.zeros(len(d1))
        for i in range(0, len(d1)):
            if np.sqrt(np.power(d1[i], 2) + np.power(d2[i], 2)) >= self.thresh:
                outputvalues[i] = self.threshval
            else:
                outputvalues[i] = 0

        return outputvalues

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, thresh, thrshvalue):
        self.thresh = thresh
        self.threshval = thrshvalue
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.pwrtresh, 'sn', 'ew', toname='pwr_th')]


class ThresholdClusterBlock(bsp.BaseProcessor):
    def clstth(self, threshdata):
        #find fixed len event by local maxima
        stateHigh = False
        eventRanges = []

        if threshdata[0] > 0:
            stateHigh = True
            eventRanges.append({'start': 0, 'end': None})

        deadcnt = 0;
        for i in range(1, len(threshdata)-1):
            deadcnt = deadcnt - 1
            if threshdata[i] > 0 and threshdata[i-1] == 0 and not stateHigh and deadcnt <= 0:
                eventRanges.append({'start': i, 'end': None})
                stateHigh = True
            if threshdata[i] > 0 and threshdata[i + 1] == 0 and stateHigh:
                eventRanges[len(eventRanges)-1]['end'] = i
                stateHigh = False
                deadcnt = self.deadlen

        if stateHigh:
            eventRanges[len(eventRanges)-1]['end'] = len(threshdata)
        if not stateHigh and threshdata[len(threshdata)-1] == 1:
            eventRanges.append({'start': len(threshdata)-1, 'end': len(threshdata)-1})

        return eventRanges

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, deadlen):
        self._children = []
        self.deadlen = deadlen
        self._prcmodes = [bsp.ProcessingMode(self.clstth, 'pwr_th', toname='clstr_th')]











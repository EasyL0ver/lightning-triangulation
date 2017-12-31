import linelement as bsp
import scipy.signal as signal
import numpy as np


class ThresholdBlock(bsp.BaseProcessor):
    def pwrtresh(self, d1):
        outputvalues = np.zeros(len(d1))
        for i in range(0, len(d1)):
            if d1[i] >= self.thresh:
                outputvalues[i] = d1[i] - self.thresh
            else:
                outputvalues[i] = 0

        return outputvalues

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, thresh, thrshvalue, inputvals):
        self.thresh = thresh
        self.threshval = thrshvalue
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.pwrtresh, inputvals, toname='pwr_th')]


class PowerBlock(bsp.BaseProcessor):
    def pwrtresh(self, d1, d2):
        if len(d1) != len(d2):
            print(self.tostring() + " vector lenghts don't match")
            return
        outputvalues = np.zeros(len(d1))
        for i in range(0, len(d1)):
            outputvalues[i] = np.sqrt(np.power(d1[i], 2) + np.power(d2[i], 2))
        return outputvalues

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self):
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.pwrtresh, 'sn', 'ew', toname='pwr')]

class ThresholdClusterFilter(object):
    pass

class ThresholdClusterBlock(bsp.BaseProcessor):
    def clstth(self, threshdata):
        #find fixed len event by local maxima
        stateHigh = False
        eventRanges = []

        relcnt = 0;
        if threshdata[0] > 0:
            stateHigh = True
            eventRanges.append({'start': 0, 'end': None})
            relcnt = self.deadlen

        for i in range(1, len(threshdata)-1):
            if threshdata[i] > 0:
                relcnt = self.deadlen
                if threshdata[i-1] == 0 and not stateHigh:
                    eventRanges.append({'start': i, 'end': None})
                    stateHigh = True
            if threshdata[i] == 0 and stateHigh and relcnt <= 0:
                eventRanges[len(eventRanges)-1]['end'] = i
                stateHigh = False
            relcnt -= 1

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











import vectorprocessor as bsp
import scipy.signal as signal
import numpy as np


class ThresholdBlock(bsp.BaseProcessor):
    def __init__(self, thresh, thrshvalue):
        self.thresh = thresh
        self.threshval = thrshvalue
        self.children = []

    def process(self, data):
        dat = data.getdataarr()
        self.calcthresh(data)
        outputvalues = np.zeros(len(dat))
        for i in range(0, len(dat)):
            if np.sqrt(np.power(dat[0][i], 2) + np.power(dat[0][i], 2)) >= self.getthresh(i):
                outputvalues[i] = self.threshval
            else:
                outputvalues[i] = 0

        dat[0] = {'dat': dat[0], 'thresh': outputvalues}
        return data


    def getthresh(self, i):
        return self.thresh

    def calcthresh(self, data):
        pass


class ThresholdClusterBlock(bsp.VectorProcessor):
    def __init__(self,deadlen):
        self.children = []
        self.deadlen = deadlen

    def process(self, data):
        #assert threshold data
        if "thresh" not in data:
            return data
        threshdata = data["thresh"]

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

        data['tcluster'] = eventRanges
        return data











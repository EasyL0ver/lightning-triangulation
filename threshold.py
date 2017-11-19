import baseprocessor as bsp
import scipy.signal as signal
import numpy as np


class ThresholdBlock(bsp.BaseProcessor):
    def __init__(self, thresh, thrshvalue):
        self.thresh = thresh
        self.threshval = thrshvalue
        self.children = []

    def process(self, data):
        self.calcthresh(data)
        outputvalues = np.zeros(len(data))
        for i in range(0, len(data)):
            if data[i] >= self.getthresh(i):
                outputvalues[i] = self.threshval
            else:
                outputvalues[i] = 0

        return {'dat': data, 'thresh': outputvalues}


    def getthresh(self,i):
        return self.thresh

    def calcthresh(self,data):
        pass


class ThresholdClusterBlock(bsp.BaseProcessor):
    def __init__(self):
        self.children = []

    def process(self, data):
        #assert threshold data
        threshdata = data["thresh"]

        #find fixed len event by local maxima
        stateHigh = False
        eventRanges = []

        if threshdata[0] > 0:
            stateHigh = True
            eventRanges.append({'start': 0, 'end': None})

        for i in range(1, len(threshdata)-1):
            if threshdata[i] > 0 and threshdata[i-1] == 0 and not stateHigh:
                eventRanges.append({'start': i, 'end': None})
                stateHigh = True
            if threshdata[i] > 0 and threshdata[i + 1] == 0 and stateHigh:
                eventRanges[len(eventRanges)-1]['end'] = i
                stateHigh = False

        if stateHigh:
            eventRanges[len(eventRanges)]['end'] = len(threshdata)
        if not stateHigh and threshdata[len(threshdata)-1] == 1:
            eventRanges.append({'start': len(threshdata)-1, 'end': len(threshdata)-1})

        data['tcluster'] = eventRanges
        return data



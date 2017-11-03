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
        for i in range(0,len(data)):
            if data[i] >= self.getthresh(i):
                outputvalues[i] = self.threshval
            else:
                outputvalues[i] = 0
        self.pushDataToChildren(outputvalues)

    def getChildren(self):
        return self.children

    def getthresh(self,i):
        return self.thresh

    def calcthresh(self,data):
        pass


class RmsThresholdBlock(ThresholdBlock):
    def __init__(self,thfactor):
        self.thfactor = thfactor
        self.children = []



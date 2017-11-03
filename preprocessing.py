import BaseSignalProcessor as bsp
import scipy.signal as signal

class PreProcessFilter(bsp.BaseSignalProcessor):
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1

        self.children = [];

    def process(self,data):
        return signal.convolve(data, self.filter)
    def getChildren(self):
        return self.children



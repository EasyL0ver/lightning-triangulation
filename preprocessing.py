from pylab import *
import scipy.signal as signal

class PreProcessFilter:
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1

    def filterData(self,data):
        return signal.convolve(data,self.filter)


import vectorprocessor as bsp
import scipy.signal as signal
import common


class HPFilter(bsp.VectorProcessor):
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1
        self.children = [];

    def process(self, data):
        return signal.convolve(data, self.filter)


class LPFilter(bsp.VectorProcessor):
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.children = [];

    def process(self, data):
        return signal.convolve(data, self.filter)



class BandStopFilter(bsp.VectorProcessor):
    def __init__(self, band, bandwidth, taps):
        f1 = band - bandwidth
        f2 = band + bandwidth
        if f1 < 0.01:
            f1 = 0.01
        if f2 > 0.99:
            f2 = 0.99
        self.filter = signal.firwin(taps, [f1, f2])
        self.children = []

    def __str__(self):
        return "BandStopFilter"

    def process(self, data):
        #common.mfreqz(self.filter)
        return signal.convolve(data, self.filter)


class RegionBasedBandStop(bsp.BaseProcessor):
    def __init__(self, bandwidth, taps):
        self.bandstopdict = dict()
        self.children = []
        self.bandwidth = bandwidth
        self.taps = taps

    def process(self, file):
        if not file.location.reqionfreq:
            return file
        locfreq = float(file.location.reqionfreq)/float(file.fsample/2)
        if locfreq not in self.bandstopdict:
            self.bandstopdict[locfreq] = BandStopFilter(locfreq, self.bandwidth, self.taps)

        datarr = file.getdataarr()
        for i in range(0, len(datarr)):
            dat = datarr[i]
            if dat is not None:
                bandstop = self.bandstopdict[locfreq]
                datarr[i] = bandstop.process(datarr[i])
                file.cachedatamodified = True
        return file










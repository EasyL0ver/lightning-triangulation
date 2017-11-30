import baseprocessor as bsp
import scipy.signal as signal


class HPFilter(bsp.BaseProcessor):
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1
        self.children = [];

    def process(self, data):
        return signal.convolve(data, self.filter)


class LPFilter(bsp.BaseProcessor):
    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.children = [];

    def process(self, data):
        return signal.convolve(data, self.filter)


class BandStopFilter(bsp.BaseProcessor):
    def __init__(self, band, bandwidth, taps):
        f1 = band - bandwidth
        f2 = band + bandwidth
        if f1 < 0.01:
            f1 = 0.01
        if f2 > 0.99:
            f2 = 0.99
        self.filter = signal.firwin(taps, [f1, f2])
        self.children = []

    def process(self, data):
        return signal.convolve(data, self.filter)










import linelement as bsp
import scipy.signal as signal
import numpy as np

import datetime as dt
import io
import numpy as np
import scipy.signal as signal
import sqlite3
import datamodels
import sys
from pylab import *


class HPFilter(bsp.BaseProcessor):
    def flt(self, data):
        a = signal.convolve(data, self.filter)
        return a

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'), bsp.ProcessingMode(self.flt, 'ew')]


class LPFilter(bsp.BaseProcessor):
    def flt(self, data):
        return signal.convolve(data, self.filter)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'), bsp.ProcessingMode(self.flt, 'ew')]


class AntiAliasingDeconvolveBlock(bsp.BaseProcessor):
    def flt(self, data):
        recovered, remainder = signal.deconvolve(data, self.filter)
        return recovered

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'),
                          bsp.ProcessingMode(self.flt, 'ew')]


class BandStopFilter(bsp.BaseProcessor):
    def flt(self, data):
        return signal.convolve(data, self.filter)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, band, bandwidth, taps):
        f1 = band - bandwidth
        f2 = band + bandwidth
        if f1 < 0.01:
            f1 = 0.01
        if f2 > 0.99:
            f2 = 0.99
        self.filter = signal.firwin(taps, [f1, f2])
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn'), bsp.ProcessingMode(self.flt, 'ew')]


class HilbertEnvelopeBlock(bsp.BaseProcessor):
    def calc_envelope(self, data):
        return np.abs(signal.hilbert(data))

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, parameter):
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.calc_envelope, parameter, toname='env')]


class AverageFilterEnvelope(bsp.BaseProcessor):
    def flt(self, data):
        return signal.convolve(data, self.filter)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, leng, parameter):
        self.filter = np.ones(leng) / leng
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, parameter, toname='env')]


class RegionBasedBandStop(bsp.BaseProcessor):
    def region_filter(self, vector, file):
        if not file.location.reqionfreq:
            return vector
        frequency = float(file.location.reqionfreq)/float(file.fsample/2)
        if frequency not in self.filter_dictionary:
            self.filter_dictionary[frequency] = BandStopFilter(frequency, self.bandwidth, self.taps)

        bandstop = self.filter_dictionary[frequency]
        return bandstop.flt(vector)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, bandwidth, taps):
        self.filter_dictionary = dict()
        self._children = []
        self.bandwidth = bandwidth
        self.taps = taps
        self._prcmodes = [bsp.ProcessingMode(self.region_filter, 'ew', 'file'),
                          bsp.ProcessingMode(self.region_filter, 'sn', 'file')]


def mfreqz(b,a=1):
    w,h = signal.freqz(b,a)
    h_dB = 20 * log10 (abs(h))
    subplot(211)
    plot(w/max(w),h_dB)
    ylim(-150, 5)
    ylabel('Magnitude (db)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Frequency response')
    subplot(212)
    h_Phase = unwrap(arctan2(imag(h),real(h)))
    plot(w/max(w),h_Phase)
    ylabel('Phase (radians)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Phase response')
    subplots_adjust(hspace=0.5)







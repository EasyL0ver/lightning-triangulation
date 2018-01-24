#-*- coding: utf-8 -*-

import datetime as dt
import io
import sqlite3

from scipy import signal
from pylab import *
from Modules import linelement as bsp
from Modules.linelement import DataBus


class ConversionError(object):
    def __init__(self):
        self.conversionSucces = True
        self.conversionErrorLog = "Wszystko spoko!"

    def reportFailure(self, errorlog):
        self.conversionSucces = False
        self.conversionErrorLog = errorlog


class TestPlotBlock(bsp.BaseProcessor):
    def on_entry(self, dbus):
        figure(self.figuren)
        super(TestPlotBlock, self).on_enter(dbus)

    def plt(self, data):
        if data is not None:
            plot(data)

    def push_data(self, data):
        if self.pltsetting:
            show()
        super(TestPlotBlock, self).push_data(data)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, figuren, pltsetting, *plots):
        self.figuren = figuren
        self._children = []
        self._prcmodes = []
        self.pltsetting = pltsetting
        for pl in plots:
            self._prcmodes.append(bsp.ProcessingMode(self.plt, pl))


class FftPlotBlock(TestPlotBlock):
    def plt(self, data):
        if data is not None:
            n = len(data)
            k = np.arange(n)
            T = n / 887.7840909
            frq = k / T
            frq = frq[range(n / 2)]

            Y = np.fft.fft(data) / n
            Y = Y[range(n / 2)]
            plot(frq, abs(Y), 'r')
            xlabel(u'Częstotliwość [Hz]')
            ylabel(u'Amplituda [pT]')


def tocartesianyxz(lon, lat):
    carvec = [None] * 3
    carvec[0] = np.cos(lon) * np.cos(lat)
    carvec[1] = np.cos(lat) * np.sin(lon)
    carvec[2] = np.sin(lat)
    return carvec


def invertbearing(ang):
    negang = ang + np.pi
    if negang > np.pi * 2:
        negang -= np.pi * 2
    return negang


def printrange(provider, date, len, entry):
    data = provider.get_data(date, len)
    for dsingle in data:
        dbus = DataBus()
        dbus.data = dsingle
        entry.on_enter(dbus)


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


def binarytonp(binary, midadc, conv):
    # use a compressor here
    out = io.BytesIO(binary)
    out.seek(0)
    output = np.load(out).astype(float64)
    output = (output - midadc)/conv
    return output


def nptobinary(npdata):
    out = io.BytesIO()
    np.save(out, npdata)
    out.seek(0)
    output = sqlite3.Binary(out.read())
    return output


def cmbdt(date,time):
    return dt.datetime.combine(date, time)




#-*- coding: utf-8 -*-

import datetime as dt
import io
import sqlite3

from scipy import signal
from pylab import *

from Data import datamodels
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


def creatmockdata(loc,start,angle):
    lent = 266350
    f = datamodels.File()
    f.headerHash = "test"
    f.mid_adc = 65536 / 2
    f.conv_fac = 19.54
    f.date = dt.datetime(month=1, day=1, year=2012).date()
    f.time = dt.datetime(month=1, day=1, year=2012).time()
    f.dat1type = "sn elf"
    f.dat2type = "ew elf"
    f.eventscreated = 0
    f.fsample = 887.7840909
    f.location = loc
    f.expectedlen = lent

    x = np.arange(lent)
    noise1 = 400 *np.sin(2 * np.pi * 50 * x / f.fsample)
    noise2 = 4000 * np.sin(2 * np.pi * 0.02 * x / f.fsample)
    noise3 = 800 + np.random.rand(lent)


    sndata = np.ones(lent)
    sndata += 65536 / 2
    #sndata += noise1
    #sndata +=noise2
    #sndata += noise3
    figure(1)

    ewdata =np.ones(lent)
    ewdata += 65536 / 2
    #ewdata += noise1
    #ewdata += noise2
    #ewdata +=noise3

    if angle:
        ewdata[start:start + 10] = 15000
        #sndata[start:start + 10] = 15000
    else:
        sndata[start:start + 10] = 15000



    f.dat1 = nptobinary(sndata)
    f.dat2 = nptobinary(ewdata)
    plot(binarytonp(f.dat1, f.mid_adc, f.conv_fac))
    plot(binarytonp(f.dat2, f.mid_adc, f.conv_fac))
    show()
    return f


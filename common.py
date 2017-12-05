import datetime as dt
import io
import numpy as np
import scipy.signal as signal
import sqlite3
import sys
from pylab import *

from Modules import vectorprocessor as bsp


class ConversionError(object):
    def __init__(self):
        self.conversionSucces = True
        self.conversionErrorLog = "Wszystko spoko!"

    def reportFailure(self, errorlog):
        self.conversionSucces = False
        self.conversionErrorLog = errorlog



class TestPlotBlock(bsp.BaseProcessor):
    def __init__(self, figuren, plot):
        self.figuren = figuren
        self.plot = plot
        self.children = None

    def process(self, data1):
        data0 = data1.getdataarr()[0]
        data1 = data1.getdataarr()[1]
        if self.plot == True:
            figure(self.figuren)
            plot(data0['dat'])
            show()
        if self.plot == False:
            print(data)


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
